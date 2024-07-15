class VisionMessage():
  """Classe que descreve uma mensagem de alteração da visão. Essa mensagem contém novos valores para pose de robôs e bola, além de uma lista que indica se o robô foi identificado ou não."""
  
  def __init__(self, n_robots):
    """Constroi a mensagem da visão com o pior cenário possível: nada identificado e todos os elementos na posição central"""
    
    self.n_robots = n_robots
    """Número de robôs aliados"""
    
    self.allyPoses = [(0,0,0,False)]*self.n_robots
    """Lista com coordenada x dos robôs (aliados e inimigos)"""

    self.advPos = []
    
    self.debug_internalContours = [None]*self.n_robots
    """Lista os contornos internos de aliados"""

    self.debug_advExtContours = []
    
    self.ball_x = 0
    """Coordenada x da bola"""
    
    self.ball_y = 0
    """Coordenada y da bola"""
    
    self.ball_found = False
    """Indica se a bola foi encontrada"""

  
  def showMessage(self):
    print(f"Número de robôs aliados: {self.n_robots}")
    print(f"Lista com coordenada x dos robôs (aliados e inimigos) {self.allyPoses}")
    print(f"Indica se a bola foi encontrada: {self.ball_found}")
    print(f"Coordenada x da bola: {self.ball_x}")
    print(f"Coordenada y da bola: {self.ball_y}")
    
  @property
  def nRobots(self):
    """Retorna o número de robôs aliados"""
    return self.n_robots
  
  def setRobot(self, index, pose, internalContours=None):
    """Diz que o robô de índice `index` foi identificado e atualiza sua pose"""
    if(index < self.n_robots):
      self.allyPoses[index] = (*pose, True)
    
    if index < self.nRobots:
      self.debug_internalContours[index] = internalContours
    
  def setEnemyRobot(self, pose, extContour=None):
    """Coloca um robô inimigo como identificado e atualiza sua pose"""
    self.advPos.append(pose)
    self.debug_advExtContours.append(extContour)
  
  def setBall(self, pos):
    """Coloca a bola como identificada e atualiza sua posição"""
    
    if pos is None: return
    self.ball_x, self.ball_y = pos[0]
    self.ball_found = True
