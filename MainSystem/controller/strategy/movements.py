from controller.tools import ang, angl, unit, angError, norm, norml, sat, shift, derivative, projectLine, insideEllipse
import numpy as np
import math

def howFrontBall(rb, rr, rg):
    return np.dot(rr[:2]-rb, unit(angl(rg-rb)))

def howPerpBall(rb, rr, rg):
    return np.dot(rr[:2]-rb, unit(angl(rg-rb)+np.pi/2))

def projectBall(rb, vb, rr, rg, limits: tuple, vrref=0.25):
    # Bola fora dos limites, retorna a própria posição da bola
    if any(np.abs(rb) > limits):
        return rb

    # Computa os tempos de interceptação possíveis
    ts = np.roots([norml(vb) ** 2 - vrref**2, 2 * np.dot(rb-rr[:2], vb), norml(rr[:2]-rb)**2 ])

    # Filtra por tempos positivos
    ts = [x for x in ts if x >= 0]

    # Não conseguiu encontrar um tempo positivo real
    if len(ts) == 0 or np.iscomplex(min(ts)):
        rbp = rb + norm(rb, rr) / vrref * vb
    
    # Computa a projeção
    else:
        t = min(ts)
        rbp = rb + t * vb

    # Acrescenta um offset
    offset = -0.06 * unit(angl(rg-rbp)) + 0.015 * unit(angl(rg-rbp) + np.pi/2)

    return rbp + offset

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

def followBally(rb, rr):
    angle = np.pi/2 if rr[1] < rb[1] else -np.pi/2
    return (0.2, rb[1], angle)

def blockBallElipse(rb, vb, rr, rm):
    a = 0.3
    b = 0.45
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

    #if not insideEllipse(rb, a, b, rm) and norm(rr, rb) < 0.09:
    #    spin = 1 if rr[1] < rb[1] else -1

    return (r[0], r[1], r_ort_angle), spinDefender(rb, rr, rm)

    #return followBally(rb, rr)

def spinDefender(rb, rr, rm):
    if norm(rb, rm) > norm(rr, rm) and norm(rr, rb) < 0.12:
        spin = 1 if rr[1] > rb[1] else -1
    else:
        spin = 0

    return spin

def spinGoalKeeper(rb, rr, rm):
    if norm(rr, rb) < 0.12:
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
