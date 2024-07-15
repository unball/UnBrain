from gi.repository import Gtk
from pkg_resources import resource_filename
from view.tools.frameSelector import FrameRenderer
from view.tools.drawing import Drawing
from controller.tools.pixel2metric import  meters2pixel,meters2pixelSize
from view.vision.mainVision.visaoAltoNivel import VisaoAltoNivel
import cv2
import numpy as np

class ParametrosVisao(FrameRenderer):
  """Essa classe implementa o FrameRenderer que permite configurar diversos parâmetros da visão"""
  
  def __init__(self, notebook, controller, visionSystem, world):
    self.__visionSystem = visionSystem
    self.__controller = controller
    self.__world = world
    super().__init__(notebook, "Parâmetros da visão")
    
  def ui(self):
    """Conteúdo a ser inserido na interface da configuração de parâmetros da visão"""
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "parametrosVisao.ui"))
    
    builder.get_object("adj_area_cont_rect").set_value(self.__visionSystem.areaRatio)
    builder.get_object("adj_area_cont_rect").connect("value-changed", self.update_area_ratio)
    
    builder.get_object("adj_min_area_internal_contour").set_value(self.__visionSystem.minInternalAreaContour)
    builder.get_object("adj_min_area_internal_contour").connect("value-changed", self.update_min_internal_area_contour)
    
    builder.get_object("adj_min_area_external_contour").set_value(self.__visionSystem.minExternalAreaContour)
    builder.get_object("adj_min_area_external_contour").connect("value-changed", self.update_min_external_area_contour)
    
    #builder.get_object("adj_stability_param").set_value(self.__visionSystem.stabilityParam)
    #builder.get_object("adj_stability_param").connect("value-changed", self.update_stability_param)
    #builder.get_object("stability_usecurrent").connect("clicked", self.use_current_identifier)
    
    return builder.get_object("main")
  
  def update_area_ratio(self, widget):
    """Atualiza na visão a razão de área triângulo/retângulo que permite diferenciar essas formas"""
    self.__controller.addEvent(self.__visionSystem.atualizarAreaRatio, widget.get_value())
  
  def update_min_internal_area_contour(self, widget):
    """Atualiza na visão a área mínima aceitável para contornos internos detectados"""
    self.__controller.addEvent(self.__visionSystem.atualizarMinInternalArea, widget.get_value())
  
  def update_min_external_area_contour(self, widget):
    """Atualiza na visão a área mínima aceitável para contornos externos detectados"""
    self.__controller.addEvent(self.__visionSystem.atualizarMinExternalArea, widget.get_value())
  
  def getFrame(self):
    """Retorna um frame que desenha retângulos ao redor dos robôs com seus identificadores e círculo ao redor da bola"""
    frame = self.__visionSystem.cameraHandler.getFrame()
    if frame is None: return None
    
    img_warpped = self.__visionSystem.warp(frame)
    img_hsv = self.__visionSystem.converterHSV(img_warpped)
    fgMask = self.__visionSystem.obterMascaraElementos(img_hsv)
    img_filtered = cv2.bitwise_and(img_warpped, img_warpped, mask=fgMask)
    message = self.__visionSystem.process(frame)
    
    Drawing.draw_field(self.__world, img_filtered)
    
    for i,allyPose in enumerate(message.allyPoses):
      if(allyPose[3]):
        x,y = meters2pixel(self.__world, (allyPose[0], allyPose[1]), img_warpped.shape)
        w,h = meters2pixelSize(self.__world, (0.08,0.08), img_warpped.shape)
        Drawing.draw_rectangle(img_filtered, (x,y), (w,h), allyPose[2], color=(0,255,0))
        #cv2.putText(img_filtered, str(i), (x-10, y+10), cv2.FONT_HERSHEY_TRIPLEX, 1, (0,0,0))
        if message.debug_internalContours[i] is not None:
          cv2.drawContours(img_filtered, message.debug_internalContours[i], -1, (255,255,255), -1)

    # Desenha camisa dos inimigos
    for advExtContour in message.debug_advExtContours:
      if advExtContour is not None:
        cv2.drawContours(img_filtered, advExtContour, -1, (0,0,255), -1)
    
    if message.ball_found:
      p = meters2pixel(self.__world, (message.ball_x, message.ball_y), img_warpped.shape)
      cv2.circle(img_filtered, p, 5, (255,0,0), 2)
      
    return img_filtered
