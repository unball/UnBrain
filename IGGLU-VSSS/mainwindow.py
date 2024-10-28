# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase, QFont
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py

from ui_form import Ui_MainWindow

sys.path.append("../src")
from loop import Loop

import threading

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        newFontId = QFontDatabase.addApplicationFont(u"./assets/fonts/Bungee.ttf")
        bungeeFont = QFontDatabase.applicationFontFamilies(newFontId)[0]

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
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


        self.unbrainLoop = None
        self.unbrainThread = None
        
        
    def mousePressEvent(self, event):
        self.oldPosition = event.globalPosition()
    
    def mouseMoveEvent(self, event):
        delta = QPointF(event.globalPosition() - self.oldPosition)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        
        self.oldPosition = event.globalPosition()
    
    def showCropField(self):
        if self.ui.showCropFieldSwitch.value() == 1:
            self.ui.visionCropFrame.showCroppedImage()
        
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
        if self.ui.myTeamSideSwitch.value() == 1:
            self.ui.fieldSideDirection.setPixmap(self.arrowLeft)
            self.ui.rightTeamSideLabel.setText("Lado aliado")
            self.ui.leftTeamSideLabel.setText("Lado inimigo")
            self.ui.myTeamSideLabel.setText("Direito")
            
        if self.ui.myTeamSideSwitch.value() == 0:
            self.ui.fieldSideDirection.setPixmap(self.arrowRight)
            self.ui.rightTeamSideLabel.setText("Lado inimigo")
            self.ui.leftTeamSideLabel.setText("Lado aliado")
            self.ui.myTeamSideLabel.setText("Esquerdo")
    
    def enableViewUvf(self):
        if self.ui.viewUvfButton.isChecked():
            self.ui.viewUvfButton.setIcon(self.closedEyeIcon)
        else:
            self.ui.viewUvfButton.setIcon(self.eyeIcon)

    def executeUnbrain(self):
        if self.unbrainLoop is None:
            print("Unbrain rodando")
            teamYellow = True if self.ui.myTeamColorLabel.text() == "Amarelo" else False
            firasim = self.ui.visionOptionsDropdown.currentIndex() == 1
            mainVision = self.ui.visionOptionsDropdown.currentIndex() == 0
            simulado = True if self.ui.gameOptionsDropdown.currentIndex() == 1 else False
            robocinVision = self.ui.visionOptionsDropdown.currentIndex() == 2
            staticEntities = self.ui.staticEntitiesRadio.isChecked()
            numRobots = [0,1,2]
            mirror = self.ui.myTeamSideSwitch.value() == 1


            self.unbrainLoop = Loop(team_yellow=teamYellow, firasim=firasim, mainvision=mainVision, simulado=simulado, static_entities=staticEntities, mirror=mirror, n_robots=numRobots, vssvision=robocinVision)
            self.unbrainThread = threading.Thread(target=self.unbrainLoop.run)
            self.unbrainThread.daemon = True
            self.unbrainThread.start()

            
        else:
            self.unbrainLoop.handle_SIGINT(None, None, shut_down=False)
            self.unbrainLoop = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
