from gi.repository import Gtk, GLib
from pkg_resources import resource_filename
from main_system.view.tools.stackSelector import StackSelector
from main_system.helpers import LoopThread
from main_system.view.strategy.highLevelRenderer import HighLevelRenderer
from tools.teleport_math import calculate_teleport_positions, calculate_ball_teleport
import time

class TeleportView(LoopThread, StackSelector):
    def __init__(self, controller, world, stack):
        self.__controller = controller
        self.__world = world
        
        if not hasattr(self.__world, "teleport_mode"):
            self.__world.teleport_mode = None
        if not hasattr(self.__world, "teleport_config"):
            self.__world.teleport_config = {}

        LoopThread.__init__(self, self.view_worker)
        StackSelector.__init__(self, stack, "configTeleport", "Teleporte")

    def ui(self):
        # We need to build the UI from the Glade file
        builder = Gtk.Builder.new_from_file(resource_filename(__name__, "teleportView.ui"))
        mainBox = builder.get_object("TeleportBox")
        
        renderContainer = builder.get_object("TeleportRender")
        self.__renderer = HighLevelRenderer(self.__world, robotsGetter=self.robotsGetter, ballGetter=self.ballGetter)
        renderContainer.add(self.__renderer)

        self.foulTypeCombo = builder.get_object("foulTypeCombo")
        self.kickerTeamCombo = builder.get_object("kickerTeamCombo")
        self.quadrantCombo = builder.get_object("quadrantCombo")

        self.btnDriveAlly = builder.get_object("btnDriveAlly")
        self.btnDriveEnemy = builder.get_object("btnDriveEnemy")
        self.btnPlaceBall = builder.get_object("btnPlaceBall")
        self.btnStopDrive = builder.get_object("btnStopDrive")

        self.btnDriveAlly.connect("clicked", self.on_drive_ally)
        self.btnDriveEnemy.connect("clicked", self.on_drive_enemy)
        self.btnPlaceBall.connect("clicked", self.on_place_ball)
        self.btnStopDrive.connect("clicked", self.on_stop_drive)

        paned = builder.get_object("paned1")
        if paned:
            paned.set_position(700)

        return mainBox

    def robotsGetter(self):
        return [self.__world.robots[i] for i in range(self.__world.n_robots)]

    def ballGetter(self):
        return self.__world.ball

    def view_worker(self):
        time.sleep(0.05)

    def _get_placements(self, for_ally=True):
        foul_name = self.foulTypeCombo.get_active_id()
        kicker_id = self.kickerTeamCombo.get_active_id()
        quadrant = int(self.quadrantCombo.get_active_id())
        
        # O time aliado comete/bate a falta se "ALLY" foi selecionado?
        ally_is_kicker = (kicker_id == "ALLY")
        is_kicker = ally_is_kicker if for_ally else not ally_is_kicker

        # Determina o lado baseado na cor e constante
        is_left_side = self.__world.fieldSide == -1  # -1 = left, 1 = right

        # Quantidade de robôs para teleportar (se for enemy não sabemos, mas assumimos que é igual ao nosso n_robots_total para formar a geometria do VSSReferee)
        n_rob = 3
        
        placements = calculate_teleport_positions(foul_name, is_kicker, is_left_side, n_rob, quadrant)
        return placements

    def on_drive_ally(self, widget):
        placements = self._get_placements(for_ally=True)
        def trigger_teleport():
            config = []
            # Garantir tamanho igual a 3 (máximo de robôs) mesmo que tenha lacunas
            for i in range(3):
                if i in placements:
                    config.append(placements[i])
                else:
                    config.append(None)
            self.__world.teleport_config["FOUL_ALLY"] = config
            self.__world.teleport_mode = "FOUL_ALLY"
        self.__controller.addEvent(trigger_teleport)

    def on_drive_enemy(self, widget):
        # Inimigo não tem loop de controle no UnBrain, entao o "Drive" deles tem que ser via Simulador (setPos)
        # Se for no MainVision, os robôs reais inimigos nao podem ser movidos pelo nosso UnBrain de qlq forma.
        placements = self._get_placements(for_ally=False)
        def trigger_enemy_teleport():
            # A gente só pode teleportar no simulador
            if self.__world.firasim or self.__world.travesim:
                # O IPC loop lida com isso. Vamos adicionar uma flag no loop.py para ler isso.
                self.__world.teleport_config["FOUL_ENEMY"] = placements
                self.__world.teleport_mode_enemy = "FOUL_ENEMY"
        self.__controller.addEvent(trigger_enemy_teleport)

    def on_place_ball(self, widget):
        foul_name = self.foulTypeCombo.get_active_id()
        quadrant = int(self.quadrantCombo.get_active_id())
        is_left_side = self.__world.fieldSide == -1
        
        bx, by = calculate_ball_teleport(foul_name, quadrant, is_left_side, self.__world.field_x_length, self.__world.field_y_length)
        def trigger_ball_teleport():
            if self.__world.firasim or self.__world.travesim:
                self.__world.teleport_ball_pos = (bx, by)
        self.__controller.addEvent(trigger_ball_teleport)

    def on_stop_drive(self, widget):
        def stop_teleport():
            self.__world.teleport_mode = None
            self.__world.teleport_mode_enemy = None
        self.__controller.addEvent(stop_teleport)

    def on_select(self, widget):
        self.start()
        self.__renderer.start()

    def on_deselect(self, widget):
        self.__renderer.stop()
        self.stop()
