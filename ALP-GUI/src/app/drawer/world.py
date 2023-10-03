from copy import copy, deepcopy

from .objects import *

class World:
    def __init__(self):
        self.clean()

    def clean(self):
        self.__ellipses = {}
        self.__rectangles = {}
        self.__robots = {}
        self.__targets = {}
        self.__lines = {}
        self.__paths = {}

    @property
    def ellipses(self):
        return copy(self.__ellipses)

    @property
    def rectangles(self):
        return copy(self.__rectangles)

    @property
    def robots(self):
        return copy(self.__robots)

    @property
    def targets(self):
        return copy(self.__targets)

    @property
    def lines(self):
        return copy(self.__lines)

    @property
    def paths(self):
        return copy(self.__paths)

    def addEllipse(self, id, x, y, a, b, th1, th2, color, fill):
        if id not in self.__ellipses:
            self.__ellipses[id] = Ellipse(id, 0, 0, 1, 1, 0, 2*np.pi, (1,0,0), True)

        self.__ellipses[id].x = x
        self.__ellipses[id].y = y
        self.__ellipses[id].a = a
        self.__ellipses[id].b = b
        self.__ellipses[id].th1 = th1
        self.__ellipses[id].th2 = th2
        self.__ellipses[id].color = color
        self.__ellipses[id].fill = fill

    def removeEllipse(self, id):
        if id in self.__ellipses:
            del self.__ellipses[id]

    def addRectangle(self, id, x, y, th, w, h, color):
        if id not in self.__rectangles:
            self.__rectangles[id] = Rectangle(id, 0, 0, 0, 0, 0, (0,0,1))

        self.__rectangles[id].x = x
        self.__rectangles[id].y = y
        self.__rectangles[id].th = th
        self.__rectangles[id].width = w
        self.__rectangles[id].height = h
        self.__rectangles[id].color = color

    def addRobot(self, id, x, y, th, dir, color):
        if id not in self.__robots:
            self.__robots[id] = Robot(id, x, y, th, dir, color)

        self.__robots[id].x = x
        self.__robots[id].y = y
        self.__robots[id].th = th
        self.__robots[id].dir = dir
        self.__robots[id].color = color

    def addTarget(self, id, x, y, th, color):
        if id not in self.__targets:
            self.__targets[id] = Target(id, x, y, th, color)

        self.__targets[id].x = x
        self.__targets[id].y = y
        self.__targets[id].th = th
        self.__targets[id].color = color

    def removeTarget(self, id):
        if id in self.__targets:
            del self.__targets[id]

    def addLine(self, id, x1, y1, x2, y2, color):
        if id not in self.__lines:
            self.__lines[id] = Line(id, x1, y1, x2, y2, color)

        self.__lines[id].x1 = x1
        self.__lines[id].y1 = y1
        self.__lines[id].x2 = x2
        self.__lines[id].y2 = y2
        self.__lines[id].color = color

    def removeLine(self, id):
        if id in self.__lines:
            del self.__lines[id]

    def addPath(self, id, points, color):
        if id not in self.__paths:
            self.__paths[id] = Path(id, points, color)

        self.__paths[id].points = points
        self.__paths[id].color = color

    def removePath(self, id):
        if id in self.__paths:
            del self.__paths[id]