import numpy as np
from model import ModelContext

class MainVisionModel(ModelContext):
  """Mantém as variáveis da visão principal vinculadas ao arquivo de configuração"""
  
  def __init__(self):
    ModelContext.__init__(self, {
      "preto_hsv": ("preto_hsv_interval", [0,94,163,360,360,360]),
      "time_hsv": ("time_hsv_interval", [13,0,0,32,360,360]),
      "bola_hsv": ("bola_hsv_interval", [0, 117, 0, 98, 360, 360]),
      "homography": ("homography_matrix", None),
      "homography_points": ("homography_points"),
      "cont_rect_area_ratio": ("cont_rect_area_ratio", 0.75),
      "min_internal_area_contour": ("min_internal_area_contour", 10),
      "min_external_area_contour": ("min_external_area_contour", 10),
      "stability_param": ("stability_param", 0.99),
      "internalPolygonPoints": ("internalPolygonPoints", [])
    })
    """Variáveis armazenadas no modelo"""
    
#    self.preto_hsv = [3,2,1,0,789,0]
#    self.preto_hsv[5] = 87
