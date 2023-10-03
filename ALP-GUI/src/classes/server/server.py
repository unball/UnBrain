import socket
import threading
import json
import traceback
import numpy as np

from app.drawer.world import World
from helpers.dict import valueOrDefault

class WorldServer:
    def __init__(self, world: World, ip: str, port: int):
        self.world = world
        self.ip = ip
        self.port = port
        self.socket = None
        self.thread = None
        self.started = False

    def start(self):
        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        self.socket.settimeout(0.1)

        self.started = True
        self.thread = threading.Thread(target=self.receiveWorker)
        self.thread.start()

    def stop(self):
        self.started = False

    def receiveWorker(self):
        while self.started:
            try:
                data = self.socket.recvfrom(4096)[0]
                dataJson = json.loads(data)
                
                self.command(dataJson)
            except socket.timeout:
                continue
            except:
                traceback.print_exc()
                continue

    def command(self, commands: list):
        for command in commands:
            if command["command"] == "placeEllipse":
                id = valueOrDefault(command, "id", 0)
                x = float(valueOrDefault(command, "x", 0))
                y = float(valueOrDefault(command, "y", 0))
                a = float(valueOrDefault(command, "a", 0))
                b = float(valueOrDefault(command, "b", 0))
                th1 = float(valueOrDefault(command, "th1", 0))
                th2 = float(valueOrDefault(command, "th2", 0))
                color = valueOrDefault(command, "color", (1,0,0))
                fill = bool(valueOrDefault(command, "fill", True))

                self.world.addEllipse(id, x, y, a, b, th1, th2, color, fill)

            elif command["command"] == "removeEllipse":
                id = int(command["id"])
                self.world.removeEllipse(id)

            elif command["command"] == "placeRectangle":
                id = int(valueOrDefault(command, "id", 0))
                x = float(valueOrDefault(command, "x", 0))
                y = float(valueOrDefault(command, "y", 0))
                th = float(valueOrDefault(command, "th", 0))
                w = float(valueOrDefault(command, "w", 0))
                h = float(valueOrDefault(command, "h", 0))
                color = valueOrDefault(command, "color", (0,1,0))

                self.world.addRectangle(id, x, y, th, w, h, color)

            elif command["command"] == "placeRobot":
                id = int(valueOrDefault(command, "id", 0))
                x = float(valueOrDefault(command, "x", 0))
                y = float(valueOrDefault(command, "y", 0))
                th = float(valueOrDefault(command, "th", 0))
                dir = float(valueOrDefault(command, "dir", 0))
                color = valueOrDefault(command, "color", (0,1,0))

                self.world.addRobot(id, x, y, th, dir, color)

            elif command["command"] == "placeTarget":
                id = int(valueOrDefault(command, "id", 0))
                x = float(valueOrDefault(command, "x", 0))
                y = float(valueOrDefault(command, "y", 0))
                th = float(valueOrDefault(command, "th", 0))
                color = valueOrDefault(command, "color", (0,1,0))

                self.world.addTarget(id, x, y, th, color)

            elif command["command"] == "removeTarget":
                id = int(command["id"])
                self.world.removeTarget(id)

            elif command["command"] == "placeLine":
                id = int(valueOrDefault(command, "id", 0))
                x1 = float(valueOrDefault(command, "x1", 0))
                y1 = float(valueOrDefault(command, "y1", 0))
                x2 = float(valueOrDefault(command, "x2", 0))
                y2 = float(valueOrDefault(command, "y2", 0))
                color = valueOrDefault(command, "color", (0,1,0))

                self.world.addLine(id, x1, y1, x2, y2, color)

            elif command["command"] == "removeLine":
                id = int(command["id"])
                self.world.removeLine(id)

            elif command["command"] == "placePath":
                id = int(valueOrDefault(command, "id", 0))
                points = np.array(command["points"])
                color = valueOrDefault(command, "color", (0,1,0))

                self.world.addPath(id, points, color)

            elif command["command"] == "removePath":
                id = int(command["id"])
                self.world.removePath(id)

            elif command["command"] == "clean":
                self.world.clean()