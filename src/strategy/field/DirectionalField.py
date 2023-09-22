
import numpy as np
from tools import angl, unit, norml, angError, filt, sat
from . import Field

class DirectionalField(Field):
    def __init__(self, th, Pb=(0,0,0), nullgamma=True):
        super().__init__(Pb)
        self.th = th

    def F(self, P):
        return self.th
    