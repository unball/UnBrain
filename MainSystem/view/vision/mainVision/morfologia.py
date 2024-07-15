from gi.repository import Gtk
from pkg_resources import resource_filename
from view.tools.frameSelector import FrameRenderer
import cv2

class Morfologia(FrameRenderer):
  """Essa classe implementa o FrameRenderer que permite configurar os filtros morfológicos"""
  
  def __init__(self, notebook, controller, visionSystem):
    self.__visionSystem = visionSystem
    self.__controller = controller
    super().__init__(notebook, "Morfologia")
    
  def ui(self):
    """Conteúdo a ser inserido na interface da configuração de parâmetros da visão"""
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "morfologia.ui"))
    
    return builder.get_object("main")
  
  def getFrame(self):
    """Retorna a máscara do que é elemento no campo após os filtros morfológicos"""
    frame = self.__visionSystem.cameraHandler.getFrame()
    if frame is None: return None
    
    img_warpped = self.__visionSystem.warp(frame)
    img_hsv = self.__visionSystem.converterHSV(img_warpped)
    fgMaskNoBall = cv2.bitwise_and(self.__visionSystem.obterMascaraElementos(img_hsv), cv2.bitwise_not(self.__visionSystem.obterMascaraBola(img_hsv)))
    return self.__visionSystem.aplicarFiltrosMorfologicos(fgMaskNoBall)
