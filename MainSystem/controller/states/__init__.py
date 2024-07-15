from abc import ABC, abstractmethod
import time

class State(ABC):
  """Classe que define um estado do backend"""
  
  def __init__(self, controller):
    super().__init__()
    
    self._controller = controller
    """O estado mantém referência ao controller pai que o instanciou"""

  @abstractmethod
  def update(self):
    """O estado deve implementar um método de `update` que será executado continuamente pela thread de backend"""
    pass


class DummyState(State):
  """Estado dummy que não faz nada"""
  
  def __init__(self, controller):
    super().__init__(controller)

  def update(self):
    """Este método apenas faz dormir por 30ms"""
    time.sleep(0.03)
    #self._controller.visionSystem.update()
