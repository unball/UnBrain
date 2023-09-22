from ctypes import *
import time
from copy import copy
import constants
import client.firasim
import signal
import sys

# class VisionMessage(Structure):
#     MAX_ROBOTS = 5
#     _fields_ = [('n_ally', c_uint),
#                 ('n_enemy', c_uint),
#                 ('valid', c_bool),
#                 ('ball_x', c_double),
#                 ('ball_y', c_double),
#                 ('ball_vx', c_double),
#                 ('ball_vy', c_double),
#                 ('ally_x', c_double * MAX_ROBOTS),
#                 ('ally_y', c_double * MAX_ROBOTS),
#                 ('ally_th', c_double * MAX_ROBOTS),
#                 ('ally_vx', c_double * MAX_ROBOTS),
#                 ('ally_vy', c_double * MAX_ROBOTS),
#                 ('ally_w', c_double * MAX_ROBOTS),
#                 ('enemy_x', c_double * MAX_ROBOTS),
#                 ('enemy_y', c_double * MAX_ROBOTS),
#                 ('enemy_th', c_double * MAX_ROBOTS),
#                 ('enemy_vx', c_double * MAX_ROBOTS),
#                 ('enemy_vy', c_double * MAX_ROBOTS),
#                 ('enemy_w', c_double * MAX_ROBOTS),
#                 ]

# class Vision:
#     def __init__(self, vss, ip, port, team_yellow):
#         self.lib = vss.lib
#         self.lib.beginVision(c_uint(port), c_char_p(bytes(ip, 'ascii')))
#         self.last_message = None
#         self.team_yellow = team_yellow

#     @staticmethod
#     def invertMessage(message):
#         invertedMessage = copy(message)
#         invertedMessage['ally_x'] = copy(message["enemy_x"])
#         invertedMessage['ally_y'] = copy(message["enemy_y"])
#         invertedMessage['ally_th'] = copy(message["enemy_th"])
#         invertedMessage['ally_vx'] = copy(message["enemy_vx"])
#         invertedMessage['ally_vy'] = copy(message["enemy_vy"])
#         invertedMessage['ally_w'] = copy(message["enemy_w"])
#         invertedMessage['enemy_x'] = copy(message["ally_x"])
#         invertedMessage['enemy_y'] = copy(message["ally_y"])
#         invertedMessage['enemy_th'] = copy(message["ally_th"])
#         invertedMessage['enemy_vx'] = copy(message["ally_vx"])
#         invertedMessage['enemy_vy'] = copy(message["ally_vy"])
#         invertedMessage['enemy_w'] = copy(message["ally_w"])
#         return invertedMessage

#     def doRead(self):
#         # Define o retorno
#         self.lib.visionRead.restype = VisionMessage

#         # Chama a função da biblioteca compartilhada
#         message = self.lib.visionRead()

#         # Copia para um dicionário em python
#         new_message = {
#             'n_ally': message.n_ally,
#             'n_enemy': message.n_enemy,
#             'valid': message.valid,
#             'ball_x': message.ball_x,
#             'ball_y': message.ball_y,
#             'ball_vx': message.ball_x,
#             'ball_vy': message.ball_y,
#             'ally_x': [x for x in message.ally_x],
#             'ally_y': [x for x in message.ally_y],
#             'ally_th': [x for x in message.ally_th],
#             'ally_vx': [x for x in message.ally_vx],
#             'ally_vy': [x for x in message.ally_vy],
#             'ally_w': [x for x in message.ally_w],
#             'enemy_x': [x for x in message.enemy_x],
#             'enemy_y': [x for x in message.enemy_y],
#             'enemy_th': [x for x in message.enemy_th],
#             'enemy_vx': [x for x in message.enemy_vx],
#             'enemy_vy': [x for x in message.enemy_vy],
#             'enemy_w': [x for x in message.enemy_w]
#         }

#         # Desaloca memória da struct
#         del message

#         # Se a mensagem for válida retorna ela
#         if new_message['valid']:
#             self.last_message = new_message
#             return new_message
        
#         # Se não, retorna a última mensagem válida
#         else: return self.last_message

#     def read(self):
#         message = self.doRead()
#         if message is not None and self.team_yellow:
#             message = Vision.invertMessage(message)
#         return message

# class Command:
#     def __init__(self, vss, ip, port, team_yellow=False):
#         self.lib = vss.lib
#         self.lib.beginCommand.restype = c_void_p
#         self.command_p = self.lib.beginCommand(c_uint(port), c_char_p(bytes(ip, 'ascii')), c_bool(team_yellow))

#     def write(self, index, vl, vr):
#         self.lib.commandWrite(c_void_p(self.command_p), c_int(index), c_double(vl), c_double(vr))

#     def writeMulti(self, actions):
#         vls = [v[0] for v in actions]
#         vrs = [v[1] for v in actions]
#         self.lib.commandsWrite(c_void_p(self.command_p), (c_double * 3)(*vls), (c_double * 3)(*vrs))

#     def setPos(self, index, x, y, th):
#         self.lib.commandPos(c_void_p(self.command_p), c_int(index), c_double(x), c_double(y), c_double(th))

#     def setBallPos(self, x, y):
#         self.lib.commandBallPos(c_void_p(self.command_p), c_double(x), c_double(y))


class VSS:
    def __init__(
        self, 
        hostVision=constants.HOST_FIRASIM_VISION, 
        portVision=constants.PORT_FIRASIM_VISION, 
        hostCommand=constants.HOST_FIRASIM_COMMAND, 
        portCommand=constants.PORT_FIRASIM_COMMAND, 
        team_yellow=False
    ):
        #self.lib = CDLL("./lib/vss.so")
        #self.vision = Vision(self, hostVision, portVision, team_yellow)
        #self.command = Command(self, hostCommand, portCommand, team_yellow)
        self.vision = firasim.FIRASimVision()
        self.command = firasim.FIRASimCommand(team_yellow=team_yellow)

        #self.vision.start()
        #signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        self.vision.stop()
        sys.exit(0)