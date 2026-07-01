"""Este módulo implementa a interface gráfica do sistema."""

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from pkg_resources import resource_filename

from main_system.view.vision.camerasView import CameraHandlerView
from main_system.view.vision.mainVision.mainVisionView import MainVisionView
from main_system.view.communication.communicationView import CommunicationHandlerView
from main_system.view.states.debugHLCView import DebugHLCView
from main_system.view.states.visionNoiseView import VisionNoiseView
from main_system.view.tools.viewThreads import ViewThreads

class View:
  def __init__(self, controller, simulator=False):
    self.__controller = controller
    self.simulator = simulator
    """Mantém uma referência ao controller"""
    
    self.__threads = ViewThreads()
    """Contém uma lista de threads de view que poderão ser finalizadas quando o programa acabar"""
    
  def on_destroy(self, window):
    """Este método é chamado quando a janela é fechada e faz com que a thread de backend acabe"""
    if hasattr(self.__controller, 'launcher') and self.__controller.launcher:
        self.__controller.launcher.stop()
    if hasattr(self.__controller, 'enemy_launcher') and self.__controller.enemy_launcher:
        self.__controller.enemy_launcher.stop()
    self.__controller.stop()
    self.__threads.stop()
    Gtk.main_quit()
    
  def registerThread(self, thread):
    """Registra uma thread de view para que possa ser finalizada quando o programa fechar"""
    self.__threads.register(thread)

  def _setup_save_button(self, saveBtn):
    """Monta o popover de confirmação 'Deseja salvar?' (Sim/Não) do botão de salvar
    configurações da interface. Só o 'Sim' persiste no disco; evita miss-click."""
    if saveBtn is None:
      return
    popover = Gtk.Popover.new(saveBtn)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
    box.set_border_width(10)
    box.pack_start(Gtk.Label(label="Deseja salvar?"), False, False, 0)
    btnBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    btnSim = Gtk.Button(label="Sim")
    btnNao = Gtk.Button(label="Não")
    btnBox.pack_start(btnSim, True, True, 0)
    btnBox.pack_start(btnNao, True, True, 0)
    box.pack_start(btnBox, False, False, 0)
    box.show_all()
    popover.add(box)
    saveBtn.set_popover(popover)

    def on_sim(_btn):
      self._save_interface_config()
      popover.popdown()
    btnSim.connect("clicked", on_sim)
    btnNao.connect("clicked", lambda _b: popover.popdown())

  def _save_interface_config(self):
    """Confirma no disco todas as configurações da interface bufferizadas."""
    from main_system.model import Model
    from main_system.model.paramsPattern import ParamsPattern
    try:
      ParamsPattern.commit_all_deferred()  # worldConfig/UVF, visionNoise, HLC params
      Model().commitPending()              # team_yellow, force_entities
      Model().flush()
      print("[Interface] Configurações salvas em config.json", flush=True)
    except Exception as e:
      import traceback
      print(f"[Interface] Falha ao salvar configurações: {e}", flush=True)
      traceback.print_exc()
  
  def run(self):
    """Executa o loop principal do Gtk e instancia os elementos de interface gráfica da janela principal"""
    
    # Adiciona os elementos estáticos da janela principal da interface
    import os
    ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.ui")
    builder = Gtk.Builder.new_from_file(ui_path)
    
    # Load CSS
    css_provider = Gtk.CssProvider()
    css_provider.load_from_path(resource_filename(__name__, "style.css"))
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    # Cria a janela
    window = builder.get_object("mainWindow")
    
    # Carrega a logo no header bar com base no tema (dark/light)
    header_logo = builder.get_object("headerLogoImage")
    if header_logo:
        from gi.repository import GdkPixbuf
        settings = Gtk.Settings.get_default()
        theme_name = settings.get_property("gtk-theme-name")
        is_dark = settings.get_property("gtk-application-prefer-dark-theme") or (theme_name and "dark" in theme_name.lower())
        
        img_name = "UnBall_transp.png" if is_dark else "UnBall_orange.png"
        img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", img_name)
        
        if os.path.exists(img_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(img_path, width=-1, height=32, preserve_aspect_ratio=True)
            header_logo.set_from_pixbuf(pixbuf)
        
    window.show_all()
    
    # Conecta o sinal de saída do programa
    window.connect("destroy", self.on_destroy)
    
    # Botão que gerencia as câmeras
    camerasBtn = builder.get_object("camerasMenuButton")
    if not self.simulator:
        CameraHandlerView(self.__controller, self.__controller.visionSystem.cameraHandler, camerasBtn)
    else:
        camerasBtn.set_visible(False)
    
    # Botão que gerencia o sistema de comunicação
    CommunicationHandlerView(self.__controller, self.__controller.communicationSystems, builder.get_object("communicationMenuButton"))

    # Botão de Time
    teamBtn = builder.get_object("teamColorButton")
    
    def on_team_toggled(btn):
        is_yellow = not btn.get_active()
        self.__controller.world.team_yellow = is_yellow
        btn.set_label("Amarelo" if is_yellow else "Azul")
        
    teamBtn.set_active(not self.__controller.world.team_yellow)
    teamBtn.set_label("Amarelo" if self.__controller.world.team_yellow else "Azul")
    teamBtn.connect("toggled", on_team_toggled)

    # Botão de salvar configurações da interface (com confirmação, p/ evitar miss-click).
    self._setup_save_button(builder.get_object("saveConfigButton"))

    # Pilha do Gtk da página principal
    mainStack = builder.get_object("mainStack")

    # ----- Opções do src/main.py (Side Panel) -----
    self.refereeCheckButton = builder.get_object("refereeCheckButton")
    self.controlCheckButton = builder.get_object("controlCheckButton")
    self.debugCheckButton = builder.get_object("debugCheckButton")
    self.ppoCheckButton = builder.get_object("ppoCheckButton")
    self.enemyAiCheckButton = builder.get_object("enemyAiCheckButton")
    self.recordCheckButton = builder.get_object("recordCheckButton")
    self.mirrorCheckButton = builder.get_object("mirrorCheckButton")
    self.usePredictorCheckButton = builder.get_object("usePredictorCheckButton")
    self.kalmanFilterCheckButton = builder.get_object("kalmanFilterCheckButton")
    self.neuralEstimatorCheckButton = builder.get_object("neuralEstimatorCheckButton")
    self.visionNoiseCheckButton = builder.get_object("visionNoiseCheckButton")
    self.disableAiCheckButton = builder.get_object("disableAiCheckButton")
    self.enemyOnCheckButton = builder.get_object("enemyOnCheckButton")
    self.nRobotsEntry = builder.get_object("nRobotsEntry")
    self.simuladorComboBox = builder.get_object("simuladorComboBox")

    if self.refereeCheckButton:
        self.refereeCheckButton.set_active(getattr(self.__controller.world, "flag_referee", False))
        self.refereeCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_referee", b.get_active()))
    if self.controlCheckButton:
        self.controlCheckButton.set_active(getattr(self.__controller.world, "flag_control", False))
        self.controlCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_control", b.get_active()))
    if self.debugCheckButton:
        self.debugCheckButton.set_active(getattr(self.__controller.world, "flag_debug", False))
        self.debugCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_debug", b.get_active()))
    if self.ppoCheckButton:
        self.ppoCheckButton.set_active(getattr(self.__controller.world, "flag_ppo_ai", False))
        self.ppoCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_ppo_ai", b.get_active()))
    if self.enemyAiCheckButton:
        self.enemyAiCheckButton.set_active(getattr(self.__controller.world, "flag_enemy_ai", False))
        self.enemyAiCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_enemy_ai", b.get_active()))
    if self.recordCheckButton:
        self.recordCheckButton.set_active(getattr(self.__controller.world, "flag_record", False))
        def _toggle_records(b):
            setattr(self.__controller.world, "flag_record", b.get_active())
            setattr(self.__controller.world, "flag_record_sim2real", b.get_active())
        self.recordCheckButton.connect("toggled", _toggle_records)
    if self.mirrorCheckButton:
        self.mirrorCheckButton.set_active(getattr(self.__controller.world, "flag_mirror", False))
        self.mirrorCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_mirror", b.get_active()))
    if self.usePredictorCheckButton:
        self.usePredictorCheckButton.set_active(getattr(self.__controller.world, "flag_use_predictor", False))
        self.usePredictorCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_use_predictor", b.get_active()))
    if self.kalmanFilterCheckButton:
        self.kalmanFilterCheckButton.set_active(getattr(self.__controller.world, "flag_use_kalman", False))
        self.kalmanFilterCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_use_kalman", b.get_active()))
    if self.neuralEstimatorCheckButton:
        self.neuralEstimatorCheckButton.set_active(getattr(self.__controller.world, "flag_use_neural_estimator", False))
        self.neuralEstimatorCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_use_neural_estimator", b.get_active()))
    if self.visionNoiseCheckButton:
        self.visionNoiseCheckButton.set_active(getattr(self.__controller.world, "flag_use_vision_noise", False))
        self.visionNoiseCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_use_vision_noise", b.get_active()))
    if self.disableAiCheckButton:
        self.disableAiCheckButton.set_active(getattr(self.__controller.world, "flag_disable_ai", False))
        self.disableAiCheckButton.connect("toggled", lambda b: setattr(self.__controller.world, "flag_disable_ai", b.get_active()))
    if self.enemyOnCheckButton:
        self.enemyOnCheckButton.set_active(getattr(self.__controller.world, "flag_enemy_on", False))
        def on_enemy_toggled(b):
            is_active = b.get_active()
            setattr(self.__controller.world, "flag_enemy_on", is_active)
            if self.__controller.launcher.is_running() and hasattr(self.__controller, 'enemy_launcher'):
                if is_active and not self.__controller.enemy_launcher.is_running():
                    sim_id = self.simuladorComboBox.get_active_id() if self.simuladorComboBox else "firasim"
                    team_color = "yellow" if self.__controller.world.team_yellow else "blue"
                    enemy_color = "blue" if team_color == "yellow" else "yellow"
                    flags = {
                        "referee": getattr(self.__controller.world, "flag_referee", False),
                        "control": getattr(self.__controller.world, "flag_control", False),
                        "debug": getattr(self.__controller.world, "flag_debug", False),
                        "ppo_ai": True,  # Enemy is always PPO
                        "enemy_ai": getattr(self.__controller.world, "flag_enemy_ai", False),
                        "record": getattr(self.__controller.world, "flag_record", False),
                        "static_entities": getattr(self.__controller.world, "flag_static_entities", False),
                        "mirror": getattr(self.__controller.world, "flag_mirror", False),
                        "use_predictor": getattr(self.__controller.world, "flag_use_predictor", False),
                        "use_kalman": getattr(self.__controller.world, "flag_use_kalman", False),
                        "disable_ai": getattr(self.__controller.world, "flag_disable_ai", False),
                        "n_robots": getattr(self.__controller.world, "flag_n_robots", "0,1,2"),
                        "force_entities": getattr(self.__controller.world, "force_entities", {}),
                    }
                    self.__controller.enemy_launcher.start(simulator_mode=sim_id, port=self.__controller.command_server.port + 2, team_color=enemy_color, flags=flags)
                elif not is_active and self.__controller.enemy_launcher.is_running():
                    self.__controller.enemy_launcher.stop()
        self.enemyOnCheckButton.connect("toggled", on_enemy_toggled)
    if self.nRobotsEntry:
        self.nRobotsEntry.set_text(getattr(self.__controller.world, "flag_n_robots", "0,1,2"))
        self.nRobotsEntry.connect("changed", lambda e: setattr(self.__controller.world, "flag_n_robots", e.get_text()))
    
    if self.simuladorComboBox:
        # Define valor inicial com base no world
        if getattr(self.__controller.world, "firasim", False):
            self.simuladorComboBox.set_active_id("firasim")
        elif getattr(self.__controller.world, "travesim", False):
            self.simuladorComboBox.set_active_id("travesim")
        elif getattr(self.__controller.world, "rsim", False):
            self.simuladorComboBox.set_active_id("rsim")
        elif getattr(self.__controller.world, "mainsystem", False):
            self.simuladorComboBox.set_active_id("mainsystem")
        else:
            self.simuladorComboBox.set_active_id("none")

    # --- INTEGRAÇÃO UNBRAIN (BOTOES ADICIONADOS EM MAIN.UI) ---
    self.startUnbrainButton = builder.get_object("startUnbrainButton")
    self.teleportFormation1Btn = builder.get_object("teleportFormation1Btn")
    self.teleportFormation2Btn = builder.get_object("teleportFormation2Btn")

    def on_start_unbrain(btn):
        if self.__controller.launcher.is_running():
            self.__controller.launcher.stop()
            if hasattr(self.__controller, 'enemy_launcher') and self.__controller.enemy_launcher.is_running():
                self.__controller.enemy_launcher.stop()
            btn.set_label("▶ Iniciar UnBrain")
        else:
            sim_id = self.simuladorComboBox.get_active_id() if self.simuladorComboBox else "firasim"
            team_color = "yellow" if self.__controller.world.team_yellow else "blue"
            
            # Coleta todas as flags do painel lateral
            flags = {
                "referee": getattr(self.__controller.world, "flag_referee", False),
                "control": getattr(self.__controller.world, "flag_control", False),
                "debug": getattr(self.__controller.world, "flag_debug", False),
                "ppo_ai": getattr(self.__controller.world, "flag_ppo_ai", False),
                "enemy_ai": getattr(self.__controller.world, "flag_enemy_ai", False),
                "record": getattr(self.__controller.world, "flag_record", False),
                "static_entities": getattr(self.__controller.world, "flag_static_entities", False),
                "mirror": getattr(self.__controller.world, "flag_mirror", False),
                "use_predictor": getattr(self.__controller.world, "flag_use_predictor", False),
                "use_kalman": getattr(self.__controller.world, "flag_use_kalman", False),
                "disable_ai": getattr(self.__controller.world, "flag_disable_ai", False),
                "n_robots": getattr(self.__controller.world, "flag_n_robots", "0,1,2"),
                "force_entities": getattr(self.__controller.world, "force_entities", {}),
            }
            
            self.__controller.launcher.start(simulator_mode=sim_id, port=self.__controller.command_server.port, team_color=team_color, flags=flags)
            
            if getattr(self.__controller.world, "flag_enemy_on", False):
                enemy_color = "blue" if team_color == "yellow" else "yellow"
                enemy_flags = flags.copy()
                enemy_flags["ppo_ai"] = True
                if hasattr(self.__controller, 'enemy_launcher'):
                    self.__controller.enemy_launcher.start(simulator_mode=sim_id, port=self.__controller.command_server.port + 2, team_color=enemy_color, flags=enemy_flags)
            
            btn.set_label("⏹ Parar UnBrain")

    if self.startUnbrainButton:
        self.startUnbrainButton.connect("clicked", on_start_unbrain)

    def on_teleport_offensive(btn):
        self.__controller.world.teleport_mode = "Offensive"

    def on_teleport_defensive(btn):
        self.__controller.world.teleport_mode = "Defensive"

    if self.teleportFormation1Btn:
        self.teleportFormation1Btn.connect("clicked", on_teleport_offensive)
    if self.teleportFormation2Btn:
        self.teleportFormation2Btn.connect("clicked", on_teleport_defensive)

    # ----------------------------------------------

    # Adiciona a pilha a view de configuração da visão de forma incondicional
    # para que possa ser ligada/desligada via o Combobox
    MainVisionView(self.__controller, self.__controller.visionSystem, self.__controller.world, mainStack)
    vision_child = mainStack.get_child_by_name("configVision")
    if vision_child:
        vision_child.set_visible(getattr(self.__controller.world, "mainsystem", False))

    DebugHLCView(self.__controller, self.__controller.world, mainStack)

    # Nova aba de Noise Sim
    from main_system.view.states.visionNoiseView import VisionNoiseView
    VisionNoiseView(self.__controller, self.__controller.world, mainStack)

    # Nova aba de Controle
    from main_system.view.states.controlView import ControlView
    ControlView(self.__controller, self.__controller.world, mainStack)

    # Nova aba de Teleporte
    from main_system.view.states.teleportView import TeleportView
    TeleportView(self.__controller, self.__controller.world, mainStack)

    # Nova aba de Treino IA
    from main_system.view.states.aiTrainingView import AITrainingView
    AITrainingView(self.__controller, self.__controller.world, mainStack)

    # Nova aba de Teste de Episódios
    from main_system.view.states.episodeTestView import EpisodeTestView
    EpisodeTestView(self.__controller, self.__controller.world, mainStack)

    # Função para o Combobox atualizar as janelas (agora fazemos isso DEPOIS que tudo foi instanciado)
    if self.simuladorComboBox:
        def on_sim_changed(combo):
            sim_id = combo.get_active_id()
            self.__controller.world.firasim = (sim_id == "firasim")
            self.__controller.world.travesim = (sim_id == "travesim")
            self.__controller.world.rsim = (sim_id == "rsim")
            self.__controller.world.mainsystem = (sim_id == "mainsystem")
            self.__controller.world.simulado = (sim_id == "simulado")

            # Atualiza aba de câmeras e visão dinamicamente
            if vision_child:
                vision_child.set_visible(self.__controller.world.mainsystem)

            # Smart Default para Kalman
            if self.kalmanFilterCheckButton:
                is_sim = sim_id in ["firasim", "travesim", "simulado", "rsim"]
                self.kalmanFilterCheckButton.set_active(not is_sim)

            # Se não estivermos em um simulador, mostra botão de câmeras
            if sim_id == "firasim" or sim_id == "travesim" or sim_id == "simulado":
                camerasBtn.set_visible(False)
            else:
                camerasBtn.set_visible(True)

        self.simuladorComboBox.connect("changed", on_sim_changed)

    # Força a aba inicial a ser a HLC
    mainStack.set_visible_child_name("configHLC")

    # Loop principal do Gtk
    Gtk.main()
