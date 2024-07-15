"""Neste módulo estão algumas classes base e funções úteis para todos os outros módulos"""

from threading import Thread

class Singleton(type):
  """Classes que herdarem de `Singleton` terão a propriedade de sempre que forem instanciadas a instância será uma referência a primeira"""
  _instances = {}
  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

class Mux(list):
  """Classe que implementa um multiplexador. Passa-se uma lista de elementos e pode-se obter um elemento com base no elemento selecionado."""
  def __init__(self, items: list, selected=0):
    super().__init__(items)
    """Elementos a serem multiplexados"""

    self.__selectedIndex = selected
    """Índice do elemento selecionado"""

  def select(self, index):
    """Seleciona um elemento de índice `index`"""
    self.__selectedIndex = index

  def selectedIndex(self):
    """Seleciona o índice do elemento selecionado"""
    return self.__selectedIndex

  def get(self):
    """Obtém o elemento selecionado"""
    return self[self.__selectedIndex]

class LoopThread():
  """Classe que implementa uma thread que fica executando repetidamente uma função `worker` passada."""
  def __init__(self, worker):
    self.__worker = worker

  def start(self):
    """Método que inicia a execução da thread de loop"""
    if self.__worker is None:
      print("Não existe um worker a executar")
      return
    self.__thread = Thread(target=self.loop)
    self.__running = True
    self.__thread.start()

  def loop(self):
    """Método que mantém o loop em execução e é usado como fluxo base para a Thread da biblioteca threading"""
    while self.__running:
      self.__worker()

  def stop(self):
    """Método que muda a flag de executando para `False`, fazendo com que a thread de loop pare"""
    self.__running = False
