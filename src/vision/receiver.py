import socket
import struct
from time import time
import vision.wrapper_pb2 as wr
import constants

class FiraClient:

    def __init__(self, 
            vision_ip=constants.HOST_VSSS_VISION,
            vision_port=constants.PORT_VSSS_VISION):
        """
        Init SSLClient object.
        Extended description of function.
        Parameters
        ----------
        vision_ip : str
            Multicast Vision IP in format '255.255.255.255'. 
        vision_port : int
            Vision Port up to 1024. 
        """

        self.vision_ip = vision_ip
        self.vision_port = vision_port

        self.vision_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.vision_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.vision_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 128)
        self.vision_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        self.vision_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, struct.pack("=4sl", socket.inet_aton(self.vision_ip), socket.INADDR_ANY)) #volta aqui dps raul myron e ana beatriz macedo dourado @raul @ana
        self.vision_sock.bind((self.vision_ip, self.vision_port))

        self.vision_sock.setblocking(True)
        self.frame = None
        self.det_frame = None
        
        self.verify_vision = False

    def receive_frame(self):
        """Receive package and decode."""
        data = None
        self.verify_vision = False
        
        while True:
            try:
                socket.setdefaulttimeout(1/30)
                self.verify_vision = False
                data, _ = self.vision_sock.recvfrom(1024)
                self.verify_vision = True

                
                
            except Exception as e:
                self.verify_vision = False
                print(e)
            if data != None:
                break
                       
        if self.verify_vision == False and data == None:
            print("**** no data received from vision ****")
        
        if data != None:
            decoded_data = wr.SSL_WrapperPacket().FromString(data)
        else: decoded_data = None
        return(decoded_data)
    