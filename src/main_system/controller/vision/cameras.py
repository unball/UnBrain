import cv2
import time
import threading
import subprocess
import numpy as np
from pkg_resources import resource_filename
from os import listdir

from main_system.model.vision.camerasModel import CameraHandlerModel


class FFmpegCameraCapture:
  """Captura frames de uma câmera V4L2 via um processo `ffmpeg` externo, em vez do
  `cv2.VideoCapture`. Existe porque o backend V4L2 do OpenCV, empiricamente, não
  consegue sustentar o FPS negociado nesta câmera (trava perto de 30fps mesmo com
  MJPG 640x480@120fps aceito pelo driver via cap.set/cap.get) — enquanto o mesmo
  modo, capturado com `ffmpeg` como processo externo, sustenta 120fps reais
  (confirmado com `ffmpeg ... -f null -` e conferido via dmesg sem nenhum aviso de
  banda/negociação). Expõe a mesma interface mínima usada pelo `_camera_drain_loop`
  (`read`/`isOpened`/`release`) para não precisar mexer no resto do pipeline.

  Uma thread própria lê continuamente do pipe do ffmpeg e guarda só o frame mais
  recente — do mesmo jeito que o CAP_PROP_BUFFERSIZE=1 fazia no cv2.VideoCapture —
  para não acumular latência caso o consumidor (o drain loop) fique mais lento que
  os 120fps que o ffmpeg entrega.
  """

  WIDTH = 640
  HEIGHT = 480
  FRAME_BYTES = WIDTH * HEIGHT * 3  # bgr24, sem padding

  def __init__(self, index):
    cmd = [
      "ffmpeg", "-hide_banner", "-loglevel", "error",
      "-f", "v4l2", "-input_format", "mjpeg",
      "-video_size", f"{self.WIDTH}x{self.HEIGHT}", "-framerate", "120",
      "-i", f"/dev/video{index}",
      "-pix_fmt", "bgr24", "-f", "rawvideo", "-an", "pipe:1",
    ]
    self.__proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    self.__lock = threading.Lock()
    self.__latest_frame = None
    # Sinaliza quando um frame NOVO chega — sem isso, read() poderia devolver o
    # mesmo frame em cache várias vezes por chamada, inflando artificialmente a
    # contagem de FPS de quem consome via um loop apertado tipo
    # `_camera_drain_loop` (cada chamada bem-sucedida a .read() conta como 1
    # frame). O cv2.VideoCapture.read() original bloqueava até o próximo frame
    # real; replicamos esse contrato aqui.
    self.__frame_ready = threading.Event()
    self.__running = True
    self.__reader_thread = threading.Thread(target=self.__read_loop, daemon=True)
    self.__reader_thread.start()

  def __read_loop(self):
    stdout = self.__proc.stdout
    try:
      while self.__running:
        buf = bytearray()
        while len(buf) < self.FRAME_BYTES:
          chunk = stdout.read(self.FRAME_BYTES - len(buf))
          if not chunk:
            self.__running = False
            return
          buf.extend(chunk)
        frame = np.frombuffer(bytes(buf), dtype=np.uint8).reshape((self.HEIGHT, self.WIDTH, 3))
        with self.__lock:
          self.__latest_frame = frame
        self.__frame_ready.set()
    except Exception:
      self.__running = False

  def isOpened(self):
    return self.__running and self.__proc.poll() is None

  def read(self):
    """Bloqueia até o próximo frame NOVO (não repete o último em cache), igual o
    cv2.VideoCapture.read() original — importante pra contagem de FPS ficar correta."""
    if not self.isOpened():
      return False, None
    got_new_frame = self.__frame_ready.wait(timeout=1.0)
    if not got_new_frame:
      return False, None
    with self.__lock:
      frame = self.__latest_frame
      self.__frame_ready.clear()
    if frame is None:
      return False, None
    return True, frame

  def release(self):
    self.__running = False
    if self.__proc.poll() is None:
      self.__proc.terminate()
      try:
        self.__proc.wait(timeout=1.0)
      except subprocess.TimeoutExpired:
        self.__proc.kill()
    if self.__proc.stdout:
      self.__proc.stdout.close()


class CameraHandler():
  """Classe que gerencia as câmeras do sistema permitindo rápida troca e retorno simples de frames"""
  def __init__(self):
    self.__cameras = []
    """Conjunto de câmeras disponíveis"""
    
    self.__model = CameraHandlerModel()
    """Modelo `MainSystem.model.vision.camerasModel.CameraHandlerModel` que mantém as variáveis permanentes do gerenciador de câmeras"""
    
    # Força a câmera a iniciar desligada (-1), ignorando o que foi salvo no vars.json da sessão passada
    self.__model.current_camera = -1

    self.__defaultFrame = cv2.imread(resource_filename(__name__, "defaultFrame.png"))
    """Armazena o frame padrão"""
    
    self.__cap = None
    """Armazena o `VideoCapture` atual"""
    
    self.__show_rotated = False
    
    self.__paused = False
    
    self.__frame_lock = threading.Lock()
    self.__latest_frame_raw = None
    self.__latest_frame_ts = None
    """Instante (time.perf_counter) em que o último frame cru foi capturado."""
    self.camera_frame_count = 0
    self.last_fps_time = time.time()
    self.current_camera_fps = 0.0
    self.__current_cap_index = -1
    
    self.__drain_thread = threading.Thread(target=self._camera_drain_loop, daemon=True)
    self.__drain_thread.start()
    
  def setScale(self, scale: float):
    """Altera o valor da escala usada no frame"""
    self.__model.frame_scale = scale
    
  def set_rotate_field(self, value: bool):
    """Atualiza flag que indica se é para mostrar o campo rotacionado ou não"""

    self.__show_rotated = value
    
  def set_paused(self, value: bool):
    """Pausa ou despausa a recepção de frames do video/camera"""
    self.__paused = value
    
  def getScale(self):
    """Obtém o valor da escala usada no frame"""
    return self.__model.frame_scale
    
  def scaleFrame(frame, scale: float):
    """Muda o tamanho, mantendo a proporção, de um frame de acordo com uma escala."""
    scale = max(scale, 0.01)
    return cv2.resize(frame, (round(frame.shape[1]*scale), round(frame.shape[0]*scale)))
    
  def _camera_drain_loop(self):
    """Loop que suga incansavelmente a câmera para evitar que o OpenCV acumule frames velhos na fila."""
    while True:
      try:
        target_index = self.__model.current_camera
        
        # Verifica se precisamos trocar de câmera (ou desligar)
        if target_index != self.__current_cap_index:
            if self.__cap is not None:
                self.__cap.release()
                self.__cap = None
            
            self.__current_cap_index = target_index
            
            if target_index == -2:
                video_path = '/home/maranhas/UnBall/UnBrain/test_videos/VSSS.mp4'
                import os
                if not os.path.exists(video_path):
                    print(f"ERRO: O vídeo de teste não foi encontrado em {video_path}")
                cap = cv2.VideoCapture(video_path)
                self.__cap = cap
            elif target_index != -1:
                # cv2.VideoCapture (backend V4L2) negocia corretamente MJPG
                # 640x480@120fps (cap.get confirma), mas empiricamente não sustenta
                # esse FPS de verdade nesta câmera (trava perto de 30fps). O mesmo
                # modo, capturado via processo `ffmpeg` externo, sustenta 120fps
                # reais — confirmado com `ffmpeg -f v4l2 ... -f null -` e sem
                # nenhum aviso de banda/negociação no dmesg. Ver FFmpegCameraCapture.
                try:
                    cap = FFmpegCameraCapture(target_index)
                    self.__cap = cap
                except Exception as e:
                    print(f"[CameraHandler] Falha ao iniciar ffmpeg para câmera {target_index}: {e}")
                    self.__cap = None

        # Leitura da câmera ativa
        if self.__cap is not None and self.__cap.isOpened():
          if self.__current_cap_index == -2 and self.__paused:
              time.sleep(0.05)
              continue
              
          ret, frame = self.__cap.read()
          if ret and frame is not None:
            if not self.__paused:
                with self.__frame_lock:
                    self.__latest_frame_raw = frame
                    self.__latest_frame_ts = time.perf_counter()
                self.camera_frame_count += 1
            
            if self.__current_cap_index == -2:
                # Simula o tempo real do FPS original do vídeo
                fps = self.__cap.get(cv2.CAP_PROP_FPS)
                if fps > 0:
                    time.sleep(1.0 / fps)
                    
                # Loop dos primeiros 38 segundos
                current_frame = self.__cap.get(cv2.CAP_PROP_POS_FRAMES)
                if fps > 0 and current_frame >= fps * 38:
                    self.__cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
          else:
            if self.__current_cap_index == -2:
                # Reinicia o vídeo automaticamente (loop caso chegue no fim antes dos 38s)
                self.__cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                time.sleep(0.005)
        else:
          time.sleep(0.01)
      except Exception as e:
        print("Drain loop EXC:", e)
        time.sleep(0.01)

  def getFrame(self):
    """Retorna um frame instantaneamente baseado na última foto tirada na Thread secundária."""
    try:
      if self.__model.current_camera == -1:
        time.sleep(0.001)
        if self.__defaultFrame is None: return None 
        if self.__show_rotated:
          frame = cv2.rotate(self.__defaultFrame, cv2.ROTATE_180)
        else:
          frame = self.__defaultFrame
        return CameraHandler.scaleFrame(frame, self.__model.frame_scale)
      
      if self.__cap is None:
        self.setCamera(self.__model.current_camera)
      
      frame = self.__latest_frame_raw
      
      if frame is None:
        time.sleep(0.001)
        return None
        
      if self.__show_rotated:
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        
      return CameraHandler.scaleFrame(frame, self.__model.frame_scale)
    except Exception as e:
      print("EXC:", e)
      print("Falha no módulo CameraHandler getFrame")
      time.sleep(0.001)
      return None

  def getFrameWithCaptureTime(self):
    """Igual a getFrame(), mas devolve (frame, capture_ts) lendo o frame cru e o
    seu instante de captura atomicamente (sob lock). Usado para medir latência
    interna do pipeline (Método C). capture_ts pode ser None se ainda não houver
    frame real (câmera desligada/sem captura)."""
    try:
      if self.__model.current_camera == -1:
        # Sem câmera real: reaproveita o frame padrão, sem timestamp de captura.
        return self.getFrame(), None

      if self.__cap is None:
        self.setCamera(self.__model.current_camera)

      with self.__frame_lock:
        frame = self.__latest_frame_raw
        ts = self.__latest_frame_ts

      if frame is None:
        time.sleep(0.001)
        return None, None

      if self.__show_rotated:
        frame = cv2.rotate(frame, cv2.ROTATE_180)

      return CameraHandler.scaleFrame(frame, self.__model.frame_scale), ts
    except Exception as e:
      print("EXC:", e)
      print("Falha no módulo CameraHandler getFrameWithCaptureTime")
      time.sleep(0.001)
      return None, None

  def getCameraFPS(self):
    """Calcula e retorna o FPS real da câmera"""
    current_time = time.time()
    dt = current_time - self.last_fps_time
    if dt >= 1.0:
        self.current_camera_fps = self.camera_frame_count / dt
        self.camera_frame_count = 0
        self.last_fps_time = current_time
    return self.current_camera_fps
    
  def setCamera(self, index):
    """Seleciona a câmera de índice `index`. A abertura/fechamento real acontece na thread de background."""
    self.__model.current_camera = index
    
  def getCamera(self):
    """Retorna o índice de câmera selecionado"""
    return self.__model.current_camera
    
  def updateCameras(self):
    """Atualiza a lista de câmeras detectadas"""
    self.__cameras = [c for c in listdir("/sys/class/video4linux/")]
    
  def getCameras(self):
    """Retorna as câmeras detectadas"""
    return self.__cameras
    
    
