import numpy as np
from tools import angl, unit, norml, angError, filt, sat, ang
from . import Field

class DefenderField(Field):
  def __init__(self, Pb, a, b, center):
    super().__init__(Pb)
    self.a = a
    self.b = b
    self.center = np.array(center)

  def F(self, P, Pb=None, retnparray=False):
    P = np.array(P)
    if len(P.shape) == 1: P = np.array([P]).T

    P[:2] = (P[:2].T - self.center).T

    d = np.abs(np.sqrt(P[0]**2 / self.a ** 2 + P[1]**2 / self.b ** 2) - 1) > 0.9

    x1 = P[0] / self.a
    x2 = P[1] / self.b
    
    ccw = angError(angl(self.Pb[:2]-self.center), angl(P)) > 0
    cw = np.bitwise_not(ccw)
    uvf = np.zeros_like(P[0])

    uvf[ccw] = np.arctan2(x1 + x2 * (1 - x1**2 - x2**2), -x2 + x1 * (1 - x1**2 - x2**2))[ccw]
    uvf[cw] = np.arctan2(-x1 + x2 * (1 - x1**2 - x2**2), x2 + x1 * (1 - x1**2 - x2**2))[cw]

    # uvf = np.arctan2(- self.b**2 * P[0], self.a**2 * P[1])
    # uvf[ccw] = uvf[ccw] + np.pi

    uvf[d] = ang((P[:2].T[d] + self.center).T, self.Pb)

    if uvf.size == 1 and not(retnparray): return uvf[0]
    return uvf
    