from gi.repository import Gtk, GLib
from pkg_resources import resource_filename
from main_system.view.tools.stackSelector import StackSelector
from main_system.helpers import LoopThread
from main_system.view.strategy.highLevelRenderer import HighLevelRenderer
import time

class ControlView(LoopThread, StackSelector):
  """Aba de Controle de Robôs em Tempo Real"""

  def __init__(self, controller, world, stack):
    self.__controller = controller
    self.__world = world
    
    # Inicializa parâmetros globais de controle se não existirem
    if not hasattr(self.__world, "global_control_params"):
        self.__world.global_control_params = {}
    if not hasattr(self.__world, "flag_control_tester"):
        self.__world.flag_control_tester = False
    if not hasattr(self.__world, "test_roles"):
        self.__world.test_roles = ["None", "None", "None"]

    # Valores padrão para carregar na UI quando um controlador é selecionado pela primeira vez
    self.default_params = {"kw": 20.0, "kp": 10.0, "mu": 0.1, "vmax": 2.0}

    self._last_team_yellow = None
    
    LoopThread.__init__(self, self.view_worker)
    StackSelector.__init__(self, stack, "configControl", "Controle")
    
  def ui(self):
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "controlView.ui"))
    mainBox = builder.get_object("ControlBox")
    
    renderContainer = builder.get_object("ControlRender")
    self.__renderer = HighLevelRenderer(self.__world, robotsGetter=self.robotsGetter, ballGetter=self.ballGetter)
    renderContainer.add(self.__renderer)
    
    self.controlSelector = builder.get_object("controlSelector")
    self.controlTesterCheckButton = builder.get_object("controlTesterCheckButton")
    
    self.robotTestSelectors = [
        builder.get_object("robot0TestSelector"),
        builder.get_object("robot1TestSelector"),
        builder.get_object("robot2TestSelector")
    ]
    
    self.spin_kw = builder.get_object("spin_kw")
    self.spin_kp = builder.get_object("spin_kp")
    self.spin_mu = builder.get_object("spin_mu")
    self.spin_vmax = builder.get_object("spin_vmax")

    self.camisaImages = [
        builder.get_object("camisaCtrlImage0"),
        builder.get_object("camisaCtrlImage1"),
        builder.get_object("camisaCtrlImage2")
    ]
    
    # Monitor de V e W
    self.label_v = builder.get_object("label_v")
    self.label_w = builder.get_object("label_w")
    
    self.controlSelector.connect("changed", self.on_control_changed)
    self.controlTesterCheckButton.connect("toggled", self.on_control_tester_toggled)
    
    for i, selector in enumerate(self.robotTestSelectors):
        selector.connect("changed", self.on_test_role_changed, i)
        
    self.spin_kw.connect("value-changed", self.on_param_changed, "kw")
    self.spin_kp.connect("value-changed", self.on_param_changed, "kp")
    self.spin_mu.connect("value-changed", self.on_param_changed, "mu")
    self.spin_vmax.connect("value-changed", self.on_param_changed, "vmax")
    
    return mainBox
    
  def robotsGetter(self):
    return [self.__world.robots[i] for i in range(self.__world.n_robots)]

  def ballGetter(self):
    return self.__world.ball

  def view_worker(self):
    """Atualiza a telemetria na UI"""
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

    # Para o monitor, ainda podemos mostrar o Robô 0 como amostra
    if self.__world.n_robots > 0:
        robot = self.__world.robots[0]
        GLib.idle_add(self.label_v.set_text, "{:.2f} m/s".format(robot.inst_vx))
        GLib.idle_add(self.label_w.set_text, "{:.2f} rad/s".format(robot.inst_w))
        
    time.sleep(0.05)
    
  def on_control_changed(self, widget):
    control_name = widget.get_active_id()
    if control_name:
        # Se for a primeira vez selecionando este controle, inicializa os parâmetros
        if control_name not in self.__world.global_control_params:
            self.__world.global_control_params[control_name] = self.default_params.copy()
            
        params = self.__world.global_control_params[control_name]
        
        # Bloqueia os sinais para não disparar 'value-changed' durante a atualização da UI
        self.spin_kw.handler_block_by_func(self.on_param_changed)
        self.spin_kp.handler_block_by_func(self.on_param_changed)
        self.spin_mu.handler_block_by_func(self.on_param_changed)
        self.spin_vmax.handler_block_by_func(self.on_param_changed)
        
        self.spin_kw.set_value(params.get("kw", 20.0))
        self.spin_kp.set_value(params.get("kp", 10.0))
        self.spin_mu.set_value(params.get("mu", 0.1))
        self.spin_vmax.set_value(params.get("vmax", 2.0))
        
        self.spin_kw.handler_unblock_by_func(self.on_param_changed)
        self.spin_kp.handler_unblock_by_func(self.on_param_changed)
        self.spin_mu.handler_unblock_by_func(self.on_param_changed)
        self.spin_vmax.handler_unblock_by_func(self.on_param_changed)

  def on_param_changed(self, widget, param_name):
    control_name = self.controlSelector.get_active_id()
    if control_name:
        if control_name not in self.__world.global_control_params:
            self.__world.global_control_params[control_name] = self.default_params.copy()
            
        val = widget.get_value()
        # Atualiza o estado global no controller/world (será enviado via IPC)
        def update_param():
            self.__world.global_control_params[control_name][param_name] = val
        self.__controller.addEvent(update_param)

  def on_control_tester_toggled(self, widget):
    is_active = widget.get_active()
    def update_flag():
        self.__world.flag_control_tester = is_active
    self.__controller.addEvent(update_flag)
    
    # Habilita/desabilita os comboboxes
    for e in self.robotTestSelectors:
        e.set_sensitive(is_active)

  def on_test_role_changed(self, widget, i):
    role = widget.get_active_id()
    def update_role():
        self.__world.test_roles[i] = role
    self.__controller.addEvent(update_role)

  def on_select(self, widget):
    self.start()
    self.__renderer.start()
    if self.controlSelector.get_active() < 0:
        self.controlSelector.set_active(0)
    # Inicializa ComboBoxes
    for i, e in enumerate(self.robotTestSelectors):
        if e.get_active() < 0:
            e.set_active_id("None")
    
  def on_deselect(self, widget):
    self.__renderer.stop()
    self.stop()
