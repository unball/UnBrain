from strategy.entity import Entity
from strategy.field.UVF import UVF
from tools import angError, norm
from control.UFC_Robust import UFC_Robust
import numpy as np
import time

class ControlTesterRobust(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)
        self._control = UFC_Robust(self.world)
        self.lastChat = 0
        self.x = 9 # Focus on UVF testing only

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
            erro_angular = abs(angError(ref_th, rob_th))

            # Como self.robot.th (rob_th) já incorpora a inversão da marcha a ré,
            # erro_angular é sempre o erro do lado do robô que está liderando o movimento.
            # Apenas aplica a histerese se não estivermos no período de carência do Anti-Stuck.
            # Sem isso, o Anti-Stuck inverte a direção, e a histerese imediatamente inverte de volta
            # no frame seguinte (porque o robô ainda não teve tempo de virar).
            if time.time() - getattr(self, 'lastChat', 0) > 1.5:
                if self.robot.direction == 1:
                    # Se está de frente, exige um erro grande para desistir e dar ré
                    if erro_angular > 110 * np.pi / 180:
                        self.robot.direction = -1
                else:
                    # Se está de ré, volta para frente assim que a frente ficar viável
                    # (Se o erro da traseira for > 80, o erro da frente é < 100)
                    if erro_angular > 80 * np.pi / 180:
                        self.robot.direction = 1

            # Anti-Stuck: Inverte a direção se ficar preso, garantindo que ele tenha 
            # tempo para sair do lugar (keepAlive) antes de checar novamente.
            if not self.robot.isAlive() and self.robot.spin == 0:
                if time.time() - self.lastChat > 1.5:
                    self.lastChat = time.time()
                    self.robot.direction *= -1
                    if hasattr(self.robot, 'keepAlive'):
                        self.robot.keepAlive(1.5)

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        
        # Salva a posição exata para traçarmos o gráfico
        with open("trajectory.csv", "a") as f:
            t = time.time() - self.world.t0 if hasattr(self.world, 't0') else time.time()
            f.write(f"{t:.4f},{self.x},{rr[0]},{rr[1]},{rr[2]}\n")

        self.robot.vref = 0
        
        # [NOVIDADE]: Validação Radial
        # Ao invés de um corte brusco num eixo X ou Y, exigimos que o robô chegue perto do ponto (raio de 12cm)
        # O UVF garantirá que ele chegue tangenciando perfeitamente a linha
        if self.x == 9:
            target = np.array([-0.375, 0.430])
            self.robot.field = UVF(self.world, (*target, 0), robot=self.robot, direction=-1, avoid_obstacles=True) 
            if norm(rr[:2], target) < 0.05: 
                self.x = 10
                
        elif self.x == 10:
            target = np.array([0.375, 0.430])
            self.robot.field = UVF(self.world, (*target, np.pi), robot= self.robot, direction=-1, avoid_obstacles=True) 
            if norm(rr[:2], target) < 0.05: 
                self.x = 11
                
        elif self.x == 11:
            target = np.array([0.375, -0.430])
            self.robot.field = UVF(self.world, (*target, 0), robot= self.robot, direction=1, avoid_obstacles=True)
            if norm(rr[:2], target) < 0.05: 
                self.x = 12
                
        elif self.x == 12:
            target = np.array([-0.375, -0.430])
            self.robot.field = UVF(self.world, (*target, np.pi), robot= self.robot, direction=1, avoid_obstacles=True)
            if norm(rr[:2], target) < 0.05:
                print("[CALIBRATOR] Volta completa!", flush=True)
                self.x = 9
