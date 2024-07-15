from abc import ABC, abstractmethod
import time
import numpy as np
from controller.communication.server_pickle import ServerPickle
from controller.vision.cameras import CameraHandler
from controller.vision.visionMessage import VisionMessage

class Vision(ABC):
  """Classe que define as interfaces que qualquer sistema de visão deve ter no sistema."""
  
  def __init__(self, world, port):
    super().__init__()
    
    self.cameraHandler = CameraHandler()
    """Instancia módulo `MainSystem.controller.vision.cameras.CameraHandler` que gerencia as câmeras e retorna os frames"""
    
    self._world = world
    """Mantém referência ao mundo"""

    self.usePastPositions = False
    self.lastCandidateUse = 0
  
    self.server_pickle = ServerPickle(port)

  @abstractmethod
  def process(self, frame):
    """Método abstrato que recebe um frame do tipo numpy array no formato (height, width, depth). Retorna uma mensagem de alteração do tipo `MainSystem.controller.vision.visionMessage.VisionMessage`"""
    pass
    
  def giveUpAndWait(self):
    """Método que impõe um atraso de 30ms por falta de frame."""
    time.sleep(0.03)
    return False
  
  def update(self):
    """Obtém um frame da câmera, chama o `Vision.process` e atualiza o mundo (`World`) com base na mensagem retornada. Retorna `False` se nada foi feito e `True` se atualizou o mundo."""
    
    frame = self.cameraHandler.getFrame()
    if frame is None: return self.giveUpAndWait()
    
    # Renova a identificação a cada 2 segundos
    if time.time()-self.lastCandidateUse > 0.66 and np.all([x.spin == 0 for x in self._world.robots]):
      self.usePastPositions = False
   
    data = self.process(frame)
    self._world.update(data)
    
    message = {
      "ball":{
        "pos_x": self._world.ball.pos[0],
        "pos_y": self._world.ball.pos[1],
        "vel_x": self._world.ball.vel[0],
        "vel_y": self._world.ball.vel[1]
      },
      "n_robots": self._world.n_robots,
      "robots":{
        i: {
          "pos_x": self._world.robots[i].inst_x,
          "pos_y": self._world.robots[i].inst_y,
          "th": self._world.robots[i].inst_th,
          "vel_x": self._world.robots[i].inst_vx,
          "vel_y": self._world.robots[i].inst_vy,
          "w": self._world.robots[i].inst_w,
          "control_params":{
            "kw": self._world.robots[i].controlSystem.getParam("kw"),
            "kp": self._world.robots[i].controlSystem.getParam("kp"),
            "L": self._world.robots[i].controlSystem.getParam("L"),
            "amax": 0.12*self._world.robots[i].controlSystem.g,
            "vmax": self._world.robots[i].controlSystem.getParam("vmax"),
            "motorangaccelmax": self._world.robots[i].controlSystem.getParam("motorangaccelmax"),
            "r": self._world.robots[i].controlSystem.getParam("r"),
            "maxangerror": self._world.robots[i].controlSystem.getParam("maxangerror"),
            "tau": self._world.robots[i].controlSystem.getParam("tau")
          }
        }
        for i in range(self._world.n_robots)
      },
      "running": self._world.running,
      "check_batteries": self._world.checkBatteries,
      "manualControlSpeedV": self._world.manualControlSpeedV,
      "manualControlSpeedW": self._world.manualControlSpeedW
    }

    self.server_pickle.send(message)

    if self.usePastPositions is False:
      self.usePastPositions = True
      self.lastCandidateUse = time.time()
    
    return True
