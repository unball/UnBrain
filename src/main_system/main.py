#!/usr/bin/env python3

"""Arquivo com a função principal do sistema"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import init_global_logger
init_global_logger()

from main_system.view import View
from main_system.controller import Controller
from main_system.model import Model
import argparse

#Argumentos
parser = argparse.ArgumentParser(description='UnBall Main System')
parser.add_argument('--port', dest='port', type=int, default=5001, help='Port number to bind the pickle socket.')
parser.add_argument('--n_robots', dest='n_robots', type=int, default=3, help='Number of robots for each time in the match.')
parser.add_argument('--simulator', dest='simulator', action='store_true', help='Set if running alongside a simulator (disables camera UI).')
args = parser.parse_args()

def main():
  """Função principal que instancia os componentes base, abre a interface gráfica e faz o flush dos dados em memória permanente ao terminar"""
  controller = Controller(port=args.port, n_robots=args.n_robots, simulator=args.simulator)
  view = View(controller, simulator=args.simulator)
  
  import signal
  import gi
  gi.require_version('GLib', '2.0')
  from gi.repository import GLib

  def sigint_handler(*args_tuple):
      print("\n[MainSystem] Ctrl+C detectado! Encerrando processos...")
      if hasattr(controller, 'launcher') and controller.launcher: controller.launcher.stop()
      if hasattr(controller, 'enemy_launcher') and controller.enemy_launcher: controller.enemy_launcher.stop()
      controller.stop()
      Model().flush()
      sys.exit(0)
      return False

  # GLib.unix_signal_add é a forma correta de capturar sinais em aplicações GTK3
  GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, sigint_handler)
  
  view.run()
  
  Model().flush()

if __name__ == "__main__":
  main()
