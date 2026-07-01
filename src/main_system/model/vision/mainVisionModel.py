import numpy as np
from main_system.model import ModelContext

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
      "internalPolygonPoints": ("internalPolygonPoints", []),
      "camera_matrix": ("camera_matrix", None),
      "dist_coeffs": ("dist_coeffs", None),
      "use_clahe": ("use_clahe", False),
      "robot_angle_offsets": ("robot_angle_offsets", [0.0, -45.0, 0.0])
    }, immediate=True)  # calibração: grava no disco imediatamente (à prova de queda de energia)
    """Variáveis armazenadas no modelo"""
    
#    self.preto_hsv = [3,2,1,0,789,0]
#    self.preto_hsv[5] = 87
