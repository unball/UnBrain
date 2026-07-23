from main_system.controller.states import State
from main_system.controller.strategy.field import UVF
from main_system.controller.strategy.strategy import Strategy
from main_system.controller.world.robot import Robot
from main_system.controller.tools import norm, adjustAngle, ang, sat, unit, angError
from main_system.controller.control import SpeedPair
from main_system.controller.control.UFC import UFC
from main_system.controller.tools.simulator import simulate, simulateBall
from main_system.model.paramsPattern import ParamsPattern
from main_system.helpers import Mux
from collections import deque
import numpy as np
import time
import copy
import json

# Teto de amostras retidas em memória pelos buffers de debug/replay. Sem isso,
# `appendDebugData` (chamado a cada tick do loop principal, até ~150-1000Hz)
# faz as listas de debugData/replayData crescerem sem limite durante toda a
# sessão em que o robô estiver "running" — em especial `replayData`, que guarda
# `copy.deepcopy()` de Robot/Ball inteiros (não só números), causando aumento
# constante de RAM e mais trabalho de GC ao longo do tempo de uso. O valor
# cobre sessões de vários minutos com folga; amostras mais antigas que isso
# são descartadas automaticamente.
_MAX_REPLAY_SAMPLES = 20000
_MAX_DEBUG_SAMPLES = 20000

class DebugHLC(ParamsPattern, State):
  """Estado de debug HLC. Executa a visão, define campos específicos para os robôs, passa um target ao controle de alto nível e envia sinal via rádio."""
  
  def __init__(self, controller):
    State.__init__(self, controller)
    ParamsPattern.__init__(self, "debugHLCState", {
      "manualControlSpeedV": 0,
      "manualControlSpeedW": 0,
      "enableManualControl": False,
      "manualControlSpeedV" : 0,
      "manualControlSpeedW" : 0,
      "selectedField": "UVF",
      "selectableFinalPoint": False,
      "runVision": True,
      "selectedHLCcontrol": 0,
      "enableDebug": True
    }, deferred=True)

    self.world = controller.world
    """Referência para o mundo"""

    self.robots = self.world.robots[:3]
    """Referência para os robôs"""

    self.initialTime = time.time()
    """Tempo inicial a ser usado como origem de tempo dos dados de debug"""

    self.firstLoopRunning = True
    self.replayInitialTime = 0

    self.t = time.time()
    """Tempo do início do loop anterior"""

    self._desired_fps = 1000
    '''Frames que o sistema idealmente roda'''

    self._frame_count = 0

    self.fps = 0.0

    self._fps_timer_start = time.perf_counter()

    self.loops = 0
    """Loops executados"""

    self.strategy = Strategy(controller.world, controller.world.robots)
    """Instância da estratégia"""

    self.debugData = {
      "time": [],
      "posX": [],
      "posY": [],
      "posTh": [],
      "posThRef": [],
      "posThErr": [],
      "velLin": [],
      "visionLin": [],
      "velAng": [],
      "visionAng": [],
      "velBallX": [],
      "velBallY": [],
      "velBallMod": [],
      "accBallX": [],
      "accBallY": [],
      "accBallMod": [],
      "velRobotX": [],
      "velRobotY": [],
      "velRobotMod": [],
      "replayData": {
        "time": deque(maxlen=_MAX_REPLAY_SAMPLES),
        "robot": deque(maxlen=_MAX_REPLAY_SAMPLES),
        "robot1": deque(maxlen=_MAX_REPLAY_SAMPLES),
        "robot2": deque(maxlen=_MAX_REPLAY_SAMPLES),
        "ball": deque(maxlen=_MAX_REPLAY_SAMPLES),
      },
      "loopTime": 0,
      "FPS": 0,
      "Camera FPS": 0,
      "controlV": 0,
      "controlW": 0,
      "visionV": 0,
      "visionW": 0,
      "visionPose": (0,0,0)
    }
    """Dados de debug"""

    self.HLCs = Mux([UFC("debugHLC")], selected=self.getParam("selectedHLCcontrol"))
    """Sistemas de controle de alto nível suportados"""

  def setFinalPoint(self, point):
    """Atualiza a posição da bola"""
    self.world.ball.raw_update(*point)

  @property
  def finalPoint(self):
    return self.world.ball.raw_pose

  def selectHLC(self, index):
    """Muda o controle alto nível selecionado"""
    self.setParam("selectedHLCcontrol", index)
    self.HLCs.select(index)

  def runStrategyCondition(self):
    """Condição para rodar a estratégia"""
    return (self.loops % 1 == 0)
  
  def saveData(self, filename):
    """Salva os dados de debug no arquivo `filename`"""
    with open(filename, "w") as f:
      json.dump(self.debugData, f, indent=4)

  def _append_bounded(self, key, value):
    """Faz `.append()` numa lista de `debugData` mantendo-a como `list` comum
    (serializável em JSON, ao contrário de um `deque`), mas cortando o excesso
    em lote (amortizado) para que não cresça sem limite ao longo de uma sessão
    longa. O corte só acontece quando passa do dobro do teto, então o custo de
    `del lst[:n]` é diluído a cada `_MAX_DEBUG_SAMPLES` chamadas."""
    lst = self.debugData[key]
    lst.append(value)
    if len(lst) > _MAX_DEBUG_SAMPLES * 2:
      del lst[:len(lst) - _MAX_DEBUG_SAMPLES]

  def appendDebugData(self, reference, speeds, dt):
    """Alimenta os dados de debug com o estado atual das variáveis"""

    if self.world.running and self.getParam("enableDebug"):
      # Alimenta dados de debug
      if self.initialTime is None: self.initialTime = time.time()

      self._append_bounded("time", time.time()-self.initialTime)
      self._append_bounded("posX", self.robots[0].x)
      self._append_bounded("posY", self.robots[0].y)
      self._append_bounded("posTh", adjustAngle(self.robots[0].th))
      self._append_bounded("posThRef", adjustAngle(reference))
      self._append_bounded("posThErr", angError(reference, self.robots[0].th))
      self._append_bounded("velLin", abs(speeds[0].v))
      self._append_bounded("visionLin", self.robots[0].velmod)
      self._append_bounded("velAng", speeds[0].w)
      self._append_bounded("visionAng", self.robots[0].w)
      self._append_bounded("velBallX", self.world.ball.vel[0])
      self._append_bounded("velBallY", self.world.ball.vel[1])
      self._append_bounded("velBallMod", self.world.ball.velmod)
      self._append_bounded("accBallX", self.world.ball.acc[0])
      self._append_bounded("accBallY", self.world.ball.acc[1])
      self._append_bounded("accBallMod", self.world.ball.accmod)
      self._append_bounded("velRobotX", self.robots[0].vel[0])
      self._append_bounded("velRobotY", self.robots[0].vel[1])
      self._append_bounded("velRobotMod", self.robots[0].velmod)

      if self.firstLoopRunning:
        for k in self.debugData["replayData"]: self.debugData["replayData"][k].clear()
        self.firstLoopRunning = False
        self.replayInitialTime = time.time()
      
      self.debugData["replayData"]["time"].append(time.time()-self.replayInitialTime)
      # `Robot`/`Ball` guardam uma referência de volta a `self.world`, e
      # `world.robots` contém os robôs de volta (referência circular) — sem o
      # `memo` abaixo, `copy.deepcopy()` seguiria essa referência e copiaria o
      # MUNDO INTEIRO (os 3 robôs + bola) a cada uma das 4 chamadas, a cada
      # frame. Pré-preenchendo o memo com `world` já "copiado para si mesmo",
      # o deepcopy reaproveita a mesma instância de `world` em vez de clonar
      # o grafo inteiro — sem alterar em nada os campos do robô/bola que de
      # fato são salvos para o replay (posição, velocidade, etc.), que
      # continuam sendo cópias independentes e congeladas no tempo.
      world_memo = {id(self.world): self.world}
      self.debugData["replayData"]["robot"].append(copy.deepcopy(self.robots[0], world_memo))
      self.debugData["replayData"]["robot1"].append(copy.deepcopy(self.robots[1], world_memo))
      self.debugData["replayData"]["robot2"].append(copy.deepcopy(self.robots[2], world_memo))
      self.debugData["replayData"]["ball"].append(copy.deepcopy(self.world.ball, world_memo))

    else: self.firstLoopRunning = True

    # Mais dados de debug
    self.debugData["loopTime"] = (dt*1000)*0.1 + self.debugData["loopTime"]*0.9
    self.debugData["FPS"] = (self.fps)*0.05 + self.debugData["FPS"]*0.95
    if self._controller.visionSystem is not None and self._controller.visionSystem.cameraHandler is not None:
      self.debugData["Camera FPS"] = self._controller.visionSystem.cameraHandler.getCameraFPS()

    if self.getParam("enableDebug"):
      self.debugData["controlV"] = speeds[0].v
      self.debugData["controlW"] = speeds[0].w
      self.debugData["visionV"] = self.robots[0].velmod
      self.debugData["visionW"] = self.robots[0].w
      self.debugData["visionPose"] = (*self.robots[0].pos, self.robots[0].th*180/np.pi)
  
  def update(self):
    """Função de loop do estado debugHLC"""

    # Computa o tempo desde o último loop e salva
    now = time.perf_counter()

    # Computa o tempo desde o último loop e salva
    dt = time.time()-self.t
    self.t = time.time()

    # Atualiza o mundo com a visão
    if self.getParam("runVision") and self._controller.visionSystem is not None:
      # Desliga a visão se um simulador físico (FiraSim/TraveSim) estiver rodando
      is_sim_active = self._controller.launcher.is_running() and self._controller.launcher.simulator_mode in ['firasim', 'travesim', 'simulado']
      if not is_sim_active:
        self._controller.visionSystem.update()

    # Condições para rodar a estratégia
    # if self.runStrategyCondition():
    #   self.strategy.run()

    # Define um controle
    # self.robots[0].controlSystem = self.HLCs.get()
    # self.robots[1].controlSystem = self.HLCs.get()
    # self.robots[2].controlSystem = self.HLCs.get()


    self._frame_count += 1

    elapsed = now - self._fps_timer_start

    if elapsed >= 0.05:
      self.fps = self._frame_count / elapsed
      # Reset para o próximo intervalo de 1 segundo
      self._fps_timer_start = now
      self._frame_count = 0
    
    # Controle manual
    if self.getParam("enableManualControl"):
      self.world.checkBatteries = True
      self.world.manualControlSpeedV = self.getParam("manualControlSpeedV")
      self.world.manualControlSpeedW = self.getParam("manualControlSpeedW")
      # Propaga ao UnBrain para o controle manual chegar aos robôs reais.
      self.world.flag_manual_control = True
    # Controle de alto nível
    else:
      self.world.checkBatteries = False
      self.world.flag_manual_control = False
      
    manualSpeed = SpeedPair(self.getParam("manualControlSpeedV"), self.getParam("manualControlSpeedW"))
    speeds = [manualSpeed, manualSpeed, manualSpeed]
    
    # Obtém o target instantâneo
    # reference = self.robots[0].field.F(self.robots[0].pose)

    # Adiciona dados de debug para gráficos e para salvar
    self.appendDebugData(0, speeds, dt)

    # if self.world.running:
    #   # Envia mensagem ao robô
    #   if self.getParam("runVision"): self._controller.communicationSystems.get().send(speeds)

    #   # Simula nova posição
    #   else:
    #     for robot, speed in zip(self.robots, speeds):
    #       simulate(robot, speed.v, -speed.w, dt=dt)
    #     simulateBall(self.world.ball)
    
    # Envia zero para os robôs
    # else: self._controller.communicationSystems.get().sendZero()

    # Garante que o tempo de loop é de no máximo 1000fps
    target_period = 1.0 / self._desired_fps
    work_time = time.perf_counter() - now
    sleep_time = target_period - work_time
    if sleep_time > 0:
      time.sleep(sleep_time)

    # Incrementa o número de loops
    self.loops += 1
