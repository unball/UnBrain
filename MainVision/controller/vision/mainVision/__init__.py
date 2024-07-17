from controller.vision import Vision
from controller.vision.visionMessage import VisionMessage
from model.vision.mainVisionModel import MainVisionModel
from controller.tools.pixel2metric import pixel2meters, meters2pixel, normToAbs
from controller.tools import norm
from view.tools.drawing import Drawing
import cv2
import numpy as np

class MainVision(Vision):
  """Classe que implementa a visão principal da UnBall, que utiliza segmentação por única cor e faz a identificação por forma."""
  
  def __init__(self, world, port):
    super().__init__(world=world, port=port)
    
    self.__model = MainVisionModel()
    """Modelo `MainSystem.model.vision.mainVisionModel.MainVisionModel` que mantém as variáveis da visão"""
    
    self.__current_frame_shape = None
    """Mantém o formato do frame, caso mude a matriz de homografia será recalculada com base nos pontos (em coordenadas relativas) selecionados"""
    
    self.__homography_points_updated = False
    
    self.__angles = np.array([0, 90, 180, -90, -180])
    """Contém uma lista que corrige o ângulo do vetor que liga o centro de massa do detalhe ao centro de massa da camisa para o ângulo que o robô anda para frente"""

  @property
  def preto_hsv(self):
    """Retorna o valor dos limites HSV para segmentação dos elementos"""
    return self.__model.preto_hsv
    
  @property
  def time_hsv(self):
    """Retorna o valor dos limites HSV para segmentação do time"""
    return self.__model.time_hsv
    
  @property
  def bola_hsv(self):
    """Retorna o valor dos limites HSV para segmentação da bola"""
    return self.__model.bola_hsv
    
  # @property
  # def use_homography(self):
  #   """Retorna a variável `use_homography` que indica se é para usar a matriz de homografia ou usar um corte retangular"""
  #   return self.__model.use_homography
  
  @property
  def areaRatio(self):
    """Retorna a variável `cont_rect_area_ratio` que contém a razão área triângulo/retângulo. Essa razão é usada para diferenciar as duas formas"""
    return self.__model.cont_rect_area_ratio
    
  @property
  def minInternalAreaContour(self):
    """Retorna a variável `min_internal_area_contour` que contém a área mínima do contorno interno aceitável. Se for detectado um contorno de área menor que essa, esse contorno será filtrado."""
    return self.__model.min_internal_area_contour
    
  @property
  def minExternalAreaContour(self):
    """Retorna a variável `min_external_area_contour` que contém a área mínima do contorno externo aceitável. Se for detectado um contorno de área menor que essa, esse contorno será filtrado."""
    return self.__model.min_external_area_contour

  def updateInternalPolygon(self, points):
    self.__model.internalPolygonPoints = points
  
  def atualizarPretoHSV(self, value, index):
    """Atualiza o valor do limite HSV de índice `index` para segmentação dos elementos."""
    self.__model.preto_hsv[index] = value
  
  def atualizarTimeHSV(self, value, index):
    """Atualiza o valor do limite HSV de índice `index` para segmentação do time."""
    self.__model.time_hsv[index] = value
  
  def atualizarBolaHSV(self, value, index):
    """Atualiza o valor do limite HSV de índice `index` para segmentação da bola."""
    self.__model.bola_hsv[index] = value
    
  # def setUseHomography(self, value):
  #   """Atualiza o valor da flag `use_homography`."""
  #   self.__model.use_homography = value
    
  def updateCropPoints(self, points):
    """Atualiza os pontos de corte retangular."""
    self.__model.crop_points = points
    
  def updateHomographyPoints(self, points):
    """Atualiza os pontos chave para calcular a matriz de homografia."""
    self.__model.homography_points = points
    self.__homography_points_updated = True
  
  def atualizarAreaRatio(self, value):
    """Atualiza o parâmetro de área que diferencia retângulo de triângulo."""
    self.__model.cont_rect_area_ratio = value
    
  def atualizarMinInternalArea(self, value):
    """Atualiza o parâmetro de área mínima do contorno interno."""
    self.__model.min_internal_area_contour = value
    
  def atualizarMinExternalArea(self, value):
    """Atualiza o parâmetro de área mínima do contorno externo."""
    self.__model.min_external_area_contour = value
  
  def get_polygon_mask(frame, points):
      mask = np.zeros((*frame.shape[:2],1), np.uint8)
      if len(points) == 0: return cv2.bitwise_not(mask)
      pts = np.array([normToAbs(x[0], frame.shape) for x in points])
      cv2.fillConvexPoly(mask, pts, 255)
      return mask

  def crop(frame, p0, p1):
    """Método de classe que corta um frame dados dois pontos \\(p_0=(x_0,y_0)\\), \\(p_1=(x_1,y_1)\\) que definem as coordenadas inicial e final desde que \\(x_0<x_1\\) e \\(y_0<y_1\\)"""
    
    x, xf = (p0[0], p1[0])
    y, yf  = (p0[1], p1[1])
    return frame[y:yf, x:xf]
    
  def getHomography(self, shape):
    """Obtém a matriz de homografia"""
    if self.__homography_points_updated or self.__current_frame_shape != shape:
      if self.__model.homography_points is None:
        return None
      self.updateHomography(self.__model.homography_points, shape)
    return self.__model.homography
    
  def updateHomography(self, points, shape):
    """Atualiza a matriz de homografia com base nos pontos selecionados e no tamanho do frame"""
    height, width, _ = shape
    
    base = np.array([[0,0],[1,0],[1,1],[0,1]])
    key_points = np.array(points) * np.array([width, height])
    
    frame_points = base * np.array([width, height])
    
    h, mask = cv2.findHomography(key_points, frame_points, cv2.RANSAC)
    
    self.__model.homography = h.tolist()
    self.__homography_points_updated = False
    self.__current_frame_shape = shape
    self.__model.homography_points = points
    self.__homography = h
  
  def warp(self, frame):
    """Método que corta de forma retangular ou via homografia a depender de `MainSystem.model.vision.mainVisionModel.MainVisionModel`"""
    
    
    homography_matrix = self.getHomography(frame.shape)
    try:
      return cv2.warpPerspective(frame, np.array(homography_matrix), (frame.shape[1], frame.shape[0]))
    except:
      return frame
        
  def converterHSV(self, img):
    """Converte uma imagem RGB para HSV e aplica um filtro gaussiano"""
    img_filtered = cv2.GaussianBlur(img, (5,5), 0)
    return cv2.cvtColor(img_filtered, cv2.COLOR_BGR2HSV)
  
  def obterMascaraElementos(self,img):
    """Retorna uma máscara do que não é fundo"""
    fgMask = cv2.inRange(img, np.array(self.__model.preto_hsv[0:3]), np.array(self.__model.preto_hsv[3:6]))
    if len(self.__model.internalPolygonPoints) != 0: 
      fgMask &= MainVision.get_polygon_mask(img, self.__model.internalPolygonPoints)[:,:,0]
    return fgMask
    
  def obterMascaraTime(self, img):
    """Retorna uma máscara dos detalhes da camisa do time"""
    return cv2.inRange(img, np.array(self.__model.time_hsv[0:3]), np.array(self.__model.time_hsv[3:6]))
    
  def obterMascaraBola(self, img):
    """Retorna uma máscara do que é bola"""
    return cv2.inRange(img, np.array(self.__model.bola_hsv[0:3]), np.array(self.__model.bola_hsv[3:6]))
    
  def identificarBola(self, mask):
    """Com base em uma máscara, retorna posição em metros e raio da bola"""
    bolaContours,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    bolaContours = [countor for countor in bolaContours if cv2.contourArea(countor) >= self.__model.min_internal_area_contour]

    if len(bolaContours) != 0:
      bolaContour = max(bolaContours, key=cv2.contourArea)
      ((x,y), radius) = cv2.minEnclosingCircle(bolaContour)
      
      return (pixel2meters(self._world, (x,y), mask.shape), radius)
    
    else: return None
    
  def aplicarFiltrosMorfologicos(self, mask):
    """Aplica filtros morfológicos com o objetivo de retirar ruido a uma mascara"""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    filtered = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    filtered = cv2.dilate(filtered, kernel, iterations=1)
    return filtered
    
  def obterComponentesConectados(self, mask):
    """Retorna uma lista de máscaras de componentes conectados com base na máscara passada"""
    num_components, components = cv2.connectedComponents(mask)
    components = self.aplicarFiltrosMorfologicos(np.uint8(components))
    return [np.uint8(np.where(components == label, 255, 0)) for label in np.unique(components)[1:]]
    
  def detectarCamisa(self, component_mask):
    """Com base na máscara de um componente conectado extrai informação de posição e ângulo parcial de uma camisa"""
    # Encontra um contorno para a camisa com base no maior contorno
    mainContours,_ = cv2.findContours(component_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mainContours = [countor for countor in mainContours if cv2.contourArea(countor)>=self.__model.min_external_area_contour]
    
    countMainContours = len(mainContours)
    
    # Contorno pequeno
    if countMainContours == 0:
      return None
      
    mainContour = max(mainContours, key=cv2.contourArea)
    
    # Encontra o menor retângulo que se inscreve no contorno
    rectangle = cv2.minAreaRect(mainContour)
    
    # Calcula a posição e ângulo parcial da camisa com base no retângulo
    center = rectangle[0]
    centerMeters = pixel2meters(self._world, center, component_mask.shape)
    angle = rectangle[-1]
    
    return center, centerMeters, angle, mainContours
  
  def definePoly(self, countor):
    """Define se o contorno é mais parecido com um triângulo ou um retângulo"""
    rect = cv2.minAreaRect(countor)
    contourArea = cv2.contourArea(countor)
    rectArea = rect[1][0]*rect[1][1]
    
    return 4 if contourArea/rectArea > self.__model.cont_rect_area_ratio else 3
    
  def obterIdentificador(self, center, candidate):
    """
    .. todo:: Falta fazer usar o centro como base para saber se o candidato é ou não razoável
    Retorna o identificador com base no centro do robô e na identificação instantânea da camisa (devida somente ao frame atual) e retorna qual deve ser o identificador mais provável.
    """
    if not self.usePastPositions: return candidate
    
    nearestIdx = np.argmin([norm(x.raw_pos, center) for x in self._world.robots[:3]])
    return nearestIdx
  
  def detectarTime(self, componentTeamMask, center, rectangleAngle, centerMeters):
    """Com base na máscara do detalhe do time extrai identifica qual é o robô aliado e obtém o ângulo total"""
    
    # Encontra os contornos internos com área maior que um certo limiar e ordena
    internalContours,_ = cv2.findContours(componentTeamMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    internalContours = [countor for countor in internalContours if cv2.contourArea(countor)>=self.__model.min_internal_area_contour]
    
    countInternalContours = len(internalContours)
    
    # Não é do nosso time
    if countInternalContours == 0:
      return None
    
    # Seleciona a forma principal
    mainShape = max(internalContours, key=cv2.contourArea)
    
    # Calcula o centro do contorno principal
    M = cv2.moments(mainShape)
    if M["m00"] == 0: return None
    
    cX = M["m10"] / M["m00"]
    cY = M["m01"] / M["m00"]
    # Define qual o polígono da figura principal
    poligono = self.definePoly(mainShape)
    
    # Computa o identificador com base na forma e no número de contornos internos
    candidato = (0 if poligono == 3 else 2) + countInternalContours -1
    if candidato >= self._world.n_robots: return None
    
    identificador = self.obterIdentificador(centerMeters, candidato)

    # Calcula o ângulo com base no vetor entre o centro do contorno principal e o centro da camisa
    calculatedAngle = 180.0/np.pi *np.arctan2(-(center[1]-cY), center[0]-cX)
    if identificador == 1:
      calculatedAngle = calculatedAngle - 45.0
    partialAngles =  -rectangleAngle + self.__angles
    estimatedAngle = partialAngles[np.abs(calculatedAngle - partialAngles).argmin()]
      
    
    return identificador, estimatedAngle, internalContours
  
  def process(self, frame):
    """Implementa o `process` da classe mãe compondo a mensagem de alteração da visão"""
    
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
    
