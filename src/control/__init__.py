from abc import ABC, abstractmethod
from tools import speeds2motors, deadzone, sat, motors2speeds_from_vl_vr
from tools.trainingCopy import NeuroControllerWrapper

# Controller = NeuroControllerWrapper(
#             model_path="best_model_firasim.pth",
#             scaler_x_path="scaler_x_firasim.pkl",
#             scaler_y_path="scaler_y_firasim.pkl"
#         )

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

        v, w = self.output(robot)

        robot.lastControlLinVel = v
        w = self.world.field.side * w * -1

        return v, w

    def actuateSimu(self, robot):
        if not robot.on: return (0,0)
        if robot.entity.__class__.__name__ ==  "AI_Attacker": 
            vl, vr = self.output(robot)
            v, w = motors2speeds_from_vl_vr(vl, vr, 0.026, 0.08)
            v, w = self.world.data_collector.collect_and_actuate(v_target=v,w_target=w)
            vr, vl = speeds2motors(v, w)
            
            return vr, vl
        
        # if robot.entity.__class__.__name__ ==  "AI_Attacker":
        #     vl, vr = self.output(robot) #Vr e Vl da Inteligencia Artificial
        #     v, w = motors2speeds_from_vl_vr(vl, vr, 0.026, 0.08)
        #     v_measured = robot.v_signed
        #     w_measured = robot.w
        #     v, w = Controller.step(v_target=v,w_target=w, v_measured=v_measured, w_measured=w_measured)
        #     vr, vl = speeds2motors(v, w)
            
        #     return vr, vl
        else:
            v, w = self.output(robot)
            robot.lastControlLinVel = v
            vr, vl = speeds2motors(v, self.world.field.side * w)

        return vr, vl