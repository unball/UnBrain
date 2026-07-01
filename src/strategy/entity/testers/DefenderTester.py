from strategy.entity import Entity
from strategy.field.ellipse import DefenderField
from strategy.movements import blockBallElipse
from tools import angError, norm
from control.defender import DefenderControl
import numpy as np
import time

class DefenderTester(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)
        self._control = DefenderControl(self.world)
        self.lastChat = 0
        
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

            if abs(angError(ref_th, rob_th)) > 120 * np.pi / 180:
                self.robot.direction *= -1

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        
        # Tempo desde o início (usado para gerar a bola fantasma no círculo)
        t = time.time() - self.world.t0 if hasattr(self.world, 't0') else time.time()
        
        with open("trajectory.csv", "a") as f:
            f.write(f"{t:.4f},3,{rr[0]},{rr[1]},{rr[2]}\n")

        self.robot.vref = 0

        # Bola Fantasma Orbitando (raio 0.6m, período de 10 segundos -> w = 2*pi/10)
        w = 2 * np.pi / 10.0
        rb = np.array([-0.3, 0.6 * np.sin(w*t)]) # A bola sobe e desce em Y
        vb = np.array([0.0, 0.6 * w * np.cos(w*t)]) # Velocidade derivativa da bola

        pose, spin = blockBallElipse(rb, vb, rr, self.world.field.areaEllipseCenter, *self.world.field.areaEllipseSize)
        self.robot.setSpin(spin)

        self.robot.field = DefenderField(pose, *self.world.field.areaEllipseSize, self.world.field.areaEllipseCenter)
