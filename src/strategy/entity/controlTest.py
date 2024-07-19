from ..entity import Entity
from strategy.field.UVF import UVF, UVFDefault
from strategy.field.DirectionalField import DirectionalField
from strategy.field.goalKeeper import GoalKeeperField
from strategy.field.attractive import AttractiveField
from strategy.movements import goalkeep, spinGoalKeeper, goToBall, goToGoal, howFrontBall, howPerpBall, blockBallElipse, mirrorPosition, spinDefender
from tools import angError, howFrontBall, howPerpBall, ang, norml, norm, angl, insideEllipse, angl, unit, projectLine
from tools.interval import Interval
from control.goalKeeper import GoalKeeperControl
from control.defender import DefenderControl
from control.UFC import UFC_Simple
from control.PIDController import PIDController
from control.SecAttacker import SecAttackerControl
import numpy as np
import math
import time

class ControlTester(Entity):
    def __init__(self, world, robot, side=1):
        super().__init__(world, robot)
        self.time_elapsed = 0
        self.best_constants = self.optimize_pid_constants()
        self._control = PIDController(self.world, *self.best_constants)
        self.lastChat = 0
        self.x = 1
        self.performance_metric = 0

    @property
    def control(self):
        return self._control
    
    def equalsTo(self, otherTester):
        return True

    def onExit(self):
        pass

    def optimize_pid_constants(self):
        best_constants = (10.0, 0.9, 0.07)  # Default values
        best_performance = float('inf')

        # Define ranges for PID constants
        kp_values = np.linspace(0.5, 3.0, 5)  # Proportional
        ki_values = np.linspace(0.1, 1.0, 5)  # Integral
        kd_values = np.linspace(0.01, 0.1, 5)  # Derivative

        for kp in kp_values:
            for ki in ki_values:
                for kd in kd_values:
                    self._control = PIDController(self.world, kp, ki, kd)
                    self.performance_metric = 0.0  # Reset performance metric
                    self.simulate_performance(kp, ki, kd)
                    if self.performance_metric < best_performance:
                        best_performance = self.performance_metric
                        best_constants = (kp, ki, kd)
        print(best_constants)
        return best_constants

    def simulate_performance(self, kp, ki, kd):
        # Simulate the robot's behavior for a defined period
        simulation_time = 10  # seconds
        dt = 0.01  # time step

        if self.robot.field is not None:
            # Desired position (target)
            target_position = self.robot.field.Pb[:2] # Example target position
            total_error = 0.0
            previous_error = 0.0
            integral = 0.0

            # Run the simulation loop
            if self.world.execTime < simulation_time:
                print(self.world.execTime)
                # Get the current position of the robot
                current_position = np.array(self.robot.pos)  # Assuming pose contains [x, y, theta]

                # Calculate the error
                error = np.linalg.norm(target_position - current_position)
                total_error += error

                # Update PID controller
                integral += error * dt
                derivative = (error - previous_error) / dt
                output = kp * error + ki * integral + kd * derivative
                
                # Simulate the robot's movement (this is a simplified representation)
                self.robot.vref = output  # Set the robot's velocity reference

                # Prepare for the next iteration
                previous_error = error
                self.world.execTime += dt
                return
            else:
                self.world.execTime = 0

            # Calculate average error over the simulation period
            average_error = total_error / (simulation_time / dt)

            # Update the performance metric
            self.performance_metric = average_error

        
    def directionDecider(self):
       if self.robot.field is not None:
            ref_th = self.robot.field.F(self.robot.pose)
            rob_th = self.robot.th

            if time.time()-self.lastChat > 0.5:
                if abs(angError(ref_th, rob_th)) > 90 * np.pi / 180:
                    self.robot.direction *= -1
                    self.lastChat = time.time()

            # Inverter a direção se o robô ficar preso em algo
                if not self.robot.isAlive() and self.robot.spin == 0:
                    self.lastChat = time.time()
                    self.robot.direction *= -1    
    
        # Performance evaluation logic
    def evaluation_logic(self):
        rr = np.array(self.robot.pose)
        target_position = self.robot.field.Pb[:2] # Example target position
        error = np.linalg.norm(rr - target_position)  # Example target position
        self.performance_metric += error  # Accumulate error for performance evaluation

    def fieldDecider(self):
        rr = np.array(self.robot.pose)
        rb = np.array(self.world.ball.pos)
        vb = np.array(self.world.ball.v)
        rg = np.array(self.world.field.goalPos)
        vr = np.array(self.robot.v)
        oneSpiralMargin = (self.world.marginPos[0]-0.15, self.world.marginPos[1])
        if self.robot.field is not None:
            target_position = self.robot.field.Pb[:2] # Example target position
        
        robotBallAngle = ang(rr, rb)
        

        #Quad 1: X = -0.375 Y = +0.430
        #Quad 2: X = +0.375 Y = +0.430
        #Quad 3: X = +0.375 Y = -0.430
        #Quad 4: X = -0.375 Y = -0.430

        #Andar para frente e para trás
        if self.x == 1:
            if not -0.410 < rr[0] < -0.310 or not 0.330 < rr[1] < 0.430: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[-0.360,0.380]), Pb=(-0.360,0.380,1.5*np.pi))
                self.evaluation_logic
                print(self.x)
                return
            self.x = 2
        if self.x == 2:
            if not +0.420 > rr[0] > +0.320 or not 0.330 < rr[1] < 0.430: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[0.370,0.380]), Pb=(0.370,0.380, np.pi))
                print(self.x)
                self.evaluation_logic
                return
            self.x = 3
        if self.x == 3:
            if not +0.430 > rr[0] > +0.330 or not -0.330 > rr[1] > -0.430: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[0.380,-0.380]), Pb=(0.380,-0.380, 1,5*np.pi))
                print(self.x)
                return
            self.x = 4
        if self.x == 4:
            if not -0.410 < rr[0] < -0.310 or not -0.330 > rr[1] > -0.430: #Não chegou no lugar certo
                self.robot.field = DirectionalField(ang(rr,[-0.360,-0.380]), Pb=(-0.360,-0.380, np.pi))
                print(self.x)
                return
            self.x = 5
        if self.x == 5:
            if not -0.410 < rr[0] < -0.310 or not 0.330 < rr[1] < 0.430: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(-0.360,0.380,np.pi))
                print(self.x)
                return
            self.x = 6
        if self.x == 6:
            if not +0.420 > rr[0] > +0.320 or not 0.330 < rr[1] < 0.430: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(0.370,0.380, np.pi))
                print(self.x)
                return
            self.x = 7
        if self.x == 7:
            if not +0.430 > rr[0] > +0.330 or not -0.330 > rr[1] > -0.430: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(0.380,-0.380, np.pi))
                print(self.x)
                return
            self.x = 8
        if self.x == 8:
            if not -0.410 < rr[0] < -0.310 or not -0.330 > rr[1] > -0.430: #Não chegou no lugar certo
                self.robot.field = AttractiveField(Pb=(-0.360,-0.380, np.pi))
                print(self.x)
                return
            self.x = 9
        if self.x == 9:
            if not -0.410 < rr[0] < -0.310 or not 0.330 < rr[1] < 0.430: #Não chegou no lugar certo
                self.robot.field = UVFDefault(self.world, (-0.360,0.380,1.5*np.pi), rr, direction=0) #AttractiveField(Pb=(-0.360,-0.380, np.pi)) 
                print(self.x)
                return
            self.x = 10
        if self.x == 10:
            if not +0.420 > rr[0] > +0.320 or not 0.330 < rr[1] < 0.430: #Não chegou no lugar certo
                self.robot.field = UVFDefault(self.world, (0.370,0.380, np.pi), rr, direction=0) #AttractiveField(Pb=(-0.360,-0.380, np.pi))
                print(self.x)
                return
            self.x = 11
        if self.x == 11:
            if not +0.430 > rr[0] > +0.330 or not -0.330 > rr[1] > -0.430: #Não chegou no lugar certo
                self.robot.field = UVFDefault(self.world, (0.380,-0.380, 1,5*np.pi), rr, direction=0)
                print(self.x)
                return
            self.x = 12
        if self.x == 12:
            if not -0.410 < rr[0] < -0.310 or not -0.330 > rr[1] > -0.430: #Não chegou no lugar certo
                self.robot.field = UVFDefault(self.world, (-0.360,-0.380, np.pi), rr, direction=0)
                print(self.x)
                return
            self.x = 1


        

        # if rr[0] == 0.375 and rr[1] == 0.430:
        #     self.robot.field = DirectionalField(np.pi, Pb=(0.375,-0.430,np.pi))
        # if rr[0] == 0.375 and rr[1] == -0.430:
        #     self.robot.field = DirectionalField(np.pi, Pb=(-0.375,-0.430,1,5*np.pi))
        # if rr[0] == -0.375 and rr[1] == -0.430 :
        #     self.robot.field = DirectionalField(np.pi, Pb=(-0.375, 0.430,np.pi))
        # else:
        #     self.robot.field = DirectionalField(ang(rr,[-0.375,0.43]), Pb=(-0.375,0.430,np.pi))
        
        # if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) + 0.10*self.robot.movState and (self.robot.movState == 1 or abs(howPerpBall(rb, rr, rg)) < 0.1) and abs(angError(robotBallAngle, rr[2])) < (20+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.22 + self.robot.movState*0.4:
        #     #if howFrontBall(rb, rr, rg) < -0.03*(1-self.robot.movState) and abs(angError(robotBallAngle, rr[2])) < (30+self.robot.movState*60)*np.pi/180 and np.abs(projectLine(rr[:2], unit(rr[2]), rg[0])) <= 0.25:
        #     if self.robot.movState == 0:
        #         self.robot.ref = (*(rr[:2] + 1000*unit(rr[2])), rr[2])
        #     pose, gammavels = goToGoal(rg, rr, vr)
        #     self.robot.vref = 999
        #     self.robot.gammavels = (0,0,0)
        #     self.robot.movState = 1
        #     Kr = None
        #     pose = self.robot.ref
        #     singleObstacle = False
        # # Se não, vai para a bola
        # else:
        #     # Vai para a bola saturada em -0.60m em x
        #     rbfiltered = np.array([rb[0] if rb[0] > -0.40 else -0.40, rb[1]])
        #     pose, gammavels = goToBall(rbfiltered, rg, vb, self.world.marginPos)
        #     self.robot.vref = 999
        #     self.robot.gammavels = gammavels
        #     self.robot.movState = 0
        #     Kr = 0.04
        #     singleObstacle = False

        
        # self.robot.field = UVFDefault(self.world, pose, rr, direction=0, Kr=Kr, singleObstacle=singleObstacle, Vr=vr)