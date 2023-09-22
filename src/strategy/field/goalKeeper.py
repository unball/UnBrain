import numpy as np
from tools import angl, unit, norml, angError, filt, sat, deadZoneDisc
from . import Field

class GoalKeeperField(Field):
  def __init__(self, Pb, xgoal):
    super().__init__(Pb)
    self.Pb = Pb
    self.y = Pb[1]
    self.x = xgoal
    self.A = (10*np.pi/180) / 0.08

  def F(self, P, Pb=None, retnparray=False):
    P = np.array(P)
    if len(P.shape) == 1: P = np.array([P]).T

    c0 = np.abs(P[0]-self.Pb[0]) > 0.07
    c1 = P[1] >= self.y
    c2 = np.bitwise_not(c1)

    uvf = np.zeros_like(P[0])
    uvf[c1] = -np.pi/2 + np.arctan(-(deadZoneDisc(P[0][c1] - self.x, 0.08)) * self.A)
    uvf[c2] = np.pi/2 + np.arctan((deadZoneDisc(P[0][c2] - self.x, 0.08)) * self.A)

    if uvf.size == 1 and not(retnparray): return uvf[0]
    return uvf