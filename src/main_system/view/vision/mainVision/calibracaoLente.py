from gi.repository import Gtk, GLib
from pkg_resources import resource_filename
from main_system.view.tools.frameSelector import FrameRenderer
import cv2
import numpy as np

class CalibracaoLente(FrameRenderer):
  """Essa classe implementa o FrameRenderer que permite capturar padrões de xadrez para calibrar a distorção da câmera"""
  
  def __init__(self, notebook, controller, visionSystem):
    self.__visionSystem = visionSystem
    self.__controller = controller
    self.__board_size = (9, 6)
    self.__objp = np.zeros((self.__board_size[0] * self.__board_size[1], 3), np.float32)
    self.__objp[:, :2] = np.mgrid[0:self.__board_size[0], 0:self.__board_size[1]].T.reshape(-1, 2)
    
    self.__objpoints = []
    self.__imgpoints = []
    
    self.__last_corners = None
    self.__last_gray = None
    
    super().__init__(notebook, "Calibrar Lente")
    
  def ui(self):
    """Conteúdo a ser inserido na interface da configuração de calibração"""
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "calibracaoLente.ui"))
    
    self.__status_label = builder.get_object("status_label")
    builder.get_object("capture_btn").connect("clicked", self.on_capture)
    builder.get_object("calibrate_btn").connect("clicked", self.on_calibrate)
    builder.get_object("reset_calib_btn").connect("clicked", self.on_reset)
    
    return builder.get_object("main")
    
  def on_capture(self, btn):
    if self.__last_corners is not None and self.__last_gray is not None:
      criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
      corners2 = cv2.cornerSubPix(self.__last_gray, self.__last_corners, (11, 11), (-1, -1), criteria)
      self.__objpoints.append(self.__objp)
      self.__imgpoints.append(corners2)
      self.__status_label.set_text(f"Capturados: {len(self.__objpoints)}")
      
  def on_reset(self, btn):
    self.__objpoints.clear()
    self.__imgpoints.clear()
    self.__status_label.set_text("Capturados: 0")
    
  def on_calibrate(self, btn):
    if len(self.__objpoints) > 0:
        if self.__last_gray is not None:
            ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
                self.__objpoints, self.__imgpoints, self.__last_gray.shape[::-1], None, None
            )
            
            if ret:
                # Modificamos através da interface oficial adicionada no __init__.py
                self.__controller.addEvent(self.__visionSystem.set_camera_params, mtx.tolist(), dist.tolist())
                self.__status_label.set_text("Calibração Salva!")
            else:
                self.__status_label.set_text("Erro ao calibrar.")
    else:
        self.__status_label.set_text("Sem capturas.")

  def getFrame(self):
    """Retorna o frame com as detecções do tabuleiro desenhadas"""
    # Para calibração de lente usamos o frame cru da câmera, sem estar warped ou undistorted!
    # Pois queremos tirar a distorção da lente física crua.
    frame = self.__visionSystem.cameraHandler.getFrame()
    if frame is None: return None
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Achar tabuleiro
    try:
        ret, corners = cv2.findChessboardCorners(gray, self.__board_size, None)
    except cv2.error:
        ret, corners = False, None
    
    if ret:
        self.__last_corners = corners
        self.__last_gray = gray
        cv2.drawChessboardCorners(frame, self.__board_size, corners, ret)
    else:
        self.__last_corners = None
        self.__last_gray = gray
        
    return frame
