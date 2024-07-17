from abc import ABC, abstractmethod
from gi.repository import Gtk

class FrameRenderer(ABC):
  """Esta classe encapsula a lógica de uma página de um GtkNotebook em que cada página produz frames diferentes a serem mostrados"""
  def __init__(self, notebook, name):
    super().__init__()
    
    self.__notebook = notebook
    self.__notebook.append_page(self.ui(), Gtk.Label(name))
    self.disconnectSpecialSignals()
    
  @abstractmethod
  def ui(self):
    """Implementa o que deve ser adicionado como filho daquela página no GtkNotebook"""
    pass
  
  @abstractmethod
  def getFrame(self):
    """Retorna o frame a ser renderizado por essa página"""
    pass
  
  def disconnectSpecialSignals(self):
    """Desconecta sinais especiais como de clique para que eles não ocorram enquanto outra página está selecionada"""
    pass
  
  def connectSpecialSignals(self):
    """Conecta sinais especiais como de clique"""
    pass

class FrameSelector():
  """Esta classe faz a multiplexação do que será mostrado a depender da página selecionada no GtkNotebook"""
  def __init__(self, notebook, frameRenderers):
    self.__frameRenderers = frameRenderers
    self.__selected = frameRenderers[0]
    self.__selected.connectSpecialSignals()
    
    notebook.connect("switch-page", self.select_frame)
  
  def select_frame(self, widget, childWidget, page):
    """Implementa a mudança de página, desconectando os sinais da página antiga e conectando os sinais da nova"""
    self.__selected.disconnectSpecialSignals()
    self.__selected = self.__frameRenderers[page]
    self.__selected.connectSpecialSignals()
  
  def getFrame(self):
    """Retorna o frame da página selecionada"""
    return self.__selected.getFrame()
