from controller.tools import unit, angl

def pixel2meters(world, position, shape):
  """Recebe o mundo, uma posição e o tamanho do frame e converte a coordenada do pixel para uma coordenada no mundo físico com o centro no centro do campo. É a operação inversa do `meters2pixel`"""
  camera_x_length = shape[1]
  camera_y_length = shape[0]
  field_x_length = world.field_x_length
  field_y_length = world.field_y_length
  x_conversion = field_x_length / camera_x_length
  y_conversion = (field_y_length / camera_y_length) * -1

  x = position[0] - camera_x_length / 2
  y = position[1] - camera_y_length / 2
  x *= x_conversion
  y *= y_conversion
  
  return (x,y)

def meters2pixel(world, position, shape):
  """Recebe o mundo, uma posição do mundo físico e o tamanho do frame e converte a coordenada para a posição equivalente em pixels. É a operação inversa do `pixel2meters`"""
  camera_x_length = shape[1]
  camera_y_length = shape[0]
  field_x_length = world.field_x_length
  field_y_length = world.field_y_length
  x_conversion = camera_x_length / field_x_length
  y_conversion = (camera_y_length / field_y_length) * -1

  x = position[0]*x_conversion
  y = position[1]*y_conversion
  x += camera_x_length / 2
  y += camera_y_length / 2
  
  return (int(x),int(y))

def meters2pixelSize(world, size, shape):
  """Recebe o mundo, um tamanho do mundo físico físico e o tamanho do frame e converte para o tamanho equivalente em pixels."""
  camera_x_length = shape[1]
  camera_y_length = shape[0]
  field_x_length = world.field_x_length
  field_y_length = world.field_y_length
  x_conversion = camera_x_length / field_x_length
  y_conversion = (camera_y_length / field_y_length)

  x = size[0]*x_conversion
  y = size[1]*y_conversion
  
  return (int(x),int(y))

def normToAbs(normPoint, shape):
  """Método que recebe um ponto \\(p=(x,y)\\) em um sistema de coordenadas normalizado \\(0\\leq x,y \\leq 1\\) e passa para um sistema de coordenadas absoluto em pixels de acordo com `shape`: \\(s=(h,w)\\), pela fórmula: \\((w\\cdot x, h\\cdot y)\\)"""
  return (round(normPoint[0]*shape[1]), round(normPoint[1]*shape[0]))

def invertAng(angle, side):
  if side == 1: return angle
  vecAng = unit(angle)
  return angl((-vecAng[0], vecAng[1]))

def invertVec(vec, side):
  if side == 1: return vec
  return (-vec[0], vec[1])