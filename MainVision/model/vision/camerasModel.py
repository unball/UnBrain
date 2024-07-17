import numpy as np
from model import ModelContext

class CameraHandlerModel(ModelContext):
  """Mantém as variáveis do gerenciador de câmeras"""
  
  def __init__(self):
    ModelContext.__init__(self, {
      "current_camera": ("camera", -1),
      "frame_scale": ("frame_scale", 1)
    })
    """Variáveis armazenadas no modelo"""
