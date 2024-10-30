"""
def process(self, frame):

# Mensagem de retorno
mensagem = VisionMessage(5)

# Corta o campo
img_warpped = self.warp(frame)

# Formata como HSV
img_hsv = self.converterHSV(img_warpped)

# Segmenta o que não é o fundo
fgMask = self.obterMascaraElementos(img_hsv)

# Segmenta o time
teamMask = self.obterMascaraTime(img_hsv)

# Segmenta a bola
bolaMask = self.obterMascaraBola(img_hsv)

# Tenta identificar uma bola
bola = self.identificarBola(bolaMask & fgMask)
mensagem.setBall(bola)

# O que não é fundo nem bola
fgMaskNoBall = cv2.bitwise_and(fgMask, cv2.bitwise_not(bolaMask))

# Encontra componentes conectados e aplica operações de abertura e dilatação
components = self.obterComponentesConectados(fgMaskNoBall)

#print([x.meanId for x in self._world.robots])

# Itera por cada elemento conectado
for componentMask in components:
    
  # Obtém dados do componente como uma camisa
  camisa = self.detectarCamisa(componentMask)
  
  # Camisa tem área pequena
  if camisa is None: continue
  
  centro, centerMeters, angulo, camisaContours = camisa
  
  # Máscara dos componentes internos do elemento
  componentTeamMask = componentMask & teamMask
  
  # Tenta identificar um aliado
  aliado = self.detectarTime(componentTeamMask, centro, angulo, centerMeters)
  if aliado is not None:
    mensagem.setRobot(aliado[0], (*centerMeters, aliado[1]*np.pi/180), internalContours=aliado[2])
  
  # Adiciona camisa como adversário
  else:
    mensagem.setEnemyRobot((*centerMeters, angulo*np.pi/180), extContour=camisaContours)

return mensagem

"""
from PySide6.QtWidgets import QFrame
from elements import Robot, Ball

class Vision:
    def __init__(self, initialFrame: QFrame, robots: list[Robot], ball: Ball) -> None:
        self. updatedFrame = initialFrame
        self.elements = {
            "robots": robots,
            "ball": ball
        }