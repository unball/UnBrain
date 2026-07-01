from main_system.controller.tools.pixel2metric import meters2pixel, normToAbs
from main_system.controller.world import Field
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
    
  
  def draw_rectangle(frame, position: tuple, size: tuple, angle: float, directionAngle=None, color=(0,255,0), baseAngle=None):
    """Desenha um retângulo na posição `position` de tamanho `size` e rotacionado de `angle`"""
    rect = (position, size, -angle*180/np.pi)
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    
    cv2.drawContours(frame, [box], 0, color, 2)
    # Desenha o centro com cor branca
    cv2.circle(frame, (int(position[0]), int(position[1])), size[0]//10, (255,255,255), -1)
    
    # Desenha a flecha base (antes do offset) em vermelho
    if baseAngle is not None:
      Drawing.draw_arrow(frame, position, baseAngle, color=(0, 0, 255), size=size[0], thickness=3)

    # Desenha a flecha apontando para frente (com offset) em branco
    Drawing.draw_arrow(frame, position, angle, color=(255, 255, 255), size=size[0], thickness=2)
    
    if directionAngle is not None:
      Drawing.draw_arrow(frame, position, directionAngle+np.pi, color=(255, 0, 255), size=size[0], thickness=2)

  def draw_robot_image(frame, position: tuple, size: tuple, angle: float, img):
    """Desenha uma imagem do robo centralizada, escalada e rotacionada"""
    # Resize the image to fit the physical robot size in pixels
    resized_img = cv2.resize(img, size)
    
    # Get image dimensions
    h, w = resized_img.shape[:2]
    
    # Calculate exact center
    cX, cY = w / 2.0, h / 2.0
    
    # Rotate the image (adjusting by +90 degrees to fix upside-down orientation)
    M = cv2.getRotationMatrix2D((cX, cY), angle * 180 / np.pi + 90, 1.0)
    
    # Calculate the new bounding box dimensions to avoid clipping
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    
    # Adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2.0) - cX
    M[1, 2] += (nH / 2.0) - cY
    
    # Perform the actual rotation and return the image
    rotated_img = cv2.warpAffine(resized_img, M, (nW, nH))
    
    # Calculate top-left corner using the new dimensions
    x_offset = int(position[0] - nW / 2.0)
    y_offset = int(position[1] - nH / 2.0)
    
    # Define bounds, clipping to frame size
    y1, y2 = max(0, y_offset), min(frame.shape[0], y_offset + nH)
    x1, x2 = max(0, x_offset), min(frame.shape[1], x_offset + nW)

    # Corresponding bounds in the rotated image
    y1_img, y2_img = y1 - y_offset, y2 - y_offset
    x1_img, x2_img = x1 - x_offset, x2 - x_offset

    # Check if the image is completely out of the frame
    if y1 >= y2 or x1 >= x2:
        return
    
    if rotated_img.shape[2] == 4:
        # Pega o canal Alpha
        alpha_s = rotated_img[y1_img:y2_img, x1_img:x2_img, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        # Fast alpha blending using numpy broadcasting
        alpha_s_3d = alpha_s[..., np.newaxis]
        alpha_l_3d = alpha_l[..., np.newaxis]
        
        frame[y1:y2, x1:x2] = (alpha_s_3d * rotated_img[y1_img:y2_img, x1_img:x2_img, :3] + 
                               alpha_l_3d * frame[y1:y2, x1:x2]).astype(np.uint8)
    
  def draw_arrow(frame, position: tuple, angle: float, color=(255,255,255), size=20, thickness=2):
    try:
        import math
        if math.isnan(position[0]) or math.isnan(position[1]) or math.isnan(angle) or math.isnan(size):
            return
        cv2.arrowedLine(frame, (int(position[0]), int(position[1])), (int(position[0]+size*np.cos(-angle)), int(position[1]+size*np.sin(-angle))), color, thickness)
    except Exception:
        pass

  def draw_polygon(frame, points):
    for i in range(len(points)-1):
      p0 = normToAbs(points[i][0], frame.shape)
      p1 = normToAbs(points[i+1][0], frame.shape)

      color = Drawing.edgeColors[points[i+1][1]]

      cv2.line(frame, p0, p1, color, thickness=2)