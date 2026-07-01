from ..entity import Entity
from strategy.field.UVF import UVF
from strategy.field.DirectionalField import DirectionalField
from tools import angError, ang
import numpy as np
import time
import sys

class TeleportEntity(Entity):
    def __init__(self, world, robot, target_x=0.0, target_y=0.0, target_th=0.0):
        super().__init__(world, robot)
        self.target_x = target_x
        self.target_y = target_y
        self.target_th = target_th
        self.lastChat = 0

    @property
    def control(self):
        # Usamos o UFC_Robust (já definido para as outras entidades)
        from control.UFC_Robust import UFC_Robust
        if not hasattr(self, '_control'):
            self._control = UFC_Robust(self.world, kw=20, kp=10, vmax=1)
        return self._control

    def equalsTo(self, other):
        return isinstance(other, TeleportEntity) and \
               self.target_x == other.target_x and \
               self.target_y == other.target_y and \
               self.target_th == other.target_th

    def onExit(self):
        pass

    def directionDecider(self):
        if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th

            if time.time() - self.lastChat > 0.5:
                if abs(angError(ref_th, rob_th)) > 90 * np.pi / 180:
                    self.robot.direction *= -1
                    self.lastChat = time.time()

                if not self.robot.isAlive() and self.robot.spin == 0:
                    self.lastChat = time.time()
                    self.robot.direction *= -1

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        
        # Distância até o alvo
        dist = np.hypot(self.target_x - rr[0], self.target_y - rr[1])
        
        if dist > 0.1:           
            # Longe do alvo: usar DirectionalField para se aproximar com o ângulo correto
            # Ou podemos simplesmente fazer um campo que aponta pro ponto
            target_ang = ang(rr, [self.target_x, self.target_y])
            self.robot.field = DirectionalField(target_ang, Pb=(self.target_x, self.target_y, self.target_th))
            self.robot.vref = 999  # Permitir movimento veloz
            # # Longe do alvo: usar UVF para se aproximar com o ângulo correto (mesmo comportamento do Control Tester)
            # target = np.array([self.target_x, self.target_y])
            # self.robot.field = UVF(self.world, (*target, self.target_th), robot=self.robot, direction=1, avoid_obstacles=True)
            # self.robot.vref = 0 # O UFC Robust já gerencia a velocidade pelo UVF
        else:
            # Chegou no alvo: remover o campo força o controle (UFC_Robust) a retornar (0,0) instantaneamente
            self.robot.field = None
            
            # DEBUG: Imprimir para o usuário ver que o controle está processando
            if getattr(self.world, 'flag_debug', getattr(self.world, 'debug', False)):
                if hasattr(self, 'last_debug_print'):
                    if time.time() - self.last_debug_print > 0.5:
                        print(f"[TeleportEntity] Robo {self.robot.id} | Dist: {dist:.3f} | vref: {self.robot.vref} | Target: {self.target_x}, {self.target_y}", file=sys.stderr)
                        self.last_debug_print = time.time()
                else:
                    self.last_debug_print = time.time()
