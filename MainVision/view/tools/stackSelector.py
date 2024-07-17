from abc import ABC, abstractmethod

class StackSelector(ABC):
  """Essa classe implementa a seleção de filhos em um `GtkStack`"""
  
  def __init__(self, stack, name, title):
    super().__init__()
    
    self._name = name
    """Nome identificador do filho no GtkStack"""
    
    self._title = title
    """Título a ser mostrado no StackSwitcher"""
    
    # Obtém o elemento de interface gráfica a ser colocado no GtkStack
    child = self.ui()
    
    # Adiciona o evento de mudança de página
    child.connect("map", self.on_select)
    child.connect("unmap", self.on_deselect)
    
    # Adiciona ao stack
    stack.add_titled(child, name, title)
  
  @abstractmethod
  def ui(self):
    """O filho deve implementar essa função deve retornar a referência ao GtkWidget raiz do filho"""
    pass
  
  def on_select(self, widget):
    """Essa função é executada quando um filho é selecionado"""
    pass
  
  def on_deselect(self, widget):
    """Essa função é executada quando um filho deixa de estar selecionado"""
    pass
