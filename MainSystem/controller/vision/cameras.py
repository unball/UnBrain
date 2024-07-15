import cv2
import time
from pkg_resources import resource_filename
from os import listdir

from model.vision.camerasModel import CameraHandlerModel

class CameraHandler():
  """Classe que gerencia as câmeras do sistema permitindo rápida troca e retorno simples de frames"""
  def __init__(self):
    self.__cameras = []
    """Conjunto de câmeras disponíveis"""
    
    self.__model = CameraHandlerModel()
    """Modelo `MainSystem.model.vision.camerasModel.CameraHandlerModel` que mantém as variáveis permanentes do gerenciador de câmeras"""
    
    self.__defaultFrame = cv2.imread(resource_filename(__name__, "defaultFrame.png"))
    """Armazena o frame padrão"""
    
    self.__cap = None
    """Armazena o `VideoCapture` atual"""
    
    self.__show_rotated = False
    """variavel de rotação de camera"""
    
    
  def setScale(self, scale: float):
    """Altera o valor da escala usada no frame"""
    self.__model.frame_scale = scale
    
  def set_rotate_field(self, value: bool):
    """Atualiza flag que indica se é para mostrar o campo rotacionado ou não"""

    self.__show_rotated = value
    
  def getScale(self):
    """Obtém o valor da escala usada no frame"""
    return self.__model.frame_scale
    
  def scaleFrame(frame, scale: float):
    """Muda o tamanho, mantendo a proporção, de um frame de acordo com uma escala."""
    scale = max(scale, 0.01)
    return cv2.resize(frame, (round(frame.shape[1]*scale), round(frame.shape[0]*scale)))
    
  def getFrame(self):
    """Retorna um frame no formato numpy (height, width, depth) com base na câmera atualmente selecionada."""
    
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
      
      if self.__cap is not None and self.__cap.isOpened():
        ret, frame = self.__cap.read()
        if self.__show_rotated:
          frame = cv2.rotate(frame, cv2.ROTATE_180)
        
        
              
        if frame is None: 
          time.sleep(0.001)
          return None
        return CameraHandler.scaleFrame(frame, self.__model.frame_scale)
    except:
      print("Falha no módulo CameraHandler getFrame")
      time.sleep(0.001)
      return None
      
    return None
    
  def setCamera(self, index):
    """Seleciona a câmera de índice `index`"""
    # Libera a câmera em uso
    if self.__cap is not None: self.__cap.release()
    
    # Aloca a nova câmera
    if index != -1: 
      cap = cv2.VideoCapture(index)
      cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
      cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

      #Codec da câmera atual
      fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
      cap.set(cv2.CAP_PROP_FOURCC, fourcc)
      cap.set(cv2.CAP_PROP_FPS, 90)
      self.__cap = cap
    
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
    
    
