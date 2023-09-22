import numpy as np
from tools import ang
from . import Field

class AttractiveField(Field):
  def __init__(self, Pb):
    super().__init__(Pb)

  def F(self, P):
      return ang(P, self.Pb)