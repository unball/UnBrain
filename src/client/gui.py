import socket
import time
import json
import numpy as np

# Global static module variables
singletonClient = None
disabled = False

def clientProvider():
    global singletonClient
    if singletonClient is None:
        singletonClient = ClientClass("localhost", 20010)
        singletonClient.start()
    return singletonClient

class ClientClass:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket = None

    def start(self):
        if not disabled: self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    def __send__(self, data: bytes):
        self.socket.sendto(data, (self.ip, self.port))

    def send(self, data: dict):
        if not disabled: self.__send__(str.encode(json.dumps(data)))

    def robotPallete(self):
        return {0: (0.5, 0.5, 1), 1: (0.5, 1, 0.5), 2: (1, 0.5, 0.5)}
    
    def drawBall(self, id, x, y, radius=0.01, color=None):
        self.drawEllipse(id, x, y, radius, radius, 0, 2*np.pi, color if color else (1,0,0), True)
        
    def drawEllipse(self, id, x, y, a, b, th1, th2, color=None, fill=True):
        self.send([{
            "command": "placeEllipse",
            "id": id,
            "x": x,
            "y": y,
            "a": a,
            "b": b,
            "th1": th1,
            "th2": th2,
            "color": color if color else self.robotPallete()[id],
            "fill": fill
        }])

    def removeEllipse(self, id):
        self.send([{
            "command": "removeEllipse",
            "id": id
        }])

    def drawRobot(self, id, x, y, th, dir, color=None):
        self.send([{
            "command": "placeRobot",
            "id": id,
            "x": x,
            "y": y,
            "th": th,
            "dir": dir,
            "color": color if color else self.robotPallete()[id]
        }])

    def drawTarget(self, id, x, y, th, color=None):
        self.send([{
            "command": "placeTarget",
            "id": id,
            "x": x,
            "y": y,
            "th": th,
            "color": color if color else self.robotPallete()[id]
        }])

    def removeTarget(self, id):
        self.send([{
            "command": "removeTarget",
            "id": id
        }])

    def drawLine(self, id, x1, y1, x2, y2, color=None):
        self.send([{
            "command": "placeLine",
            "id": id,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "color": color if color else self.robotPallete()[id]
        }])

    def removeLine(self, id):
        self.send([{
            "command": "removeLine",
            "id": id
        }])

    def drawPath(self, id, points: np.array, color=None):
        self.send([{
            "command": "placePath",
            "id": id,
            "points": points.tolist(),
            "color": color if color else self.robotPallete()[id]
        }])

    def removePath(self, id):
        self.send([{
            "command": "removePath",
            "id": id
        }])

if __name__ == "__main__":
    client = ClientClass("localhost", 20010)
    client.start()

    count = 1
    t0 = time.time()

    client.send([{"command": "clean"}])

    while True:
        client.send([
            {
                "command": "placeCircle",
                "id": count,
                "x": 0.5*np.abs(np.sin(10*time.time()))*np.sin(time.time()),
                "y": 0.5*np.abs(np.sin(10*time.time()))*np.cos(time.time()),
                "radius": 0.01
            }
        ])

        count += 1
        
        time.sleep(0.016)