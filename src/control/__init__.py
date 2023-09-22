from abc import ABC, abstractmethod
from tools import speeds2motors, deadzone, sat
import numpy as np
import time

class Control(ABC):
    def __init__(self, world):
        ABC.__init__(self)

        self.world = world

    @abstractmethod
    def output(self, robot):
        pass

    def actuate(self, robot):
        if not robot.on:
            return (0, 0)
        
        # if robot.id == 0:
        #     return (1,1)
        # elif robot.id == 1:
        #     return (2,2)
        # elif robot.id == 2:
        #     return (3,3)

        v, w = self.output(robot)
        robot.lastControlLinVel = v
        
        vr, vl = speeds2motors(v, w)

        vr = int(deadzone(sat(vr, 223), 32, -32))
        vl = int(deadzone(sat(vl, 223), 32, -32))

        # print(
        #     f"ur: {ur}\ter: {vr - vision_vr}, vr: {vr}, vision_vr: {vision_vr}")
        # print(
        #     f"ul: {ul}\tel: {vl - vision_vl}, vl: {vl}, vision_vl: {vision_vl}")
        # print(
        #     f"ur: {ur}\tev: {v - robot.v_signed}, v: {v}, vision_v: {robot.v_signed}")
        # print(
        #     f"ul: {ul}\tew: {w - vision_w}, w: {w}, vision_w: {vision_w}")
        
        return vr, vl



