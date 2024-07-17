from controller.tools import adjustAngle, ang
import numpy as np

def simulate(robot, v, w, dt=0.033, r=0.03, L=0.075):
    """Esta função implementa um simulador para o robô"""
    if w != 0:
        R = abs(v) / w
        rc = (robot.raw_x - R * np.sin(robot.dir_raw_th), robot.raw_y + R * np.cos(robot.dir_raw_th))
        dth = w * dt
        x = rc[0] + abs(R) * np.cos(ang(rc, robot.raw_pos) + dth)
        y = rc[1] + abs(R) * np.sin(ang(rc, robot.raw_pos) + dth)
        th = adjustAngle(robot.dir_raw_th + dth)
    else:
        x = robot.raw_x + abs(v) * dt * np.cos(robot.dir_raw_th)
        y = robot.raw_y + abs(v) * dt * np.sin(robot.dir_raw_th)
        th = robot.dir_raw_th

    robot.dir_raw_update(x,y,th)
    robot.calc_velocities(dt)

t = 0
m = 1
def simulateBall(ball, dt=0.033):
    global t
    global m
    if abs(t) >= 1: m *= -1
    t = t + dt * m
    x = 0.4 * t
    y = 0.4 * t
    ball.update(x,y,0)
    ball.calc_velocities(dt)