from abc import ABC, abstractmethod
from tools import speeds2motors, deadzone, sat, motors2speeds_from_vl_vr
# from tools.training import SimToRealWrapper

# Controller = SimToRealWrapper(
            # model_path="best_model_travesim.pth",
            # scaler_x_path="scaler_x_travesim.pkl",
            # scaler_y_path="scaler_y_travesim.pkl",
            # use_lstm=True
        # )

class Control(ABC):
    def __init__(self, world):
        ABC.__init__(self)

        self.world = world

    @abstractmethod
    def output(self, robot):
        pass

    '''def actuate(self, robot):
        if not robot.on: return (0,0)

        v, w = self.output(robot)
        robot.lastControlLinVel = v
        return speeds2motors(v, self.world.field.side * w)'''
    def actuate(self, robot):
        if not robot.on: return (0, 0)
        if robot.entity.__class__.__name__ ==  "AI_Attacker": 
            vl, vr = self.output(robot)
            # self.world.data_collector.collect(vl_AI=vl,vr_AI=vr)
            v, w = motors2speeds_from_vl_vr(vl, vr, self.world.mode)
            return v, w

        v, w = self.output(robot)

        robot.lastControlLinVel = v
        w = self.world.field.side * w * -1

        return v, w

    def actuateSimu(self, robot):
        if not robot.on: return (0,0)
        if robot.entity.__class__.__name__ ==  "AI_Attacker": 
            vl, vr = self.output(robot)
            self.world.data_collector.collect(vl_AI=vl,vr_AI=vr)
            return vl, vr
        
        # if robot.entity.__class__.__name__ ==  "AI_Attacker":
        #     vl, vr = self.output(robot) #Vr e Vl da Inteligencia Artificial
        #     v, w = motors2speeds_from_vl_vr(vl, vr, 0.026, 0.08)
        #     v, w = Controller.step(v,w)
        #     vr, vl = speeds2motors(v, w, self.world.mode)
            
        #     return vl, vr
        else:
            v, w = self.output(robot)
            robot.lastControlLinVel = v
            vl, vr = speeds2motors(v, self.world.field.side * w, self.world.mode)

        return vl, vr