from threading import Thread

class ViewThreads():
  """Classe que implementa uma lista de threads e permite finalizar todas de uma só vez"""
  def __init__(self):
    self.__threads = []

  def stop(self):
    """Este método finaliza todas as threads registradas de uma só vez"""
    for thread in self.__threads: thread.stop()

  def register(self, thread):
    """Este método registra uma thread"""
    self.__threads.append(thread)
