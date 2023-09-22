from .area import Area
from tools import unit, norml, angl, angleRange
import numpy as np

class AvoidCircle(Area):
    def __init__(self, center, radius):
        super().__init__()
        self.center = np.array(center)
        self.radius = radius

    def nearestTo(self, P):
        # argmin_t |self.P(t) - P|
        P = np.array(P)[:2]

        v = P - self.center
        v = self.radius * v / norml(v)

        return angleRange(angl(v)) / (2*np.pi)

    def P(self, t):
        return self.center + self.radius*unit(2*np.pi*t)