import numpy as np
from main_system.model import ModelContext

class CortarCampoModel(ModelContext):
  """Mantém as variáveis como pontos clicados para a view de cortar campo"""
  
  def __init__(self):
    ModelContext.__init__(self, {
      "clicked_points_homography": ("clicked_points_homography", []),
    }, immediate=True)  # calibração de campo: grava no disco imediatamente
    """Variáveis armazenadas no modelo"""
