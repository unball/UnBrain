from scipy.stats import alpha
from gi.repository import Gdk
from main_system.view.tools.cv2Renderer import cv2Renderer
from main_system.view.tools.drawing import Drawing
from main_system.controller.tools.pixel2metric import meters2pixel,pixel2meters,meters2pixelSize,invertAng,invertVec
from main_system.controller.tools import angl, unit
import numpy as np
import cv2
import itertools

import os

class HighLevelRenderer(cv2Renderer):
  def __init__(self, world, robotsGetter=None, ballGetter=None, on_click=None, on_scroll=None):
    # target_fps=60: este renderer só desenha o estado do mundo (robôs, campo
    # vetorial, bola) — não processa imagem de câmera nenhuma — então não há
    # ganho perceptível em desenhar acima da taxa de um monitor comum. Ao
    # contrário do cv2Renderer da aba de visão (MainVisionView), cujo worker É
    # o próprio pipeline de visão e por isso continua no padrão de 150 FPS.
    super().__init__(worker=self.renderer, target_fps=60)
    
    self.__world = world
    
    self.__robotsGetter = robotsGetter
    self.__ballGetter = ballGetter
    
    self.robot_images_yellow = {}
    self.robot_images_blue = {}
    self._load_robot_images()
    
    self.__movingRobot = None
    self.__mousePosition = (0,0)
    self.__on_click = on_click
    self.__on_scroll = on_scroll
    self.arrow_size = 15
    self.showField = -1
    self.positions = []
    
    # Adiciona eventos de mouse e trackpad
    eventBox = self.getEventBox()
    eventBox.connect("motion-notify-event", self.frameMouseOver)
    eventBox.connect("button-press-event", self.frameClick)
    eventBox.connect("button-release-event", self.frameRelease)
    eventBox.add_events(Gdk.EventMask.SMOOTH_SCROLL_MASK)
    eventBox.connect("scroll-event", self.frameScroll)

  def _load_robot_images(self):
    """Carrega as imagens dos robôs e gera versões azuis a partir das amarelas"""
    import os
    base_path = os.path.join(os.path.dirname(__file__), "..", "states", "images")
    for i in range(3):
      img_path = os.path.join(base_path, f"camisa{i}.png")
      blue_path = os.path.join(base_path, f"camisa_blue{i}.png")
      if os.path.exists(img_path):
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is not None:
            self.robot_images_yellow[i] = img
            
            # Make a blue version only for yellow pixels (Hue between 20 and 40)
            img_hsv = cv2.cvtColor(img[:,:,:3], cv2.COLOR_BGR2HSV)
            lower_yellow = np.array([15, 50, 50])
            upper_yellow = np.array([45, 255, 255])
            mask = cv2.inRange(img_hsv, lower_yellow, upper_yellow)
            
            img_hsv[:,:,0] = np.where(mask > 0, (img_hsv[:,:,0] + 80) % 180, img_hsv[:,:,0])
            blue_bgr = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)
            
            # Combine back with alpha channel
            blue_img = np.zeros_like(img)
            blue_img[:,:,:3] = blue_bgr
            blue_img[:,:,3] = img[:,:,3]
            self.robot_images_blue[i] = blue_img
            
            if not os.path.exists(blue_path):
                cv2.imwrite(blue_path, blue_img)
    
  @property
  def robots(self):
    if self.__robotsGetter is None: return []
    return self.__robotsGetter()

  @property
  def ball(self):
    if self.__ballGetter is None: return self.__world.ball
    return self.__ballGetter()
  
  def cursorDistance(self, position: tuple):
    """Calcula a distância da posição atual do mouse a `position`"""
    return abs(self.__mousePosition[0]-position[0])+abs(self.__mousePosition[1]-position[1])
    
  def findNearRobot(self):
    """Encontra um robô na lista de robos que esteja próximo do mouse"""
    width, height = self.getShape()
    w,h = meters2pixelSize(self.__world, (0.075,0.075), (height, width))
    nearRobots = [r for r in self.robots if self.cursorDistance(meters2pixel(self.__world, r.raw_pose, (height, width))) < w]
    if(len(nearRobots) != 0):
      return nearRobots[0]
    else: return None
      
  def frameMouseOver(self, widget, event):
    """Executado quando um mouse passa por cima da área de renderização, se um robô tiver sido selecionado, atualiza sua posição"""
    width, height = self.getShape()
    self.__mousePosition = (int(event.x), int(event.y))
    if self.__movingRobot is not None:
      position = pixel2meters(self.__world, (int(event.x), int(event.y)), (height, width))
      self.__movingRobot.raw_update(position[0], position[1], self.__movingRobot.raw_th)
  
  def frameClick(self, widget, event):
    """Executado quando um clique é feito na área de renderização, se um robô estiver perto da área de clique, marca o robô como selecionado"""
    nearRobot = self.findNearRobot()
    if nearRobot is not None:
        self.__movingRobot = nearRobot
    else:
      width, height = self.getShape()
      if self.__on_click is not None: self.__on_click(pixel2meters(self.__world, (int(event.x), int(event.y)), (height, width)))
  
  def frameScroll(self, widget, event):
    """Executado quando há evento de scroll, atualiza o ângulo do robô mais próximo"""
    nearRobot = self.findNearRobot()
    if nearRobot is not None:
        nearRobot.raw_th = nearRobot.raw_th+event.delta_y*0.1
    if self.__on_scroll is not None:
      width, height = self.getShape()
      mouse = pixel2meters(self.__world, (int(event.x), int(event.y)), (height, width))
      self.__on_scroll(mouse, event.delta_y)
          
  def frameRelease(self, widget, event):
    """Executado quando um clique é solto, faz o robô selecionado ficar `None`"""
    self.__movingRobot = None
    
  def draw_robot(self, frame, robot, idx):
    """Desenha um robô e seu target no frame"""
    import math
    # Se a posição contiver NaN, pula o desenho deste robô
    if any(math.isnan(x) for x in robot.raw_pose):
        return
        
    # Obtém posição em pixels do robô
    position = meters2pixel(self.__world, robot.raw_pose, frame.shape)
    w,h = meters2pixelSize(self.__world, (0.075,0.075), frame.shape)
    if w <= 0 or h <= 0:
      return
    
    # Desenha de outra cor o robô próximo do mouse
    robotColor = (255,0,0) if self.cursorDistance(position) < w else (0,255,0)
    
    # Desenha o retângulo do robô e a imagem (se existir)
    if idx in self.robot_images_yellow:
        img = self.robot_images_yellow[idx] if self.__world.team_yellow else self.robot_images_blue[idx]
        Drawing.draw_robot_image(frame, position, (w,h), robot.dir_raw_th, img)
    
    # Desenha o quadrado verde acima da camisa
    Drawing.draw_rectangle(frame, position, (w,h), robot.raw_th, directionAngle=robot.dir_raw_th, color=robotColor)

    if robot.entity is not None:
      cv2.circle(frame, (int(position[0]+w//2), int(position[1]-h//2)), w//10, color=robot.entity.color, thickness=-1)

    if robot.field is not None:
      # Desenha o campo na posição do robô
      Drawing.draw_arrow(frame, position, invertAng(robot.field.F(robot.pose), self.__world.fieldSide), color=(0,255,0), size=w)
    
      # Desenha o target do campo
      Drawing.draw_arrow(frame, meters2pixel(self.__world, invertVec(robot.field.Pb, self.__world.fieldSide), frame.shape), invertAng(robot.field.Pb[2], self.__world.fieldSide), color=(0,255,0), size=meters2pixelSize(self.__world, (0.08,0), frame.shape)[0])

    if self.cursorDistance(position) < w:
      # Escreve o número do robô
      cv2.putText(frame, str(idx), (int(position[0]+w), int(position[1]+h)), cv2.FONT_HERSHEY_SIMPLEX, 0.08*w/2*0.5, (255,255,255))

      # Escreve a letra da entidade do robô
      if robot.entity is not None:
        cv2.putText(frame, str(robot.entity.name[0]), (int(position[0]+w), int(position[1]-h*0.7)), cv2.FONT_HERSHEY_SIMPLEX, 0.08*w/2*0.5, (255,255,255))
    
  def draw_field(self, frame):
    """Desenha o campo no frame"""    

    # [HLC] Modo IPC: o UnBrain amostra o campo REAL da entidade numa thread separada
    # e envia a grade de ângulos. Aqui só desenhamos as setas a partir dela.
    grid = getattr(self.__world, 'hlc_uvf_grid', None)
    if self.showField != -1 and grid is not None and grid.get("robot") == self.showField:
      nx, ny = grid["nx"], grid["ny"]
      xs = np.linspace(grid["minx"], grid["maxx"], nx)
      ys = np.linspace(grid["miny"], grid["maxy"], ny)
      angles = grid["angles"]
      # Tamanho da seta adaptado ao espaçamento da grade em pixels, para as setas não
      # se sobreporem quando a densidade aumenta (~70% da célula).
      p0 = meters2pixel(self.__world, (self.__world.fieldSide * xs[0], ys[0]), frame.shape)
      p1 = meters2pixel(self.__world, (self.__world.fieldSide * xs[1], ys[0]), frame.shape) if nx > 1 else (p0[0]+self.arrow_size, p0[1])
      cell = abs(p1[0] - p0[0]) or self.arrow_size
      arrow_sz = max(6, int(cell * 0.7))
      k = 0
      for gy in ys:
        for gx in xs:
          pos = meters2pixel(self.__world, (self.__world.fieldSide * gx, gy), frame.shape)
          Drawing.draw_arrow(frame, pos, invertAng(angles[k], self.__world.fieldSide),
                             color=(128,128,128), size=arrow_sz, thickness=1)
          k += 1
    else:
      # Fallback (modo standalone): campo local do robô, se existir.
      field = None
      if self.showField != -1 and len(self.robots) > self.showField:
          field = self.robots[self.showField].field

      if self.showField != -1 and field is not None:
        # Desenha todo o campo
        x = np.arange(0, frame.shape[1], self.arrow_size)
        y = np.arange(0, frame.shape[0], self.arrow_size)
        pix = np.array(list(itertools.product(x,y)))
        P = np.array(pixel2meters(self.__world, pix.T, frame.shape))
        P[0] = self.__world.fieldSide * P[0]
        fP = field.F(P, retnparray=True)

        for i,p in enumerate(fP):
          Drawing.draw_arrow(frame, (pix[i][0],pix[i][1]), invertAng(p, self.__world.fieldSide), color=(128,128,128), size=self.arrow_size, thickness=1)

    if self.ball is not None and not (np.isnan(self.ball.raw_pos[0]) or np.isnan(self.ball.raw_pos[1])):
      # Desenha a bola
      cv2.circle(frame, meters2pixel(self.__world, self.ball.raw_pos, frame.shape), meters2pixelSize(self.__world, (0.015,0), frame.shape)[0], color=(0,0,255), thickness=-1)

      # Desenha a velocidade da bola
      Drawing.draw_arrow(frame, meters2pixel(self.__world, self.ball.raw_pos, frame.shape), angl(self.ball.raw_vel), color=(0,0,255), size=meters2pixelSize(self.__world, (self.ball.velmod,0), frame.shape)[0])

    # Desenha obstáculos pontuais com transparência
    enemy_color = (255, 0, 0) if self.__world.team_yellow else (0, 255, 255)
    overlay = frame.copy()
    for enemy in self.__world.enemyRobots:
      if isinstance(enemy, dict):
        x, y, th, idx = enemy['x'], enemy['y'], enemy['theta'], enemy['id']
        # Ignora posições inválidas: NaN/inf (não capturado por >1000) ou fora do campo.
        if not (np.isfinite(x) and np.isfinite(y)) or abs(x) > 1000 or abs(y) > 1000:
          continue
        w, h = meters2pixelSize(self.__world, (0.075,0.075), frame.shape)
        w, h = int(w), int(h)
        if w <= 0 or h <= 0:
            continue
        position = meters2pixel(self.__world, (x, y), frame.shape)

        is_yellow = not self.__world.team_yellow
        img_dict = self.robot_images_yellow if is_yellow else self.robot_images_blue

        if idx in img_dict:
            img = img_dict[idx]
            Drawing.draw_robot_image(frame, position, (w,h), th, img)

        Drawing.draw_rectangle(frame, position, (w,h), th, directionAngle=th, color=enemy_color)
      else:
        # Ignora posições inválidas: NaN/inf (não capturado por >1000) ou fora do campo.
        if not (np.isfinite(enemy[0]) and np.isfinite(enemy[1])) or abs(enemy[0]) > 1000 or abs(enemy[1]) > 1000:
          continue
        center = radius = None
        try:
          center = meters2pixel(self.__world, enemy, frame.shape)
          radius = meters2pixelSize(self.__world, (0.0375,0), frame.shape)[0]
          cv2.circle(overlay, center, radius, color=enemy_color, thickness=-1)
        except Exception as e:
          # Não derruba a thread do renderer por um inimigo ruim: loga e segue.
          print(f"[HLC] pulei inimigo inválido: {enemy}, center={center}, radius={radius} ({e})")
          continue
    
    # Aplica transparência (alpha=0.4 para os inimigos)
    cv2.addWeighted(overlay, 0.55, frame, 0.8, 0, frame)
    # Desenha pontos de interesse do campo
    #for point in field.interestPoints():
    #  Drawing.draw_arrow(frame, meters2pixel(self.__world, point, frame.shape), point[2], color=(128,128,128), size=arrow_size)
    

    #cv2.polylines(frame,[np.array([meters2pixel(self.__world, pos, frame.shape) for pos in self.positions[-500:]])],False,(255,255,255),1)
  
  def renderer(self):
    """Desenha um frame para o renderizador"""
    
    # Obtém o tamanho adequado a renderizar
    width, height = self.getShape()
    
    import os
    if not hasattr(self, '_cached_campo_bg') or not hasattr(self, '_cached_shape') or self._cached_shape != (width, height):
        campo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "campo.png")
        if os.path.exists(campo_path):
            img = cv2.imread(campo_path)
            self._cached_campo_bg = cv2.resize(img, (width, height))
            self._cached_shape = (width, height)
        else:
            self._cached_campo_bg = None
            self._cached_shape = (width, height)
            
    if self._cached_campo_bg is not None:
        frame = self._cached_campo_bg.copy()
    else:
        # Cria um frame do tamanho adequado com tudo preto
        frame = np.zeros((height,width,3), np.uint8)
        # Desenha os lados de campo
        Drawing.draw_field(self.__world, frame)

    Drawing.draw_polygon(frame, self.__world.edges)

    # Desenha o campo de vetores
    self.draw_field(frame)
    
    # Desenha os robôs e suas trajetórias
    for i,robot in enumerate(self.robots):
      self.draw_robot(frame, robot, i)
      self.positions.append(robot.pos)

    # Só renderiza a parte interna do campo 
    from main_system.controller.vision.mainVision import MainVision
    mask = MainVision.get_polygon_mask(frame, self.__world.edges)
    frame = cv2.bitwise_and(frame, frame, mask=mask)
    
    return frame
