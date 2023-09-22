import socket
import pathlib
moduleFolder = str(pathlib.Path(__file__).parent.absolute())
import sys
sys.path.append(moduleFolder + '/protobuf/')
# import vssref_command_pb2
# import vssref_common_pb2
# import vssref_placement_pb2
import constants

class RefereeCommands:
    def __init__(self, host=constants.HOST_REFEREE, port=constants.PORT_REFEREE_COMMAND):
        self.host = host
        self.port = port
        self.socket = self.createSocket(host, port)

    def createSocket(self, host, port, blocking = False):
        # create UDP c  
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(blocking)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        sock.bind((host, port))
        
        selfHost = socket.gethostbyname(socket.gethostname())
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(selfHost))
        sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(host) + socket.inet_aton(selfHost))

        return sock

    def color2side(color):
        if color == vssref_common_pb2.Color.YELLOW: return -1
        elif color == vssref_common_pb2.Color.BLUE: return 1
        else: return 0

    def receive(self):
        try:
            data = self.socket.recv(512)
            
            if len(data) > 0:
                command = vssref_command_pb2.VSSRef_Command()
                command.ParseFromString(data)
                return command
            return None        
        except:
            return None

class RefereePlacement:
    def __init__(self, host=constants.HOST_REFEREE, port=constants.PORT_REFEREE_REPLACEMENT, team_yellow = False):
        self.host = host
        self.port = port
        self.team_yellow = team_yellow

        self.socket = self.createSocket(host, port)

    def createSocket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((host, port))

        return sock

    def send(self, robotsPos):
        placement = vssref_placement_pb2.VSSRef_Placement()

        placement.world.teamColor = vssref_common_pb2.Color.YELLOW if self.team_yellow else vssref_common_pb2.Color.BLUE

        for i,pos in robotsPos:
            robot = placement.world.robots.add()
            robot.robot_id = i
            robot.x = pos[0] * RefereeCommands.color2side(placement.world.teamColor)
            robot.y = pos[1] * RefereeCommands.color2side(placement.world.teamColor)
            robot.orientation = pos[2]

        self.socket.send(placement.SerializeToString())


if __name__ == "__main__":
    rc = RefereeCommands('224.5.23.2', 10003)
    rpb = RefereePlacement('224.5.23.2', 10004)
    rpy = RefereePlacement('224.5.23.2', 10004, True)

    while True:
        command = rc.receive()
        if command is None: continue
        
        print(command)

        rpb.send([(0,0,0), (0.5,0.5,0), (-0.5,-0.5,0)])
        rpy.send([(0,0,0), (0.5,0.5,0), (-0.5,-0.5,0)])

