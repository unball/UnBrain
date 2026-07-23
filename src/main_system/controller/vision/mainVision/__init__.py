from main_system.controller.vision import Vision
from main_system.controller.vision.visionMessage import VisionMessage
from main_system.model.vision.mainVisionModel import MainVisionModel
from main_system.controller.tools.pixel2metric import pixel2meters, meters2pixel, normToAbs
from main_system.controller.tools import norm
from main_system.view.tools.drawing import Drawing
import cv2
import numpy as np
import time

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

    self._angle_filter_deg = {}
    """Estado (graus, domínio DESEMBRULHADO/contínuo) da média móvel exponencial
    de ângulo por identificador. Ver `_finalize_angle`."""

    self._last_seen_time = {}
    """Timestamp (time.time()) da última vez que cada id foi reclamado com
    sucesso em `_assign_ids`. Usado para "rebaixar" um robô perdido de volta a
    NÃO-VISTO após `LOST_TIMEOUT_S` sem casamento por posição — sem isso,
    `poseDefined` nunca voltava a False e um robô ocluso por tempo suficiente
    para se deslocar >MAX_TRACK_DIST_M ficava permanentemente sem dono (nem
    posição nem forma o recuperavam): o robô "sumia" da interface."""

    self.__undistort_cache = None
    """Cache dos mapas de `cv2.initUndistortRectifyMap` usados por `apply_undistort`.
    Guarda (w, h, K, D, map1, map2); é invalidado só quando K, D ou o tamanho do
    frame mudam (ex.: recalibração de lente ou troca de resolução de câmera)."""

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

  @property
  def use_clahe(self):
    return self.__model.use_clahe
    
  @use_clahe.setter
  def use_clahe(self, value):
    self.__model.use_clahe = value

  @property
  def robot_angle_offsets(self):
    offsets = self.__model.robot_angle_offsets
    while len(offsets) < 5:
        offsets.append(0.0)
    return offsets

  def set_camera_params(self, K, D):
    self.__model.camera_matrix = K
    self.__model.dist_coeffs = D

  def get_camera_params(self, frame_shape):
    K = self.__model.camera_matrix
    D = self.__model.dist_coeffs
    
    if K is None or D is None:
      # Fallback aproximado adaptativo
      h, w = frame_shape[:2]
      fx = w * 1.17
      fy = fx
      cx = w / 2.0
      cy = h / 2.0
      K = [[fx, 0.0, cx], [0.0, fy, cy], [0.0, 0.0, 1.0]]
      D = [[-0.12, 0.0, 0.0, 0.0, 0.0]]
      
    return np.array(K, dtype=np.float32), np.array(D, dtype=np.float32)

  def _get_undistort_maps(self, K, D, shape):
    """Retorna os mapas de undistort cacheados para `(K, D, shape)`, recalculando
    só quando algum desses três mudar. `cv2.undistort` por baixo dos panos chama
    `initUndistortRectifyMap` (caro: monta um mapa pixel-a-pixel) toda vez que é
    invocado; aqui isso é feito uma única vez e reaproveitado via `cv2.remap`
    (que só faz a reamostragem, sem recalcular o mapa) em cada frame."""
    h, w = shape[:2]
    cache = self.__undistort_cache
    if (cache is not None and cache[0] == w and cache[1] == h
        and np.array_equal(cache[2], K) and np.array_equal(cache[3], D)):
      return cache[4], cache[5]

    map1, map2 = cv2.initUndistortRectifyMap(K, D, None, K, (w, h), cv2.CV_16SC2)
    self.__undistort_cache = (w, h, K.copy(), D.copy(), map1, map2)
    return map1, map2

  def apply_undistort(self, frame):
    K, D = self.get_camera_params(frame.shape)
    map1, map2 = self._get_undistort_maps(K, D, frame.shape)
    return cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)

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
    
  def atualizarRobotAngleOffset(self, value, index):
    """Atualiza o offset de ângulo da frente de um robô específico."""
    self.__model.robot_angle_offsets[index] = value
  
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
    
    frame = self.apply_undistort(frame)
    
    if self.use_clahe:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
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
    area = cv2.contourArea(countor)
    
    rect = cv2.minAreaRect(countor)
    rectArea = rect[1][0]*rect[1][1]
    
    # Utiliza também o minEnclosingTriangle para ter uma métrica robusta em cantos/blobs
    _, tri = cv2.minEnclosingTriangle(countor)
    triArea = cv2.contourArea(tri)
    
    ratioRect = area / rectArea if rectArea > 0 else 0
    ratioTri = area / triArea if triArea > 0 else 0
    
    # Se o RatioTri for melhor (muito próximo de 1.0) ou se ele ganha do RatioRect, é triângulo
    # Triângulos tendem a ter RatioTri ~ 1.0 e RatioRect ~ 0.5
    # Retângulos tendem a ter RatioRect ~ 1.0 e RatioTri ~ 0.5
    if ratioTri > ratioRect:
        return 3
        
    return 4 if ratioRect > self.__model.cont_rect_area_ratio else 3
    
  def analisarTime(self, componentTeamMask, center, centerMeters):
    """Extrai a FORMA (candidato) e o VETOR de orientação de um blob aliado, SEM
    decidir o id — a atribuição de id é GLOBAL e acontece em `_assign_ids`
    depois de todos os blobs do frame terem sido coletados. Retorna None se o
    componente não for do nosso time (sem contorno da cor do time)."""
    internalContours,_ = cv2.findContours(componentTeamMask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    internalContours = [c for c in internalContours if cv2.contourArea(c) >= self.__model.min_internal_area_contour]
    if len(internalContours) == 0:
      return None

    mainShape = max(internalContours, key=cv2.contourArea)
    M = cv2.moments(mainShape)
    if M["m00"] == 0:
      return None
    cX = M["m10"] / M["m00"]
    cY = M["m01"] / M["m00"]

    poligono = self.definePoly(mainShape)
    candidato = (0 if poligono == 3 else 2) + len(internalContours) - 1
    if candidato >= self._world.n_robots:
      # Forma inválida como seed, mas o blob É aliado — mantém como candidato de
      # TRACK (por posição). Antes virava "adversário", perdendo um robô real.
      candidato = None

    # ÂNGULO ROBUSTO: centróide de TODA a máscara da cor do time (momentos da
    # máscara inteira), não do maior contorno isolado. Com a segmentação
    # fragmentada (faixa HSV estreita) "o maior contorno" pisca entre fragmentos
    # frame a frame e joga o centróide — e o ângulo — para todo lado. A máscara
    # inteira é estável a isso. Se não houver massa, mantém o centróide do maior
    # contorno (cX,cY).
    Mfull = cv2.moments(componentTeamMask, binaryImage=True)
    if Mfull["m00"] > 0:
      cX = Mfull["m10"] / Mfull["m00"]
      cY = Mfull["m01"] / Mfull["m00"]

    # Vetor detalhe(cor do time) -> centro da camisa (y invertido p/ coords de
    # imagem). Convenção de "frente" preservada; só a estabilidade mudou.
    dx = center[0] - cX
    dy = -(center[1] - cY)
    mag = float(np.hypot(dx, dy))

    return {"centerMeters": centerMeters, "candidato": candidato,
            "internalContours": internalContours, "dx": dx, "dy": dy, "mag": mag}

  def _assign_ids(self, blobs):
    """Atribuição 1-para-1 GLOBAL blob->id.

    O que causava a troca constante: a atribuição anterior (argmin/greedy) era
    dependente da ORDEM dos componentes conectados, que muda de frame a frame;
    com dois robôs próximos, quem é processado primeiro "ganha" o id e a
    identidade pisca. Aqui montamos a matriz de distâncias blob×robô e
    resolvemos por MENOR distância primeiro (global, independente de ordem):
    cada blob e cada id são usados no máximo uma vez.

    IMPORTANTE (regressão corrigida): o gate SEED/TRACK é POR ROBÔ, não global.
    Uma versão anterior usava `seeded = all(robôs poseDefined)` — enquanto
    QUALQUER robô ainda não tivesse sido visto, TODOS os blobs (inclusive os já
    rastreados corretamente por posição) voltavam a ser classificados por
    FORMA a cada frame. Como a classificação de forma é ruidosa com a
    calibração atual (`cont_rect_area_ratio` quase sempre dá "retângulo"), um
    robô já identificado corretamente podia ser reclassificado para o id
    errado só porque o terceiro robô ainda não apareceu — pior que o código
    original (que usava forma só no 1º frame processado, nunca mais depois).

    RECUPERAÇÃO DE ROBÔ "PERDIDO" (2ª regressão corrigida): `poseDefined` do
    `Element` nunca volta a False sozinho — uma vez visto, um robô fica
    "conhecido" PARA SEMPRE. Combinado com o teto de distância abaixo, um robô
    ocluso (por outro robô, pela bola, por uma mão) tempo suficiente para se
    deslocar mais que o teto ficava sem dono: não casa por posição (longe
    demais do `raw_pos` congelado) nem por forma (não está mais em `unknown`)
    — o robô "sumia" da interface até, por sorte, reaparecer bem perto de onde
    sumiu. Agora, todo id conhecido não reclamado neste frame tem seu tempo
    desde a última vez visto checado: passado `LOST_TIMEOUT_S`, ele é
    REBAIXADO (poseDefined=False) e volta a ser elegível para semeadura por
    forma no PASSO 2 deste mesmo frame.

    Agora:
    - Robôs JÁ VISTOS (`poseDefined`) só são casados por POSIÇÃO (nearest-
      neighbor global, nunca mais por forma) — a menos que tenham acabado de
      ser rebaixados por timeout.
    - Robôs AINDA NÃO VISTOS (ou recém rebaixados) só são semeados por FORMA
      (candidato), usando os blobs que sobraram após o casamento por posição."""
    n = self._world.n_robots
    assign = {}
    if n == 0:
      return assign

    now = time.time()
    LOST_TIMEOUT_S = 1.0  # tempo sem casamento por posição até rebaixar p/ "não visto"

    known = [i for i in range(n) if self._world.robots[i].poseDefined]
    unknown = [i for i in range(n) if not self._world.robots[i].poseDefined]

    if not blobs:
      return assign

    # 1) Robôs já vistos: casamento global por posição (menor distância primeiro),
    # com TETO de distância. Sem teto, com só 1 blob e 1 robô conhecido restando,
    # o casamento greedy forçava o par mesmo a quase 1m de distância — roubando
    # o id de um robô conhecido de um blob que na verdade era outro robô ainda
    # não visto. O teto (bem maior que o deslocamento real entre frames, mas
    # bem menor que o campo) deixa esses blobs caírem para o passo 2 (forma).
    MAX_TRACK_DIST_M = 0.30
    usadosB, usadosI = set(), set()
    if known:
      pares = []
      for bi, b in enumerate(blobs):
        for i in known:
          d = norm(b["centerMeters"], self._world.robots[i].raw_pos)
          if d <= MAX_TRACK_DIST_M:
            pares.append((d, bi, i))
      pares.sort(key=lambda t: t[0])
      for _, bi, i in pares:
        if bi in usadosB or i in usadosI:
          continue
        assign[bi] = i
        usadosB.add(bi)
        usadosI.add(i)

    # 1b) Rebaixa por timeout quem ficou "conhecido" mas não foi reclamado.
    for i in known:
      if i in usadosI:
        continue
      if now - self._last_seen_time.get(i, now) > LOST_TIMEOUT_S:
        self._world.robots[i].poseDefined = False
        unknown.append(i)

    # 2) Robôs não vistos (ou recém rebaixados): semeados por FORMA, só com os
    # blobs que sobraram do passo 1.
    for bi, b in enumerate(blobs):
      if bi in usadosB:
        continue
      c = b["candidato"]
      if c is not None and c in unknown and c not in usadosI:
        assign[bi] = c
        usadosB.add(bi)
        usadosI.add(c)

    for i in usadosI:
      self._last_seen_time[i] = now

    return assign

  def _finalize_angle(self, identificador, dx, dy, mag):
    """Finaliza o ângulo do robô `identificador` a partir do vetor de
    orientação (detalhe->centro da camisa), suavizado por uma média móvel
    exponencial no domínio DESEMBRULHADO (contínuo, sem limite de ±180°), com
    peso proporcional à magnitude do vetor em pixels. Retorna (est, base) em
    graus, normalizados em [-180,180].

    REGRESSÃO CORRIGIDA (2ª rodada): a versão anterior CONGELAVA o ângulo
    (reusava o último valor bom para sempre) sempre que `mag` ficasse abaixo de
    um limiar fixo (3px). Para camisas cujo detalhe de cor fica fisicamente
    perto do centro geométrico da camisa, essa condição é quase SEMPRE
    verdadeira — o ângulo nunca mais era atualizado, reproduzindo o mesmo
    sintoma do latch antigo em world.py (robô físico giranco infinitamente,
    interface mostrando ângulo constante), só que nascendo aqui.

    Agora nenhuma leitura é descartada: cada frame entra na média com peso
    proporcional a `mag` (leituras de vetor curto — mais suscetíveis a ruído
    de segmentação, já que erro angular ~ atan(ruído_px / mag_px) cresce muito
    quando mag é pequeno — pesam pouco, mas nunca ZERO). O ângulo sempre
    acompanha a rotação real (inclusive muitas voltas seguidas, pois a média é
    feita no domínio desembrulhado), só que mais suavizado quando o sinal geo-
    métrico é fraco."""
    raw = 180.0 / np.pi * np.arctan2(dy, dx)

    REFERENCE_PX = 8.0   # magnitude (px) a partir da qual a leitura já é 100% confiável
    MIN_ALPHA = 0.05     # piso: mesmo um vetor bem curto ainda pesa um pouco,
                         # para o ângulo NUNCA travar de vez

    prev = self._angle_filter_deg.get(identificador)
    if prev is None or mag < 1e-6:
      # Primeira leitura deste id, ou vetor verdadeiramente nulo (direção
      # indefinida): usa o valor cru como ponto de partida, sem suavizar.
      calc = raw if prev is None else prev
      self._angle_filter_deg[identificador] = calc
    else:
      # Desembrulha `raw` para o valor mais próximo de `prev` (continuidade
      # através da virada ±180°) antes de suavizar.
      delta = ((raw - prev + 180) % 360) - 180
      raw_unwrapped = prev + delta
      # alpha vai até 1.0 (SEM lag, valor cru) assim que mag>=REFERENCE_PX —
      # só suaviza de fato (e só então introduz atraso) quando o sinal é
      # fraco. Isso evita o lag artificial de girar rápido com leitura boa.
      alpha = MIN_ALPHA + (1.0 - MIN_ALPHA) * min(1.0, mag / REFERENCE_PX)
      calc = prev + alpha * (raw_unwrapped - prev)
      self._angle_filter_deg[identificador] = calc

    est = calc + self.__model.robot_angle_offsets[identificador]
    est = (est + 180) % 360 - 180
    calc = (calc + 180) % 360 - 180
    return est, calc

  def process(self, frame):
    """Implementa o `process` da classe mãe compondo a mensagem de alteração da visão"""
    
    # Mensagem de retorno
    mensagem = VisionMessage(self._world.n_robots)

    # Corta o campo
    img_warpped = self.warp(frame)
    
    # Formata como HSV
    img_hsv = self.converterHSV(img_warpped)
    
    # Segmenta o que não é o fundo
    fgMask = self.obterMascaraElementos(img_hsv)

    # Cacheia o frame warpado e a máscara de elementos deste frame para que
    # consumidores de DISPLAY (ex.: ParametrosVisao, VisaoAltoNivel) não
    # precisem recalcular warp+HSV+máscara só para desenhar por cima do
    # resultado — antes disso, cada um deles refazia esse pipeline inteiro e
    # AINDA chamava `process()` de novo (que o refaz mais uma vez), triplicando
    # o trabalho de CV no mesmo frame quando a aba de visão estava aberta.
    self.last_warpped_frame = img_warpped
    self.last_elements_mask = fgMask

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

    # 1ª passada: coleta os blobs aliados (com forma + vetor de ângulo, ainda
    # SEM id) e envia os não-aliados como adversários.
    allyBlobs = []
    for componentMask in components:
      camisa = self.detectarCamisa(componentMask)
      if camisa is None:
        continue
      centro, centerMeters, angulo, camisaContours = camisa
      componentTeamMask = componentMask & teamMask
      dados = self.analisarTime(componentTeamMask, centro, centerMeters)
      if dados is None:
        mensagem.setEnemyRobot((*centerMeters, angulo*np.pi/180), extContour=camisaContours)
      else:
        allyBlobs.append(dados)

    # 2ª passada: atribuição GLOBAL blob->id (independente da ordem dos
    # componentes) e emissão da pose de cada robô identificado.
    assign = self._assign_ids(allyBlobs)
    for bi, dados in enumerate(allyBlobs):
      identificador = assign.get(bi)
      if identificador is None:
        continue  # blob aliado sem id livre (excedente/ruído): ignora
      estAngulo, baseAngle = self._finalize_angle(
          identificador, dados["dx"], dados["dy"], dados["mag"])
      cm = dados["centerMeters"]
      mensagem.setRobot(
          identificador, (cm[0], cm[1], estAngulo * np.pi / 180.0),
          dados["internalContours"], baseAngle * np.pi / 180.0)

    return mensagem
