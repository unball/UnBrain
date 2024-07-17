import numpy as np
from model import ModelContext

class CortarCampoInternoModel(ModelContext):
  """Mantém as variáveis como pontos clicados para a view de cortar campo interno"""

  def __init__(self):
    ModelContext.__init__(self, {
      "points": ("points", []),
      "done": ("done", False)
    })
    """Variáveis armazenadas no modelo"""
