from gi.repository import Gdk
from view.tools.cv2Renderer import cv2Renderer
from view.tools.drawing import Drawing
from controller.tools.pixel2metric import meters2pixel,pixel2meters,meters2pixelSize,invertAng,invertVec
from controller.tools import angl, unit
from controller.vision.mainVision import MainVision
import numpy as np
import cv2
import itertools

class HighLevelRenderer(cv2Renderer):
  def __init__(self, world, robotsGetter=None, ballGetter=None, on_click=None, on_scroll=None):
    super().__init__(worker=self.renderer)
    
    self.__world = world
    
    self.__robotsGetter = robotsGetter
    self.__ballGetter = ballGetter
    
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
    # Obtém posição em pixels do robô
    position = meters2pixel(self.__world, robot.raw_pose, frame.shape)
    w,h = meters2pixelSize(self.__world, (0.075,0.075), frame.shape)
    
    # Desenha de outra cor o robô próximo do mouse
    robotColor = (255,0,0) if self.cursorDistance(position) < w else (0,255,0)
    
    # Desenha o retângulo do robô
    Drawing.draw_rectangle(frame, position, (w,h), robot.raw_th, directionAngle=robot.dir_raw_th, color=robotColor)

    if robot.entity is not None:
      cv2.circle(frame, position, w//10, color=robot.entity.color, thickness=-1)

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

    # Desenha a bola
    cv2.circle(frame, meters2pixel(self.__world, self.ball.raw_pos, frame.shape), meters2pixelSize(self.__world, (0.015,0), frame.shape)[0], color=(0,0,255), thickness=-1)

    # Desenha a velocidade da bola
    Drawing.draw_arrow(frame, meters2pixel(self.__world, self.ball.raw_pos, frame.shape), angl(self.ball.raw_vel), color=(0,0,255), size=meters2pixelSize(self.__world, (self.ball.velmod,0), frame.shape)[0])

    # Desenha obstáculos pontuais
    for enemy in self.__world.enemyRobots:
      cv2.circle(frame, meters2pixel(self.__world, enemy, frame.shape), meters2pixelSize(self.__world, (0.010,0), frame.shape)[0], color=(0,255,255), thickness=-1)

    # Desenha pontos de interesse do campo
    #for point in field.interestPoints():
    #  Drawing.draw_arrow(frame, meters2pixel(self.__world, point, frame.shape), point[2], color=(128,128,128), size=arrow_size)
    

    #cv2.polylines(frame,[np.array([meters2pixel(self.__world, pos, frame.shape) for pos in self.positions[-500:]])],False,(255,255,255),1)
  
  def renderer(self):
    """Desenha um frame para o renderizador"""
    
    # Obtém o tamanho adequado a renderizar
    width, height = self.getShape()
    
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
    mask = MainVision.get_polygon_mask(frame, self.__world.edges)
    frame = cv2.bitwise_and(frame, frame, mask=mask)
    
    return frame
