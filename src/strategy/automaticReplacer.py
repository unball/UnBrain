
from client.referee import RefereeCommands
from strategy.entity.automaticPlacement import AutomaticPlacement
import numpy as np 
from communication.serialWifi import SerialRadio

class AutomaticReplacer():
    def __init__(self, world):
        super().__init__()

        self.world = world
        self.radio = SerialRadio()

    def send(self, pose):
        #rr = np.array(self.robot.pose)
        # ap = AutomaticPlacement()

        rr0 = np.array(self.world.team[pose[0][0]].pose)
        rr1 = np.array(self.world.team[pose[1][0]].pose)
        rr2 = np.array(self.world.team[pose[2][0]].pose)

        # atualiza entidade de todos os robos para posicionamento automatico
        
        # ap = AutomaticPlacement(self.world, self.world.team[pose[0][0]], pose[0][1])
        # self.world.team[pose[0][0]].updateEntity(AutomaticPlacement)
        # ap = AutomaticPlacement(self.world, self.world.team[pose[1][0]],pose[1][1])
        # self.world.team[pose[1][0]].updateEntity(AutomaticPlacement)
        # ap = AutomaticPlacement(self.world, self.world.team[pose[2][0]],pose[2][1])
        # self.world.team[pose[2][0]].updateEntity(AutomaticPlacement)

        # TODO: descobrir quais saos os ids dos robos de verdade durante o jogo
        self.world.team[pose[0][0]].entity = AutomaticPlacement(self.world, self.world.team[pose[0][0]], pose[0][1])
        self.world.team[pose[1][0]].entity = AutomaticPlacement(self.world, self.world.team[pose[1][0]], pose[1][1])
        self.world.team[pose[2][0]].entity = AutomaticPlacement(self.world, self.world.team[pose[2][0]], pose[2][1])

        for robot in self.world.team:
            robot.updateSpin()
            if robot.entity is not None:
                robot.entity.fieldDecider()
                robot.entity.directionDecider()

        # para todos os robos quando receber foul que nao seja game on, stop ou halt
        # envia v, w = 0 para robos 0,1,2 
        control_output = [(0,0), (0,0), (0,0)] 
        self.radio.send(control_output)


        while(rr0[0] > pose[0][1][0] or rr0[1] > pose[0][1][1] or rr0[2] > pose[0][1][2] ):
            control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None] 
            self.radio.send(control_output)

        while(rr1[0] > pose[1][1][0] or rr1[1] > pose[1][1][1] or rr1[2] > pose[1][1][2] ):
            control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None] 
            self.radio.send(control_output)

        while(rr2[0] > pose[2][1][0] or rr2[1] > pose[2][1][1] or rr2[2] > pose[2][1][2] ):
            control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None] 
            self.radio.send(control_output)
        
        
