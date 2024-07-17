import subprocess
import time
import importlib
from helpers import Singleton

class Process():
  """Classe que abstrai um processo"""
  def __init__(self, command, aliveChecker = None):
    self.__command = command
    """Comando de inicalização do processo"""
    
    self.__process = None
    """Contém o processo gerado pela biblioteca `subprocess`"""
    
    self.__aliveChecker = aliveChecker
    """Se existir, mantém referência a uma função que verifica se o processo já foi iniciado por outro processo no computador, dessa forma ele não será iniciado mais de uma vez"""

  def run(self):
    """Executa o processo"""
    # Não faz nada se o processo estiver rodando
    if self.__aliveChecker is not None:
      if self.__aliveChecker():
        return
    
    # Se não estiver definido cria um novo subprocesso
    if self.__process is None:
      self.__process = subprocess.Popen(self.__command.split(" "))
    
    # Se o processo terminou tenta abrir novamente
    while self.__process.poll() is not None:
      print("\"" + self.__command + "\" não está rodando, tentando abrir em 5 segundos...")
      self.__process = subprocess.Popen(self.__command.split(" "))
      time.sleep(5)
  
  def terminate(self):
    """Termina o processo"""
    if self.__process is None:
      return
    self.__process.terminate()

    # Wait until process really terminates
    while(self.__process.poll() is not None): time.sleep(1)

    
    self.__process = None

def roscorechecker():
  """Esta função é capaz de dizer se o `roscore` já foi iniciado por outro processo no computador."""
  try:
    import rosgraph
    rosgraph.Master("/rostopic").getPid()
    return True
  except:
    return False

class RosHandler(metaclass=Singleton):
  """Gerencia os processos `roscore` e `rosrun` do ROS para haver comunicação com o rádio"""
  def __init__(self):
    self.__processes = {
      "radioSerial": Process("rosrun rosserial_arduino serial_node.py /dev/ttyUSB0 _baud:=115200"),
      "roscore": Process("roscore", aliveChecker=roscorechecker)
    }
    """Processos que o gerenciador suporta"""
  
  @classmethod
  def create(cls):
    if importlib.util.find_spec('rospy') is None:
      return None

    else:
      return cls()

  def runProcess(self, processKey):
    """Inicia o processo de chave `processKey` definido em `__processes`"""
    if self.__processes.get(processKey) is None: return
    self.__processes[processKey].run()
  
  def terminateAll(self):
    """Mata todos os processos inicados"""
    for _,process in self.__processes.items():
      process.terminate()
