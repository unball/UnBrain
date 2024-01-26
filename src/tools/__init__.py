import numpy as np

# Constantes físicas do robô
wheel_reduction = 5

# Supostamente devia ser
#r = 0.0325
#L = 0.075

# O que realmente é
r = 0.02
L = 0.080

def speeds2motors(v: float, w: float) -> (int, int):
  """Recebe velocidade linear e angular e retorna velocidades para as duas rodas"""

  # Computa a velocidade angular de rotação de cada roda
  vr = (v + (L/2)*w) / r#/ (2*np.pi*r) * wheel_reduction
  vl = (v - (L/2)*w) / r#/ (2*np.pi*r) * wheel_reduction

  #if fabs(vr) > max_motor_speed or fabs(vl) > max_motor_speed:
  #  vr = max_motor_speed * vr / max(vr, vl)
  #  vl = max_motor_speed * vl / max(vr, vl)
  
  # vr *= convertion
  # vl *= convertion
  
  return vl, vr

def motors2linvel(vl: float, vr: float) -> float:
  # Computa a velocidade angular de rotação de cada roda
  return (vr + vl) * (2*np.pi*r) / wheel_reduction / 2

def angl(p0: tuple):
  """Calcula o ângulo da tupla `p0` no plano este ângulo está em \\((-\\pi,\\pi]\\)"""
  return np.arctan2(p0[1], p0[0])

def unit(angle):
  """Retorna um vetor unitário de ângulo `angle` no formato de numpy array"""
  return np.array([np.cos(angle), np.sin(angle)])

def norm(p0: tuple, p1: tuple):
  """Calcula a distância entre as tuplas `p0` e `p1` no plano"""
  return np.sqrt((p1[0]-p0[0])**2+(p1[1]-p0[1])**2)

def norml(p0: tuple):
  """Calcula a norma de `p0"""
  return np.sqrt((p0[0])**2+(p0[1])**2)

def angError(reference: float, current: float) -> float:
  """Calcula o erro angular entre `reference` e `current` de modo que este erro esteja no intervalo de \\((-\\pi,\\pi]\\) e o sinal do erro indique qual deve ser a orientação para seguir a referência, de modo que positivo é anti-horário e negativo é horário"""
  diff = np.arccos(np.cos(reference-current))
  sign = (np.sin(reference-current) >= 0)*2-1
  return sign * diff

def adjustAngle(angle: float) -> float:
  """Pega um ângulo em \\(\\mathbb{R}\\) e leva para o correspondente em \\((-\\pi,\\pi]\\)"""
  return angError(angle, 0)

def sat(x: float, amp: float):
  """Satura um número real `x` entre `amp` e `-amp`"""
  return max(min(x, amp), -amp)

def sats(x: float, ampn: float, ampp: float):
  return max(min(x, ampp), ampn)

def ang(p0: tuple, p1: tuple):
  """Calcula o ângulo entre as tuplas `p0` e `p1` no plano, este ângulo está em \\((-\\pi,\\pi]\\)"""
  return np.arctan2(p1[1]-p0[1], p1[0]-p0[0])

def filt(x: float, amp: float):
  if np.abs(x) > np.abs(amp): return 0
  else: return x

def fixAngle(angle: float):
  if abs(angle) > np.pi/2:
    return (angle + np.pi/2) % (np.pi) - np.pi/2
  else:
    return angle

def derivative(vs, dt, order=1):
    if order == 1: return (vs[0] - vs[1]) / dt
    elif order == 2: return (vs[0] - 2*vs[1] + vs[2]) / dt**2

def angularDerivative(vs, dt, order=1):
    if order == 1: return adjustAngle(vs[0] - vs[1]) / dt
    elif order == 2: return adjustAngle(vs[0] - 2*vs[1] + vs[2]) / dt**2

def howFrontBall(rb, rr, rg):
    return np.dot(rr[:2]-rb, unit(angl(rg-rb)))

def howPerpBall(rb, rr, rg):
    return np.dot(rr[:2]-rb, unit(angl(rg-rb)+np.pi/2))

def projectLine(r, v, xline):
  return ((xline-r[0])/v[0])*v[1] + r[1] if v[0] != 0 else 0

def insideEllipse(r, a, b, rm):
  """ Retorna se a posição r está dentro da elipse de parâmetros a, b e centro rm"""
  return ((r[0]-rm[0])/a)**2+((r[1]-rm[1])/b)**2 < 1

def angleRange(th):
  if th >= 0 and th <= np.pi: return th
  else: return th + 2*np.pi

def deadZone(x, w):
  return x-np.sign(x)*w if np.abs(x) > w else 0

def deadZoneDisc(x, w):
  return x if np.abs(x) > w else 0

def distToBall(pa, pb, pc):
  """ Retorna a distância entre ponto c e reta que passa por a e b"""
  a = (pa[1] - pb[1])
  b = (pa[0] - pb[1])
  c = pa[0]*pb[1] - (pb[0] + pa[1])
  return np.abs((a*pc[0] + b*pc[1] + c)) / np.sqrt(a**2 + b**2)

def perpl(r):
  return np.array([r[1], -r[0]])
  
def bestWithHyst(state: int, possibleStates: list, possibleStatesDistances: list, hyst: float):
  if state in possibleStates:
    distances = np.array(possibleStatesDistances) + [hyst for s in possibleStates if s != state]
  else:
    distances = np.array(possibleStatesDistances)

  best = np.argmin(distances)
  return possibleStates[best]