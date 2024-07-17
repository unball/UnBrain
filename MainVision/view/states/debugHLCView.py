from gi.repository import Gtk, GLib
from pkg_resources import resource_filename
from view.tools.stackSelector import StackSelector
from view.strategy.highLevelRenderer import HighLevelRenderer
from view.tools.viewMux import ViewMux
from controller.states.debugHLC import DebugHLC
from controller.tools import norm
from helpers import LoopThread
from view.tools.plotter import Plotter
import numpy as np
import time

class DebugHLCView(LoopThread, StackSelector):
  """Classe que gerencia a view de depurador do controle de alto nível"""

  def __init__(self, controller, world, stack):
    self.__controller = controller
    self.__world = world
    self.__controllerState = None
    self.limit = 250
    self.replay = False
    self.reprTime = 0
    self.beginReplayTime = 0
    self.running = False
    self.replayTimeScale = 1
    LoopThread.__init__(self, self.view_worker)
    StackSelector.__init__(self, stack, "configHLC", "HLC")

  def ui(self):
    # Carrega os elementos estáticos
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "debugHLCView.ui"))

    # Elementos internos
    mainBox = builder.get_object("HLCBox")
    renderContainer = builder.get_object("HLCRender")
    self.enableDebug = builder.get_object("HLCDebugEnable")
    self.playPauseButton = builder.get_object("HLCPlayPause")
    saveData = builder.get_object("HLCSaveData")
    replay = builder.get_object("HLCViewReplay")
    self.replayTimeScaleAdj = builder.get_object("HLCViewReplayTimeScale")
    self.UVF_r = builder.get_object("HLC_UVF_r")
    self.UVF_Kr = builder.get_object("HLC_UVF_Kr")
    self.UVF_Kr_single = builder.get_object("HLC_UVF_Kr_single")
    self.UVF_horRepSize = builder.get_object("HLC_UVF_horRepSize")
    self.UVF_horMinDist = builder.get_object("HLC_UVF_horMinDist")
    self.UVF_verRepSize = builder.get_object("HLC_UVF_verRepSize")
    self.UVF_verGoalSize = builder.get_object("HLC_UVF_verGoalSize")
    self.UVF_verMinDist = builder.get_object("HLC_UVF_verMinDist")
    self.UVF_ponRadius = builder.get_object("HLC_UVF_ponRadius")
    self.UVF_ponDistanceRadius = builder.get_object("HLC_UVF_ponDistanceRadius")
    self.UVF_ponMinAvoidanceAngle = builder.get_object("HLC_UVF_ponMinAvoidanceAngle")
    self.UVF_showField = builder.get_object("HLC_UVF_showField")
    self.UVF_invertField = builder.get_object("HLCInvertField")
    self.robotEntitySelectors = [
      builder.get_object("HLCRobot0Entity"),
      builder.get_object("HLCRobot1Entity"),
      builder.get_object("HLCRobot2Entity")
    ]
    self.selectableFinalPoint = builder.get_object("HLCSelectableFinalPoint")

    self.HLCcontrolList = ViewMux(self.__controller)
    HLCcontrolListBox = builder.get_object("HLCControlChooserBox")
    HLCcontrolListBox.pack_end(self.HLCcontrolList, True, True, 0)

    self.fieldList = builder.get_object("HLCFieldChooser")
    self.manualControl = builder.get_object("HLCSwitchManualControl")
    self.manualControlLin = builder.get_object("manualControlLin")
    self.manualControlAng = builder.get_object("manualControlAng")
    self.useVisionButton = builder.get_object("HLCUseVision")
    
    # Labels
    self.loopTimeLabel = builder.get_object("HLCLoopTime")
    self.controlVLabel = builder.get_object("HLCcontrolV")
    self.controlWLabel = builder.get_object("HLCcontrolW")
    self.visionVLabel = builder.get_object("HLCvisionV")
    self.visionWLabel = builder.get_object("HLCvisionW")
    self.visionPoseLabel = builder.get_object("HLCvisionPose")

    self.__renderer = HighLevelRenderer(self.__world, robotsGetter=self.robotsGetter, ballGetter=self.ballGetter, on_click=self.on_click, on_scroll=self.on_scroll)
    """Instancia o renderizador, ele é do tipo GtkFrame"""

    # Adiciona o renderizador ao GtkBox
    renderContainer.add(self.__renderer)

    # Adiciona os gráficos
    self.__plots = {
      "PlotPosTh": (Plotter(), ("posTh","posThRef","posThErr")),
      "PlotBallVel": (Plotter(), ("velBallMod", "velBallX","velBallY")),
      "PlotBallAcc": (Plotter(), ("accBallMod", "accBallX","accBallY")),
      "PlotVelLin": (Plotter(), ("visionLin","velLin")),
      "PlotVelAng": (Plotter(), ("visionAng","velAng")),
      "PlotRobotVel": (Plotter(), ("velRobotMod", "velRobotX","velRobotY"))
    }
    for el in self.__plots: builder.get_object(el).add(self.__plots[el][0])

    # Liga os sinais
    self.playPauseButton.connect("toggled", self.playPause)
    self.enableDebug.connect("state-set", self.setHLCParam_state_set, "enableDebug")
    saveData.connect("clicked", self.saveData)
    replay.connect("toggled", self.setReplay)
    self.replayTimeScaleAdj.connect("value-changed", self.setReplayTimeScale)
    self.UVF_r.connect("value-changed", self.setWorldParam, "UVF_r")
    self.UVF_Kr.connect("value-changed", self.setWorldParam, "UVF_Kr")
    self.UVF_Kr_single.connect("value-changed", self.setWorldParam, "UVF_Kr_single")
    self.UVF_horRepSize.connect("value-changed", self.setWorldParam, "UVF_horRepSize")
    self.UVF_horMinDist.connect("value-changed", self.setWorldParam, "UVF_horMinDist")
    self.UVF_verRepSize.connect("value-changed", self.setWorldParam, "UVF_verRepSize")
    self.UVF_verGoalSize.connect("value-changed", self.setWorldParam, "UVF_verGoalSize")
    self.UVF_verMinDist.connect("value-changed", self.setWorldParam, "UVF_verMinDist")
    self.UVF_ponRadius.connect("value-changed", self.setWorldParam, "UVF_ponRadius")
    self.UVF_ponDistanceRadius.connect("value-changed", self.setWorldParam, "UVF_ponDistanceRadius")
    self.UVF_ponMinAvoidanceAngle.connect("value-changed", self.setWorldParam, "UVF_ponMinAvoidanceAngle")
    self.UVF_showField.connect("changed", self.setShowField)
    self.UVF_invertField.connect("state-set", self.setWorldFieldSide)
    self.selectableFinalPoint.connect("state-set", self.setHLCParam_state_set, "selectableFinalPoint")
    self.fieldList.connect("row-activated", self.fieldChooser)
    self.manualControl.connect("state-set", self.setHLCParam_state_set, "enableManualControl")
    self.manualControlLin.connect("value-changed", self.setHLCParam, "manualControlSpeedV")
    self.manualControlAng.connect("value-changed", self.setHLCParam, "manualControlSpeedW")
    self.useVisionButton.connect("state-set",  self.setHLCParam_state_set, "runVision")
    for i,e in enumerate(self.robotEntitySelectors): e.connect("changed", self.setWorldRobotPreferedEntity, i)

    return mainBox

  def setShowField(self, widget):
      self.__renderer.showField = int(widget.get_active_id())

  def setWorldRobotPreferedEntity(self, widget, i):
      self.__controller.addEvent(self.__world.setPreferedEntity, i, widget.get_active_id())

  def on_click(self, p):
    finalPoint = (*p, self.__controllerState.finalPoint[2])
    self.__controller.addEvent(self.__controllerState.setFinalPoint, finalPoint)

  def on_scroll(self, mouse, delta):
    finalPoint = (*self.__controllerState.finalPoint[:2], self.__controllerState.finalPoint[2]+delta*0.1)
    if norm(finalPoint, mouse) < 0.03:
      self.__controller.addEvent(self.__controllerState.setFinalPoint, finalPoint)

  def view_worker(self):
    GLib.idle_add(self.loopTimeLabel.set_text, "{:.2f} ms".format(self.__controllerState.debugData["loopTime"]))
    GLib.idle_add(self.controlVLabel.set_text, "{:.2f} m/s".format(self.__controllerState.debugData["controlV"]))
    GLib.idle_add(self.controlWLabel.set_text, "{:.2f} rad/s".format(self.__controllerState.debugData["controlW"]))
    GLib.idle_add(self.visionVLabel.set_text, "{:.2f} m/s".format(self.__controllerState.debugData["visionV"]))
    GLib.idle_add(self.visionWLabel.set_text, "{:.2f} rad/s".format(self.__controllerState.debugData["visionW"]))
    GLib.idle_add(self.visionPoseLabel.set_text, "x: {:.2f} m\ny: {:.2f} m\nth: {:6.2f} º".format(*self.__controllerState.debugData["visionPose"]))
    for key in self.__plots:
      GLib.idle_add(self.__plots[key][0].set_data, *self.getData(*self.__plots[key][1]))
      GLib.idle_add(self.__plots[key][0].queue_draw)
    time.sleep(0.03)

  def getData(self, *dataNames):
    if self.__controllerState is None: return [],[]
    xdata = []
    ydata = []
    for name in dataNames:
      d = self.__controllerState.debugData[name][-self.limit:]
      xdata.append([i for i in range(len(d))])
      ydata.append(d)
    return xdata, ydata

  def replayData(self, key, reprTime):
    idx = np.searchsorted(np.array(self.__controllerState.debugData["replayData"]["time"]), reprTime)
    if idx >= len(self.__controllerState.debugData["replayData"][key]):
      self.playPauseButton.set_active(False)
      idx = 0
    return self.__controllerState.debugData["replayData"][key][idx]

  def ballGetter(self):
    if self.__controllerState is None: return []
    if self.replay:
      if self.running: self.reprTime = (time.time()-self.beginReplayTime) / self.replayTimeScale
      return self.replayData("ball", self.reprTime)
    else:
      return self.__world.ball

  def robotsGetter(self):
    if self.__controllerState is None: return []
    if self.replay:
      if self.running: self.reprTime = (time.time()-self.beginReplayTime) / self.replayTimeScale
      return [self.replayData("robot", self.reprTime), self.replayData("robot1", self.reprTime), self.replayData("robot2", self.reprTime)]
    else:
      return self.__controllerState.robots

  def getRowByName(self, listBox, key):
    for i in range(5):
      row = listBox.get_row_at_index(i)
      if row is None: return
      if row.get_name() == key: return row

  def playPause(self, widget):
    self.running = widget.get_active()
    self.beginReplayTime = time.time()
    if self.replay:
      self.__controller.addEvent(self.__world.setRunning, False)
    else:
      self.__controller.addEvent(self.__world.setRunning, self.running)

  def setReplay(self, widget):
    self.replay = widget.get_active()
    self.playPauseButton.set_active(False)

  def setReplayTimeScale(self, widget):
    self.replayTimeScale = widget.get_value()

  def saveData(self, widget):
    dialog = Gtk.FileChooserDialog("Salvar arquivo", None, Gtk.FileChooserAction.SAVE,
      (Gtk.STOCK_CANCEL,
       Gtk.ResponseType.CANCEL,
       Gtk.STOCK_SAVE,
       Gtk.ResponseType.ACCEPT))

    dialog.connect("response", self.saveDataResponse)
    dialog.show()

  def saveDataResponse(self, dialog, response):
    if response == Gtk.ResponseType.ACCEPT:
      self.__controller.addEvent(self.__controllerState.saveData, dialog.get_filename())
    dialog.destroy()

  def setHLCParam(self, widget, key):
    self.__controller.addEvent(self.__controllerState.setParam, key, widget.get_value())

  def setWorldParam(self, widget, key):
    self.__controller.addEvent(self.__world.setParam, key, widget.get_value())

  def setHLCParam_state_set(self, widget, state, key):
    self.__controller.addEvent(self.__controllerState.setParam, key, state)

  def setWorldFieldSide(self, widget, state):
    self.__controller.addEvent(self.__world.setFieldSide, -1 if state else 1)

  def fieldChooser(self, widget, row):
    self.__controller.addEvent(self.__controllerState.setParam, "selectedField", row.get_name())

  def updateParam(self, widget, controlSystem, key):
    self.__controller.addEvent(controlSystem.setParam, key, widget.get_value())

  def on_select(self, widget):
    self.__controllerState = DebugHLC(self.__controller)

    self.HLCcontrolList.setMux(self.__controllerState.HLCs)

    # Define valores padrão
    self.selectableFinalPoint.set_state(self.__controllerState.getParam("selectableFinalPoint"))
    self.enableDebug.set_state(self.__controllerState.getParam("enableDebug"))
    self.UVF_r.set_value(self.__world.getParam("UVF_r"))
    self.UVF_Kr.set_value(self.__world.getParam("UVF_Kr"))
    self.UVF_Kr_single.set_value(self.__world.getParam("UVF_Kr_single"))
    self.UVF_horRepSize.set_value(self.__world.getParam("UVF_horRepSize"))
    self.UVF_horMinDist.set_value(self.__world.getParam("UVF_horMinDist"))
    self.UVF_verRepSize.set_value(self.__world.getParam("UVF_verRepSize"))
    self.UVF_verGoalSize.set_value(self.__world.getParam("UVF_verGoalSize"))
    self.UVF_verMinDist.set_value(self.__world.getParam("UVF_verMinDist"))
    self.UVF_ponRadius.set_value(self.__world.getParam("UVF_ponRadius"))
    self.UVF_ponDistanceRadius.set_value(self.__world.getParam("UVF_ponDistanceRadius"))
    self.UVF_ponMinAvoidanceAngle.set_value(self.__world.getParam("UVF_ponMinAvoidanceAngle"))
    self.fieldList.select_row(self.getRowByName(self.fieldList, self.__controllerState.getParam("selectedField")))
    self.manualControl.set_state(self.__controllerState.getParam("enableManualControl"))
    self.manualControlLin.set_value(self.__controllerState.getParam("manualControlSpeedV"))
    self.manualControlAng.set_value(self.__controllerState.getParam("manualControlSpeedW"))
    self.useVisionButton.set_state(self.__controllerState.getParam("runVision"))
    for i,e in enumerate(self.robotEntitySelectors): self.setWorldRobotPreferedEntity(e, i)

    self.__controller.addEvent(self.__controller.setState, self.__controllerState)
    self.__renderer.start()
    self.start()

  def on_deselect(self, widget):
    self.__renderer.stop()
    self.stop()
    self.__controller.addEvent(self.__controller.unsetState)
