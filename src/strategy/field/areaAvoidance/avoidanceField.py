from ...field import Field
from .area import Area
from tools import angl, fixAngle, unit
import numpy as np

class AvoidanceField(Field):
    def __init__(self, mainField: Field, avoidanceArea: Area, borderSize = 0.20, conflictAngle = 5):
        super().__init__(mainField.Pb)

        self.mainField = mainField
        self.avoidanceArea = avoidanceArea
        self.borderSize = borderSize
        self.conflictAngle = conflictAngle * np.pi / 180

    def F(self, P):
        tn = self.avoidanceArea.nearestTo(P)
        d = self.avoidanceArea.distanceTo(tn, P)

        if d <= 0:
            return angl(self.avoidanceArea.normalTo(tn))
        elif d >= self.borderSize:
            return self.mainField.F(P)
        else:
            return angl((d/self.borderSize) * unit(self.mainField.F(P)) + (1-d/self.borderSize) * self.avoidanceArea.normalTo(tn))

    def inConflict(self):
        return np.abs(fixAngle(normalAngle - mainAngle - np.pi)) < self.conflictAngle