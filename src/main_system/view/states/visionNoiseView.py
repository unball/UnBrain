from gi.repository import Gtk
from main_system.view.tools.stackSelector import StackSelector

class VisionNoiseView(StackSelector):
  """Classe que gerencia a view de configuração de ruído de visão"""

  def __init__(self, controller, world, stack):
    self.__controller = controller
    self.__world = world
    StackSelector.__init__(self, stack, "configNoise", "Vision Noise")

  def ui(self):
    scrolled = Gtk.ScrolledWindow()
    scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    mainBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
    mainBox.set_margin_left(10)
    mainBox.set_margin_right(10)
    mainBox.set_margin_top(10)
    mainBox.set_margin_bottom(10)
    scrolled.add(mainBox)

    def add_switch(box, label_text, param_key):
      hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
      lbl = Gtk.Label(label=label_text)
      lbl.set_halign(Gtk.Align.START)
      switch = Gtk.Switch()
      switch.set_active(self.__world.get_vision_noise_config().get(param_key, False))
      
      switch.connect("state-set", lambda w, state: (self.__controller.addEvent(self.__world.set_noise_param, param_key, state), False)[1])
      
      hbox.pack_start(lbl, True, True, 0)
      hbox.pack_end(switch, False, False, 0)
      box.pack_start(hbox, False, False, 0)
      return switch

    def add_slider(box, label_text, param_key, min_val, max_val, step):
      hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
      lbl = Gtk.Label(label=label_text)
      lbl.set_halign(Gtk.Align.START)
      adj = Gtk.Adjustment(
          value=self.__world.get_vision_noise_config().get(param_key, min_val),
          lower=min_val,
          upper=max_val,
          step_increment=step,
          page_increment=step*10,
          page_size=0
      )
      scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
      scale.set_digits(3 if step < 0.01 else 2)
      scale.set_size_request(200, -1)
      
      scale.connect("value-changed", lambda w: self.__controller.addEvent(self.__world.set_noise_param, param_key, w.get_value()))
      
      hbox.pack_start(lbl, True, True, 0)
      hbox.pack_end(scale, False, False, 0)
      box.pack_start(hbox, False, False, 0)
      return scale

    # 1. P-G Noise Frame
    pg_frame = Gtk.Frame(label="P-G (Poisson-Gaussian) Noise")
    pg_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    pg_box.set_border_width(10)
    pg_frame.add(pg_box)
    add_switch(pg_box, "Enable P-G Noise", "pg_noise_enabled")
    add_slider(pg_box, "Base Standard Deviation (std_base)", "pg_noise_std_base", 0.001, 0.05, 0.001)
    add_slider(pg_box, "Scale Standard Deviation (std_scale)", "pg_noise_std_scale", 0.001, 0.02, 0.001)
    mainBox.pack_start(pg_frame, False, False, 0)

    # 2. Gilbert-Elliott Frame
    ge_frame = Gtk.Frame(label="Gilbert-Elliott Packet Dropout")
    ge_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    ge_box.set_border_width(10)
    ge_frame.add(ge_box)
    add_switch(ge_box, "Enable Gilbert-Elliott Dropout", "ge_dropout_enabled")
    add_slider(ge_box, "P (Good -> Bad state probability)", "ge_p", 0.01, 0.2, 0.01)
    add_slider(ge_box, "Q (Bad -> Good state probability)", "ge_q", 0.1, 0.5, 0.01)
    add_slider(ge_box, "Eg (Good state drop probability)", "ge_eg", 0.0, 0.05, 0.005)
    add_slider(ge_box, "Eb (Bad state drop probability)", "ge_eb", 0.8, 1.0, 0.01)
    mainBox.pack_start(ge_frame, False, False, 0)

    # 3. Outlier Frame
    out_frame = Gtk.Frame(label="Outlier Noise (Teleportation)")
    out_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    out_box.set_border_width(10)
    out_frame.add(out_box)
    add_switch(out_box, "Enable Outliers", "outlier_enabled")
    add_slider(out_box, "Outlier Probability", "outlier_prob", 0.001, 0.05, 0.001)
    add_slider(out_box, "Outlier Range (m)", "outlier_range", 0.5, 2.0, 0.1)
    mainBox.pack_start(out_frame, False, False, 0)


    # 4. Targets Frame
    targets_frame = Gtk.Frame(label="Target Entities")
    targets_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    targets_box.set_border_width(10)
    targets_frame.add(targets_box)
    add_switch(targets_box, "Apply to Ball", "apply_to_ball")
    add_switch(targets_box, "Apply to Robot 0", "apply_to_robot_0")
    add_switch(targets_box, "Apply to Robot 1", "apply_to_robot_1")
    add_switch(targets_box, "Apply to Robot 2", "apply_to_robot_2")
    mainBox.pack_start(targets_frame, False, False, 0)

    # 5. Domain Randomization Frame
    dr_frame = Gtk.Frame(label="Domain Randomization Limits")
    dr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    dr_box.set_border_width(10)
    dr_frame.add(dr_box)
    add_switch(dr_box, "Enable Domain Randomization", "domain_randomization_enabled")
    add_slider(dr_box, "Randomization Interval (Frames)", "domain_randomization_interval", 100, 10000, 100)
    add_slider(dr_box, "pg_noise_std_base_min", "pg_noise_std_base_min", 0.001, 0.05, 0.001)
    add_slider(dr_box, "pg_noise_std_base_max", "pg_noise_std_base_max", 0.001, 0.05, 0.001)
    add_slider(dr_box, "pg_noise_std_scale_min", "pg_noise_std_scale_min", 0.001, 0.02, 0.001)
    add_slider(dr_box, "pg_noise_std_scale_max", "pg_noise_std_scale_max", 0.001, 0.02, 0.001)
    add_slider(dr_box, "ge_p_min", "ge_p_min", 0.01, 0.2, 0.01)
    add_slider(dr_box, "ge_p_max", "ge_p_max", 0.01, 0.2, 0.01)
    add_slider(dr_box, "ge_q_min", "ge_q_min", 0.1, 0.5, 0.01)
    add_slider(dr_box, "ge_q_max", "ge_q_max", 0.1, 0.5, 0.01)
    add_slider(dr_box, "ge_eg_min", "ge_eg_min", 0.0, 0.05, 0.005)
    add_slider(dr_box, "ge_eg_max", "ge_eg_max", 0.0, 0.05, 0.005)
    add_slider(dr_box, "ge_eb_min", "ge_eb_min", 0.8, 1.0, 0.01)
    add_slider(dr_box, "ge_eb_max", "ge_eb_max", 0.8, 1.0, 0.01)
    add_slider(dr_box, "outlier_prob_min", "outlier_prob_min", 0.001, 0.05, 0.001)
    add_slider(dr_box, "outlier_prob_max", "outlier_prob_max", 0.001, 0.05, 0.001)
    add_slider(dr_box, "outlier_range_min", "outlier_range_min", 0.5, 2.0, 0.1)
    add_slider(dr_box, "outlier_range_max", "outlier_range_max", 0.5, 2.0, 0.1)
    mainBox.pack_start(dr_frame, False, False, 0)

    # 6. System Delay Frame
    delay_frame = Gtk.Frame(label="System Delay Simulator")
    delay_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    delay_box.set_border_width(10)
    delay_frame.add(delay_box)
    add_slider(delay_box, "System Delay (ms)", "system_delay_ms", 0, 200, 10)
    mainBox.pack_start(delay_frame, False, False, 0)

    # Sim-to-Real Recording Button
    record_btn = Gtk.Button(label="Gravar Dados Sim-to-Real")
    # Conecta de forma assíncrona usando addEvent para manter a UI responsiva
    record_btn.connect("clicked", lambda w: self.__controller.addEvent(setattr, self.__world, "flag_record_sim2real", True))
    mainBox.pack_start(record_btn, False, False, 10)

    scrolled.show_all()
    return scrolled
