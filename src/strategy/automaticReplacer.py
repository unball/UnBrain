
from client.referee import RefereeCommands
from strategy.entity.automaticPlacement import AutomaticPlacement
import numpy as np
class AutomaticReplacer():
    def __init__(self, automaticPositions):
        super().__init__(automaticPositions)

        self.pose = automaticPositions

    def send(self):
        rr = np.array(self.robot.pos)
        ap = AutomaticPlacement()

        # atualiza entidade de todos os robos para posicionamento automatico
        self.world.team[0].updateEntity(ap(self.pose[0]))
        self.world.team[1].updateEntity(ap(self.pose[1]))
        self.world.team[2].updateEntity(ap(self.pose[2]))

        for robot in self.world.team:
            robot.updateSpin()
            if robot.entity is not None:
                robot.entity.fieldDecider()
                robot.entity.directionDecider()

        # para todos os robos quando receber foul que nao seja game on, stop ou halt
        # envia v, w = 0 para robos 0,1,2 
        control_output = [(0,0), (0,0), (0,0)] 
        self.radio.send(control_output)

        while(rr[0] > self.pose[0] or rr[1] > self.pose[1] or rr[2] > self.pose[2] ):
            control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None] 
            self.radio.send(control_output)
        
        
