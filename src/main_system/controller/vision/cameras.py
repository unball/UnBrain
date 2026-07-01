import cv2
import time
import threading
from pkg_resources import resource_filename
from os import listdir

from main_system.model.vision.camerasModel import CameraHandlerModel

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
                cap = cv2.VideoCapture(target_index)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
                cap.set(cv2.CAP_PROP_FOURCC, fourcc)
                cap.set(cv2.CAP_PROP_FPS, 120)
                # Buffer de 1 frame: entrega sempre o frame mais recente em vez de
                # acumular frames antigos (reduz latência de visão e a torna constante).
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                self.__cap = cap

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
    
    
