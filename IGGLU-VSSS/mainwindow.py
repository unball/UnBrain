# This Python file uses the following encoding: utf-8
import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt, QPointF, QSize
from PySide6.QtGui import QPixmap, QIcon
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py

from ui_form import Ui_MainWindow
from pyqt5Custom import ToggleSwitch

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.arrowLeft = QPixmap(u"assets/icons/arrow_left.svg")
        self.arrowRight = QPixmap(u"assets/icons/arrow_right.svg")
        
        self.yellowFlagIcon = QIcon()
        self.yellowFlagIcon.addFile(u"assets/icons/yellow_flag.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.blueFlagIcon = QIcon()
        self.blueFlagIcon.addFile(u"assets/icons/blue_flag.svg", QSize(), QIcon.Normal, QIcon.Off)
        
        
    def mousePressEvent(self, event):
        self.oldPosition = event.globalPosition()
    
    def mouseMoveEvent(self, event):
        delta = QPointF(event.globalPosition() - self.oldPosition)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        
        self.oldPosition = event.globalPosition()
    

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
