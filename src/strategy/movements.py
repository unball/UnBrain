import numpy as np
import scipy
from tools import unit, angl, ang, norm, sat, howFrontBall, norml, projectLine, insideEllipse, howPerpBall, perpl, angError, derivative
import math

def goToBall(rb, rg, vb, rl):
    # Acrescenta um offset
    if any(np.abs(rb) > rl):
        offset = 0
    else:
        offset = -0 * unit(angl(rg-rb)) #+ 0.015 * unit(angl(rg-rb) + np.pi/2)

    rb = rb + offset
    
    # Ângulo da bola até o gol
    angle = ang(rb, rg)

    dth = derivative(lambda x : ang((x, rb[1]), rg), rb[0]) * vb[0] + derivative(lambda y : ang((rb[0], y), rg), rb[1]) * vb[1]
    v = (*vb, dth)
    return np.array([*rb[:2], angle]), v

def avoidObstacle(rt, rr, rl, rps):
    obstacles = []
    
    a = rt[:2] - rr
    p = perpl(unit(ang(rr, rt[:2])))
    
    for rp in rps:
        A = np.array([a, p]).T
        b = rp - rr

        [alpha, beta] = np.linalg.solve(A, b)

        if np.abs(beta) < 0.10 and alpha > 0 and alpha < min(1, 0.30 / norml(a)):
            obstacles.append([rp, alpha, beta])

    if len(obstacles) == 0:
        return rt

    obstacles = np.array(obstacles, dtype=object)

    # Nearest obstacle has smallest alpha
    nearestIndex = np.argmin(obstacles[:,1])
    rpn, alphan, betan = obstacles[nearestIndex]

    # Possible virtual targets
    rtv1 = rpn - 0.10 * p * np.sign(betan)
    rtv2 = rpn + 0.10 * p * np.sign(betan)

    # Choose
    if np.all(np.abs(rtv1) < rl):
        return np.array([*rtv1, ang(rr, rt)])
    elif np.all(np.abs(rtv2) < rl):
        return np.array([*rtv2, ang(rr, rt)])
    else:
        return rt

def goToGoal(rg, rr, vr):
    # Ponto de destino é a posição do gol com o ângulo do robô até o gol
    angle = ang(rr, rg)
    dth = derivative(lambda x : ang((x, rr[1]), rg), rr[0]) * vr[0] + derivative(lambda y : ang((rr[0], y), rg), rr[1]) * vr[1]

    return np.array([*rg[:2], angle]), (0,0,-dth)

def goalkeep(rb, vb, rr, rg):
    xGoal = rg[0]
    #testar velocidade minima (=.15?)
    ytarget = projectLine(rb, vb, xGoal)
    if ((vb[0]) < -0.1): #and  ((rb[0]) > .15) and np.abs(ytarget) < 0.2:
        #verificar se a projeção está no gol
        #projetando vetor até um xGoal-> y = (xGoal-Xball) * Vyball/Vxball + yBall 
        ytarget = sat(ytarget, 0.20)
        angle = np.pi/2 if rr[1] < ytarget else -np.pi/2
        return (xGoal, ytarget, angle)
    #Se não acompanha o y
    ytarget = sat(rb[1],0.20)
    angle = np.pi/2 if rr[1] < ytarget else -np.pi/2
    return np.array([xGoal, ytarget, angle])
 
def blockBallElipse(rb, vb, rr, rm, a, b):
    e = np.array([1/a, 1/b])
    spin = 0
    
    d = norml(e*(rr[:2]-rm))
    #if np.abs(d-1) < 0.5: e = e / d

    finalTarget = rm

    vb = rb - finalTarget
    k = 1/np.sqrt(np.dot(e*vb, e*vb)) #* np.sign(vb[0])
    r = finalTarget + k *(vb)
    r_ = r-rm
    o = math.atan2(r_[1], r_[0])
    t = math.atan2(a*math.sin(o), b*math.cos(o))
    r_ort = (-a*math.sin(t), b*math.cos(t))
    r_ort_angle = math.atan2(r_ort[1], r_ort[0])
    
    if rr[1] > r[1] and r_ort_angle > 0: r_ort_angle = r_ort_angle+np.pi
    if rr[1] < r[1] and r_ort_angle < 0: r_ort_angle = r_ort_angle+np.pi

    if not insideEllipse(rb, a, b, rm) and norm(rr, rb) < 0.09:
       spin = 1 if rr[1] > rb[1] else -1

    # if insideEllipse(rb, a, b, rm):
    #     return (r[0], -r[1], r_ort_angle), spin
    
    return (r[0], r[1], r_ort_angle), spin
    # return (r[0], r[1], r_ort_angle)
    
def spinGoalKeeper(rb, rr, rm):
    if norm(rr, rb) < 0.1:
        spin = 1 if rr[1] > rb[1] else -1
    else:
        spin = 0

    return spin

def intercept(rr, rb, direction, rg, vb, vrref=0.5, arref=1.4):

    A = np.array([
        [direction[0] * vrref, -vb[0]],
        [direction[1] * vrref, -vb[1]],
    ])

    B = np.array([
        rb[0] - rr[0],
        rb[1] - rr[1]
    ])

    try:
        tvec = scipy.linalg.solve(A, B)
        #if tvec[0] < 0: return False

        t1 = tvec[0]#np.sqrt(2 * tvec[0])
        t2 = tvec[1]

        r = rb + t2 * vb
        #print([t1, t2])
        if abs(t1 - t2) < 0.09 and t1 >= 0 and r[0] < rg[0] - 0.1 and r[0] >= 0:
            return True
        else:
            return False
    except:
        return False

def spinDefender(rb, rr, rm):
    if norm(rb, rm) > norm(rr, rm) and norm(rr, rb) < 0.12:
        spin = 1 if rr[1] > rb[1] else -1
    else:
        spin = 0

    return spin

def mirrorPosition(rr, vr, rb, rg):
    angle = -1 * ang(rb, rg)

    dx = vr[0]
    dy = -vr[1]
    dth = 0

    return (rr[0]-.1, -1 * rr[1], angle), (dx, dy, dth)

    # r1 = rr - rb
    # r2 = vb - unit(ang(rr, rg)) * vrref

    # t1 = r1[0] / r2[0]
    # t2 = r1[1] / r2[1]

    # rp1 = rb + t2 * vb
    # rp2 = rr + unit(ang(rr, rg)) * vrref * t1

    # #print("t1: {}\tt2: {}".format(t1, t2))

    # if norm(rp1, rp2) < 0.05 and t1 >= 0 and rp1[0] < rg[0]:
    #     return True

    # else:
    #     return False
