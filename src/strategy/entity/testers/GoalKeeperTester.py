from strategy.entity import Entity
from strategy.field.DirectionalField import DirectionalField
from tools import angError, norm
from control.goalKeeper import GoalKeeperControl
import numpy as np
import time

class GoalKeeperTester(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)
        self._control = GoalKeeperControl(self.world)
        self.lastChat = 0
        self.state = 1
        
        # Inicia o arquivo de log de trajetória caso não exista, ou appenda
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

            if time.time()-self.lastChat > 1:
                if abs(angError(ref_th, rob_th)) > 90 * np.pi / 180:
                    self.robot.direction *= -1
                    self.lastChat = time.time()

                # Inverter a direção se o robô ficar preso
                if not self.robot.isAlive() and self.robot.spin == 0:
                    self.lastChat = time.time()
                    self.robot.direction *= -1   

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        
        # Salva a posição exata para traçarmos o gráfico
        with open("trajectory.csv", "a") as f:
            t = time.time() - self.world.t0 if hasattr(self.world, 't0') else time.time()
            f.write(f"{t:.4f},{self.state},{rr[0]},{rr[1]},{rr[2]}\n")

        self.robot.vref = 0
        
        # Teste Goleiro: Pêndulo na linha do gol
        x_goal = -0.70
        y_top = 0.20
        y_bot = -0.20

        if self.state == 1:
            target = np.array([x_goal, y_top])
            self.robot.field = DirectionalField(np.pi/2, Pb=(x_goal, y_top, np.pi/2))
            if norm(rr[:2], target) < 0.05:
                self.state = 2
                
        elif self.state == 2:
            target = np.array([x_goal, y_bot])
            self.robot.field = DirectionalField(-np.pi/2, Pb=(x_goal, y_bot, -np.pi/2))
            if norm(rr[:2], target) < 0.05:
                print("[CALIBRATOR] Goleiro: Pêndulo completo!", flush=True)
                self.state = 1
