"""Módulo que reune os componentes de backend do sistema."""

from threading import Thread
import queue
from gi.repository import GLib

from controller.vision.mainVision import MainVision
from controller.communication.rosRadio import RosRadio
from controller.communication.serialRadio import SerialRadio
from controller.communication.rosHandler import RosHandler
from controller.states import DummyState
from controller.world import World
from helpers import Mux

class Controller:
  """Classe que declara a thread do backend e define o estado do sistema"""
  
  def __init__(self, port, n_robots):
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
    
    self.visionSystem = MainVision(self.world, port)
    """Instância do sistema de visão"""
    
    self.communicationSystems = Mux([SerialRadio(self.world)])
    """Instância do sistema que se comunica com o rádio"""
    
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
      except:
        print("Failed to run queued event")
            
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
      # Executa eventos agendados
      self.runQueuedEvents()
      
      # Executa o update do estado atual
      self.__state.update()
    
    # Para o rosHandler, se tiver sido habilitado
    RosHandler().terminateAll()
    
    self.communicationSystems[0].closeSerial()
