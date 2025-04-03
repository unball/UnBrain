from control import Control
from ..entity import Entity


class AI_Attacker(Entity):
    def __init__(self, world, robot):
        Entity.__init__(self, world, robot)
        self.robot = robot
        self.world = world
        self.env = None
        self._control = AI_Control(self.world)

    @property
    def control(self):
        return self._control
    
    def fieldDecider(self):
        # 1. Verificar se existe e a env
        # 2. Se existe:
        # 3.     Atualizar o observation
        # 4.     Realizar um step
        # 5. Se não existe:
        # 6.     Criar a env
        # 7.     Atualizar o observation
        # 8.     Realizar um step
        # 9. Atualizar o control com o resultado do step
        pass

    def directionDecider(self):
        # não será usado
        pass

    def equalsTo(self, otherEntityOfSameClass):
        return self.robot == otherEntityOfSameClass.robot

    def onExit(self):
        self.isLocked = False

    def isLocked(self):
        return False
    

class AI_Control(Control):
    def __init__(self, world):
        Control.__init__(self, world)
        self.model = None
        self.observation = None

    def output(self, robot, obs):
        # 1. Verificar se existe o model
        # 2. Se existir:
        # 3.     Fazer o get_action
        # 4. Se não existir:
        # 5.     Criar o model
        # 6.     Fazer o get_action
        pass