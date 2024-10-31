from PySide6.QtWidgets import (
    QFrame, QWidget, QVBoxLayout, QHBoxLayout,
    QSpacerItem, QSizePolicy, QLabel, QGridLayout, 
    QPushButton
)
from PySide6.QtCore import (
    QSize, Qt, QPointF, QRect, Signal, Slot
)
from PySide6.QtGui import (
    QCursor, QPixmap, QFont, QIcon, QImage, QPen,
    QPainter
)

from customClasses.core import *
from customClasses.elements import *
from customClasses.vision import *

import numpy as np
import cv2 as cv

NROBOTS = 3

class QHeader(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setObjectName(u"header")
        self.setCursor(QCursor(Qt.SizeAllCursor))

        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(SizePolicies["Expanding_Preferred"])

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 0, 5, 0)

        self.appTitle = QHBoxLayout()
        self.appTitle.setSpacing(3)
        self.appTitle.setObjectName(u"appTitle")

        self.appLogo = QLabel(self)
        self.appLogo.setObjectName(u"appLogo")

        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.appLogo.sizePolicy().hasHeightForWidth())
        self.appLogo.setSizePolicy(SizePolicies["Fixed_Fixed"])

        self.appLogo.setPixmap(QPixmap(u"assets/icons/UnBall_Logo_Preto.svg"))
        self.appLogo.setScaledContents(True)

        self.appTitle.addWidget(self.appLogo)

        self.appName = QLabel(self)
        self.appName.setObjectName(u"appName")

        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.appName.sizePolicy().hasHeightForWidth())
        self.appName.setSizePolicy(SizePolicies["Fixed_Fixed"])

        font = QFont()
        font.setFamilies([u"Roboto"])
        font.setPointSize(18)

        self.appName.setFont(font)
        self.appName.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.appTitle.addWidget(self.appName)

        self.appHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.appTitle.addItem(self.appHeaderSpacer)

        self.horizontalLayout.addLayout(self.appTitle)

        self.appControls = QHBoxLayout()
        self.appControls.setSpacing(0)
        self.appControls.setObjectName(u"appControls")

        self.minButton = QPushButton(self)
        self.minButton.setObjectName(u"minButton")
        self.minButton.setCursor(QCursor(Qt.PointingHandCursor))

        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.minButton.sizePolicy().hasHeightForWidth())
        self.minButton.setSizePolicy(SizePolicies["Fixed_Fixed"])

        minIcon = QIcon()
        minIcon.addFile(u"assets/icons/min.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.minButton.setIcon(minIcon)
        self.minButton.setIconSize(QSize(25, 6))
        self.minButton.setFlat(True)

        self.appControls.addWidget(self.minButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.maxButton = QPushButton(self)
        self.maxButton.setObjectName(u"maxButton")
        self.maxButton.setCursor(QCursor(Qt.PointingHandCursor))

        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.maxButton.sizePolicy().hasHeightForWidth())
        self.maxButton.setSizePolicy(SizePolicies["Fixed_Fixed"])

        maxIcon = QIcon()
        maxIcon.addFile(u"assets/icons/max.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.maxButton.setIcon(maxIcon)
        self.maxButton.setIconSize(QSize(25, 22))
        self.maxButton.setCheckable(True)
        self.maxButton.setFlat(True)

        self.appControls.addWidget(self.maxButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.closeButton = QPushButton(self)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setCursor(QCursor(Qt.PointingHandCursor))

        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.closeButton.sizePolicy().hasHeightForWidth())
        self.closeButton.setSizePolicy(SizePolicies["Fixed_Fixed"])

        closeIcon = QIcon()
        closeIcon.addFile(u"assets/icons/close.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.closeButton.setIcon(closeIcon)
        self.closeButton.setIconSize(QSize(25, 22))
        self.closeButton.setFlat(True)

        self.appControls.addWidget(self.closeButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.horizontalLayout.addLayout(self.appControls)

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
        self.verticalLayout_22.setContentsMargins(3, 3, 3, 3)
        
        self.robotInfoHeader = QFrame(self)
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.robotInfoHeader.sizePolicy().hasHeightForWidth())
        self.robotInfoHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.robotInfoHeader.setMinimumSize(QSize(340, 0))
        self.robotInfoHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.robotInfoHeader.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_31 = QHBoxLayout(self.robotInfoHeader)
        self.horizontalLayout_31.setSpacing(0)
        self.horizontalLayout_31.setContentsMargins(0, 0, 0, 0)
        
        self.robotRole = QLabel(self.robotInfoHeader)
        self.robotRole.setFont(Fonts["font3"])

        self.horizontalLayout_31.addWidget(self.robotRole)

        self.robotInfoSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_31.addItem(self.robotInfoSpacer)

        self.robotCommStatus = QLabel(self.robotInfoHeader)
        #self.robotCommStatus.setObjectName(f"{uuid()}_robotCommStatus")
        self.robotCommStatus.setFont(Fonts["font2"])
        self.robotCommStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_31.addWidget(self.robotCommStatus)


        self.verticalLayout_22.addWidget(self.robotInfoHeader)

        self.robotInfoValues = QFrame(self)
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.robotInfoValues.sizePolicy().hasHeightForWidth())
        self.robotInfoValues.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.robotInfoValues.setMinimumSize(QSize(340, 0))
        self.robotInfoValues.setFrameShape(QFrame.Shape.NoFrame)
        self.robotInfoValues.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_32 = QHBoxLayout(self.robotInfoValues)
        self.horizontalLayout_32.setSpacing(0)
        self.horizontalLayout_32.setContentsMargins(0, 0, 0, 0)
        
        self.robotBox = QFrame(self.robotInfoValues)
        self.robotBox.setFrameShape(QFrame.Shape.NoFrame)
        self.robotBox.setFrameShadow(QFrame.Shadow.Raised)
        
        self.verticalLayout_23 = QVBoxLayout(self.robotBox)
        self.verticalLayout_23.setSpacing(0)
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        
        self.robotImageBox = QFrame(self.robotBox)
        
        SizePolicies["Preferred_Preferred"].setHeightForWidth(self.robotImageBox.sizePolicy().hasHeightForWidth())
        self.robotImageBox.setSizePolicy(SizePolicies["Preferred_Preferred"])
        
        self.robotImageBox.setFrameShape(QFrame.Shape.NoFrame)
        self.robotImageBox.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_33 = QHBoxLayout(self.robotImageBox)
        self.horizontalLayout_33.setSpacing(0)
        self.horizontalLayout_33.setContentsMargins(0, 0, 0, 0)
        
        self.robotImage = QLabel(self.robotImageBox)
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.robotImage.sizePolicy().hasHeightForWidth())
        
        self.robotImage.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.robotImage.setMinimumSize(QSize(50, 50))
        self.robotImage.setMaximumSize(QSize(50, 50))
        self.robotImage.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.robotImage.setPixmap(QPixmap(f"assets/camisa{self.robot.id}.png"))
        self.robotImage.setScaledContents(True)
        self.robotImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_33.addWidget(self.robotImage)

        self.verticalLayout_23.addWidget(self.robotImageBox)

        self.robotBoxSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_23.addItem(self.robotBoxSpacer)

        self.robotCharge = QLabel(self.robotBox)
        self.robotCharge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_23.addWidget(self.robotCharge)


        self.horizontalLayout_32.addWidget(self.robotBox)

        self.robotInfo = QGridLayout()
        self.robotIdLabel = QLabel(self.robotInfoValues)
        self.robotIdLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotIdLabel, 0, 0, 1, 1)

        self.robotIdValue = QLabel(self.robotInfoValues)
        self.robotIdValue.setFont(Fonts["font3"])
        self.robotIdValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotIdValue, 0, 1, 1, 1)

        self.robotPosLabel = QLabel(self.robotInfoValues)
        self.robotPosLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotPosLabel, 1, 0, 1, 1)

        self.robotPosValue = QLabel(self.robotInfoValues)
        self.robotPosValue.setFont(Fonts["font3"])
        self.robotPosValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotPosValue, 1, 1, 1, 1)

        self.robotAngleLabel = QLabel(self.robotInfoValues)
        self.robotAngleLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotAngleLabel, 2, 0, 1, 1)

        self.robotAngleValue = QLabel(self.robotInfoValues)
        self.robotAngleValue.setFont(Fonts["font3"])
        self.robotAngleValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotAngleValue, 2, 1, 1, 1)

        self.speedReadLabel = QLabel(self.robotInfoValues)
        self.speedReadLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.speedReadLabel, 3, 0, 1, 1)

        self.speedReadValue = QLabel(self.robotInfoValues)
        self.speedReadValue.setFont(Fonts["font3"])
        self.speedReadValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.speedReadValue, 3, 1, 1, 1)

        self.speedSentLabel = QLabel(self.robotInfoValues)
        self.speedSentLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.speedSentLabel, 4, 0, 1, 1)

        self.speedSentValue = QLabel(self.robotInfoValues)
        self.speedSentValue.setFont(Fonts["font3"])
        self.speedSentValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.speedSentValue, 4, 1, 1, 1)

        self.robotFreqLabel = QLabel(self.robotInfoValues)
        self.robotFreqLabel.setFont(Fonts["font2"])

        self.robotInfo.addWidget(self.robotFreqLabel, 5, 0, 1, 1)

        self.robotFreqValue = QLabel(self.robotInfoValues)
        self.robotFreqValue.setFont(Fonts["font3"])
        self.robotFreqValue.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.robotInfo.addWidget(self.robotFreqValue, 5, 1, 1, 1)


        self.horizontalLayout_32.addLayout(self.robotInfo)


        self.verticalLayout_22.addWidget(self.robotInfoValues)

    def retranslateUi(self) -> None:
        self.robotRole.setText(self.robot.role) 
                                                                         
        self.robotCommStatus.setText(f"<html><head/><body><p>Comunica\u00e7\u00e3o: <span style=\" color:#3e7239;\">{self.robot.status}</span></p></body></html>")
        self.robotCharge.setText(f"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Bateria</span><span style=\" font-size:8pt;\">: {self.robot.battery}%</span></p></body></html>")
        self.robotIdLabel.setText(u"ID")
        self.robotIdValue.setText(self.robot.id)
        self.robotPosLabel.setText(u"Posi\u00e7\u00e3o")
        self.robotPosValue.setText(f"x: {self.robot.x} m y: {self.robot.y} m")
        self.robotAngleLabel.setText(u"Orienta\u00e7\u00e3o")
        self.robotAngleValue.setText(f"th: {self.robot.orientation} graus")
        self.speedReadLabel.setText(u"Velocidade lida")
        self.speedReadValue.setText(f"v: {self.robot.linearSpeed} m/s w: {self.robot.angularSpeed} rad/s")
        self.speedSentLabel.setText(u"Velocidade enviada")
        self.speedSentValue.setText(f"v: {self.robot.linearSpeed} m/s w: {self.robot.angularSpeed} rad/s")
        self.robotFreqLabel.setText(u"Frequ\u00eancia de envio")
        self.robotFreqValue.setText(f"{self.robot.frequency} MHz")

class Editor(QLabel):
    edited = Signal(QPixmap)
    def __init__(self, parent: QWidget, defaultImage: QPixmap):
        super().__init__(parent)
        
        self.defaultImage = defaultImage
        self.setPixmap(self.defaultImage)
        
        self.editedImage = self.defaultImage.copy()
        
        self.robots = [Robot(id = str(n)) for n in range(NROBOTS)]
        self.ball = Ball()
        
        self.vision = Vision(self)
    
    
    @Slot()
    def updateEditedImage(self):
        self.edited.emit(self.editedImage)
    
    def clearFrame(self):
        self.setPixmap(self.defaultImage.copy())
    
    def calcRelativePosition(self, position):
        labelPosition = position
        labelSize = self.size()
        
        pixmapSize = self.pixmap().size()
        relativePosition = labelPosition - self.rect().topLeft()
        
        pixmapPosition = QPointF(
            (relativePosition.x() * pixmapSize.width() / labelSize.width()),
            (relativePosition.y() * pixmapSize.height() / labelSize.height())
        )
        
        return pixmapPosition

class SegmentEditor(Editor):
    def __init__(self, parent: QWidget, defaultImage: QPixmap):
        super().__init__(parent, defaultImage)
       
        self.hsvRange = [0, 38, 198, 179, 255, 255]
    
    def segmentImage(self):
        image = self.defaultImage.copy()
        height, width = image.height(), image.width()
        
        cvImage = self.pixmapToCv(image)
        hsvImage = cv.cvtColor(cvImage, cv.COLOR_BGR2HSV)
       
        minHsv = np.array(self.hsvRange[0:3])
        maxHsv = np.array(self.hsvRange[3:6])
            
        mask = cv.inRange(hsvImage, minHsv, maxHsv)
        
        self.editedImage = self.cvToPixmap(mask, width, height)
        self.setPixmap(self.editedImage)
            
        
    def pixmapToCv(self, qpixmap):
        qimage = qpixmap.toImage()
        qimage = qimage.convertToFormat(QImage.Format.Format_RGB888)
        
        height, width = qimage.height(), qimage.width()
        channels = qimage.depth() // 8
        
        cvImage = np.frombuffer(qimage.bits(), dtype=np.uint8, count=height * width * channels).reshape((height, width, channels))
        
        return cvImage
    
    def cvToPixmap(self, cvImage, width, height):
        bgrImage = cv.cvtColor(cvImage, cv.COLOR_GRAY2BGR) 
        qimage = QImage(bgrImage.data, width, height, width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        return pixmap
    
    def updateMinHue(self, value):
        self.hsvRange[0] = value
        self.segmentImage()
        self.detectElements()
        
    def updateMaxHue(self, value):
        self.hsvRange[3] = value
        self.segmentImage()
        self.detectElements()
    
    def updateMinSaturation(self, value):
        self.hsvRange[1] = value
        self.segmentImage()
        self.detectElements()
        
    def updateMaxSaturation(self, value):
        self.hsvRange[4] = value
        self.segmentImage()
        self.detectElements()
    
    def updateMinValue(self, value):
        self.hsvRange[2] = value
        self.segmentImage()
        self.detectElements()
        
    def updateMaxValue(self, value):
        self.hsvRange[5] = value
        self.segmentImage()
        self.detectElements()
        
    def detectElements(self):
        opencvImage = self.pixmapToCv(self.editedImage)
        opencvImage = cv.cvtColor(opencvImage, cv.COLOR_BGR2GRAY)
        ball = self.vision.findBall(opencvImage)
        print(ball)
class CropEditor(Editor):
    def __init__(self, parent: QWidget, defaultImage: QPixmap):
        super().__init__(parent, defaultImage)
                
        self.pen = QPen()
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.pen.setColor(Qt.red)
        
        self.clickedPoints = []
    
    def mousePressEvent(self, event):
        position = event.position()
        pixmap_position = self.calcRelativePosition(position)
        
        if len(self.clickedPoints) <= 2:
            self.clickedPoints.append(position)
            self.drawPoint(pixmap_position)
            
        elif len(self.clickedPoints) == 3:
            self.clickedPoints.append(position)
            rect = list(map(self.calcRelativePosition, self.clickedPoints))
            self.drawRect(rect)
        else:
            self.clearFrame()
            self.clickedPoints.clear()
            
        
    def drawPoint(self, pixmap_position):
        canvas = self.pixmap()

        painter = QPainter(canvas)
        self.pen.setWidth(10)
        painter.setPen(self.pen)
        painter.drawPoint(pixmap_position.x(), pixmap_position.y())
        painter.end()

        self.setPixmap(canvas)
    
    def drawRect(self, rect):
        self.drawPoint(rect[-1])
        canvas = self.pixmap()

        painter = QPainter(canvas)
        self.pen.setWidth(1)
        painter.setPen(self.pen)
        painter.drawPolygon(rect)
        painter.end()
        
        self.cropImage(rect)
        self.setPixmap(canvas)
    
    def cropImage(self, points):
        p1 = QPointF(points[0]).toPoint()
        p2 = QPointF(points[2]).toPoint()
        rect = QRect(p1, p2)
        self.editedImage = self.defaultImage.copy(rect)
    
    def showEditedImage(self):
        self.setPixmap(self.editedImage)