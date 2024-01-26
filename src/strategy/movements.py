import numpy as np
import scipy
from tools import unit, angl, ang, norm, sat, howFrontBall, norml, projectLine, insideEllipse, howPerpBall, perpl
import math

def goToBall(rb, vb, rg, rr, rl, vravg, offset=0.015):
    rb = rb.copy()
    #rbp = rb + vb * norm(rb, rr) / (vravg + 0.00001)

    u = np.roots([norml(vb) ** 2 - (max(vravg-0.05, 0.3))**2, 2 * np.dot(rb-rr[:2], vb), norml(rr[:2]-rb)**2])
    u = [x for x in u if x >= 0 and not(np.iscomplex(x))]

    if len(u) == 0 or norm(rb, rr) < 0.1:
        rbp = rb
    else:
        rbp = rb + u * vb
        
    #rbp = rb

    # Não precisa ir para o futuro se já está atras da bola indo para tras ou na frente da bola indo para frente
    if howFrontBall(rr, rb, rg) < 0 and howFrontBall(rbp, rb, rg) < 0 or howFrontBall(rr, rb, rg) > 0 and howFrontBall(rbp, rb, rg) > 0:
        rbp = rb

    #rbp[0] = max(rbp[0], -rl[0])
    rbp[0] = sat(rbp[0], rl[0])
    rbp[1] = sat(rbp[1], rl[1])
    offsetVector = offset * unit(angl(rg-rbp))#+ 0.015 * unit(angl(rg-rb) + np.pi/2)

    # Limita x da bola no nosso lado
    rbp[0] = max(rbp[0], -0.20)

    target = rbp + offsetVector
    target[0] = sat(target[0], rl[0])
    target[1] = sat(target[1], rl[1])
    
    # Ângulo da bola até o gol
    if abs(rbp[1]) >= rl[1]: angle = 0
    else: angle = ang(target, rg)

    return np.array([*target[:2], angle])

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

def goalkeep(rb, vb, rr, rg):
    xGoal = rg[0] 

    #projeta a velocidade da bola 
    ytarget = projectLine(rb, vb, xGoal+0.05)
    if ((vb[0]) < -0.03): #and  ((rb[0]) > .15) and np.abs(ytarget) < 0.2:
        #verificar se a projeção está no gol
        ytarget = sat(ytarget, 0.2)
        angle = np.pi/2 if rr[1] < ytarget else -np.pi/2
        return (xGoal, ytarget, angle)

    #Se não, acompanha o y
    ytarget = sat(rb[1], 0.2 + 0.27 * (rb[0] < -0.6 and abs(rb[1]) < 0.37))
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
    if norm(rr, rb) < 0.08:
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
