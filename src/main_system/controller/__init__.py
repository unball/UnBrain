"""Módulo que reune os componentes de backend do sistema."""

from threading import Thread
import queue
import time
try:
    from gi.repository import GLib
except ImportError:
    GLib = None


import os
headless = os.environ.get('UNBRAIN_HEADLESS') == '1'

if not headless:
    from main_system.controller.communication.rosRadio import RosRadio
    from main_system.controller.communication.serialRadio import SerialRadio
    from main_system.controller.communication.rosHandler import RosHandler
    from main_system.controller.states import DummyState
    from main_system.helpers import Mux
    from client.client_pickle import ClientPickle

from main_system.controller.world import World

class Controller:
  """Classe que declara a thread do backend e define o estado do sistema"""
  
  def __init__(self, port, n_robots, simulator=False):
    self.__thread = Thread(target=self.loop)
    """Thread que executa o backend do sistema"""
    
    self.__state = DummyState(self)
    """Estado atual do sistema"""
    
    self.__quitRequested = False
    """Flag que indica se o loop do backend deve terminar"""
    
    self.__events = queue.Queue()
    """Eventos agendados. Essa fila é útil para que a view agende eventos a serem executados no momento oportuno pelo backend, evitando condições de corrida."""
    
    self.world = World(n_robots=n_robots)
    """Essa é uma instância do mundo. O mundo contém informações sobre estado do campo como posição de robôs, velocidades, posição de bola e limites do campo."""
    
    self.visionSystem = None
    if not simulator:
        from main_system.controller.vision.mainVision import MainVision
        self.visionSystem = MainVision(self.world, port)
        """Instância do sistema de visão"""
    
    radios = []
    if not simulator:
        radios.append(SerialRadio(self.world))
    self.communicationSystems = Mux(radios)
    """Instância do sistema que se comunica com o rádio"""
    
    from main_system.controller.communication.server_pickle import ServerPickle
    self.command_server = ServerPickle(port)
    """Servidor para enviar comandos da UI para o UnBrain"""
    
    self.enemy_command_server = ServerPickle(port + 2)
    """Servidor para enviar comandos da UI para o UnBrain Inimigo"""
    
    self.state_client = ClientPickle(port=port+1)
    """Cliente para receber o estado do UnBrain"""
    
    from main_system.controller.launcher import UnBrainLauncher
    self.launcher = UnBrainLauncher()
    """Gerenciador do subprocesso do UnBrain"""
    
    self.enemy_launcher = UnBrainLauncher()
    """Gerenciador do subprocesso do UnBrain Inimigo"""
    
    self.__thread.start()
  
  def addEvent(self, method, *args, run_when_done_with_glib=None):
    """Adiciona um evento a fila de eventos agendados para serem executados no início do próximo loop do backend. Se `run_when_done_with_glib` estiver definido como a tupla `(method,args)` o método dessa tupla será executado depois que o evento for executado."""
    self.__events.put({"method": method, "args": args, "glib_run": run_when_done_with_glib})
  
  def runQueuedEvents(self):
    """Método que executa eventos agendados"""
    
    while not self.__events.empty():
      try:
        event = self.__events.get_nowait()
        event["method"](*event["args"])
        if event["glib_run"] is not None:
          GLib.idle_add(event["glib_run"][0], *event["glib_run"][1:])
      except Exception as e:
        print("Failed to run queued event")
        import traceback
        traceback.print_exc()
            
  def stop(self):
    """Faz a flag `__quitRequested` ser `True`, o que provocará a parada de `loop` na thread de controller."""
    self.__quitRequested = True
    
  def setState(self, state):
    """Define o estado que será executado no `loop`"""
    self.__state = state
    
  def unsetState(self):
    """Define que o estado a ser executado no `loop` é um estado que não faz nada."""
    self.__state = DummyState(self)
  
  def loop(self):
    """Loop principal da thread de backend"""
    
    while not self.__quitRequested:
      t_start = time.time()
      # Executa eventos agendados
      self.runQueuedEvents()
      
      # Recebe estado do mundo do UnBrain
      try:
          state_msg = self.state_client.receive()
          if state_msg is not None:
              self.world.update_from_state(state_msg)
      except Exception as e:
          import traceback
          traceback.print_exc()
      
      # Envia o estado da UI para o UnBrain
      try:
        ui_message = {
          "ball":{
            "pos_x": self.world.ball.x,
            "pos_y": self.world.ball.y,
            "vel_x": self.world.ball.inst_vx,
            "vel_y": self.world.ball.inst_vy,
            "raw_x": self.world.ball.raw_x,
            "raw_y": self.world.ball.raw_y
          },
          "n_robots": self.world.n_robots,
          "robots":{
            i: {
              "pos_x": self.world.robots[i].inst_x,
              "pos_y": self.world.robots[i].inst_y,
              "th": self.world.robots[i].inst_th,
              "vel_x": self.world.robots[i].inst_vx,
              "vel_y": self.world.robots[i].inst_vy,
              "w": self.world.robots[i].inst_w,
              "raw_x": self.world.robots[i].raw_x,
              "raw_y": self.world.robots[i].raw_y,
              "raw_th": getattr(self.world.robots[i], 'raw_th', self.world.robots[i].inst_th)
            }
            for i in range(self.world.n_robots)
          },
          "running": self.world.running,
          "check_batteries": self.world.checkBatteries,
          "manualControlSpeedV": self.world.manualControlSpeedV,
          "manualControlSpeedW": self.world.manualControlSpeedW,
          "manual_control": getattr(self.world, "flag_manual_control", False),
          "team_yellow": self.world.team_yellow,
          # [ENG] Novas flags dinâmicas IPC
          "use_predictor": getattr(self.world, 'use_predictor', False),
          "disable_ai": getattr(self.world, 'disable_ai', False),
          "teleport_mode": getattr(self.world, 'teleport_mode', None),
          "teleport_mode_enemy": getattr(self.world, 'teleport_mode_enemy', None),
          "teleport_ball_pos": getattr(self.world, 'teleport_ball_pos', None),
          "teleport_config": getattr(self.world, 'teleport_config', {}),
          "global_control_params": getattr(self.world, "global_control_params", {}),
          "hlc_uvf_overrides": getattr(self.world, "hlc_uvf_overrides", {}),
          "flags": {
            "referee": getattr(self.world, "flag_referee", False),
            "control": getattr(self.world, "flag_control_tester", False),
            "test_roles": getattr(self.world, "test_roles", ["None", "None", "None"]),
            "debug": getattr(self.world, "flag_debug", False),
            "ppo_ai": getattr(self.world, "flag_ppo_ai", False),
            "enemy_ai": getattr(self.world, "flag_enemy_ai", False),
            "record": getattr(self.world, "flag_record", False),
            "record_sim2real": getattr(self.world, "flag_record_sim2real", False),
            "static_entities": getattr(self.world, "flag_static_entities", False),
            "use_kalman": getattr(self.world, "flag_use_kalman", False),
            "use_neural_estimator": getattr(self.world, "flag_use_neural_estimator", False),
            "use_vision_noise": getattr(self.world, "flag_use_vision_noise", False),
            "mirror": getattr(self.world, "flag_mirror", False),
            "use_predictor": getattr(self.world, "flag_use_predictor", False),
            "disable_ai": getattr(self.world, "flag_disable_ai", False),
            "n_robots": getattr(self.world, "flag_n_robots", "0,1,2"),
            "force_entities": getattr(self.world, "force_entities", {}),
            "episode_test_run":        getattr(self.world, "flag_episode_test_run", False),
            "episode_test_seed":       getattr(self.world, "flag_episode_test_seed", 0),
            "episode_test_max_steps":  getattr(self.world, "flag_episode_test_max_steps", 1200),
            "episode_test_n_episodes": getattr(self.world, "flag_episode_test_n_episodes", 1),
            "episode_test_type":       getattr(self.world, "flag_episode_test_type", "heatmap_team"),
            "episode_test_n_enemies":  getattr(self.world, "flag_episode_test_n_enemies", 0),
            "episode_test_enemy_entity": getattr(self.world, "flag_episode_test_enemy_entity", ""),
            "hlc_show_field":          getattr(self.world, "flag_hlc_show_field", -1),
            "episode_test_is_fixed":   getattr(self.world, "flag_episode_test_is_fixed", True),
          }
        }
        self.command_server.send(ui_message)
        
        if hasattr(self, 'enemy_command_server') and getattr(self.world, 'flag_enemy_on', False):
            self.enemy_command_server.send(ui_message)
        
        # Limpa APENAS os triggers oneshot após enviar
        if getattr(self.world, 'teleport_mode_enemy', None) is not None:
            self.world.teleport_mode_enemy = None
        if getattr(self.world, 'teleport_ball_pos', None) is not None:
            self.world.teleport_ball_pos = None
            
      except Exception as e:
        import traceback
        traceback.print_exc()
      
      # Executa o update do estado atual
      self.__state.update()

      # Controle preciso de FPS (120 FPS max) para a UI quando estiver no simulador
      # ou quando a visão foi desativada, evitando starvation da thread do GTK
      dt = time.time() - t_start
      target_dt = 1.0 / 150.0
      if dt < target_dt:
          time.sleep(target_dt - dt)
    
    # Para o rosHandler, se tiver sido habilitado
    RosHandler().terminateAll()
    
    if len(self.communicationSystems) > 0:
      self.communicationSystems[0].closeSerial()
