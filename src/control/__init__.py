from abc import ABC, abstractmethod
from tools import speeds2motors, deadzone, sat

class Control(ABC):
    def __init__(self, world):
        ABC.__init__(self)

        self.world = world

    @abstractmethod
    def output(self, robot):
        pass

    '''def actuate(self, robot):
        if not robot.on: return (0,0)

        v, w = self.output(robot)
        robot.lastControlLinVel = v
        return speeds2motors(v, self.world.field.side * w)'''
    def actuate(self, robot):
        if not robot.on: return (0, 0)

        v, w = self.output(robot)
        
        robot.lastControlLinVel = v
        
        vr, vl = speeds2motors(v, self.world.field.side * w)

        vr = int(deadzone(sat(vr, 223), 32, -32))
        vl = int(deadzone(sat(vl, 223), 32, -32))

        #print("VL", vl,"VR", vr)
        
        return vr, vl
    def actuateSimu(self, robot):
        if not robot.on: return (0,0)

        v, w = self.output(robot)
        robot.lastControlLinVel = v
        return speeds2motors(v, self.world.field.side * w)