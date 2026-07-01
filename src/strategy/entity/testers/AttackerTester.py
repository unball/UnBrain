from strategy.entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from tools import angError, ang, norm
from control.UFC_Robust import UFC_Robust
import numpy as np
import time

class AttackerTester(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)
        self._control = UFC_Robust(self.world)
        self.lastChat = 0
        self.state = 1
        self.target_uvf = np.array([0.0, 0.0])
        self.target_goal = np.array([0.7, 0.0]) # Representa o gol oponente
        
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

            if time.time()-self.lastChat > 0.5:
                if abs(angError(ref_th, rob_th)) > 120 * np.pi / 180:
                    self.robot.direction *= -1
                    self.lastChat = time.time()
                
                if not self.robot.isAlive() and self.robot.spin == 0:
                    self.lastChat = time.time()
                    self.robot.direction *= -1

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        t = time.time() - self.world.t0 if hasattr(self.world, 't0') else time.time()
        
        with open("trajectory.csv", "a") as f:
            f.write(f"{t:.4f},{self.state},{rr[0]},{rr[1]},{rr[2]}\n")

        self.robot.vref = 0

        # State 1: UVF para o meio do campo mirando no gol
        if self.state == 1:
            approach_angle = ang(self.target_uvf, self.target_goal)
            self.robot.field = UVF(world=self.world, robot=self.robot, Pb=(*self.target_uvf, approach_angle), direction=0, radius=0.07)
            
            # Se tangenciou e alinhou:
            if norm(rr[:2], self.target_uvf) < 0.05 and abs(angError(rr[2], approach_angle)) < 0.2:
                self.state = 2

        # State 2: Arrancada Direta para o "Gol"
        elif self.state == 2:
            dash_angle = ang(self.target_uvf, self.target_goal)
            self.robot.field = DirectionalField(dash_angle, Pb=(*rr[:2], dash_angle))
            self.robot.vref = 2.0 # Velocidade máxima
            
            if rr[0] > 0.6: # Passou do meio do caminho para o gol
                print("[CALIBRATOR] Atacante: Arrancada completa! Invertendo.", flush=True)
                # Inverte o campo de teste para ir para o outro lado
                self.target_goal = np.array([-0.7, 0.0])
                self.target_uvf = np.array([0.0, 0.0])
                self.state = 1
