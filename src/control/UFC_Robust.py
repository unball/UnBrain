from tools import norm, ang, angError, sat, speeds2motors, fixAngle, filt, unit, angl, norml, sats, get_Lr
from tools.interval import Interval
from control import Control
import numpy as np
import math
import time
import os
import json

class UFC_Robust(Control):
    """Controle unificado Robusto, com prevenção anti-deadlock aprimorada."""
    def __init__(self, world, kw=20, kp=10, mu=0.1, vmax=2.0, enableInjection=False):
      Control.__init__(self, world)

      self.g = 9.87
      self.kw = kw
      self.kp = kp
      self.mu = mu
      self.amax = self.mu * self.g
      self.vmax = vmax
      self.L = get_Lr(self.world.mode)[0]

      self.lastth = 0
      self.interval = Interval(filter=True, initial_dt=0.001)

    def output(self, robot):
        if robot.field is None: return 0,0

        th = robot.field.F(robot.pose)
        
        eth = angError(th, robot.th)
        dt = self.interval.getInterval()
        dth = angError(th, self.lastth) / dt
        phi = robot.field.phi(robot.pose)
        gamma = robot.field.gamma(dth, robot.velmod, phi)

        linear_thresh = 0.1
        if np.abs(eth) < linear_thresh:
            kw_linear = self.kw / np.sqrt(linear_thresh)
            omega = kw_linear * eth + gamma
        else:
            omega = self.kw * np.sign(eth) * np.sqrt(np.abs(eth)) + gamma

        max_safe_omega = (2 * self.vmax) / self.L
        omega = sat(omega, max_safe_omega * 0.95)

        if phi != 0:
            v1 = (-np.abs(omega) + np.sqrt(omega**2 + 4 * np.abs(phi) * self.amax)) / (2*np.abs(phi))
        else:
            v1 = self.vmax if omega == 0 else self.amax / np.abs(omega)

        v2 = (2*self.vmax - self.L * np.abs(omega)) / (2 + self.L * np.abs(phi))
        v3 = self.kp * norm(robot.pose, robot.field.Pb) + robot.vref
        # v3 = self.kp * norm(robot.pose, robot.field.Pb) ** 2 + robot.vref
        # [NOVIDADE]: Piso mínimo de velocidade linear (anti-estrangulamento v1)
        v_floor = 0.8
        if v1 < v_floor:
            v1 = v_floor

        v  = max(min(v1,v2,v3), 0)
        w = v * phi + omega

        self.lastth = th
        robot.lastControlLinVel = v

        if robot.spin == 0: return (v * robot.direction, w)
        else: return (0, 60 * robot.spin)
