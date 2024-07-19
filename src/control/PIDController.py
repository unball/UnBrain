from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, L, unit, angl, norml, sats
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time 

class PIDController(Control):
  def __init__(self, world, Kp, Ki, Kd):
    super().__init__(world)
    self.Kp = Kp
    self.Ki = Ki
    self.Kd = Kd
    self.kw = 64.0
    self.prev_error_v = 0
    self.integral_v = 0
    self.prev_error_w = 0
    self.integral_w = 0
    self.vmax = 2.0
    self.interval = Interval()  # Assuming Interval is a class handling time intervals
  
  def update(self, setpoint, actual_position, prev_error, integral):
    error = setpoint - actual_position
    integral += error
    derivative = error - prev_error
    prev_error = error
    output = self.Kp * error + self.Ki * integral + self.Kd * derivative
    return output, prev_error, integral


  def output(self, robot):
    if robot.field is None:
        return 0, 0

    # Desired position and orientation
    desired_position = robot.field.Pb[:2]  # Ball position or target position
    desired_orientation = robot.field.F(robot.pose)  # Target orientation based on field

    # Current position and orientation
    current_position = robot.pose[:2]
    current_orientation = robot.th

    # Update PID for linear velocity
    v_setpoint = np.linalg.norm(desired_position - current_position)
    v_actual = robot.velmod
    v_control, self.prev_error_v, self.integral_v = self.update(v_setpoint, v_actual, self.prev_error_v, self.integral_v)

    # Update PID for angular velocity
    w_setpoint = angError(desired_orientation, current_orientation)
    w_actual = robot.w
    w_control, self.prev_error_w, self.integral_w = self.update(w_setpoint, w_actual, self.prev_error_w, self.integral_w)

    # Clip velocities to the maximum allowed values
    v_control = np.clip(v_control, -self.vmax, self.vmax)
    w_control = np.clip(w_control, -self.kw, self.kw)
    
    # Set the robot's velocity reference based on the control outputs
    robot.vref = v_control * robot.direction  # Set linear velocity reference
    
    print("w:", w_control)
    print("v:", v_control)

    return v_control * robot.direction, w_control

class Interval:
  def __init__(self):
    self.last_time = time.time()

  def getInterval(self):
    current_time = time.time()
    interval = current_time - self.last_time
    self.last_time = current_time
    return interval
