from main_system.controller.world.element import Element
from main_system.controller.tools.kalman import KalmanFilter
from main_system.controller.tools import insideRect

def shift(data, array):
    return [data] + array[1:]

class Ball(Element):
  """Classe filha de `Element` que implementa a abstração da bola no mundo."""

  def __init__(self, world):
    super().__init__(world)

  def insideGoalArea(self):
    """Retorna se a bola está na área do gol  ou não"""
    return insideRect(self.pos, self.world.allyGoalPos, self.world.goalAreaSize)

  @property
  def pos(self, step=3):
    """Retorna a posição \\([x,y]\\) do oaliadobjeto como uma lista."""
    vx, vy = self.vel
    return [self.x+vx*self.world.dt*step, self.y+vy*self.world.dt*step]