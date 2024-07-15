#!/usr/bin/env python3

"""Arquivo com a função principal do sistema"""

from view import View
from controller import Controller
from model import Model
import argparse

#Argumentos
parser = argparse.ArgumentParser(description='UnBall Main System')
parser.add_argument('--port', dest='port', type=int, default=5001, help='Port number to bind the pickle socket.')
parser.add_argument('--n_robots', dest='n_robots', type=int, default=5, help='Number of robots for each time in the match.')
args = parser.parse_args()

def main():
  """Função principal que instancia os componentes base, abre a interface gráfica e faz o flush dos dados em memória permanente ao terminar"""
  controller = Controller(port=args.port, n_robots=3)
  view = View(controller)
  
  view.run()
  
  Model().flush()

if __name__ == "__main__":
  main()
