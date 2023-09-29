
from client.referee import RefereeCommands

class AutomaticPlacement:
    def __init__():
        return 

    def send(self, robotsPos):

        # lembrar q cada foul tem q parar os robos 

        self.world.team[2].updateEntity(automatic(pose))
        self.world.team[1].updateEntity(automatic(pose))
        self.world.team[0].updateEntity(automatic(pose))

        control_output = [robot.entity.control.actuate(robot) for robot in self.world.team if robot.entity is not None] 
        self.radio.send(control_output)
