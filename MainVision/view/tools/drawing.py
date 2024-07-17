from controller.tools.pixel2metric import meters2pixel, normToAbs
from controller.world import Field
import numpy as np
import cv2

class Drawing():
  """Esta classe contém diversas funções que fazem desenho de bordas de campo, elipses, retângulos rotacionados, etc"""

  edgeColors = {"repulsive": (0,0,255), "goalRepulsive": (0,100,255), "goalAttractive": (0,255,0)}
  
  def draw_left_rectangle(image, color, thickness=5):
    """Desenha um retângulo que ocupa o lado esquerdo do campo"""
    height, width, _ = image.shape
    cv2.line(image, (int(width/2)-thickness,0), (0,0), color, thickness)
    cv2.line(image, (0,0), (0, height), color, thickness)
    cv2.line(image, (int(width/2)-thickness,height), (0, height), color, thickness)

  def draw_right_rectangle(image, color, thickness=5):
    """Desenha um retângulo que ocupa o lado direito do campo"""
    height, width, _ = image.shape
    cv2.line(image, (int(width/2)+thickness,0), (width,0), color, thickness)
    cv2.line(image, (width,0), (width, height), color, thickness)
    cv2.line(image, (width, height), (int(width/2)+thickness, height), color, thickness)

  def draw_middle_line(image):
    """Desenha uma linha no meio do campo"""
    height, width, _ = image.shape
    cv2.line(image, (int(width/2),0), (int(width/2),height), (100,100,100), 1)

  def draw_field(world, processed_image):
    """Desenha os retângulos esquerdo e direito de cores que dependem do lado aliado e inimigo, desenha também uma linha de meio de campo"""
    Drawing.draw_left_rectangle(processed_image, (0,255,0) if world.fieldSide == Field.LEFT else (0,0,255))
    Drawing.draw_right_rectangle(processed_image, (0,255,0) if world.fieldSide == Field.RIGHT else (0,0,255))
    Drawing.draw_middle_line(processed_image)

  def draw_internal_field(world, frame, frameShape):
    mainPt1 = meters2pixel(world, (-world.internal_limit_x, world.internal_limit_y), frameShape)
    mainPt2 = meters2pixel(world, (world.internal_limit_x, -world.internal_limit_y), frameShape)
    cv2.rectangle(frame,mainPt1,mainPt2,(50,50,50),-1)
    mainGaolPt1 = meters2pixel(world, (-(world.internal_limit_x+world.internal_x_goal), world.internal_y_goal), frameShape)
    mainGaolPt2 = meters2pixel(world, ((world.internal_limit_x+world.internal_x_goal), -world.internal_y_goal), frameShape)
    cv2.rectangle(frame,mainGaolPt1,mainGaolPt2,(50,50,50),-1)

  def draw_ellipse(world, frame, a, b):
    """.. important:: Fazer receber o centro da elipse, no lugar de desenhar em uma posição fixa definida por parâmetros do mundo
    Desenha uma elipse de eixos horizontal de tamanho `a` e vertical de tamanho `b`"""
    height, width, _ = frame.shape
    ellipseCenter = meters2pixel(world, (world.internal_limit_x*world.fieldSide, 0), frame.shape)
    ellipseAxis = (int(a*width/world.field_x_length),int(b*height/world.field_y_length))
    cv2.ellipse(frame, ellipseCenter, ellipseAxis, 0, 0, 360, (100,100,100), 1)
    
  
  def draw_rectangle(frame, position: tuple, size: tuple, angle: float, directionAngle=None, color=(0,255,0)):
    """Desenha um retângulo na posição `position` de tamanho `size` e rotacionado de `angle`"""
    rect = (position, size, -angle*180/np.pi)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(frame,[box],0,color,2)
    cv2.circle(frame, (int(position[0]+size[0]/2*np.cos(-angle)), int(position[1]+size[0]/2*np.sin(-angle))), size[0]//10, (255,255,255), -1)
    if directionAngle is not None:
      cv2.circle(frame, (int(position[0]+size[0]/2*np.cos(-directionAngle)), int(position[1]+size[0]/2*np.sin(-directionAngle))), size[0]//15, (255,0,255), -1)
    
  def draw_arrow(frame, position: tuple, angle: float, color=(255,255,255), size=20, thickness=2):
    cv2.arrowedLine(frame, position, (position[0]+int(size*np.cos(-angle)), position[1]+int(size*np.sin(-angle))), color, thickness)

  def draw_polygon(frame, points):
    for i in range(len(points)-1):
      p0 = normToAbs(points[i][0], frame.shape)
      p1 = normToAbs(points[i+1][0], frame.shape)

      color = Drawing.edgeColors[points[i+1][1]]

      cv2.line(frame, p0, p1, color, thickness=2)