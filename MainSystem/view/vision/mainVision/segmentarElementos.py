from gi.repository import Gtk
from pkg_resources import resource_filename
from view.tools.frameSelector import FrameRenderer

class SegmentarElementos(FrameRenderer):
  """Essa classe implementa o FrameRenderer que permite configurar a segmentação dos elementos"""
  
  def __init__(self, notebook, controller, visionSystem):
    self.__visionSystem = visionSystem
    self.__controller = controller
    super().__init__(notebook, "Segmentar elementos")
    
  def ui(self):
    """Conteúdo a ser inserido na interface da configuração de segmentação de elementos"""
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "segmentarHSV.ui"))
    
    for index,name in enumerate(["hmin", "smin", "vmin", "hmax", "smax", "vmax"]):
      element = builder.get_object(name)
      element.set_value(self.__visionSystem.preto_hsv[index])
      element.connect("value-changed", self.update_hsv_interval, index)
    
    return builder.get_object("main")
    
  def update_hsv_interval(self, widget, index):
    """Atualiza na visão o valor HSV selecionado"""
    self.__controller.addEvent(self.__visionSystem.atualizarPretoHSV, int(widget.get_value()), index)
  
  def getFrame(self):
    """Retorna a máscara do que é elemento no campo"""
    frame = self.__visionSystem.cameraHandler.getFrame()
    if frame is None: return None
    
    img_warpped = self.__visionSystem.warp(frame)
    img_hsv = self.__visionSystem.converterHSV(img_warpped)
    return self.__visionSystem.obterMascaraElementos(img_hsv)
