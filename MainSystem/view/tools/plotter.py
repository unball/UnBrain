from gi.repository import Gtk, Gdk, GLib
from helpers import LoopThread
import cairo
import numpy as np
from threading import Thread
import time
import math

class Plotter(Gtk.DrawingArea, LoopThread):
  def __init__(self, worker=None, args=()):
    # Herda de DrawingArea
    Gtk.DrawingArea.__init__(self)

    # Dados a serem renderizados
    self.xdata = []
    self.ydata = []
    self.colors = [(0,0,0,1),(0,255,0,1),(0,0,255,1)]

    self.xdatamin = math.inf
    self.xdatamax = 0
    self.ydatamin = math.inf
    self.ydatamax = 0

    self.xplotpos = 75
    self.yplotpos = 20

    self.xtickspaddingright = 10
    self.ytickspaddingtop = 10

    self.plotpaddingright = 50
    self.plotpaddingbottom = 50

    self.mouse_x = 0
    self.mouse_y = 0

    self.avoidDivZero = 0.000001


    # Evento de desenho
    self.connect("draw", self.on_draw)
    self.connect("motion-notify-event", self.on_motion)
    self.set_events(Gdk.EventMask.POINTER_MOTION_MASK)

    self.set_vexpand(True)

    self.show()

    self.__worker = worker
    self.__args = args

    LoopThread.__init__(self, self.data_worker)

  @property
  def plotwidth(self):
    return self.get_allocation().width-self.xplotpos-self.plotpaddingright

  @property
  def plotheight(self):
    return self.get_allocation().height-self.yplotpos-self.plotpaddingbottom

  @property
  def xticks(self):
    return max(1, self.plotwidth // 100)

  @property
  def yticks(self):
    return max(1, self.plotheight // 30)

  @property
  def mouse_value_x(self):
    return 20

  @property
  def mouse_value_y(self):
    return self.yplotpos + self.plotheight + self.plotpaddingbottom - 20

  def data_worker(self):
    xdata, ydata = self.__worker(*self.__args)
    GLib.idle_add(self.set_data, xdata, ydata)
    GLib.idle_add(self.queue_draw)
    time.sleep(0.03)

  def on_motion(self, widget, event):
    if event.type == Gdk.EventType.MOTION_NOTIFY:
      self.mouse_x = event.x
      self.mouse_y = event.y
      self.queue_draw()

  def on_draw(self, widget, cr):
    #self.draw_arrow(cr, 20, 250, 20, 20)
    #self.draw_arrow(cr, 20, 250, 750, 250)

    if self.draw_plot(cr):
      self.draw_x_values(cr)
      self.draw_y_values(cr)
      self.draw_mouse_values(cr)

    self.draw_rectangle(cr, self.xplotpos, self.yplotpos, self.plotwidth, self.plotheight, color=(0, 0, 0, 0.6))

  def x_pixel_to_coord(self, x):
    if x < self.xplotpos or x > self.xplotpos + self.plotwidth: return -1
    return self.xdatamin + (x - self.xplotpos)*(self.xdatamax-self.xdatamin+self.avoidDivZero)/self.plotwidth

  def x_coord_to_nearest_y(self, x):
    return [yd[np.argmin(np.abs(x-xd))] for xd,yd in zip(self.xdata,self.ydata)]

  def x_coord_to_nearest_x(self, x):
    joinedx = np.concatenate(self.xdata)
    return joinedx[np.argmin(np.abs(joinedx-x))]

  def x_coord_to_x_pixel(self, x):
    return self.xplotpos + (x-self.xdatamin)/(self.xdatamax-self.xdatamin+self.avoidDivZero)*self.plotwidth

  def y_coord_to_y_pixel(self, y):
    return self.yplotpos + (-y+(self.ydatamax))/(self.ydatamax-self.ydatamin+self.avoidDivZero)*self.plotheight

  def draw_mouse_values(self, cr):
    x_coord = self.x_pixel_to_coord(self.mouse_x)
    text = "x: " + "{:.2E}".format(x_coord) + "; y: [" + '; '.join(["{:.2E}".format(y) for y in self.x_coord_to_nearest_y(x_coord)]) + "]"
    self.draw_text(cr, self.mouse_value_x, self.mouse_value_y, text, anchor='nl')

  def draw_x_values(self, cr):
    values = np.linspace(self.xdatamin, self.xdatamax, self.xticks+1)

    for i,value in enumerate(values):
      self.draw_text(cr, self.xplotpos+i*self.plotwidth/self.xticks, self.yplotpos+self.ytickspaddingtop+self.plotheight, "{:.2E}".format(value), anchor='nc')

  def draw_y_values(self, cr):
    values = np.linspace(self.ydatamax, self.ydatamin, self.yticks+1)

    for i,value in enumerate(values):
      self.draw_text(cr, self.xplotpos-self.xtickspaddingright, self.yplotpos+i*self.plotheight/self.yticks, "{:.2E}".format(value))

  def draw_text(self, cr, x, y, text, color=(0,0,0,1), anchor='ce'):
    cr.set_source_rgba(*color)
    cr.set_font_size(13)
    textExtents = cr.text_extents(text)

    if anchor == 'ce':
      cr.move_to(x-textExtents.width, y+textExtents.height/2)
    if anchor == 'nc':
      cr.move_to(x-textExtents.width/2, y+textExtents.height)
    if anchor == 'nl':
      cr.move_to(x, y+textExtents.height)
    cr.show_text(text)

  def inside_plot(self, x, y):
    if x < self.xplotpos or x > self.xplotpos + self.plotwidth or y < self.yplotpos or y > self.yplotpos + self.plotheight: return False
    return True

  def draw_ball(self, cr, x, y, color=(0,0,0,1), radius=4):
    cr.set_source_rgba(*color)
    cr.arc(x, y, radius, 0, 2*np.pi)
    cr.fill()

  def draw_rectangle(self, cr, x, y, w, h, linewidth=0.5, color=(0,0,0,1)):
    cr.set_line_width(linewidth)
    cr.set_source_rgba(*color)
    cr.rectangle(x, y, w, h)
    cr.stroke()

  def is_nonzero_float(self, n):
    if not self.is_float(n) or n == 0: return False
    return True

  def is_float(self, n):
    if math.isinf(n) or math.isnan(n): return False
    return True

  def validLimits(self):
    if not self.is_float(self.xdatamax) or not self.is_float(self.xdatamin) or not self.is_float(self.ydatamax) or not self.is_float(self.ydatamin):
      return False
    #if not self.is_nonzero_float(self.xdatamax-self.xdatamin): return False
    #if not self.is_nonzero_float(self.ydatamax-self.ydatamin): return False
    return True

  def draw_line(self, cr, xa, ya, xb, yb, linewidth=0.5, color=(0,0,0,1)):
    cr.set_line_width(linewidth)
    cr.set_source_rgba(*color)
    cr.move_to(xa, ya)
    cr.line_to(xb, yb)
    cr.stroke()

  def draw_arrow(self, cr, xa, ya, xb, yb):
    angle = np.arctan2(yb-ya, xb-xa)
    width = 3
    height = 7
    self.draw_line(cr, xa, ya, xb, yb)
    self.draw_line(cr, xb+width*np.cos(angle+np.pi/2), yb+width*np.sin(angle+np.pi/2), xb-width*np.cos(angle+np.pi/2), yb-width*np.sin(angle+np.pi/2))
    self.draw_line(cr, xb+width*np.cos(angle+np.pi/2), yb+width*np.sin(angle+np.pi/2), xb+height*np.cos(angle), yb+height*np.sin(angle))
    self.draw_line(cr, xb-width*np.cos(angle+np.pi/2), yb-width*np.sin(angle+np.pi/2), xb+height*np.cos(angle), yb+height*np.sin(angle))

  def draw_plot(self, cr, linewidth=1, color=(0,0,0,1)):
    if len(self.xdata) == 0: return False
    for x in self.xdata:
      if x.size == 0: return False
    for y in self.ydata:
      if y.size == 0: return False

    cr.set_line_width(linewidth)
    cr.set_source_rgba(*color)

    self.xdatamin = min([x.min() for x in self.xdata])
    self.xdatamax = max([x.max() for x in self.xdata])

    #self.ydatamin = min(self.ydatamin, min([x.min() for x in self.ydata]))
    #self.ydatamax = max(self.ydatamax, max([x.max() for x in self.ydata]))
    self.ydatamin = min([x.min() for x in self.ydata])
    self.ydatamax = max([x.max() for x in self.ydata])

    if not self.validLimits(): return False

    for j in range(len(self.xdata)):
      xpt = self.xplotpos + (self.xdata[j]-self.xdatamin)/(self.xdatamax-self.xdatamin+self.avoidDivZero)*self.plotwidth
      ypt = self.yplotpos + (-self.ydata[j]+(self.ydatamax))/(self.ydatamax-self.ydatamin+self.avoidDivZero)*self.plotheight

      if self.xdata[j].size <= 1: continue
      for i in range(self.xdata[j].size-1):
        self.draw_line(cr, xpt[i], ypt[i], xpt[i+1], ypt[i+1], color=self.colors[j])
        #self.draw_ball(cr, xpt[i], ypt[i], color=(*self.colors[j][:3], 0.2), radius=2)

    for i in range(self.yticks+1):
      self.draw_line(cr, self.xplotpos, self.yplotpos+i*self.plotheight/self.yticks, self.xplotpos+self.plotwidth, self.yplotpos+i*self.plotheight/self.yticks, color=(0,0,0,0.4))

    for i in range(self.xticks+1):
      self.draw_line(cr, self.xplotpos+i*self.plotwidth/self.xticks, self.yplotpos, self.xplotpos+i*self.plotwidth/self.xticks, self.yplotpos+self.plotheight, color=(0,0,0,0.4))

    xmousecoord = self.x_coord_to_nearest_x(self.x_pixel_to_coord(self.mouse_x))
    ymousecoords = self.x_coord_to_nearest_y(xmousecoord)

    for j,ycoord in enumerate(ymousecoords):
      x = self.x_coord_to_x_pixel(xmousecoord)
      y = self.y_coord_to_y_pixel(ycoord)

      if(self.inside_plot(x, y)):
        self.draw_ball(cr, x, y, color=self.colors[j])

    return True

  def set_data(self, xdata, ydata):
    nxdata = []
    nydata = []
    for x,y in zip(xdata,ydata):
      nxdata.append(np.array(x))
      nydata.append(np.array(y))
    self.xdata = nxdata
    self.ydata = nydata
