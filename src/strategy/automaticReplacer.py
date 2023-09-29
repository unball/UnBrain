
from client.referee import RefereeCommands
from strategy.entity.automaticPlacement import AutomaticPlacement

class AutomaticReplacer():
    def __init__(self, automaticPositions):
        super().__init__(automaticPositions)

        self.pose = automaticPositions

    def send(self):

        ap = AutomaticPlacement()

        # atualiza entidade de todos os robos para posicionamento automatico
        self.world.team[2].updateEntity(ap(self.pose[0]))
        self.world.team[1].updateEntity(ap(self.pose[1]))
        self.world.team[0].updateEntity(ap(self.pose[2]))

        # para todos os robos quando receber foul que nao seja game on, stop ou halt
        # envia v, w = 0 para robos 0,1,2 
        control_output = [(0,0), (0,0), (0,0)] 
        self.radio.send(control_output)

        # enquanto nao chegar na posição desejada, calcula v,w e envia para robos
        # while (nao chegou na posição desejada)
        control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None] 
        self.radio.send(control_output)
        
        # quando chegar, corrige orientação dos robos
