from gi.repository import Gtk
from pkg_resources import resource_filename
from view.tools.cv2Renderer import cv2Renderer
from view.tools.frameSelector import FrameSelector
from view.tools.stackSelector import StackSelector
from view.vision.mainVision.cortarCampo import CortarCampo
from view.vision.mainVision.cortarCampoInterno import CortarCampoInterno
from view.vision.mainVision.segmentarElementos import SegmentarElementos
from view.vision.mainVision.morfologia import Morfologia
from view.vision.mainVision.segmentarBola import SegmentarBola
from view.vision.mainVision.segmentarTime import SegmentarTime
from view.vision.mainVision.parametrosVisao import ParametrosVisao
from view.vision.mainVision.parametrosVisao import VisaoAltoNivel
import cv2

class MainVisionView(StackSelector):
  """Classe que gerencia a view de configuração da visão"""
  
  def __init__(self, controller, visionSystem, world, stack):
    self.__controller = controller
    self.__visionSystem = visionSystem
    self.__world = world
    super().__init__(stack, "configVision", "Visão")
  
  def ui(self):
    # Carrega os elementos estáticos
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "mainVision.ui"))
    
    # Elementos internos
    mainBox = builder.get_object("mainVisionBox")
    notebook = builder.get_object("mainVisionNotebook")
    frameBox = builder.get_object("mainVisionFrame")
    
    self.__renderer = cv2Renderer(worker=self.renderer, interpolation=cv2.INTER_NEAREST)
    """Instancia o renderizador, ele é do tipo GtkFrame"""
    
    # Adiciona o renderizador ao GtkBox
    frameBox.pack_start(self.__renderer, True, True, 0)
    frameBox.reorder_child(self.__renderer, 0)
    
    self.__frameSelector = FrameSelector(notebook, [
      CortarCampo(notebook, self.__controller, self.__visionSystem, self.__renderer.getEventBox()),
      CortarCampoInterno(notebook, self.__controller, self.__visionSystem, self.__renderer.getEventBox()),
      SegmentarElementos(notebook, self.__controller, self.__visionSystem),
      SegmentarBola(notebook, self.__controller, self.__visionSystem),
      Morfologia(notebook, self.__controller, self.__visionSystem),
      SegmentarTime(notebook, self.__controller, self.__visionSystem),
      ParametrosVisao(notebook, self.__controller, self.__visionSystem, self.__world),
      VisaoAltoNivel(notebook, self.__controller, self.__visionSystem, self.__world)
    ])
    """Contém o seletor de frameRenderer"""
    
    return mainBox
    
  def on_select(self, widget):
    self.__renderer.start()
    
  def on_deselect(self, widget):
    self.__renderer.stop()
    
  def renderer(self):
    """Este método retorna o frame de acordo com a página selecionada"""
    return self.__frameSelector.getFrame()
