from controller.control import SpeedPair
from abc import ABC, abstractmethod

class Communication(ABC):
  """Classe mãe que define as interfaces do sistema de comunicação"""
  def __init__(self, world):
    super().__init__()
    self._world = world

  @abstractmethod
  def send(self, msg):
    """Qualquer sistema de comunicação deve implementar o método `send` que recebe uma mensagem no formato de lista de `MainSystem.controller.control.SpeedPair`"""
    pass
  
  def sendZero(self):
    """Envia uma mensagem com velocidades nulas"""
    self.send([SpeedPair() for i in range(self._world.n_robots)])
