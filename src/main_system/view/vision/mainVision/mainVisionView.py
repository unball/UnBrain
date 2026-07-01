from gi.repository import Gtk
from pkg_resources import resource_filename
from main_system.view.tools.cv2Renderer import cv2Renderer
from main_system.view.tools.frameSelector import FrameSelector
from main_system.view.tools.stackSelector import StackSelector
from main_system.view.vision.mainVision.cortarCampo import CortarCampo
from main_system.view.vision.mainVision.cortarCampoInterno import CortarCampoInterno
from main_system.view.vision.mainVision.segmentarElementos import SegmentarElementos
from main_system.view.vision.mainVision.morfologia import Morfologia
from main_system.view.vision.mainVision.segmentarBola import SegmentarBola
from main_system.view.vision.mainVision.segmentarTime import SegmentarTime
from main_system.view.vision.mainVision.parametrosVisao import ParametrosVisao
from main_system.view.vision.mainVision.parametrosVisao import VisaoAltoNivel
from main_system.view.vision.mainVision.calibracaoLente import CalibracaoLente
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
    
    if self.__visionSystem is not None:
      self.__frameRenderers = [
        CalibracaoLente(notebook, self.__controller, self.__visionSystem),
        CortarCampo(notebook, self.__controller, self.__visionSystem, self.__renderer.getEventBox()),
        CortarCampoInterno(notebook, self.__controller, self.__visionSystem, self.__renderer.getEventBox()),
        SegmentarElementos(notebook, self.__controller, self.__visionSystem),
        SegmentarBola(notebook, self.__controller, self.__visionSystem),
        Morfologia(notebook, self.__controller, self.__visionSystem),
        SegmentarTime(notebook, self.__controller, self.__visionSystem),
        ParametrosVisao(notebook, self.__controller, self.__visionSystem, self.__world),
        VisaoAltoNivel(notebook, self.__controller, self.__visionSystem, self.__world)
      ]
    else:
      class DummyRenderer:
        def __init__(self, notebook):
          self.page = Gtk.Label(label="Visão desabilitada no modo Simulador")
          self.page.show()
          notebook.append_page(self.page, Gtk.Label(label="Visão"))
        def getFrame(self):
          import numpy as np
          return np.zeros((480, 640, 3), dtype=np.uint8)
        def connectSpecialSignals(self): pass
        def disconnectSpecialSignals(self): pass

      self.__frameRenderers = [DummyRenderer(notebook)]
      
    self.__frameSelector = FrameSelector(notebook, self.__frameRenderers)
    """Contém o seletor de frameRenderer"""
    resetCurrentBtn = builder.get_object("resetCurrentBtn")
    resetAllBtn = builder.get_object("resetAllBtn")
    
    def on_reset_current(btn):
      selected = self.__frameSelector.get_selected()
      if hasattr(selected, 'reset'):
        selected.reset()
        
    def on_reset_all(btn):
      for renderer in self.__frameRenderers:
        if hasattr(renderer, 'reset'):
          renderer.reset()
          
    resetCurrentBtn.connect("clicked", on_reset_current)
    resetAllBtn.connect("clicked", on_reset_all)
    
    return mainBox
    
  def on_select(self, widget):
    self.__renderer.start()
    
  def on_deselect(self, widget):
    self.__renderer.stop()
    
  def renderer(self):
    """Este método retorna o frame de acordo com a página selecionada"""
    return self.__frameSelector.getFrame()
