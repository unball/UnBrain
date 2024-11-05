# This Python file uses the following encoding: utf-8
import sys
import argparse
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt, QPointF, QSize, QTimer
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase, QFont
import signal

sys.path.append("../src")
from loop import Loop

import threading
from mainWindowUi import MainWindowUi
from customClasses.elements import *

NROBOTS = 3
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.robots = [Robot(id = str(n)) for n in range(NROBOTS)]

        newFontId = QFontDatabase.addApplicationFont(u"./assets/fonts/Bungee.ttf")
        bungeeFont = QFontDatabase.applicationFontFamilies(newFontId)[0]

        self.ui = MainWindowUi()
        self.ui.setupUi(self, self.robots)
        
        self.ui.header.appName.setStyleSheet(f"font-family: {bungeeFont}; font-size: 20px;")
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.arrowLeft = QPixmap(u"assets/icons/arrow_left.svg")
        self.arrowRight = QPixmap(u"assets/icons/arrow_right.svg")
        
        self.yellowFlagIcon = QIcon()
        self.yellowFlagIcon.addFile(u"assets/icons/yellow_flag.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.blueFlagIcon = QIcon()
        self.blueFlagIcon.addFile(u"assets/icons/blue_flag.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.closedEyeIcon = QIcon()
        self.closedEyeIcon.addFile(u"assets/icons/mdi_eye-off.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.eyeIcon = QIcon()
        self.eyeIcon.addFile(u"assets/icons/mdi_eye.svg", QSize(), QIcon.Normal, QIcon.Off)

        self.unbrainLoopRunning = False
        self.unbrainThread = None
        
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.updateLoopInfos)
        self.updateTimer.start(500)

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPosition()
    
    def mouseMoveEvent(self, event):
        delta = QPointF(event.globalPosition() - self.oldPosition)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        
        self.oldPosition = event.globalPosition()
    
    def showCropField(self):
        if self.ui.showCropFieldSwitch.isChecked():
            self.ui.visionCropFrame.showCroppedImage()
        
        else: 
            self.ui.visionCropFrame.clearFrame()
    
    def showCropInnerField(self):
        if self.ui.showInnerCropFieldSwitch.isChecked():
            self.ui.visionInnerCropFrame.showCroppedImage()
        
        else: 
            self.ui.visionCropFrame.clearFrame()
    
    def changeTeamColor(self):
        if self.ui.switchTeamColorButton.isChecked():
            self.ui.switchTeamColorButton.setIcon(self.yellowFlagIcon)
            self.ui.switchTeamColorButton.setIconSize(QSize(24, 22))
            self.ui.myTeamColorLabel.setText("Amarelo")
        
        else:
            self.ui.switchTeamColorButton.setIcon(self.blueFlagIcon)
            self.ui.switchTeamColorButton.setIconSize(QSize(24, 22))
            self.ui.myTeamColorLabel.setText("Azul")
   
    def changeFieldSideArrow(self):
        if self.ui.myTeamSideSwitch.isChecked():
            self.ui.fieldSideDirection.setPixmap(self.arrowLeft)
            self.ui.rightTeamSideLabel.setText("Lado aliado")
            self.ui.leftTeamSideLabel.setText("Lado inimigo")
            self.ui.myTeamSideLabel.setText("Direito")
            
        else:
            self.ui.fieldSideDirection.setPixmap(self.arrowRight)
            self.ui.rightTeamSideLabel.setText("Lado inimigo")
            self.ui.leftTeamSideLabel.setText("Lado aliado")
            self.ui.myTeamSideLabel.setText("Esquerdo")
    
    def enableViewUvf(self):
        if self.ui.viewUvfButton.isChecked():
            self.ui.viewUvfButton.setIcon(self.closedEyeIcon)
        else:
            self.ui.viewUvfButton.setIcon(self.eyeIcon)
    
    def updatePosSourceLabel(self):
        if self.ui.posSourceSwitch.isChecked():
            self.ui.posSourceLabel.setText("Posicionamento do juiz virtual")
        else:
            self.ui.posSourceLabel.setText("Posicionamento do juiz manual")

    def executeUnbrain(self):
        if not self.unbrainLoopRunning:
            self.robot_inds = [int(i) for i in (self.ui.nrobotsLineEdit.text()).split(",")] if self.ui.nrobotsLineEdit.text() else [0,1,2]
            
            # TODO: corrigir self.robots
            self.robots = [Robot(id=str(n)) for n in self.robot_inds] #implementacao provisoria de robots
            self.ball = Ball() #implementacao provisoria de ball
            # TODO: precisa refazer esses dois (via objeto world)

            print("Unbrain rodando")
            teamYellow = True if self.ui.myTeamColorLabel.text() == "Amarelo" else False
            firasim = self.ui.visionOptionsDropdown.currentIndex() == 1
            mainVision = self.ui.visionOptionsDropdown.currentIndex() == 0
            simulado = True if self.ui.gameOptionsDropdown.currentIndex() == 1 else False
            robocinVision = self.ui.visionOptionsDropdown.currentIndex() == 2
            staticEntities = self.ui.staticEntitiesRadio.isChecked()
            nRobots = self.robot_inds
            mirror = self.ui.myTeamSideSwitch.isChecked()

            self.unbrainLoopRunning = True
            self.unbrainLoop = Loop(team_yellow=teamYellow, firasim=firasim, mainvision=False, simulado=simulado, static_entities=staticEntities, mirror=mirror, n_robots=nRobots, vssvision=robocinVision)
            self.unbrainThread = threading.Thread(target=self.unbrainLoop.run)
            self.unbrainThread.daemon = True
            self.unbrainThread.start()
            self.ui.execButton.setChecked(True)

            signal.signal(signal.SIGINT, self.unbrainLoop.handle_SIGINT)

        else:
            print("Unbrain pausado")
            self.unbrainLoop.handle_SIGINT(None, None, shut_down=False)
            self.unbrainLoopRunning = False
            self.ui.execButton.setChecked(False)

    def stopUnbrain(self):
        print("Unbrain parado")
        self.unbrainLoop.handle_SIGINT(None, None, shut_down=False)
        self.unbrainLoop = None
        self.unbrainLoopRunning = False

    def updateLoopInfos(self):
        if self.unbrainLoop is not None:
            ball = self.unbrainLoop.world.ball
            robots = self.unbrainLoop.world.team
            
            self.ui.ballPosValue.setText(f"x: {ball.pos[0]:.1f} y: {ball.pos[1]:.1f}")
            self.ui.ballSpeedValue.setText(f"{ball.velmod:.1f} m/s")
            for ind in self.robot_inds:
                robots[ind].status = "ON" if robots[ind].on else "OFF"
                self.ui.robotInfoBoxArray[ind].robotRole.setText(robots[ind].entity.__class__.__name__)
                self.ui.robotInfoBoxArray[ind].robotPosValue.setText(f"x: {robots[ind].x:.1f} y: {robots[ind].y:.1f}")
                self.ui.robotInfoBoxArray[ind].robotAngleValue.setText(f"th: {robots[ind].th:.1f} graus")
                self.ui.robotInfoBoxArray[ind].robotCommStatus.setText(f"<html><head/><body><p>Comunica\u00e7\u00e3o: <span style=\" color:#3e7239;\">{robots[ind].status}</span></p></body></html>")
                self.ui.robotInfoBoxArray[ind].speedReadValue.setText(f"v: {robots[ind].velmod:.1f} w: {robots[ind].w:.1f}")
                self.ui.robotInfoBoxArray[ind].speedSentValue.setText(f"v: {robots[ind].lastControlLinVel:.1f} w: {robots[ind].lastControlAngVel:.1f}")
            #self.ui.ballAccValue.setText(f"{ball.accmod:.1f}")
            # self.ui.ballAccValue.setText(f"{ball.accmod:.1f} m/s²")   accmod não implementado
        else:
            for ind in self.robot_inds:
                self.ui.robotInfoBoxArray[ind].robotCommStatus.setText(f"<html><head/><body><p>Comunica\u00e7\u00e3o: <span style=\" color:#3e7239;\">OFF</span></p></body></html>")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(prog="IGGLU - VSSS")
    # parser.add_argument("--nrobots", "-n", type=int, default=3)
    # args = parser.parse_args()
    # NROBOTS = args.nrobots
    
    app = QApplication(sys.argv)
    
    widget = MainWindow()
    widget.show()
    
    sys.exit(app.exec())
