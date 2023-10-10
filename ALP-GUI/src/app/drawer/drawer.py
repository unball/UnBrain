import gi
import cairo
import time
import numpy as np

from gi.repository import Gtk, GObject
from app.drawer.world import World
from app.drawer.objects import *

class Drawer:
    def __init__(self, drawingArea: Gtk.DrawingArea, worldProvider):
        self.drawingArea = drawingArea
        self.worldProvider = worldProvider

        self.fieldSurface = cairo.ImageSurface.create_from_png("src/assets/campo.png")

        drawingArea.connect("draw", self.onDraw)
        self.drawTimeSheduler()

    @property
    def world(self):
        return self.worldProvider()

    def drawTimeSheduler(self):
        GObject.timeout_add(16, self.drawTimeSheduler)
        self.drawingArea.queue_draw()

    def moveToFieldCoordinateSystem(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        w = da.get_allocation().width
        h = da.get_allocation().height

        paddingScale = 0.9

        # Fill with black
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.rectangle(0, 0, w, h)
        ctx.fill()

        # Computes valid proportion
        whp = 1.7 / 1.3

        # Change coordinates to center
        ctx.translate(w / 2, h / 2)

        # Scales according to drawing area size to keep proportion
        if w / h > whp:
            ctx.scale(whp * h / 1.7, -h / 1.3)
        else:
            ctx.scale(w / 1.7, -w / whp / 1.3)

        ctx.scale(paddingScale, paddingScale)
        
        # Fills with gray valid field area 
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.rectangle(-1.7 / 2, -1.3 / 2, 1.7, 1.3)
        ctx.fill()

        # Fills with field lines
        ctx.save()
        ctx.translate(-1.7 / 2, 1.3 / 2)
        ctx.scale(1.7/720, -1.3/551)
        ctx.set_source_surface(self.fieldSurface, 0, 0)
        ctx.paint_with_alpha(0.1)
        ctx.restore()

    def onDraw(self, da: Gtk.DrawingArea, ctx: cairo.Context):
        # Changes to field coordinate system
        self.moveToFieldCoordinateSystem(da, ctx)

        # Draw rectangles
        for rectangle in self.world.rectangles.values():
            rectangle.draw(da, ctx)

        # Draw targets
        for target in self.world.targets.values():
            target.draw(da, ctx)

        # Draw paths
        for path in self.world.paths.values():
            path.draw(da, ctx)

        # Draw lines
        for line in self.world.lines.values():
            line.draw(da, ctx)

        # Draw robots
        for robot in self.world.robots.values():
            robot.draw(da, ctx)

        # Draw ellipses
        for ellipse in self.world.ellipses.values():
            ellipse.draw(da, ctx)