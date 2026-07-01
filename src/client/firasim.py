import socket
import pathlib
moduleFolder = str(pathlib.Path(__file__).parent.absolute())
import sys
sys.path.append(moduleFolder + '/protobuf/')
sys.path.append(moduleFolder + '/../')
import command_pb2
import common_pb2
import packet_pb2
import replacement_pb2
import constants
import numpy as np
import time
import threading
import copy

class FIRASimVision:
    def __init__(self, host=constants.HOST_FIRASIM_VISION, port=constants.PORT_FIRASIM_VISION):
        self.host = host
        self.port = port
        self.socket = self.createSocket(host, port)

        # self._receiveThread = threading.Thread(target=self.loop)
        # self._lock = threading.Lock()
        # self._packet = None
        # self._run = False

    def createSocket(self, host, port, blocking = False):
        # create UDP c  
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(blocking)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, 'SO_REUSEPORT'):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        sock.bind((host, port))
        
        selfHost = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(selfHost))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(host) + socket.inet_aton(selfHost))

        return sock

    def read(self):
        try:
            self.socket.settimeout(0.0) # Non-blocking para drenar o buffer instantaneamente
            
            messages = []
            while True:
                try:
                    data = self.socket.recv(65536)
                    if len(data) > 0:
                        env = packet_pb2.Environment()
                        env.ParseFromString(data)
                        messages.append(env)
                except (BlockingIOError, socket.timeout, Exception):
                    break

            if messages:
                return messages
            return None
        except Exception as e:
            print("Vision error: ", e)
            return None

    def __del__(self):
        try:
            self.socket.close()
        except Exception:
            pass

    # def loop(self):
    #     while self._run:
    #         packet = self.receive()

    #         if not self._lock.locked():
    #             self._lock.acquire()
    #             self._packet = packet
    #             self._lock.release()

    #         time.sleep(0.016)

    # def read(self):
    #     self._lock.acquire()
    #     packet = copy.deepcopy(self._packet)
    #     self._lock.release()

    #     return packet

    # def start(self):
    #     self._run = True
    #     self._receiveThread.start()

    # def stop(self):
    #     self._run = False

class FIRASimCommand:
    def __init__(self, host=constants.HOST_FIRASIM_COMMAND, team_yellow = False, is_travesim = False):
        self.host = host
        self._team_yellow = team_yellow
        self.is_travesim = is_travesim
        
        self.setup_sockets()

    @property
    def team_yellow(self):
        return self._team_yellow

    @team_yellow.setter
    def team_yellow(self, value):
        if self._team_yellow != value:
            self._team_yellow = value
            self.setup_sockets()

    def setup_sockets(self):
        if hasattr(self, 'socket') and self.socket:
            try: self.socket.close()
            except Exception: print("FiraSim connection refused! Is the simulator running on port?" )
            
        if hasattr(self, 'socket_replacer') and self.socket_replacer and self.socket_replacer != getattr(self, 'socket', None):
            try: self.socket_replacer.close()
            except Exception: print("FiraSim connection refused! Is the simulator running on port?" )
            
        self.port = constants.port_fira(self._team_yellow, self.is_travesim)
        self.socket = self.createSocket(self.host, self.port)

        self.replacer_port = 20011 if self.is_travesim else self.port
        if self.replacer_port == self.port:
            self.socket_replacer = self.socket
        else:
            self.socket_replacer = self.createSocket(self.host, self.replacer_port)

    def createSocket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        sock.connect((host, port))

        return sock

    def write(self, index, vl, vr):
        packet = packet_pb2.Packet()
        command = packet.cmd.robot_commands.add()

        command.yellowteam = self.team_yellow
        command.id = index
        command.wheel_left = vl
        command.wheel_right = vr

        try:
            self.socket.send(packet.SerializeToString())
        except BlockingIOError:
            pass
        except ConnectionRefusedError:
            print("FiraSim connection refused! Is the simulator running on port?" )

    def writeMulti(self, actions, robot_ids=None):
        packet = packet_pb2.Packet()
        for i, (vl, vr) in enumerate(actions):
            if i < len(robot_ids):
                command = packet.cmd.robot_commands.add()

                command.yellowteam = self.team_yellow
                command.id = robot_ids[i]
                command.wheel_left = float(vl)
                command.wheel_right = float(vr)
        try:
            self.socket.send(packet.SerializeToString())
        except BlockingIOError:
            pass
        except ConnectionRefusedError:
            # FiraSim não está rodando; ignora silenciosamente em vez de crashar
            print("FiraSim connection refused! Is the simulator running on port?" )

    def setPos(self, index, x, y, th, is_enemy=False):
        packet = packet_pb2.Packet()
        robotReplacement = packet.replace.robots.add()
        robot = robotReplacement.position

        robotReplacement.yellowteam = (not self.team_yellow) if is_enemy else self.team_yellow
        robotReplacement.turnon = True

        robot.robot_id = index
        robot.x = x
        robot.y = y
        robot.orientation = th
        robot.vx = 0
        robot.vy = 0
        robot.vorientation = 0

        try:
            self.socket_replacer.send(packet.SerializeToString())
        except BlockingIOError:
            pass
        

    def setBallPos(self, x, y):
        packet = packet_pb2.Packet()
        ballReplacement = packet.replace.ball

        ballReplacement.x = x
        ballReplacement.y = y
        try:
            self.socket_replacer.send(packet.SerializeToString())
        except BlockingIOError:
            pass
        except ConnectionRefusedError:
            print("FiraSim Replacer connection refused!", file=sys.stderr)

    def __del__(self):
        try:
            self.socket.close()
            if hasattr(self, 'socket_replacer') and self.socket_replacer and self.socket_replacer != getattr(self, 'socket', None):
                self.socket_replacer.close()
        except Exception:
            pass

if __name__ == "__main__":
    command = FIRASimCommand()
    vision = FIRASimVision()
    vision.start()

    # while True:
    #     command.setBallPos(*np.random.random(2))
    #     time.sleep(1000)

    t0 = time.time()
    while True:
        packet = vision.read()
        try:
            self.socket_replacer.send(packet.SerializeToString())
        except ConnectionRefusedError:
            print("FiraSim Replacer connection refused!", file=sys.stderr)
            print(packet)
            print((t1 - t0)*1000)
            t0 = t1
        command.write(0, 10, -10)
        time.sleep(0.033)
