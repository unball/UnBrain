from gi.repository import Gtk, GLib
from pkg_resources import resource_filename
from main_system.view.tools.stackSelector import StackSelector
from main_system.view.strategy.highLevelRenderer import HighLevelRenderer
from main_system.view.tools.viewMux import ViewMux
from main_system.controller.states.debugHLC import DebugHLC
from main_system.controller.tools import norm
from main_system.helpers import LoopThread
from main_system.view.tools.plotter import Plotter
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
    # Variáveis reais do UVF do runtime UnBrain (src/strategy/field/UVF.py)
    self.UVF_radius     = builder.get_object("HLC_UVF_radius")
    self.UVF_Kr         = builder.get_object("HLC_UVF_Kr")
    self.UVF_Ko         = builder.get_object("HLC_UVF_Ko")
    self.UVF_dminWall   = builder.get_object("HLC_UVF_dminWall")
    self.UVF_dminRobot  = builder.get_object("HLC_UVF_dminRobot")
    self.UVF_deltaWall  = builder.get_object("HLC_UVF_deltaWall")
    self.UVF_deltaRobot = builder.get_object("HLC_UVF_deltaRobot")
    self.UVF_deltaB     = builder.get_object("HLC_UVF_deltaB")
    self.UVF_showField = builder.get_object("HLC_UVF_showField")
    self.UVF_invertField = builder.get_object("HLCInvertField")
    self.robotEntitySelectors = [
      builder.get_object("HLCRobot0Entity"),
      builder.get_object("HLCRobot1Entity"),
      builder.get_object("HLCRobot2Entity")
    ]
    self.selectableFinalPoint = builder.get_object("HLCSelectableFinalPoint")
    self.staticEntitiesCheckButton = builder.get_object("staticEntitiesCheckButton")

    self.camisaImages = [
      builder.get_object("camisaImage0"),
      builder.get_object("camisaImage1"),
      builder.get_object("camisaImage2")
    ]
    self._last_team_yellow = None
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
    self.cameraFPSTitle = builder.get_object("CameraFPSTitle")
    self.cameraFPSLabel = builder.get_object("CameraFPSValue")
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
    self.UVF_radius.connect("value-changed", self.setWorldParam, "UVF_radius")
    self.UVF_Kr.connect("value-changed", self.setWorldParam, "UVF_Kr")
    self.UVF_Ko.connect("value-changed", self.setWorldParam, "UVF_Ko")
    self.UVF_dminWall.connect("value-changed", self.setWorldParam, "UVF_dmin_wall")
    self.UVF_dminRobot.connect("value-changed", self.setWorldParam, "UVF_dmin_robot")
    self.UVF_deltaWall.connect("value-changed", self.setWorldParam, "UVF_delta_wall")
    self.UVF_deltaRobot.connect("value-changed", self.setWorldParam, "UVF_delta_robot")
    self.UVF_deltaB.connect("value-changed", self.setWorldParam, "UVF_delta_b")
    self.UVF_showField.connect("changed", self.setShowField)
    self.UVF_invertField.connect("state-set", self.setWorldFieldSide)
    self.selectableFinalPoint.connect("state-set", self.setHLCParam_state_set, "selectableFinalPoint")
    self.fieldList.connect("row-activated", self.fieldChooser)
    self.manualControl.connect("state-set", self.setHLCParam_state_set, "enableManualControl")
    self.manualControlLin.connect("value-changed", self.setHLCParam, "manualControlSpeedV")
    self.manualControlAng.connect("value-changed", self.setHLCParam, "manualControlSpeedW")
    self.useVisionButton.connect("state-set",  self.setHLCParam_state_set, "runVision")
    self.staticEntitiesCheckButton.connect("toggled", self.on_static_entities_toggled)
    for i, e in enumerate(self.robotEntitySelectors):
        e.connect("changed", self.setWorldRobotPreferedEntity, i)

    return mainBox

  def on_static_entities_toggled(self, widget):
    is_active = widget.get_active()
    self.setWorldFlag_toggled(widget, "flag_static_entities")
    for e in self.robotEntitySelectors:
        e.set_sensitive(is_active)

  def setShowField(self, widget):
      idx = int(widget.get_active_id())
      self.__renderer.showField = idx
      # Propaga ao UnBrain para ligar/desligar a thread amostradora do campo real.
      self.__controller.addEvent(self._set_hlc_show_field_flag, idx)

  def _set_hlc_show_field_flag(self, idx):
      self.__world.flag_hlc_show_field = idx

  def setWorldRobotPreferedEntity(self, widget, i):
      self.__controller.addEvent(self.updateRobotEntity, i, widget.get_active_id())

  def on_click(self, p):
    finalPoint = (*p, self.__controllerState.finalPoint[2])
    self.__controller.addEvent(self.__controllerState.setFinalPoint, finalPoint)

  def on_scroll(self, mouse, delta):
    finalPoint = (*self.__controllerState.finalPoint[:2], self.__controllerState.finalPoint[2]+delta*0.1)
    if norm(finalPoint, mouse) < 0.03:
      self.__controller.addEvent(self.__controllerState.setFinalPoint, finalPoint)

  def view_worker(self):
    if self._last_team_yellow != self.__world.team_yellow:
      self._last_team_yellow = self.__world.team_yellow
      import os
      from pkg_resources import resource_filename
      base_path = resource_filename(__name__, "images")
      for i, img_widget in enumerate(self.camisaImages):
          if img_widget is not None:
              img_name = f"camisa{i}.png" if self._last_team_yellow else f"camisa_blue{i}.png"
              full_path = os.path.join(base_path, img_name)
              if os.path.exists(full_path):
                  GLib.idle_add(img_widget.set_from_file, full_path)

    GLib.idle_add(self.loopTimeLabel.set_text, "{:.2f} FPS".format(self.__controllerState.debugData["FPS"]))
    
    vision_active = self.__controllerState._controller.visionSystem is not None
    GLib.idle_add(self.cameraFPSTitle.set_visible, vision_active)
    GLib.idle_add(self.cameraFPSLabel.set_visible, vision_active)
    if vision_active:
        GLib.idle_add(self.cameraFPSLabel.set_text, "{:.2f} FPS".format(self.__controllerState.debugData["Camera FPS"]))
    
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
    if len(self.__controllerState.debugData["replayData"][key]) == 0:
      return None
    idx = np.searchsorted(np.array(self.__controllerState.debugData["replayData"]["time"]), reprTime)
    if idx >= len(self.__controllerState.debugData["replayData"][key]):
      self.playPauseButton.set_active(False)
      idx = 0
    return self.__controllerState.debugData["replayData"][key][idx]

  def ballGetter(self):
    if self.__controllerState is None: return []
    if self.replay:
      if self.running: self.reprTime = (time.time()-self.beginReplayTime) / self.replayTimeScale
      data = self.replayData("ball", self.reprTime)
      if data is not None: return data
    
    return self.__world.ball

  def robotsGetter(self):
    if self.__controllerState is None: return []
    if self.replay:
      if self.running: self.reprTime = (time.time()-self.beginReplayTime) / self.replayTimeScale
      
      data = [self.replayData("robot", self.reprTime), self.replayData("robot1", self.reprTime), self.replayData("robot2", self.reprTime)]
      if data[0] is not None: return data
      
    return self.__controllerState.robots

  def getRowByName(self, listBox, key):
    for i in range(5):
      row = listBox.get_row_at_index(i)
      if row is None: return
      if row.get_name() == key: return row

  def updateRobotEntity(self, id, val):
    # Usa setPreferedEntity para que a mudança seja persistida no config.json
    self.__world.setPreferedEntity(id, val)


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
    value = widget.get_value()
    self.__controller.addEvent(self.__world.setParam, key, value)
    # Registra como override do UVF (só os params editados pelo usuário) para o
    # UnBrain aplicar na estratégia real. Enquanto vazio, o artigo fica intacto.
    self.__controller.addEvent(self._record_uvf_override, key, value)

  def _record_uvf_override(self, key, value):
    if getattr(self.__world, 'hlc_uvf_overrides', None) is None:
      self.__world.hlc_uvf_overrides = {}
    self.__world.hlc_uvf_overrides[key] = value

  def setHLCParam_state_set(self, widget, state, key):
    self.__controller.addEvent(self.__controllerState.setParam, key, state)

  def setWorldFlag_toggled(self, widget, key):
    self.__controller.addEvent(setattr, self.__world, key, widget.get_active())

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
    is_static = getattr(self.__world, "flag_static_entities", False)
    self.staticEntitiesCheckButton.set_active(is_static)
    for e in self.robotEntitySelectors:
        e.set_sensitive(is_static)
    self.selectableFinalPoint.set_state(self.__controllerState.getParam("selectableFinalPoint"))
    self.enableDebug.set_state(self.__controllerState.getParam("enableDebug"))
    self.UVF_radius.set_value(self.__world.getParam("UVF_radius"))
    self.UVF_Kr.set_value(self.__world.getParam("UVF_Kr"))
    self.UVF_Ko.set_value(self.__world.getParam("UVF_Ko"))
    self.UVF_dminWall.set_value(self.__world.getParam("UVF_dmin_wall"))
    self.UVF_dminRobot.set_value(self.__world.getParam("UVF_dmin_robot"))
    self.UVF_deltaWall.set_value(self.__world.getParam("UVF_delta_wall"))
    self.UVF_deltaRobot.set_value(self.__world.getParam("UVF_delta_robot"))
    self.UVF_deltaB.set_value(self.__world.getParam("UVF_delta_b"))
    self.fieldList.select_row(self.getRowByName(self.fieldList, self.__controllerState.getParam("selectedField")))
    self.manualControl.set_state(self.__controllerState.getParam("enableManualControl"))
    self.manualControlLin.set_value(self.__controllerState.getParam("manualControlSpeedV"))
    self.manualControlAng.set_value(self.__controllerState.getParam("manualControlSpeedW"))
    self.useVisionButton.set_state(self.__controllerState.getParam("runVision"))

    # Restaura os dropdowns de entidade com base no force_entities do world
    force_ents = getattr(self.__world, "force_entities", {})
    for i, e in enumerate(self.robotEntitySelectors):
        saved_role = force_ents.get(str(i))
        if saved_role:
            e.set_active_id(saved_role)
        self.setWorldRobotPreferedEntity(e, i)


    self.__controller.addEvent(self.__controller.setState, self.__controllerState)
    self.__renderer.start()
    self.start()

  def on_deselect(self, widget):
    self.__renderer.stop()
    self.stop()
    self.__controller.addEvent(self.__controller.unsetState)
