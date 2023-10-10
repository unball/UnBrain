import gi
import cairo
import numpy as np

from gi.repository import Gtk
from abc import ABC, abstractmethod

class Object(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def draw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        pass

class Ellipse(Object):
    def __init__(self, id, x, y, a, b, th1, th2, color, fill):
        self.id = id
        self.x = x
        self.y = y
        self.a = a
        self.b = b
        self.th1 = th1
        self.th2 = th2
        self.color = color
        self.fill = fill

    def draw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        ctx.save()
        ctx.set_source_rgb(*self.color)
        ctx.set_line_width(0.02)
        ctx.translate(self.x, self.y)
        ctx.scale(self.a, self.b)
        ctx.arc(0, 0, 1, self.th1, self.th2)
        if self.fill: ctx.fill()
        else: ctx.stroke()
        ctx.restore()

class Target(Object):
    def __init__(self, id, x, y, th, color):
        self.id = id
        self.x = x
        self.y = y
        self.th = th
        self.color = color
        self.arrow_length = 0.04
        self.arrowhead_angle = np.pi/6
        self.arrowhead_length = 0.02
    
    def draw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        ctx.set_source_rgb(*self.color)
        ctx.arc(self.x, self.y, 0.01, 0, 2*np.pi)
        ctx.fill()

        ctx.move_to(self.x, self.y)

        ctx.rel_line_to(self.arrow_length * np.cos(self.th), self.arrow_length * np.sin(self.th))
        ctx.rel_move_to(-self.arrowhead_length * np.cos(self.th - self.arrowhead_angle), -self.arrowhead_length * np.sin(self.th - self.arrowhead_angle))
        ctx.rel_line_to(self.arrowhead_length * np.cos(self.th - self.arrowhead_angle), self.arrowhead_length * np.sin(self.th - self.arrowhead_angle))
        ctx.rel_line_to(-self.arrowhead_length * np.cos(self.th + self.arrowhead_angle), -self.arrowhead_length * np.sin(self.th + self.arrowhead_angle))

        ctx.set_source_rgb(*self.color)
        ctx.set_line_width(0.01)
        ctx.stroke()

class Rectangle(Object):
    def __init__(self, id, x, y, th, width, height, color):
        self.id = id
        self.x = x
        self.y = y
        self.th = th
        self.width = width
        self.height = height
        self.color = color

    def draw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        ctx.save()
        ctx.set_source_rgb(*self.color)
        ctx.set_line_width(0.01)
        ctx.translate(self.x, self.y)
        ctx.rotate(self.th%(2*np.pi))
        ctx.rectangle(-self.width/2,-self.height/2, self.width, self.height)
        ctx.stroke()
        ctx.restore()

class Line(Object):
    def __init__(self, id, x1, y1, x2, y2, color):
        self.id = id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.color = color
        
    def draw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        ctx.set_source_rgb(*self.color)
        ctx.set_line_width(0.01)
        ctx.move_to(self.x1, self.y1)
        ctx.line_to(self.x2, self.y2)
        ctx.stroke()

class Path(Object):
    def __init__(self, id, points, color):
        self.id = id
        self.points = points
        self.color = color

    def draw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        ctx.set_source_rgb(*self.color)
        ctx.set_line_width(0.005)

        ctx.move_to(*self.points[0])
        for point in self.points[1:]:
            ctx.line_to(*point)

        ctx.stroke()

class Robot(Object):
    def __init__(self, id, x, y, th, dir, color):
        self.id = id
        self.x = x
        self.y = y
        self.th = th
        self.dir = dir
        self.color = color
        self.width = 0.07
        self.height = 0.06
        self.wheelPadding = 0.01
        self.dirIndicatorWidth = 0.02
        self.dirIndicatorHeight = 0.03

    def draw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        
        ctx.save()
        ctx.set_source_rgb(*self.color)
        ctx.translate(self.x, self.y)
        ctx.rotate(self.th if self.th >= 0 else (2*np.pi+self.th))

        # Robot body
        ctx.set_line_width(0.01)
        ctx.rectangle(-self.width/2,-self.height/2, self.width, self.height)
        ctx.stroke()
        
        # Robot wheels
        ctx.set_line_width(0.005)
        ctx.move_to(-(self.width/2 - 0.005), -(self.height/2 + self.wheelPadding))
        ctx.line_to(+(self.width/2 - 0.005), -(self.height/2 + self.wheelPadding))
        ctx.stroke()

        ctx.move_to(-(self.width/2 - 0.005), +(self.height/2 + self.wheelPadding))
        ctx.line_to(+(self.width/2 - 0.005), +(self.height/2 + self.wheelPadding))
        ctx.stroke()

        # Robot canonical direction
        ctx.set_line_width(0.005)
        ctx.set_source_rgba(*self.color, 0.5)
        ctx.rectangle(self.width/2-self.dirIndicatorWidth, -self.dirIndicatorHeight/2, self.dirIndicatorWidth, self.dirIndicatorHeight)
        ctx.stroke()

        # Robot direction
        ctx.set_source_rgba(*self.color)
        ctx.save()
        if self.dir == -1: ctx.scale(-1,1) 
        else: ctx.scale(1,1)
        ctx.rectangle(self.width/2-self.dirIndicatorWidth, -self.dirIndicatorHeight/2, self.dirIndicatorWidth, self.dirIndicatorHeight)
        ctx.restore()
        ctx.fill()
        
        ctx.restore()
