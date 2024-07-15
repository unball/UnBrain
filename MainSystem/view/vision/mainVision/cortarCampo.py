from gi.repository import Gtk
from pkg_resources import resource_filename
from view.tools.frameSelector import FrameRenderer
from controller.tools.pixel2metric import normToAbs
from model.vision.cortarCampoModel import CortarCampoModel
import cv2
import numpy as np

class CortarCampo(FrameRenderer):
  """FrameRenderer que implementa a configuração de corte de campo, tanto com corte retangular quanto com homografia"""
  
  def __init__(self, notebook, controller, visionSystem, eventBox):
    self.__visionSystem = visionSystem
    self.__controller = controller
    self.__eventBox = eventBox
    
    self.__show_warpped = False
    """Indica se é para renderizar uma versão cortada ou não do frame vindo da camera"""
    
    self.__model = CortarCampoModel()
    """Mantém as variáveis permanentes do módulo view de cortar campo"""
    
    self.__current_mouse_position = (0,0)
    """Mantém a posição do mouse em cima do frame"""
    
    
    super().__init__(notebook, "Cortar campo")
    
  def ui(self):
    """Conteúdo a ser inserido na interface da configuração de cortar campo"""
    
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "cortarCampo.ui"))
    builder.get_object("campo_switch").connect("state-set", self.set_show_mode)
    self.__eventBox.connect("button-press-event", self.update_points)
    self.__eventBox.connect("motion-notify-event", self.mouse_over)
    
    return builder.get_object("main")
    
  def connectSpecialSignals(self):
    """Desbloqueia os sinais de clique e mouse sobreposto"""
    self.__eventBox.handler_unblock_by_func(self.update_points)
    self.__eventBox.handler_unblock_by_func(self.mouse_over)
    
  def disconnectSpecialSignals(self):
    """Bloqueia os sinais de clique e mouse sobreposto"""
    self.__eventBox.handler_block_by_func(self.update_points)
    self.__eventBox.handler_block_by_func(self.mouse_over)
  
  def set_show_mode(self, widget, value):
    """Atualiza flag que indica se é para mostrar o campo cortado ou não"""
    self.__show_warpped = value
  
  def set_crop_mode(self, widget, value):
    """Atualiza flag da visão que indica se é para usar ou não homografia"""
    self.__controller.addEvent(self.__visionSystem.setUseHomography, value)
    
  def getRelPoint(self, widget, event):
    """Com base no evento e no widget de eventBox, calcula a posição relativa do mouse no frame"""
    x = event.x/widget.get_allocated_width()
    y = event.y/widget.get_allocated_height()
    
    return (x,y)
    
  def update_points(self, widget, event):
    """Se não estiver mostrando a imagem cortada, o clique adicionará o ponto clicado na lista de pontos clicados de homografia ou de corte retangular, a depender dea flag `use_homography` da visão. Se o número de pontos for suficiente para fazer o corte, atualiza a visão com esses pontos."""
    if self.__show_warpped: return
    
    point = self.getRelPoint(widget, event)
    
    if len(self.__model.clicked_points_homography) == 4: self.__model.clicked_points_homography.clear()
    self.__model.clicked_points_homography.append(point)
      
    self.update_vision_points()
  
  def update_vision_points(self):
    """Atualiza a visão com os novos pontos"""
    if len(self.__model.clicked_points_homography) == 4:
      self.__controller.addEvent(self.__visionSystem.updateHomographyPoints, self.__model.clicked_points_homography.copy())
   
  def mouse_over(self, widget, event):
    """Evento quando o mouse sobrepõe o frame, este método atualiza a posição relativa do mouse"""
    self.__current_mouse_position = self.getRelPoint(widget, event)
    
  def getFrame(self):
    """Produz o frame a ser renderizado pelo modo de configuração do corte de campo"""
    frame = self.__visionSystem.cameraHandler.getFrame()
    if frame is None: return None
    
    if self.__show_warpped: return self.__visionSystem.warp(frame)
    else:
      color = (0,255,0) if len(self.__model.clicked_points_homography) == 4 else (255,255,255)
      mousePos = normToAbs(self.__current_mouse_position, frame.shape)
  
      # Draw line for each pair of points
      if len(self.__model.clicked_points_homography) > 1:
        for i in range(len(self.__model.clicked_points_homography)-1):
          p0 = normToAbs(self.__model.clicked_points_homography[i], frame.shape)
          p1 = normToAbs(self.__model.clicked_points_homography[i+1], frame.shape)
          cv2.line(frame, p0, p1, color, thickness=2)
      
      # Closes rectangle
      if len(self.__model.clicked_points_homography) == 4:
        p0 = normToAbs(self.__model.clicked_points_homography[0], frame.shape)
        p1 = normToAbs(self.__model.clicked_points_homography[3], frame.shape)
        cv2.line(frame, p0, p1, color, thickness=2)
      
      # Draw helping line from last chosen point to current mouse position
      if len(self.__model.clicked_points_homography) > 0 and len(self.__model.clicked_points_homography) < 4:
        plast = normToAbs(self.__model.clicked_points_homography[-1], frame.shape)
        p0 = normToAbs(self.__model.clicked_points_homography[0], frame.shape)
        cv2.line(frame, plast, mousePos, (255,255,255))
        # Draw extra line from first chosen point to current position when it's the last point to be chosen
        if len(self.__model.clicked_points_homography) == 3:
          cv2.line(frame, p0, mousePos, color)
      
      for i in range(len(self.__model.clicked_points_homography)):
        p0 = normToAbs(self.__model.clicked_points_homography[i], frame.shape)
        cv2.circle(frame, p0, 5, color, thickness=-1)
        
      return frame
        
        
