from gi.repository import Gtk, GLib, GdkPixbuf
from pkg_resources import resource_filename
from main_system.view.tools.stackSelector import StackSelector
from main_system.view.strategy.highLevelRenderer import HighLevelRenderer
from main_system.helpers import LoopThread
import os
import time

HEATMAP_PATH = os.path.join(os.getcwd(), "data", "heatmap_result.png")

class EpisodeTestView(LoopThread, StackSelector):
    """Classe que gerencia a view de testes episódicos na UI do GTK"""

    def __init__(self, controller, world, stack):
        self.__controller = controller
        self.__world = world
        self.is_testing = False
        self._test_acked = False  # True depois que UnBrain confirmou episode_testing_running=True
        self._heatmap_mtime = 0.0  # mtime do último heatmap exibido
        LoopThread.__init__(self, self.view_worker)
        StackSelector.__init__(self, stack, "configEpisodeTest", "Episode Test")

    def ui(self):
        builder = Gtk.Builder.new_from_file(resource_filename(__name__, "episodeTestView.ui"))

        mainBox          = builder.get_object("EpisodeTestBox")
        renderContainer  = builder.get_object("EpisodeTestRender")
        self.btnStartTest   = builder.get_object("btnStartTest")
        self.btnShowHeatmap = builder.get_object("btnShowHeatmap")
        self.spinSeed       = builder.get_object("spinSeed")
        self.spinMaxSteps   = builder.get_object("spinMaxSteps")
        self.spinNEpisodes  = builder.get_object("spinNEpisodes")
        self.comboTestType  = builder.get_object("comboTestType")
        self.chk3v3         = builder.get_object("chk3v3")
        self.btn1v1         = builder.get_object("btn1v1")
        self.comboEnemyEntity = builder.get_object("comboEnemyEntity")
        self.chkFixedPositions = builder.get_object("chkFixedPositions")
        self.lblStatus      = builder.get_object("lblStatus")
        self.lblEpisodeSeed = builder.get_object("lblEpisodeSeed")

        self.comboTestType.set_active_id("heatmap_team")
        self.comboEnemyEntity.set_active_id("goalkeeper")

        self.btnStartTest.connect("toggled", self.on_start_toggled)
        self.btnShowHeatmap.connect("clicked", self.on_show_heatmap)

        self.__renderer = HighLevelRenderer(
            self.__world,
            robotsGetter=self.robotsGetter,
            ballGetter=self.ballGetter,
            on_click=None,
            on_scroll=None,
        )
        renderContainer.add(self.__renderer)
        return mainBox

    def on_start_toggled(self, widget):
        self.is_testing = widget.get_active()
        seed       = int(self.spinSeed.get_value())
        max_steps  = int(self.spinMaxSteps.get_value())
        n_episodes = int(self.spinNEpisodes.get_value())
        test_type  = self.comboTestType.get_active_id() or "heatmap_team"

        # Modo 1v1 controlado tem precedência sobre o checkbox 3v3 passivo:
        # liga 1 inimigo controlado pela entidade escolhida.
        is_1v1 = self.btn1v1.get_active()
        if is_1v1:
            n_enemies = 1
            enemy_entity = self.comboEnemyEntity.get_active_id() or "goalkeeper"
        else:
            n_enemies = 3 if self.chk3v3.get_active() else 0
            enemy_entity = ""  # inimigos passivos (ou nenhum)
            
        is_fixed = self.chkFixedPositions.get_active()

        if self.is_testing:
            self._test_acked = False
            GLib.idle_add(self.btnShowHeatmap.set_sensitive, False)
            self.lblStatus.set_text("Status: Rodando Teste...")
            self.lblEpisodeSeed.set_text(f"Seed Atual: {seed}")
            self.set_test_flags(True, seed, max_steps, n_episodes, test_type, n_enemies, enemy_entity, is_fixed)
        else:
            self._test_acked = False
            self.lblStatus.set_text("Status: Parado")
            self.set_test_flags(False, 0, 0, 0, "", 0, "", False)

    def set_test_flags(self, is_running, seed, max_steps, n_episodes, test_type, n_enemies=0, enemy_entity="", is_fixed=True):
        def send_flags():
            self.__world.flag_episode_test_run        = is_running
            self.__world.flag_episode_test_seed       = seed
            self.__world.flag_episode_test_max_steps  = max_steps
            self.__world.flag_episode_test_n_episodes = n_episodes
            self.__world.flag_episode_test_type       = test_type
            self.__world.flag_episode_test_n_enemies  = n_enemies
            self.__world.flag_episode_test_enemy_entity = enemy_entity
            self.__world.flag_episode_test_is_fixed   = is_fixed
        self.__controller.addEvent(send_flags)

    def view_worker(self):
        # Só auto-cancela DEPOIS que o UnBrain confirmou via IPC (evita race condition
        # no primeiro ciclo onde episode_testing_running ainda é False).
        if hasattr(self.__world, "episode_testing_running"):
            if self.__world.episode_testing_running:
                self._test_acked = True
            if self.is_testing and self._test_acked and not self.__world.episode_testing_running:
                GLib.idle_add(self.btnStartTest.set_active, False)
                self._check_heatmap_ready()

        time.sleep(0.05)

    def _check_heatmap_ready(self):
        """Habilita o botão de heatmap se o arquivo foi (re)gerado após o último teste."""
        try:
            mtime = os.path.getmtime(HEATMAP_PATH)
            if mtime > self._heatmap_mtime:
                self._heatmap_mtime = mtime
                GLib.idle_add(self.btnShowHeatmap.set_sensitive, True)
        except OSError:
            pass

    def on_show_heatmap(self, widget):
        if not os.path.exists(HEATMAP_PATH):
            return
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(HEATMAP_PATH)
        except Exception:
            return

        dialog = Gtk.Dialog(title="Heatmap — Resultado", flags=0)
        dialog.set_default_size(pixbuf.get_width(), pixbuf.get_height())
        dialog.add_button("Fechar", Gtk.ResponseType.CLOSE)

        img = Gtk.Image.new_from_pixbuf(pixbuf)
        dialog.get_content_area().pack_start(img, True, True, 0)
        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def ballGetter(self):
        return self.__world.ball

    def robotsGetter(self):
        return [self.__world.robots[i] for i in range(self.__world.n_robots)]

    def on_select(self, widget):
        self.__renderer.start()
        self.start()

    def on_deselect(self, widget):
        self.__renderer.stop()
        self.stop()
