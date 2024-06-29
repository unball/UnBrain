import pygame
import os
from classes.work.workers import GUI

os.environ['SDL_VIDEO_CENTERED'] = '1'

gui = GUI()
gui.run()