# This Python file uses the following encoding: utf-8
import sys
import argparse
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtGui import QPixmap, QIcon, QFontDatabase, QFont

from mainWindowUi import MainWindowUi
from customClasses.elements import *

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.robots = [Robot(id=str(n)) for n in range(NROBOTS)]
        
        self.ball = Ball()
        
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="IGGLU - VSSS")
    parser.add_argument("--nrobots", "-n", type=int, default=3)
    args = parser.parse_args()
    NROBOTS = args.nrobots
    
    app = QApplication(sys.argv)
    
    widget = MainWindow()
    widget.show()
    
    sys.exit(app.exec())
