from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QSpacerItem, QSizePolicy, QLabel, QGridLayout,
)
from PySide6.QtCore import QSize, Qt, QCoreApplication
from PySide6.QtGui import QCursor, QPixmap
from core import SizePolicies, Fonts
from uuid import uuid4 as uuid
from elements import Robot

class RobotLayout(QFrame):
    def __init__(self, parent: QWidget, robot: Robot) -> None:
        super().__init__(parent)
        
        self.robot = robot
        
        self.setObjectName(f"robotInfoBox{self.robot.id}")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.setMinimumSize(QSize(350, 0))
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        self.verticalLayout_22 = QVBoxLayout(self)
        self.verticalLayout_22.setSpacing(3)
        #self.verticalLayout_22.setObjectName(f"{uuid()}_verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(3, 3, 3, 3)
        
        self.robotInfoHeader = QFrame(self)
        #self.robotInfoHeader.setObjectName(f"{uuid()}_robotInfoHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.robotInfoHeader.sizePolicy().hasHeightForWidth())
        self.robotInfoHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.robotInfoHeader.setMinimumSize(QSize(340, 0))
        self.robotInfoHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.robotInfoHeader.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_31 = QHBoxLayout(self.robotInfoHeader)
        self.horizontalLayout_31.setSpacing(0)
        #self.horizontalLayout_31.setObjectName(f"{uuid()}_horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(0, 0, 0, 0)
        
        self.robotRoleDropdown = QComboBox(self.robotInfoHeader)
        
        #self.robotRoleDropdown.setObjectName(f"{uuid()}_robotRoleDropdown")
        self.robotRoleDropdown.setFont(Fonts["font3"])
        self.robotRoleDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.robotRoleDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        
        self.robotRoleDropdown.addItem("")
        self.robotRoleDropdown.addItem("")
        self.robotRoleDropdown.addItem("")
        self.robotRoleDropdown.addItem("")

        self.horizontalLayout_31.addWidget(self.robotRoleDropdown)

        self.robotInfoSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_31.addItem(self.robotInfoSpacer)

        self.robotCommStatus = QLabel(self.robotInfoHeader)
        #self.robotCommStatus.setObjectName(f"{uuid()}_robotCommStatus")
        self.robotCommStatus.setFont(Fonts["font2"])
        self.robotCommStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_31.addWidget(self.robotCommStatus)


        self.verticalLayout_22.addWidget(self.robotInfoHeader)

        self.robotInfoValues = QFrame(self)
        #self.robotInfoValues.setObjectName(f"{uuid()}_robotInfoValues")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.robotInfoValues.sizePolicy().hasHeightForWidth())
        self.robotInfoValues.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.robotInfoValues.setMinimumSize(QSize(340, 0))
        self.robotInfoValues.setFrameShape(QFrame.Shape.NoFrame)
        self.robotInfoValues.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_32 = QHBoxLayout(self.robotInfoValues)
        self.horizontalLayout_32.setSpacing(0)
        #self.horizontalLayout_32.setObjectName(f"{uuid()}_horizontalLayout_32")
        self.horizontalLayout_32.setContentsMargins(0, 0, 0, 0)
        self.robotBox = QFrame(self.robotInfoValues)
        #self.robotBox.setObjectName(f"{uuid()}_robotBox")
        self.robotBox.setFrameShape(QFrame.Shape.NoFrame)
        self.robotBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_23 = QVBoxLayout(self.robotBox)
        self.verticalLayout_23.setSpacing(0)
        #self.verticalLayout_23.setObjectName(f"{uuid()}_verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.robotImageBox = QFrame(self.robotBox)
        #self.robotImageBox.setObjectName(f"{uuid()}_robotImageBox")
        SizePolicies["Preferred_Preferred"].setHeightForWidth(self.robotImageBox.sizePolicy().hasHeightForWidth())
        self.robotImageBox.setSizePolicy(SizePolicies["Preferred_Preferred"])
        self.robotImageBox.setFrameShape(QFrame.Shape.NoFrame)
        self.robotImageBox.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_33 = QHBoxLayout(self.robotImageBox)
        self.horizontalLayout_33.setSpacing(0)
        #self.horizontalLayout_33.setObjectName(f"{uuid()}_horizontalLayout_33")
        self.horizontalLayout_33.setContentsMargins(0, 0, 0, 0)
        self.robotImage = QLabel(self.robotImageBox)
        #self.robotImage.setObjectName(f"{uuid()}_robotImage")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.robotImage.sizePolicy().hasHeightForWidth())
        self.robotImage.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.robotImage.setMinimumSize(QSize(50, 50))
        self.robotImage.setMaximumSize(QSize(50, 50))
        self.robotImage.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.robotImage.setPixmap(QPixmap(u"assets/camisa0.png"))
        self.robotImage.setScaledContents(True)
        self.robotImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_33.addWidget(self.robotImage)


        self.verticalLayout_23.addWidget(self.robotImageBox)

        self.robotBoxSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_23.addItem(self.robotBoxSpacer)

        self.robotCharge = QLabel(self.robotBox)
        #self.robotCharge.setObjectName(f"{uuid()}_robotCharge")
        self.robotCharge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.robotCharge)


        self.horizontalLayout_32.addWidget(self.robotBox)

        self.robotInfo = QGridLayout()
        #self.robotInfo.setObjectName(f"{uuid()}_robotInfo")
        self.robotIdLabel = QLabel(self.robotInfoValues)
        #self.robotIdLabel.setObjectName(f"{uuid()}_robotIdLabel")
        self.robotIdLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotIdLabel, 0, 0, 1, 1)

        self.robotIdValue = QLabel(self.robotInfoValues)
        #self.robotIdValue.setObjectName(f"{uuid()}_robotIdValue")
        self.robotIdValue.setFont(Fonts["font3"])
        self.robotIdValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotIdValue, 0, 1, 1, 1)

        self.robotPosLabel = QLabel(self.robotInfoValues)
        #self.robotPosLabel.setObjectName(f"{uuid()}_robotPosLabel")
        self.robotPosLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotPosLabel, 1, 0, 1, 1)

        self.robotPosValue = QLabel(self.robotInfoValues)
        #self.robotPosValue.setObjectName(f"{uuid()}_robotPosValue")
        self.robotPosValue.setFont(Fonts["font3"])
        self.robotPosValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotPosValue, 1, 1, 1, 1)

        self.robotAngleLabel = QLabel(self.robotInfoValues)
        #self.robotAngleLabel.setObjectName(f"{uuid()}_robotAngleLabel")
        self.robotAngleLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotAngleLabel, 2, 0, 1, 1)

        self.robotAngleValue = QLabel(self.robotInfoValues)
        #self.robotAngleValue.setObjectName(f"{uuid()}_robotAngleValue")
        self.robotAngleValue.setFont(Fonts["font3"])
        self.robotAngleValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotAngleValue, 2, 1, 1, 1)

        self.speedReadLabel = QLabel(self.robotInfoValues)
        #self.speedReadLabel.setObjectName(f"{uuid()}_speedReadLabel")
        self.speedReadLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.speedReadLabel, 3, 0, 1, 1)

        self.speedReadValue = QLabel(self.robotInfoValues)
        #self.speedReadValue.setObjectName(f"{uuid()}_speedReadValue")
        self.speedReadValue.setFont(Fonts["font3"])
        self.speedReadValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.speedReadValue, 3, 1, 1, 1)

        self.speedSentLabel = QLabel(self.robotInfoValues)
        #self.speedSentLabel.setObjectName(f"{uuid()}_speedSentLabel")
        self.speedSentLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.speedSentLabel, 4, 0, 1, 1)

        self.speedSentValue = QLabel(self.robotInfoValues)
        #self.speedSentValue.setObjectName(f"{uuid()}_speedSentValue")
        self.speedSentValue.setFont(Fonts["font3"])
        self.speedSentValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.speedSentValue, 4, 1, 1, 1)

        self.robotFreqLabel = QLabel(self.robotInfoValues)
        #self.robotFreqLabel.setObjectName(f"{uuid()}_robotFreqLabel")
        self.robotFreqLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotFreqLabel, 5, 0, 1, 1)

        self.robotFreqValue = QLabel(self.robotInfoValues)
        #self.robotFreqValue.setObjectName(f"{uuid()}_robotFreqValue")
        self.robotFreqValue.setFont(Fonts["font3"])
        self.robotFreqValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotFreqValue, 5, 1, 1, 1)


        self.horizontalLayout_32.addLayout(self.robotInfo)


        self.verticalLayout_22.addWidget(self.robotInfoValues)

    def retranslateUi(self) -> None:
        self.robotRoleDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.robotRoleDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.robotRoleDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.robotRoleDropdown.setItemText(3, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.robotRoleDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.robotCommStatus.setText(QCoreApplication.translate("MainWindow", f"<html><head/><body><p>Comunica\u00e7\u00e3o: <span style=\" color:#3e7239;\">{self.robot.status}</span></p></body></html>", None))
        self.robotCharge.setText(QCoreApplication.translate("MainWindow", f"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Bateria</span><span style=\" font-size:8pt;\">: {self.robot.battery}%</span></p></body></html>", None))
        self.robotIdLabel.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        self.robotIdValue.setText(QCoreApplication.translate("MainWindow", self.robot.id, None))
        self.robotPosLabel.setText(QCoreApplication.translate("MainWindow", u"Posi\u00e7\u00e3o", None))
        self.robotPosValue.setText(QCoreApplication.translate("MainWindow", f"x: {self.robot.x} m y: {self.robot.y} m", None))
        self.robotAngleLabel.setText(QCoreApplication.translate("MainWindow", u"Orienta\u00e7\u00e3o", None))
        self.robotAngleValue.setText(QCoreApplication.translate("MainWindow", u"th: {self.robot.orientation} graus", None))
        self.speedReadLabel.setText(QCoreApplication.translate("MainWindow", u"Velocidade lida", None))
        self.speedReadValue.setText(QCoreApplication.translate("MainWindow", f"v: {self.robot.linearSpeed} m/s w: {self.robot.angularSpeed} rad/s", None))
        self.speedSentLabel.setText(QCoreApplication.translate("MainWindow", u"Velocidade enviada", None))
        self.speedSentValue.setText(QCoreApplication.translate("MainWindow", f"v: {self.robot.linearSpeed} m/s w: {self.robot.angularSpeed} rad/s", None))
        self.robotFreqLabel.setText(QCoreApplication.translate("MainWindow", u"Frequ\u00eancia de envio", None))
        self.robotFreqValue.setText(QCoreApplication.translate("MainWindow", f"{self.robot.frequency} MHz", None))