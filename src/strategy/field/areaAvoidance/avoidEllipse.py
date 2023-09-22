from .area import Area
from tools import unit, norml, angl, angleRange
import numpy as np

class AvoidEllipse(Area):
    def __init__(self, center, a, b):
        super().__init__()
        self.center = np.array(center)
        self.a = a
        self.b = b

    def nearestTo(self, P):
        # argmin_t |self.P(t) - P|
        P = np.array(P)[:2]

        e = np.array([1/self.a, 1/self.b])
        v = P - self.center
        v = e*v
        v = v / norml(v)

        return angleRange(angl(v)) / (2*np.pi)

    def P(self, t):
        return self.center + np.array([self.a * np.cos(2 * np.pi * t), self.b * np.sin(2 * np.pi * t)])