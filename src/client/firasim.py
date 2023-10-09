import socket
import pathlib

moduleFolder = str(pathlib.Path(__file__).parent.absolute())
import sys


from google.protobuf.json_format import MessageToJson

sys.path.append(moduleFolder + '/protobuf/')
sys.path.append(moduleFolder + '/../')

import json

import packet_pb2
import constants
import numpy as np
import time

import struct

class FIRASimVision:
    
    print("FIRASIM VISION INITIATED")
    
    def __init__(self, host=constants.HOST_FIRASIM_VISION, port=constants.PORT_FIRASIM_VISION):
        
        super(FIRASimVision, self).__init__()
        self.frame = {}
        
        self.host = host
        self.port = port
        
        self.socket = self.createSocket(host, port)
        self.socket.recv(1024)
        self._fps = 0
        
        print("FIRASIM VISION SOCKET", self.host, self.port)
        
        
        
    def assign_vision(self, game):
        self.game = game
        
    def createSocket(self, host, port):
        # create UDP c  
        
        print("Starting vision...")
        print("Vision completed!")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        sock.bind((host, port))
        
        mreq = struct.pack(
            "4sl",
            socket.inet_aton(self.host),
            socket.INADDR_ANY
        )

        sock.setsockopt(
            socket.IPPROTO_IP, 
            socket.IP_ADD_MEMBERSHIP, 
            mreq
        )
        
        selfHost = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(selfHost))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(host) + socket.inet_aton(selfHost))
        
        return sock

    def read(self):
       
        data = self.socket.recv(1024)        
        
        while True:
            
            environment = packet_pb2.Environment()
            data = self.socket.recv(1024)
            environment.ParseFromString(data)
            
            environment = json.loads(MessageToJson(environment))
            
            return environment
           
            
class FIRASimCommand:
    print("FIRASIM COMMANDS INITIATED")
    def __init__(self, host=constants.HOST_FIRASIM_COMMAND, port=constants.PORT_FIRASIM_COMMAND, team_yellow = False):
        
        self.host = host
        self.port = port
        self.team_yellow = team_yellow
        self.socket = self.createSocket(host, port)
        

    def createSocket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((host, port))
        
        return sock

    def write(self, index, vl, vr):
        packet = packet_pb2.Packet()
        command = packet.cmd.robot_commands.add()

        command.yellowteam = self.team_yellow
        command.id = index
        command.wheel_left = vl
        command.wheel_right = vr

        self.socket.send(packet.SerializeToString())

    def writeMulti(self, actions):
        packet = packet_pb2.Packet()

        for i, (vl, vr) in enumerate(actions):
            command = packet.cmd.robot_commands.add()

            command.yellowteam = self.team_yellow
            command.id = i
            command.wheel_left = vl
            command.wheel_right = vr
        
        self.socket.send(packet.SerializeToString())

    def setPos(self, index, x, y, th):
        packet = packet_pb2.Packet()
        robotReplacement = packet.replace.robots.add()
        robot = robotReplacement.position

        robotReplacement.yellowteam = self.team_yellow
        robotReplacement.turnon = True

        robot.robot_id = index
        robot.x = x
        robot.y = y
        robot.orientation = th
        robot.vx = 0
        robot.vy = 0
        robot.vorientation = 0

        self.socket.send(packet.SerializeToString())
        

    def setBallPos(self, x, y):
        packet = packet_pb2.Packet()
        ballReplacement = packet.replace.ball

        ballReplacement.x = x
        ballReplacement.y = y

        self.socket.send(packet.SerializeToString())

if __name__ == "__main__":
    command = FIRASimCommand()
    vision = FIRASimVision()
    vision.start()

    t0 = time.time()
    
    while True:
        packet = vision.run()
        if packet is not None:
            t1 = time.time()
            print(packet)
            print((t1 - t0)*1000)
            t0 = t1
        command.write(0, 10, -10)
        time.sleep(0.033)
