from abc import ABC, abstractmethod
from model.paramsPattern import ParamsPattern

class SpeedPair():
  """Classe que mantém velocidade angular e linear de atuação do controle"""
  def __init__(self, v=0, w=0):
    self.v = v
    self.w = w
  
  def __repr__(self):
    """Faz o pretty-print das velocidades"""
    return "{" + "v: {0}, w: {1}".format(self.v, self.w) + "}"


class HLC(ABC, ParamsPattern):
  """Classe mãe de um controle de alto nível"""

  def __init__(self, name, source, default):
    ABC.__init__(self)
    ParamsPattern.__init__(self, source, default, name=name)

  @abstractmethod
  def actuate(self, reference, robot, spin):
    """Este método deve fazer a atuação do controle de alto nível na planta, ele recebe a referência, o robô e se é para executar spin. Retorna a velocidade linear e angular."""
    pass
