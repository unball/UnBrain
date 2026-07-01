from strategy.entity import Entity
from strategy.field.UVF import UVF
from tools import angError, ang, norm
from control.UFC import UFC_Simple
import numpy as np
import time

class MidfielderTester(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)
        self._control = UFC_Simple(self.world, enableInjection=False)
        self.lastChat = 0
        self.state = 1
        
        with open("trajectory.csv", "a") as f:
            f.write("time,state,x,y,th\n")

    @property
    def control(self):
        return self._control
    
    def equalsTo(self, otherTester):
        return True

    def onExit(self):
        pass
        
    def directionDecider(self):
        if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th

            if time.time()-self.lastChat > 0.3:
                if abs(angError(ref_th, rob_th)) > 90 * np.pi / 180:
                    self.robot.direction *= -1
                    self.lastChat = time.time()
                
                if not self.robot.isAlive() and self.robot.spin == 0:
                    self.lastChat = time.time()
                    self.robot.direction *= -1

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        vr = np.array(self.robot.v)
        v_mag = np.linalg.norm(vr)

        t = time.time() - self.world.t0 if hasattr(self.world, 't0') else time.time()
        
        with open("trajectory.csv", "a") as f:
            f.write(f"{t:.4f},{self.state},{rr[0]},{rr[1]},{rr[2]}\n")

        self.robot.vref = 0

        # State 1: Flanco superior
        if self.state == 1:
            target = np.array([0.1, 0.3])
            self.robot.field = UVF(self.world, (*target, 0), self.robot, radius=0.05)
            
            # Chegou e estabilizou a velocidade (parada seca)
            if norm(rr[:2], target) < 0.05 and v_mag < 0.1:
                self.state = 2

        # State 2: Flanco inferior
        elif self.state == 2:
            target = np.array([0.1, -0.3])
            self.robot.field = UVF(self.world, (*target, 0), self.robot, radius=0.05)
            
            # Chegou e estabilizou a velocidade
            if norm(rr[:2], target) < 0.05 and v_mag < 0.1:
                print("[CALIBRATOR] Midfielder: Ziguezague completo!", flush=True)
                self.state = 1
