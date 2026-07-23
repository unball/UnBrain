from abc import ABC, abstractmethod
import time
import numpy as np
from main_system.controller.communication.server_pickle import ServerPickle
from main_system.controller.vision.cameras import CameraHandler
from main_system.controller.vision.visionMessage import VisionMessage

# Método C: liga a medição de latência interna do pipeline de visão (buffer da
# câmera + thread de captura + process() + world.update()). Imprime uma linha
# resumida ~1x por segundo. Desligue (False) em produção para não poluir o log.
VISION_LATENCY_DEBUG = False

class Vision(ABC):
  """Classe que define as interfaces que qualquer sistema de visão deve ter no sistema."""

  def __init__(self, world, port):
    super().__init__()

    self.cameraHandler = CameraHandler()
    """Instancia módulo `MainSystem.controller.vision.cameras.CameraHandler` que gerencia as câmeras e retorna os frames"""

    self._world = world
    """Mantém referência ao mundo"""

    # Não usados por MainVision (que decide seed vs. track sozinha, olhando
    # `poseDefined` dos robôs em `_assign_ids`). Mantidos por compatibilidade
    # caso outra implementação de Vision os utilize.
    self.usePastPositions = False
    self.lastCandidateUse = 0

    # Acumuladores da medição de latência (Método C)
    self._lat_n = 0
    self._lat_staleness = 0.0
    self._lat_proc = 0.0
    self._lat_total = 0.0
    self._lat_last_print = time.perf_counter()

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
    
    frame, capture_ts = self.cameraHandler.getFrameWithCaptureTime()
    if frame is None: return self.giveUpAndWait()

    # Identidade é SEED-ÚNICO: `MainVision._assign_ids` semeia por forma só
    # enquanto nem todos os robôs têm pose definida e, depois, rastreia por
    # posição (associação global). O re-seed PERIÓDICO por forma que existia
    # aqui (a cada 2s) foi REMOVIDO: com a calibração de forma atual (config
    # intencional) ele re-semeava com um sinal ruidoso e embaralhava a
    # identidade a cada 2s — era uma fonte direta da "troca constante" de
    # robôs. Sem hardware para recalibrar a forma, rastrear é mais estável.
    t_start = time.perf_counter()
    data = self.process(frame)
    self._world.update(data)
    t_end = time.perf_counter()

    if VISION_LATENCY_DEBUG and capture_ts is not None:
      self._report_latency(capture_ts, t_start, t_end)

    return True

  def _report_latency(self, capture_ts, t_start, t_end):
    """Método C: acumula latência interna e imprime média ~1x/s.
    staleness = atraso do frame ao ser consumido (buffer da câmera + thread);
    process   = tempo de process() + world.update();
    total     = da captura até o world atualizado."""
    self._lat_staleness += (t_start - capture_ts) * 1000.0
    self._lat_proc      += (t_end - t_start) * 1000.0
    self._lat_total     += (t_end - capture_ts) * 1000.0
    self._lat_n += 1

    now = time.perf_counter()
    if now - self._lat_last_print >= 1.0 and self._lat_n > 0:
      n = self._lat_n
      stale, proc, total = self._lat_staleness/n, self._lat_proc/n, self._lat_total/n
      print(f"[VISION LAT] staleness={stale:5.1f} ms | process={proc:5.1f} ms | "
            f"total={total:5.1f} ms | ~delay_steps={round(total/25.0)} (timestep 25ms) | n={n}",
            flush=True)
      self._lat_n = 0
      self._lat_staleness = self._lat_proc = self._lat_total = 0.0
      self._lat_last_print = now
