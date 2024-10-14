# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLayout, QMainWindow, QPushButton, QRadioButton,
    QScrollArea, QSizePolicy, QSlider, QSpacerItem,
    QSpinBox, QTabWidget, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.ApplicationModal)
        MainWindow.resize(1000, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setStyleSheet(u"* {\n"
"	margin: 0;\n"
"	padding: 0;\n"
"	background-color: #a5a5a5;\n"
"}\n"
"\n"
"Line {\n"
"	background: #000;\n"
"}\n"
"\n"
"QRadioButton::indicator::checked {\n"
"	background: #000;\n"
"	border: 2px solid;\n"
"	border-radius: 7px;\n"
"}\n"
"\n"
"QRadioButton::indicator::unchecked {\n"
"	border: 2px solid;\n"
"	border-radius: 7px;\n"
"}\n"
"\n"
"#closeButton, #resizeButton, #minButton {\n"
"	margin: 0;\n"
"	padding: 0;\n"
"	background-color: transparent;\n"
"	border: none;\n"
"}\n"
"\n"
"#optionsLabel {\n"
"	color: #494848;\n"
"}\n"
"\n"
"QComboBox {\n"
"	color: #494848;\n"
"}\n"
"\n"
"#execButton {\n"
"	display: flex;\n"
"	padding: 3px;\n"
"	background-color: #38B12D;\n"
"	border-radius: 5px;\n"
"}\n"
"\n"
"#line {\n"
"	background: #000;\n"
"}\n"
"")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(0, 40, 1001, 761))
        self.tabWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.tabWidget.setStyleSheet(u"color: #494848;")
        self.tabWidget.setTabPosition(QTabWidget.TabPosition.North)
        self.tabWidget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tabWidget.setElideMode(Qt.TextElideMode.ElideNone)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setMovable(False)
        self.tabWidget.setTabBarAutoHide(True)
        self.sysTab = QWidget()
        self.sysTab.setObjectName(u"sysTab")
        self.sysTabWidget = QTabWidget(self.sysTab)
        self.sysTabWidget.setObjectName(u"sysTabWidget")
        self.sysTabWidget.setGeometry(QRect(540, 100, 441, 471))
        self.sysTabWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.sysTabWidget.setStyleSheet(u"color: #494848;")
        self.sysTabWidget.setDocumentMode(True)
        self.debugTab = QWidget()
        self.debugTab.setObjectName(u"debugTab")
        self.debugScrollArea = QScrollArea(self.debugTab)
        self.debugScrollArea.setObjectName(u"debugScrollArea")
        self.debugScrollArea.setGeometry(QRect(0, 0, 441, 441))
        self.debugScrollArea.setWidgetResizable(True)
        self.debugScrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.debugAreaContent = QWidget()
        self.debugAreaContent.setObjectName(u"debugAreaContent")
        self.debugAreaContent.setGeometry(QRect(0, 0, 439, 439))
        self.robotInfo = QFrame(self.debugAreaContent)
        self.robotInfo.setObjectName(u"robotInfo")
        self.robotInfo.setGeometry(QRect(10, 40, 421, 214))
        self.robotInfo.setFrameShape(QFrame.Shape.StyledPanel)
        self.robotInfo.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.robotInfo)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.robotFeedback = QHBoxLayout()
        self.robotFeedback.setObjectName(u"robotFeedback")
        self.robotRole = QComboBox(self.robotInfo)
        self.robotRole.addItem("")
        self.robotRole.addItem("")
        self.robotRole.addItem("")
        self.robotRole.setObjectName(u"robotRole")
        self.robotRole.setCursor(QCursor(Qt.PointingHandCursor))
        self.robotRole.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.robotFeedback.addWidget(self.robotRole)

        self.debugCommSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.robotFeedback.addItem(self.debugCommSpacer)

        self.debugComm = QHBoxLayout()
        self.debugComm.setObjectName(u"debugComm")
        self.commLabel = QLabel(self.robotInfo)
        self.commLabel.setObjectName(u"commLabel")
        self.commLabel.setCursor(QCursor(Qt.PointingHandCursor))

        self.debugComm.addWidget(self.commLabel)

        self.commStatus = QLabel(self.robotInfo)
        self.commStatus.setObjectName(u"commStatus")
        self.commStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.debugComm.addWidget(self.commStatus)


        self.robotFeedback.addLayout(self.debugComm)


        self.gridLayout_2.addLayout(self.robotFeedback, 0, 0, 1, 2)

        self.robotFrame = QVBoxLayout()
        self.robotFrame.setObjectName(u"robotFrame")
        self.robotImage = QLabel(self.robotInfo)
        self.robotImage.setObjectName(u"robotImage")
        self.robotImage.setPixmap(QPixmap(u"assets/camisa0.png"))
        self.robotImage.setScaledContents(True)

        self.robotFrame.addWidget(self.robotImage)

        self.robotCharge = QLabel(self.robotInfo)
        self.robotCharge.setObjectName(u"robotCharge")

        self.robotFrame.addWidget(self.robotCharge)


        self.gridLayout_2.addLayout(self.robotFrame, 1, 0, 1, 1)

        self.robotInfoContent = QVBoxLayout()
        self.robotInfoContent.setObjectName(u"robotInfoContent")
        self.robotId = QHBoxLayout()
        self.robotId.setObjectName(u"robotId")
        self.idLabel = QLabel(self.robotInfo)
        self.idLabel.setObjectName(u"idLabel")

        self.robotId.addWidget(self.idLabel)

        self.robotIdSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.robotId.addItem(self.robotIdSpacer)

        self.idValue = QLabel(self.robotInfo)
        self.idValue.setObjectName(u"idValue")

        self.robotId.addWidget(self.idValue)


        self.robotInfoContent.addLayout(self.robotId)

        self.position = QHBoxLayout()
        self.position.setObjectName(u"position")
        self.posLabel = QLabel(self.robotInfo)
        self.posLabel.setObjectName(u"posLabel")

        self.position.addWidget(self.posLabel)

        self.posSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.position.addItem(self.posSpacer)

        self.xPos = QLabel(self.robotInfo)
        self.xPos.setObjectName(u"xPos")

        self.position.addWidget(self.xPos)

        self.yPos = QLabel(self.robotInfo)
        self.yPos.setObjectName(u"yPos")

        self.position.addWidget(self.yPos)


        self.robotInfoContent.addLayout(self.position)

        self.orientation = QHBoxLayout()
        self.orientation.setObjectName(u"orientation")
        self.orientationLabel = QLabel(self.robotInfo)
        self.orientationLabel.setObjectName(u"orientationLabel")

        self.orientation.addWidget(self.orientationLabel)

        self.orientationSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.orientation.addItem(self.orientationSpacer)

        self.orientationValue = QLabel(self.robotInfo)
        self.orientationValue.setObjectName(u"orientationValue")

        self.orientation.addWidget(self.orientationValue)


        self.robotInfoContent.addLayout(self.orientation)

        self.rSpeed = QHBoxLayout()
        self.rSpeed.setObjectName(u"rSpeed")
        self.rSpeedLabel = QLabel(self.robotInfo)
        self.rSpeedLabel.setObjectName(u"rSpeedLabel")

        self.rSpeed.addWidget(self.rSpeedLabel)

        self.rSpeedSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rSpeed.addItem(self.rSpeedSpacer)

        self.rVSpeed = QLabel(self.robotInfo)
        self.rVSpeed.setObjectName(u"rVSpeed")

        self.rSpeed.addWidget(self.rVSpeed)

        self.rWSpeed = QLabel(self.robotInfo)
        self.rWSpeed.setObjectName(u"rWSpeed")

        self.rSpeed.addWidget(self.rWSpeed)


        self.robotInfoContent.addLayout(self.rSpeed)

        self.sSpeed = QHBoxLayout()
        self.sSpeed.setObjectName(u"sSpeed")
        self.sSpeedLabel = QLabel(self.robotInfo)
        self.sSpeedLabel.setObjectName(u"sSpeedLabel")

        self.sSpeed.addWidget(self.sSpeedLabel)

        self.sPeedSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.sSpeed.addItem(self.sPeedSpacer)

        self.sVSpeed = QLabel(self.robotInfo)
        self.sVSpeed.setObjectName(u"sVSpeed")

        self.sSpeed.addWidget(self.sVSpeed)

        self.sWSpeed = QLabel(self.robotInfo)
        self.sWSpeed.setObjectName(u"sWSpeed")

        self.sSpeed.addWidget(self.sWSpeed)


        self.robotInfoContent.addLayout(self.sSpeed)

        self.frequency = QHBoxLayout()
        self.frequency.setObjectName(u"frequency")
        self.freqLabel = QLabel(self.robotInfo)
        self.freqLabel.setObjectName(u"freqLabel")

        self.frequency.addWidget(self.freqLabel)

        self.freqSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.frequency.addItem(self.freqSpacer)

        self.freqValue = QLabel(self.robotInfo)
        self.freqValue.setObjectName(u"freqValue")

        self.frequency.addWidget(self.freqValue)


        self.robotInfoContent.addLayout(self.frequency)


        self.gridLayout_2.addLayout(self.robotInfoContent, 1, 1, 1, 1)

        self.layoutWidget = QWidget(self.debugAreaContent)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 10, 421, 20))
        self.debugHeader = QHBoxLayout(self.layoutWidget)
        self.debugHeader.setObjectName(u"debugHeader")
        self.debugHeader.setContentsMargins(0, 0, 0, 0)
        self.debugTitle = QLabel(self.layoutWidget)
        self.debugTitle.setObjectName(u"debugTitle")

        self.debugHeader.addWidget(self.debugTitle)

        self.nRobots = QLabel(self.layoutWidget)
        self.nRobots.setObjectName(u"nRobots")
        self.nRobots.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.debugHeader.addWidget(self.nRobots)

        self.robotInfo_2 = QFrame(self.debugAreaContent)
        self.robotInfo_2.setObjectName(u"robotInfo_2")
        self.robotInfo_2.setGeometry(QRect(10, 270, 421, 214))
        self.robotInfo_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.robotInfo_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_3 = QGridLayout(self.robotInfo_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.robotFeedback_2 = QHBoxLayout()
        self.robotFeedback_2.setObjectName(u"robotFeedback_2")
        self.robotRole_2 = QComboBox(self.robotInfo_2)
        self.robotRole_2.addItem("")
        self.robotRole_2.addItem("")
        self.robotRole_2.addItem("")
        self.robotRole_2.setObjectName(u"robotRole_2")
        self.robotRole_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.robotRole_2.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.robotFeedback_2.addWidget(self.robotRole_2)

        self.debugCommSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.robotFeedback_2.addItem(self.debugCommSpacer_2)

        self.debugComm_2 = QHBoxLayout()
        self.debugComm_2.setObjectName(u"debugComm_2")
        self.commLabel_2 = QLabel(self.robotInfo_2)
        self.commLabel_2.setObjectName(u"commLabel_2")
        self.commLabel_2.setCursor(QCursor(Qt.PointingHandCursor))

        self.debugComm_2.addWidget(self.commLabel_2)

        self.commStatus_2 = QLabel(self.robotInfo_2)
        self.commStatus_2.setObjectName(u"commStatus_2")
        self.commStatus_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.debugComm_2.addWidget(self.commStatus_2)


        self.robotFeedback_2.addLayout(self.debugComm_2)


        self.gridLayout_3.addLayout(self.robotFeedback_2, 0, 0, 1, 2)

        self.robotFrame_2 = QVBoxLayout()
        self.robotFrame_2.setObjectName(u"robotFrame_2")
        self.robotImage_2 = QLabel(self.robotInfo_2)
        self.robotImage_2.setObjectName(u"robotImage_2")
        self.robotImage_2.setPixmap(QPixmap(u"assets/camisa0.png"))
        self.robotImage_2.setScaledContents(True)

        self.robotFrame_2.addWidget(self.robotImage_2)

        self.robotCharge_2 = QLabel(self.robotInfo_2)
        self.robotCharge_2.setObjectName(u"robotCharge_2")

        self.robotFrame_2.addWidget(self.robotCharge_2)


        self.gridLayout_3.addLayout(self.robotFrame_2, 1, 0, 1, 1)

        self.robotInfoContent_2 = QVBoxLayout()
        self.robotInfoContent_2.setObjectName(u"robotInfoContent_2")
        self.robotId_2 = QHBoxLayout()
        self.robotId_2.setObjectName(u"robotId_2")
        self.idLabel_2 = QLabel(self.robotInfo_2)
        self.idLabel_2.setObjectName(u"idLabel_2")

        self.robotId_2.addWidget(self.idLabel_2)

        self.robotIdSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.robotId_2.addItem(self.robotIdSpacer_2)

        self.idValue_2 = QLabel(self.robotInfo_2)
        self.idValue_2.setObjectName(u"idValue_2")

        self.robotId_2.addWidget(self.idValue_2)


        self.robotInfoContent_2.addLayout(self.robotId_2)

        self.position_2 = QHBoxLayout()
        self.position_2.setObjectName(u"position_2")
        self.posLabel_2 = QLabel(self.robotInfo_2)
        self.posLabel_2.setObjectName(u"posLabel_2")

        self.position_2.addWidget(self.posLabel_2)

        self.posSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.position_2.addItem(self.posSpacer_2)

        self.xPos_2 = QLabel(self.robotInfo_2)
        self.xPos_2.setObjectName(u"xPos_2")

        self.position_2.addWidget(self.xPos_2)

        self.yPos_2 = QLabel(self.robotInfo_2)
        self.yPos_2.setObjectName(u"yPos_2")

        self.position_2.addWidget(self.yPos_2)


        self.robotInfoContent_2.addLayout(self.position_2)

        self.orientation_2 = QHBoxLayout()
        self.orientation_2.setObjectName(u"orientation_2")
        self.orientationLabel_2 = QLabel(self.robotInfo_2)
        self.orientationLabel_2.setObjectName(u"orientationLabel_2")

        self.orientation_2.addWidget(self.orientationLabel_2)

        self.orientationSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.orientation_2.addItem(self.orientationSpacer_2)

        self.orientationValue_2 = QLabel(self.robotInfo_2)
        self.orientationValue_2.setObjectName(u"orientationValue_2")

        self.orientation_2.addWidget(self.orientationValue_2)


        self.robotInfoContent_2.addLayout(self.orientation_2)

        self.rSpeed_2 = QHBoxLayout()
        self.rSpeed_2.setObjectName(u"rSpeed_2")
        self.rSpeedLabel_2 = QLabel(self.robotInfo_2)
        self.rSpeedLabel_2.setObjectName(u"rSpeedLabel_2")

        self.rSpeed_2.addWidget(self.rSpeedLabel_2)

        self.rSpeedSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.rSpeed_2.addItem(self.rSpeedSpacer_2)

        self.rVSpeed_2 = QLabel(self.robotInfo_2)
        self.rVSpeed_2.setObjectName(u"rVSpeed_2")

        self.rSpeed_2.addWidget(self.rVSpeed_2)

        self.rWSpeed_2 = QLabel(self.robotInfo_2)
        self.rWSpeed_2.setObjectName(u"rWSpeed_2")

        self.rSpeed_2.addWidget(self.rWSpeed_2)


        self.robotInfoContent_2.addLayout(self.rSpeed_2)

        self.sSpeed_2 = QHBoxLayout()
        self.sSpeed_2.setObjectName(u"sSpeed_2")
        self.sSpeedLabel_2 = QLabel(self.robotInfo_2)
        self.sSpeedLabel_2.setObjectName(u"sSpeedLabel_2")

        self.sSpeed_2.addWidget(self.sSpeedLabel_2)

        self.sPeedSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.sSpeed_2.addItem(self.sPeedSpacer_2)

        self.sVSpeed_2 = QLabel(self.robotInfo_2)
        self.sVSpeed_2.setObjectName(u"sVSpeed_2")

        self.sSpeed_2.addWidget(self.sVSpeed_2)

        self.sWSpeed_2 = QLabel(self.robotInfo_2)
        self.sWSpeed_2.setObjectName(u"sWSpeed_2")

        self.sSpeed_2.addWidget(self.sWSpeed_2)


        self.robotInfoContent_2.addLayout(self.sSpeed_2)

        self.frequency_2 = QHBoxLayout()
        self.frequency_2.setObjectName(u"frequency_2")
        self.freqLabel_2 = QLabel(self.robotInfo_2)
        self.freqLabel_2.setObjectName(u"freqLabel_2")

        self.frequency_2.addWidget(self.freqLabel_2)

        self.freqSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.frequency_2.addItem(self.freqSpacer_2)

        self.freqValue_2 = QLabel(self.robotInfo_2)
        self.freqValue_2.setObjectName(u"freqValue_2")

        self.frequency_2.addWidget(self.freqValue_2)


        self.robotInfoContent_2.addLayout(self.frequency_2)


        self.gridLayout_3.addLayout(self.robotInfoContent_2, 1, 1, 1, 1)

        self.debugScrollArea.setWidget(self.debugAreaContent)
        self.sysTabWidget.addTab(self.debugTab, "")
        self.navigationTab = QWidget()
        self.navigationTab.setObjectName(u"navigationTab")
        self.navScrollArea = QScrollArea(self.navigationTab)
        self.navScrollArea.setObjectName(u"navScrollArea")
        self.navScrollArea.setGeometry(QRect(0, 0, 441, 441))
        self.navScrollArea.setWidgetResizable(True)
        self.navScrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.navAreaContents = QWidget()
        self.navAreaContents.setObjectName(u"navAreaContents")
        self.navAreaContents.setGeometry(QRect(0, 0, 439, 439))
        self.layoutWidget1 = QWidget(self.navAreaContents)
        self.layoutWidget1.setObjectName(u"layoutWidget1")
        self.layoutWidget1.setGeometry(QRect(10, 80, 421, 50))
        self.viewUvf = QHBoxLayout(self.layoutWidget1)
        self.viewUvf.setObjectName(u"viewUvf")
        self.viewUvf.setContentsMargins(0, 0, 0, 0)
        self.viewUvfLabel = QLabel(self.layoutWidget1)
        self.viewUvfLabel.setObjectName(u"viewUvfLabel")

        self.viewUvf.addWidget(self.viewUvfLabel)

        self.pointsNumber = QVBoxLayout()
        self.pointsNumber.setObjectName(u"pointsNumber")
        self.pointsNumberLabel = QLabel(self.layoutWidget1)
        self.pointsNumberLabel.setObjectName(u"pointsNumberLabel")

        self.pointsNumber.addWidget(self.pointsNumberLabel)

        self.pointsNumberSpin = QSpinBox(self.layoutWidget1)
        self.pointsNumberSpin.setObjectName(u"pointsNumberSpin")
        sizePolicy.setHeightForWidth(self.pointsNumberSpin.sizePolicy().hasHeightForWidth())
        self.pointsNumberSpin.setSizePolicy(sizePolicy)
        self.pointsNumberSpin.setCursor(QCursor(Qt.IBeamCursor))
        self.pointsNumberSpin.setStyleSheet(u"color: #494848;")
        self.pointsNumberSpin.setWrapping(False)
        self.pointsNumberSpin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pointsNumberSpin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.pointsNumberSpin.setSuffix(u"")
        self.pointsNumberSpin.setMaximum(10)

        self.pointsNumber.addWidget(self.pointsNumberSpin)


        self.viewUvf.addLayout(self.pointsNumber)

        self.uvfViewIcon = QLabel(self.layoutWidget1)
        self.uvfViewIcon.setObjectName(u"uvfViewIcon")
        sizePolicy.setHeightForWidth(self.uvfViewIcon.sizePolicy().hasHeightForWidth())
        self.uvfViewIcon.setSizePolicy(sizePolicy)
        self.uvfViewIcon.setPixmap(QPixmap(u"assets/icons/Eye.svg"))
        self.uvfViewIcon.setScaledContents(True)

        self.viewUvf.addWidget(self.uvfViewIcon)

        self.layoutWidget2 = QWidget(self.navAreaContents)
        self.layoutWidget2.setObjectName(u"layoutWidget2")
        self.layoutWidget2.setGeometry(QRect(10, 140, 421, 24))
        self.selectField = QHBoxLayout(self.layoutWidget2)
        self.selectField.setObjectName(u"selectField")
        self.selectField.setContentsMargins(0, 0, 0, 0)
        self.selectFieldLabel = QLabel(self.layoutWidget2)
        self.selectFieldLabel.setObjectName(u"selectFieldLabel")

        self.selectField.addWidget(self.selectFieldLabel)

        self.selectFieldDropdown = QComboBox(self.layoutWidget2)
        self.selectFieldDropdown.addItem("")
        self.selectFieldDropdown.setObjectName(u"selectFieldDropdown")
        self.selectFieldDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.selectFieldDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.selectField.addWidget(self.selectFieldDropdown)

        self.robotUvfTitle = QLabel(self.navAreaContents)
        self.robotUvfTitle.setObjectName(u"robotUvfTitle")
        self.robotUvfTitle.setGeometry(QRect(10, 50, 41, 18))
        self.layoutWidget3 = QWidget(self.navAreaContents)
        self.layoutWidget3.setObjectName(u"layoutWidget3")
        self.layoutWidget3.setGeometry(QRect(10, 180, 421, 42))
        self.lastPoint = QHBoxLayout(self.layoutWidget3)
        self.lastPoint.setObjectName(u"lastPoint")
        self.lastPoint.setContentsMargins(0, 0, 0, 0)
        self.lastPointLabel = QVBoxLayout()
        self.lastPointLabel.setObjectName(u"lastPointLabel")
        self.lastPointLabel.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        self.lastPointName = QLabel(self.layoutWidget3)
        self.lastPointName.setObjectName(u"lastPointName")

        self.lastPointLabel.addWidget(self.lastPointName)

        self.lastPointDescription = QLabel(self.layoutWidget3)
        self.lastPointDescription.setObjectName(u"lastPointDescription")

        self.lastPointLabel.addWidget(self.lastPointDescription)


        self.lastPoint.addLayout(self.lastPointLabel)

        self.lastPointSlider = QSlider(self.layoutWidget3)
        self.lastPointSlider.setObjectName(u"lastPointSlider")
        sizePolicy.setHeightForWidth(self.lastPointSlider.sizePolicy().hasHeightForWidth())
        self.lastPointSlider.setSizePolicy(sizePolicy)
        self.lastPointSlider.setMaximumSize(QSize(30, 15))
        self.lastPointSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.lastPointSlider.setMaximum(1)
        self.lastPointSlider.setOrientation(Qt.Orientation.Horizontal)

        self.lastPoint.addWidget(self.lastPointSlider)

        self.layoutWidget4 = QWidget(self.navAreaContents)
        self.layoutWidget4.setObjectName(u"layoutWidget4")
        self.layoutWidget4.setGeometry(QRect(10, 230, 421, 112))
        self.gridLayout = QGridLayout(self.layoutWidget4)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.uvfRadius = QVBoxLayout()
        self.uvfRadius.setObjectName(u"uvfRadius")
        self.uvfRadiusLabel = QLabel(self.layoutWidget4)
        self.uvfRadiusLabel.setObjectName(u"uvfRadiusLabel")

        self.uvfRadius.addWidget(self.uvfRadiusLabel)

        self.uvfRadiusSpinner = QSpinBox(self.layoutWidget4)
        self.uvfRadiusSpinner.setObjectName(u"uvfRadiusSpinner")
        sizePolicy.setHeightForWidth(self.uvfRadiusSpinner.sizePolicy().hasHeightForWidth())
        self.uvfRadiusSpinner.setSizePolicy(sizePolicy)
        self.uvfRadiusSpinner.setCursor(QCursor(Qt.IBeamCursor))
        self.uvfRadiusSpinner.setStyleSheet(u"color: #494848;")
        self.uvfRadiusSpinner.setWrapping(False)
        self.uvfRadiusSpinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uvfRadiusSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.uvfRadiusSpinner.setSuffix(u"")
        self.uvfRadiusSpinner.setMaximum(10)

        self.uvfRadius.addWidget(self.uvfRadiusSpinner)


        self.gridLayout.addLayout(self.uvfRadius, 0, 0, 1, 1)

        self.uvfConst = QVBoxLayout()
        self.uvfConst.setObjectName(u"uvfConst")
        self.uvfConstLabel = QLabel(self.layoutWidget4)
        self.uvfConstLabel.setObjectName(u"uvfConstLabel")

        self.uvfConst.addWidget(self.uvfConstLabel)

        self.uvfConstSpinner = QSpinBox(self.layoutWidget4)
        self.uvfConstSpinner.setObjectName(u"uvfConstSpinner")
        sizePolicy.setHeightForWidth(self.uvfConstSpinner.sizePolicy().hasHeightForWidth())
        self.uvfConstSpinner.setSizePolicy(sizePolicy)
        self.uvfConstSpinner.setCursor(QCursor(Qt.IBeamCursor))
        self.uvfConstSpinner.setStyleSheet(u"color: #494848;")
        self.uvfConstSpinner.setWrapping(False)
        self.uvfConstSpinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uvfConstSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.uvfConstSpinner.setSuffix(u"")
        self.uvfConstSpinner.setMaximum(10)

        self.uvfConst.addWidget(self.uvfConstSpinner)


        self.gridLayout.addLayout(self.uvfConst, 0, 1, 1, 1)

        self.uvfUniConst = QVBoxLayout()
        self.uvfUniConst.setObjectName(u"uvfUniConst")
        self.uvfUniConstLabel = QLabel(self.layoutWidget4)
        self.uvfUniConstLabel.setObjectName(u"uvfUniConstLabel")

        self.uvfUniConst.addWidget(self.uvfUniConstLabel)

        self.uvfUniConstSpinner = QSpinBox(self.layoutWidget4)
        self.uvfUniConstSpinner.setObjectName(u"uvfUniConstSpinner")
        sizePolicy.setHeightForWidth(self.uvfUniConstSpinner.sizePolicy().hasHeightForWidth())
        self.uvfUniConstSpinner.setSizePolicy(sizePolicy)
        self.uvfUniConstSpinner.setCursor(QCursor(Qt.IBeamCursor))
        self.uvfUniConstSpinner.setStyleSheet(u"color: #494848;")
        self.uvfUniConstSpinner.setWrapping(False)
        self.uvfUniConstSpinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uvfUniConstSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.uvfUniConstSpinner.setSuffix(u"")
        self.uvfUniConstSpinner.setMaximum(10)

        self.uvfUniConst.addWidget(self.uvfUniConstSpinner)


        self.gridLayout.addLayout(self.uvfUniConst, 1, 1, 1, 1)

        self.robotUvfId = QComboBox(self.navAreaContents)
        self.robotUvfId.addItem("")
        self.robotUvfId.addItem("")
        self.robotUvfId.addItem("")
        self.robotUvfId.setObjectName(u"robotUvfId")
        self.robotUvfId.setGeometry(QRect(10, 10, 72, 22))
        self.robotUvfId.setCursor(QCursor(Qt.PointingHandCursor))
        self.robotUvfId.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.navScrollArea.setWidget(self.navAreaContents)
        self.sysTabWidget.addTab(self.navigationTab, "")
        self.decisionTab = QWidget()
        self.decisionTab.setObjectName(u"decisionTab")
        self.decisionScrollArea = QScrollArea(self.decisionTab)
        self.decisionScrollArea.setObjectName(u"decisionScrollArea")
        self.decisionScrollArea.setGeometry(QRect(0, 0, 441, 441))
        self.decisionScrollArea.setWidgetResizable(True)
        self.decisionScrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decisionAreaContent = QWidget()
        self.decisionAreaContent.setObjectName(u"decisionAreaContent")
        self.decisionAreaContent.setGeometry(QRect(0, 0, 439, 439))
        self.layoutWidget_16 = QWidget(self.decisionAreaContent)
        self.layoutWidget_16.setObjectName(u"layoutWidget_16")
        self.layoutWidget_16.setGeometry(QRect(10, 10, 421, 20))
        self.decisionHeader = QHBoxLayout(self.layoutWidget_16)
        self.decisionHeader.setObjectName(u"decisionHeader")
        self.decisionHeader.setContentsMargins(0, 0, 0, 0)
        self.decisionTitle = QLabel(self.layoutWidget_16)
        self.decisionTitle.setObjectName(u"decisionTitle")

        self.decisionHeader.addWidget(self.decisionTitle)

        self.decisionDescrption = QLabel(self.layoutWidget_16)
        self.decisionDescrption.setObjectName(u"decisionDescrption")
        self.decisionDescrption.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.decisionHeader.addWidget(self.decisionDescrption)

        self.layoutWidget5 = QWidget(self.decisionAreaContent)
        self.layoutWidget5.setObjectName(u"layoutWidget5")
        self.layoutWidget5.setGeometry(QRect(10, 40, 220, 111))
        self.staticEntities = QVBoxLayout(self.layoutWidget5)
        self.staticEntities.setObjectName(u"staticEntities")
        self.staticEntities.setContentsMargins(0, 0, 0, 0)
        self.staticEntitiesRadio = QRadioButton(self.layoutWidget5)
        self.staticEntitiesRadio.setObjectName(u"staticEntitiesRadio")
        self.staticEntitiesRadio.setChecked(True)

        self.staticEntities.addWidget(self.staticEntitiesRadio)

        self.robot0RoleDecision = QHBoxLayout()
        self.robot0RoleDecision.setObjectName(u"robot0RoleDecision")
        self.robot0RoleLabel = QLabel(self.layoutWidget5)
        self.robot0RoleLabel.setObjectName(u"robot0RoleLabel")

        self.robot0RoleDecision.addWidget(self.robot0RoleLabel)

        self.robot0RoleSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.robot0RoleDecision.addItem(self.robot0RoleSpacer)

        self.robot0RoleDropdown = QComboBox(self.layoutWidget5)
        self.robot0RoleDropdown.addItem("")
        self.robot0RoleDropdown.addItem("")
        self.robot0RoleDropdown.addItem("")
        self.robot0RoleDropdown.setObjectName(u"robot0RoleDropdown")
        self.robot0RoleDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.robot0RoleDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.robot0RoleDecision.addWidget(self.robot0RoleDropdown)


        self.staticEntities.addLayout(self.robot0RoleDecision)

        self.robot1RoleDecision = QHBoxLayout()
        self.robot1RoleDecision.setObjectName(u"robot1RoleDecision")
        self.robot1RoleLabel = QLabel(self.layoutWidget5)
        self.robot1RoleLabel.setObjectName(u"robot1RoleLabel")

        self.robot1RoleDecision.addWidget(self.robot1RoleLabel)

        self.robot1RoleSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.robot1RoleDecision.addItem(self.robot1RoleSpacer)

        self.robot1RoleSpinner = QComboBox(self.layoutWidget5)
        self.robot1RoleSpinner.addItem("")
        self.robot1RoleSpinner.addItem("")
        self.robot1RoleSpinner.addItem("")
        self.robot1RoleSpinner.setObjectName(u"robot1RoleSpinner")
        self.robot1RoleSpinner.setCursor(QCursor(Qt.PointingHandCursor))
        self.robot1RoleSpinner.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.robot1RoleDecision.addWidget(self.robot1RoleSpinner)


        self.staticEntities.addLayout(self.robot1RoleDecision)

        self.robot2RoleDecision = QHBoxLayout()
        self.robot2RoleDecision.setObjectName(u"robot2RoleDecision")
        self.robot2RoleLabel = QLabel(self.layoutWidget5)
        self.robot2RoleLabel.setObjectName(u"robot2RoleLabel")

        self.robot2RoleDecision.addWidget(self.robot2RoleLabel)

        self.robot2RoleSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.robot2RoleDecision.addItem(self.robot2RoleSpacer)

        self.robot2RoleDropdown = QComboBox(self.layoutWidget5)
        self.robot2RoleDropdown.addItem("")
        self.robot2RoleDropdown.addItem("")
        self.robot2RoleDropdown.addItem("")
        self.robot2RoleDropdown.setObjectName(u"robot2RoleDropdown")
        self.robot2RoleDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.robot2RoleDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.robot2RoleDecision.addWidget(self.robot2RoleDropdown)


        self.staticEntities.addLayout(self.robot2RoleDecision)

        self.dynamicEntitiesRadio = QRadioButton(self.decisionAreaContent)
        self.dynamicEntitiesRadio.setObjectName(u"dynamicEntitiesRadio")
        self.dynamicEntitiesRadio.setGeometry(QRect(10, 170, 161, 24))
        self.posBox = QFrame(self.decisionAreaContent)
        self.posBox.setObjectName(u"posBox")
        self.posBox.setGeometry(QRect(10, 250, 421, 161))
        self.posBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.posBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.posBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.virtualJudgePos = QHBoxLayout()
        self.virtualJudgePos.setObjectName(u"virtualJudgePos")
        self.virtualJudgePosLabel = QLabel(self.posBox)
        self.virtualJudgePosLabel.setObjectName(u"virtualJudgePosLabel")

        self.virtualJudgePos.addWidget(self.virtualJudgePosLabel)

        self.virtualJudgePosSlider = QSlider(self.posBox)
        self.virtualJudgePosSlider.setObjectName(u"virtualJudgePosSlider")
        sizePolicy.setHeightForWidth(self.virtualJudgePosSlider.sizePolicy().hasHeightForWidth())
        self.virtualJudgePosSlider.setSizePolicy(sizePolicy)
        self.virtualJudgePosSlider.setMaximumSize(QSize(30, 15))
        self.virtualJudgePosSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.virtualJudgePosSlider.setMaximum(1)
        self.virtualJudgePosSlider.setOrientation(Qt.Orientation.Horizontal)

        self.virtualJudgePos.addWidget(self.virtualJudgePosSlider)


        self.verticalLayout_2.addLayout(self.virtualJudgePos)

        self.manualJudgePos = QHBoxLayout()
        self.manualJudgePos.setObjectName(u"manualJudgePos")
        self.manualJudgePosLabel = QLabel(self.posBox)
        self.manualJudgePosLabel.setObjectName(u"manualJudgePosLabel")

        self.manualJudgePos.addWidget(self.manualJudgePosLabel)

        self.manualJudgePosSlider = QSlider(self.posBox)
        self.manualJudgePosSlider.setObjectName(u"manualJudgePosSlider")
        sizePolicy.setHeightForWidth(self.manualJudgePosSlider.sizePolicy().hasHeightForWidth())
        self.manualJudgePosSlider.setSizePolicy(sizePolicy)
        self.manualJudgePosSlider.setMaximumSize(QSize(30, 15))
        self.manualJudgePosSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.manualJudgePosSlider.setMaximum(1)
        self.manualJudgePosSlider.setOrientation(Qt.Orientation.Horizontal)

        self.manualJudgePos.addWidget(self.manualJudgePosSlider)


        self.verticalLayout_2.addLayout(self.manualJudgePos)

        self.selectPos = QHBoxLayout()
        self.selectPos.setObjectName(u"selectPos")
        self.selectPosLabel = QLabel(self.posBox)
        self.selectPosLabel.setObjectName(u"selectPosLabel")

        self.selectPos.addWidget(self.selectPosLabel)

        self.selectPosDropdown = QComboBox(self.posBox)
        self.selectPosDropdown.addItem("")
        self.selectPosDropdown.addItem("")
        self.selectPosDropdown.addItem("")
        self.selectPosDropdown.setObjectName(u"selectPosDropdown")
        sizePolicy.setHeightForWidth(self.selectPosDropdown.sizePolicy().hasHeightForWidth())
        self.selectPosDropdown.setSizePolicy(sizePolicy)
        self.selectPosDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.selectPosDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.selectPos.addWidget(self.selectPosDropdown)


        self.verticalLayout_2.addLayout(self.selectPos)

        self.posTiming = QLabel(self.posBox)
        self.posTiming.setObjectName(u"posTiming")

        self.verticalLayout_2.addWidget(self.posTiming)

        self.selectPosTitle = QLabel(self.decisionAreaContent)
        self.selectPosTitle.setObjectName(u"selectPosTitle")
        self.selectPosTitle.setGeometry(QRect(10, 220, 121, 18))
        self.horizontalLine = QFrame(self.decisionAreaContent)
        self.horizontalLine.setObjectName(u"horizontalLine")
        self.horizontalLine.setGeometry(QRect(10, 200, 421, 16))
        self.horizontalLine.setFrameShape(QFrame.HLine)
        self.horizontalLine.setFrameShadow(QFrame.Sunken)
        self.decisionScrollArea.setWidget(self.decisionAreaContent)
        self.sysTabWidget.addTab(self.decisionTab, "")
        self.ballInfo = QFrame(self.sysTab)
        self.ballInfo.setObjectName(u"ballInfo")
        self.ballInfo.setGeometry(QRect(10, 580, 321, 131))
        self.ballInfo.setFrameShape(QFrame.Shape.StyledPanel)
        self.ballInfo.setFrameShadow(QFrame.Shadow.Raised)
        self.widget = QWidget(self.ballInfo)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 50, 301, 62))
        self.ballInfoContent = QHBoxLayout(self.widget)
        self.ballInfoContent.setObjectName(u"ballInfoContent")
        self.ballInfoContent.setContentsMargins(0, 0, 0, 0)
        self.ball = QVBoxLayout()
        self.ball.setObjectName(u"ball")
        self.ballPosLabel = QLabel(self.widget)
        self.ballPosLabel.setObjectName(u"ballPosLabel")

        self.ball.addWidget(self.ballPosLabel)

        self.ballPos = QFrame(self.widget)
        self.ballPos.setObjectName(u"ballPos")
        self.ballPos.setFrameShape(QFrame.Shape.StyledPanel)
        self.ballPos.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.ballPos)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.xBallPos = QLabel(self.ballPos)
        self.xBallPos.setObjectName(u"xBallPos")

        self.horizontalLayout_2.addWidget(self.xBallPos)

        self.yBallPos = QLabel(self.ballPos)
        self.yBallPos.setObjectName(u"yBallPos")

        self.horizontalLayout_2.addWidget(self.yBallPos)


        self.ball.addWidget(self.ballPos)


        self.ballInfoContent.addLayout(self.ball)

        self.speed = QVBoxLayout()
        self.speed.setObjectName(u"speed")
        self.speedInfoLabel = QLabel(self.widget)
        self.speedInfoLabel.setObjectName(u"speedInfoLabel")

        self.speed.addWidget(self.speedInfoLabel)

        self.speedInfo = QFrame(self.widget)
        self.speedInfo.setObjectName(u"speedInfo")
        self.speedInfo.setFrameShape(QFrame.Shape.StyledPanel)
        self.speedInfo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.speedInfo)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.speedValue = QLabel(self.speedInfo)
        self.speedValue.setObjectName(u"speedValue")

        self.horizontalLayout_3.addWidget(self.speedValue)


        self.speed.addWidget(self.speedInfo)


        self.ballInfoContent.addLayout(self.speed)

        self.acceleration = QVBoxLayout()
        self.acceleration.setObjectName(u"acceleration")
        self.accLabel = QLabel(self.widget)
        self.accLabel.setObjectName(u"accLabel")

        self.acceleration.addWidget(self.accLabel)

        self.accInfo = QFrame(self.widget)
        self.accInfo.setObjectName(u"accInfo")
        self.accInfo.setFrameShape(QFrame.Shape.StyledPanel)
        self.accInfo.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.accInfo)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.accValue = QLabel(self.accInfo)
        self.accValue.setObjectName(u"accValue")

        self.horizontalLayout_4.addWidget(self.accValue)


        self.acceleration.addWidget(self.accInfo)


        self.ballInfoContent.addLayout(self.acceleration)

        self.widget1 = QWidget(self.ballInfo)
        self.widget1.setObjectName(u"widget1")
        self.widget1.setGeometry(QRect(10, 10, 301, 22))
        self.ballInfoHeader = QHBoxLayout(self.widget1)
        self.ballInfoHeader.setObjectName(u"ballInfoHeader")
        self.ballInfoHeader.setContentsMargins(0, 0, 0, 0)
        self.ballTitle = QLabel(self.widget1)
        self.ballTitle.setObjectName(u"ballTitle")

        self.ballInfoHeader.addWidget(self.ballTitle)

        self.ballInfoHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.ballInfoHeader.addItem(self.ballInfoHeaderSpacer)

        self.ballStatus = QLabel(self.widget1)
        self.ballStatus.setObjectName(u"ballStatus")
        self.ballStatus.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.ballInfoHeader.addWidget(self.ballStatus)

        self.communication = QFrame(self.sysTab)
        self.communication.setObjectName(u"communication")
        self.communication.setGeometry(QRect(350, 580, 631, 131))
        self.communication.setFrameShape(QFrame.Shape.StyledPanel)
        self.communication.setFrameShadow(QFrame.Shadow.Raised)
        self.layoutWidget6 = QWidget(self.communication)
        self.layoutWidget6.setObjectName(u"layoutWidget6")
        self.layoutWidget6.setGeometry(QRect(430, 10, 191, 101))
        self.log = QVBoxLayout(self.layoutWidget6)
        self.log.setObjectName(u"log")
        self.log.setContentsMargins(0, 0, 0, 0)
        self.logLabel = QLabel(self.layoutWidget6)
        self.logLabel.setObjectName(u"logLabel")

        self.log.addWidget(self.logLabel)

        self.logInfo = QScrollArea(self.layoutWidget6)
        self.logInfo.setObjectName(u"logInfo")
        self.logInfo.setWidgetResizable(True)
        self.logBox = QWidget()
        self.logBox.setObjectName(u"logBox")
        self.logBox.setGeometry(QRect(0, 0, 187, 73))
        self.logContent = QLabel(self.logBox)
        self.logContent.setObjectName(u"logContent")
        self.logContent.setGeometry(QRect(0, 0, 191, 71))
        self.logInfo.setWidget(self.logBox)

        self.log.addWidget(self.logInfo)

        self.layoutWidget7 = QWidget(self.communication)
        self.layoutWidget7.setObjectName(u"layoutWidget7")
        self.layoutWidget7.setGeometry(QRect(10, 10, 416, 101))
        self.commInfo = QVBoxLayout(self.layoutWidget7)
        self.commInfo.setObjectName(u"commInfo")
        self.commInfo.setContentsMargins(0, 0, 0, 0)
        self.commTitle = QLabel(self.layoutWidget7)
        self.commTitle.setObjectName(u"commTitle")

        self.commInfo.addWidget(self.commTitle)

        self.commContent = QHBoxLayout()
        self.commContent.setObjectName(u"commContent")
        self.visionComm = QVBoxLayout()
        self.visionComm.setObjectName(u"visionComm")
        self.visionCommHeader = QHBoxLayout()
        self.visionCommHeader.setObjectName(u"visionCommHeader")
        self.visionCommLabel = QLabel(self.layoutWidget7)
        self.visionCommLabel.setObjectName(u"visionCommLabel")

        self.visionCommHeader.addWidget(self.visionCommLabel)

        self.visionCommSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.visionCommHeader.addItem(self.visionCommSpacer)

        self.visionCommStatus = QLabel(self.layoutWidget7)
        self.visionCommStatus.setObjectName(u"visionCommStatus")
        self.visionCommStatus.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.visionCommHeader.addWidget(self.visionCommStatus)


        self.visionComm.addLayout(self.visionCommHeader)

        self.visionPort = QFrame(self.layoutWidget7)
        self.visionPort.setObjectName(u"visionPort")
        self.visionPort.setFrameShape(QFrame.Shape.StyledPanel)
        self.visionPort.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_9 = QVBoxLayout(self.visionPort)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.visionPortValue = QLabel(self.visionPort)
        self.visionPortValue.setObjectName(u"visionPortValue")

        self.verticalLayout_9.addWidget(self.visionPortValue)


        self.visionComm.addWidget(self.visionPort)


        self.commContent.addLayout(self.visionComm)

        self.refereeComm = QVBoxLayout()
        self.refereeComm.setObjectName(u"refereeComm")
        self.refereeCommHeader = QHBoxLayout()
        self.refereeCommHeader.setObjectName(u"refereeCommHeader")
        self.refereeCommLabel = QLabel(self.layoutWidget7)
        self.refereeCommLabel.setObjectName(u"refereeCommLabel")

        self.refereeCommHeader.addWidget(self.refereeCommLabel)

        self.refereeCommSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.refereeCommHeader.addItem(self.refereeCommSpacer)

        self.refereeCommStatus = QLabel(self.layoutWidget7)
        self.refereeCommStatus.setObjectName(u"refereeCommStatus")
        self.refereeCommStatus.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.refereeCommHeader.addWidget(self.refereeCommStatus)


        self.refereeComm.addLayout(self.refereeCommHeader)

        self.refereePort = QFrame(self.layoutWidget7)
        self.refereePort.setObjectName(u"refereePort")
        self.refereePort.setFrameShape(QFrame.Shape.StyledPanel)
        self.refereePort.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.refereePort)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.refereePortValue = QLabel(self.refereePort)
        self.refereePortValue.setObjectName(u"refereePortValue")

        self.verticalLayout_10.addWidget(self.refereePortValue)


        self.refereeComm.addWidget(self.refereePort)


        self.commContent.addLayout(self.refereeComm)

        self.transComm = QVBoxLayout()
        self.transComm.setObjectName(u"transComm")
        self.transCommHeader = QHBoxLayout()
        self.transCommHeader.setObjectName(u"transCommHeader")
        self.transCommLabel = QLabel(self.layoutWidget7)
        self.transCommLabel.setObjectName(u"transCommLabel")

        self.transCommHeader.addWidget(self.transCommLabel)

        self.transCommSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.transCommHeader.addItem(self.transCommSpacer)

        self.transCommStatus = QLabel(self.layoutWidget7)
        self.transCommStatus.setObjectName(u"transCommStatus")
        self.transCommStatus.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.transCommHeader.addWidget(self.transCommStatus)


        self.transComm.addLayout(self.transCommHeader)

        self.transPort = QFrame(self.layoutWidget7)
        self.transPort.setObjectName(u"transPort")
        self.transPort.setFrameShape(QFrame.Shape.StyledPanel)
        self.transPort.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.transPort)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.transPortValue = QLabel(self.transPort)
        self.transPortValue.setObjectName(u"transPortValue")

        self.verticalLayout_11.addWidget(self.transPortValue)


        self.transComm.addWidget(self.transPort)


        self.commContent.addLayout(self.transComm)


        self.commInfo.addLayout(self.commContent)

        self.widget2 = QWidget(self.sysTab)
        self.widget2.setObjectName(u"widget2")
        self.widget2.setGeometry(QRect(10, 100, 521, 471))
        self.display = QVBoxLayout(self.widget2)
        self.display.setObjectName(u"display")
        self.display.setContentsMargins(0, 0, 0, 0)
        self.image = QLabel(self.widget2)
        self.image.setObjectName(u"image")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.image.sizePolicy().hasHeightForWidth())
        self.image.setSizePolicy(sizePolicy1)
        self.image.setMouseTracking(False)
        self.image.setLineWidth(0)
        self.image.setPixmap(QPixmap(u"assets/display.png"))
        self.image.setScaledContents(True)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.display.addWidget(self.image)

        self.displayControls = QHBoxLayout()
        self.displayControls.setObjectName(u"displayControls")
        self.controlButtons = QHBoxLayout()
        self.controlButtons.setSpacing(0)
        self.controlButtons.setObjectName(u"controlButtons")
        self.prevButton = QPushButton(self.widget2)
        self.prevButton.setObjectName(u"prevButton")
        sizePolicy.setHeightForWidth(self.prevButton.sizePolicy().hasHeightForWidth())
        self.prevButton.setSizePolicy(sizePolicy)
        self.prevButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon = QIcon()
        icon.addFile(u"assets/icons/prev.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.prevButton.setIcon(icon)
        self.prevButton.setIconSize(QSize(25, 20))
        self.prevButton.setFlat(True)

        self.controlButtons.addWidget(self.prevButton)

        self.stopButton = QPushButton(self.widget2)
        self.stopButton.setObjectName(u"stopButton")
        sizePolicy.setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(sizePolicy)
        self.stopButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(u"assets/icons/stop_red.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.stopButton.setIcon(icon1)
        self.stopButton.setIconSize(QSize(25, 20))
        self.stopButton.setFlat(True)

        self.controlButtons.addWidget(self.stopButton)

        self.playButton = QPushButton(self.widget2)
        self.playButton.setObjectName(u"playButton")
        sizePolicy.setHeightForWidth(self.playButton.sizePolicy().hasHeightForWidth())
        self.playButton.setSizePolicy(sizePolicy)
        self.playButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon2 = QIcon()
        icon2.addFile(u"assets/icons/play_gray.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.playButton.setIcon(icon2)
        self.playButton.setIconSize(QSize(25, 20))
        self.playButton.setFlat(True)

        self.controlButtons.addWidget(self.playButton)

        self.nextButton = QPushButton(self.widget2)
        self.nextButton.setObjectName(u"nextButton")
        sizePolicy.setHeightForWidth(self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(sizePolicy)
        self.nextButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon3 = QIcon()
        icon3.addFile(u"assets/icons/next.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.nextButton.setIcon(icon3)
        self.nextButton.setIconSize(QSize(25, 20))
        self.nextButton.setFlat(True)

        self.controlButtons.addWidget(self.nextButton)


        self.displayControls.addLayout(self.controlButtons)

        self.displaySpeedSpinner = QDoubleSpinBox(self.widget2)
        self.displaySpeedSpinner.setObjectName(u"displaySpeedSpinner")
        sizePolicy.setHeightForWidth(self.displaySpeedSpinner.sizePolicy().hasHeightForWidth())
        self.displaySpeedSpinner.setSizePolicy(sizePolicy)
        self.displaySpeedSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.displaySpeedSpinner.setDecimals(1)
        self.displaySpeedSpinner.setMaximum(5.000000000000000)
        self.displaySpeedSpinner.setSingleStep(0.500000000000000)

        self.displayControls.addWidget(self.displaySpeedSpinner)

        self.fieldDirections = QHBoxLayout()
        self.fieldDirections.setObjectName(u"fieldDirections")
        self.teamSideDirection = QLabel(self.widget2)
        self.teamSideDirection.setObjectName(u"teamSideDirection")

        self.fieldDirections.addWidget(self.teamSideDirection)

        self.teamSideArrow = QLabel(self.widget2)
        self.teamSideArrow.setObjectName(u"teamSideArrow")
        sizePolicy.setHeightForWidth(self.teamSideArrow.sizePolicy().hasHeightForWidth())
        self.teamSideArrow.setSizePolicy(sizePolicy)
        self.teamSideArrow.setPixmap(QPixmap(u"assets/icons/arrow_right.svg"))
        self.teamSideArrow.setScaledContents(True)

        self.fieldDirections.addWidget(self.teamSideArrow)

        self.enemySideDirection = QLabel(self.widget2)
        self.enemySideDirection.setObjectName(u"enemySideDirection")

        self.fieldDirections.addWidget(self.enemySideDirection)


        self.displayControls.addLayout(self.fieldDirections)


        self.display.addLayout(self.displayControls)

        self.widget3 = QWidget(self.sysTab)
        self.widget3.setObjectName(u"widget3")
        self.widget3.setGeometry(QRect(10, 10, 981, 81))
        self.sysTabHeader = QHBoxLayout(self.widget3)
        self.sysTabHeader.setSpacing(3)
        self.sysTabHeader.setObjectName(u"sysTabHeader")
        self.sysTabHeader.setContentsMargins(0, 0, 0, 0)
        self.optionVision = QFrame(self.widget3)
        self.optionVision.setObjectName(u"optionVision")
        self.optionVision.setFrameShape(QFrame.Shape.StyledPanel)
        self.optionVision.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.optionVision)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(3, 3, 3, 3)
        self.vision = QVBoxLayout()
        self.vision.setObjectName(u"vision")
        self.visionLabel = QLabel(self.optionVision)
        self.visionLabel.setObjectName(u"visionLabel")
        self.visionLabel.setStyleSheet(u"")
        self.visionLabel.setScaledContents(True)

        self.vision.addWidget(self.visionLabel)

        self.visionDropdown = QComboBox(self.optionVision)
        self.visionDropdown.addItem("")
        self.visionDropdown.addItem("")
        self.visionDropdown.addItem("")
        self.visionDropdown.setObjectName(u"visionDropdown")
        self.visionDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.visionDropdown.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.visionDropdown.setStyleSheet(u"")
        self.visionDropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        self.visionDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.vision.addWidget(self.visionDropdown)


        self.horizontalLayout.addLayout(self.vision)

        self.optionVisionSpacer = QSpacerItem(30, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.optionVisionSpacer)

        self.gameOptions = QVBoxLayout()
        self.gameOptions.setObjectName(u"gameOptions")
        self.optionsLabel = QLabel(self.optionVision)
        self.optionsLabel.setObjectName(u"optionsLabel")
        self.optionsLabel.setStyleSheet(u"")
        self.optionsLabel.setScaledContents(True)

        self.gameOptions.addWidget(self.optionsLabel)

        self.optionsDropdown = QComboBox(self.optionVision)
        self.optionsDropdown.addItem("")
        self.optionsDropdown.addItem("")
        self.optionsDropdown.setObjectName(u"optionsDropdown")
        self.optionsDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.optionsDropdown.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.optionsDropdown.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        self.optionsDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.gameOptions.addWidget(self.optionsDropdown)


        self.horizontalLayout.addLayout(self.gameOptions)


        self.sysTabHeader.addWidget(self.optionVision)

        self.teamSettings = QFrame(self.widget3)
        self.teamSettings.setObjectName(u"teamSettings")
        self.teamSettings.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.teamSettings.setStyleSheet(u"")
        self.teamSettings.setFrameShape(QFrame.Shape.StyledPanel)
        self.teamSettings.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.teamSettings)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(3, 3, 3, 3)
        self.teamColorBox = QHBoxLayout()
        self.teamColorBox.setObjectName(u"teamColorBox")
        self.teamColor = QHBoxLayout()
        self.teamColor.setObjectName(u"teamColor")
        self.teamColorName = QLabel(self.teamSettings)
        self.teamColorName.setObjectName(u"teamColorName")
        self.teamColorName.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.teamColor.addWidget(self.teamColorName)

        self.teamColorFlag = QPushButton(self.teamSettings)
        self.teamColorFlag.setObjectName(u"teamColorFlag")
        self.teamColorFlag.setCursor(QCursor(Qt.PointingHandCursor))
        icon4 = QIcon()
        icon4.addFile(u"assets/icons/blue_flag.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.teamColorFlag.setIcon(icon4)
        self.teamColorFlag.setIconSize(QSize(30, 30))
        self.teamColorFlag.setFlat(True)

        self.teamColor.addWidget(self.teamColorFlag)


        self.teamColorBox.addLayout(self.teamColor)

        self.teamColorSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.teamColorBox.addItem(self.teamColorSpacer)

        self.teamColorLabel = QLabel(self.teamSettings)
        self.teamColorLabel.setObjectName(u"teamColorLabel")

        self.teamColorBox.addWidget(self.teamColorLabel)


        self.verticalLayout.addLayout(self.teamColorBox)

        self.teamSideBox = QHBoxLayout()
        self.teamSideBox.setObjectName(u"teamSideBox")
        self.teamSide = QHBoxLayout()
        self.teamSide.setObjectName(u"teamSide")
        self.teamSideName = QLabel(self.teamSettings)
        self.teamSideName.setObjectName(u"teamSideName")
        self.teamSideName.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.teamSide.addWidget(self.teamSideName)

        self.teamSideSwitch = QSlider(self.teamSettings)
        self.teamSideSwitch.setObjectName(u"teamSideSwitch")
        self.teamSideSwitch.setCursor(QCursor(Qt.PointingHandCursor))
        self.teamSideSwitch.setMaximum(1)
        self.teamSideSwitch.setOrientation(Qt.Orientation.Horizontal)

        self.teamSide.addWidget(self.teamSideSwitch)


        self.teamSideBox.addLayout(self.teamSide)

        self.teamSIdeSpacer = QSpacerItem(350, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.teamSideBox.addItem(self.teamSIdeSpacer)

        self.teamSideLabel = QLabel(self.teamSettings)
        self.teamSideLabel.setObjectName(u"teamSideLabel")

        self.teamSideBox.addWidget(self.teamSideLabel)


        self.verticalLayout.addLayout(self.teamSideBox)


        self.sysTabHeader.addWidget(self.teamSettings)

        self.execButton = QPushButton(self.widget3)
        self.execButton.setObjectName(u"execButton")
        sizePolicy.setHeightForWidth(self.execButton.sizePolicy().hasHeightForWidth())
        self.execButton.setSizePolicy(sizePolicy)
        self.execButton.setMaximumSize(QSize(130, 36))
        self.execButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.execButton.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.execButton.setAutoFillBackground(False)
        self.execButton.setStyleSheet(u"color: #fff;")
        icon5 = QIcon()
        icon5.addFile(u"assets/icons/play.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.execButton.setIcon(icon5)
        self.execButton.setCheckable(True)

        self.sysTabHeader.addWidget(self.execButton)

        self.tabWidget.addTab(self.sysTab, "")
        self.visionTab = QWidget()
        self.visionTab.setObjectName(u"visionTab")
        self.skipStepButton = QPushButton(self.visionTab)
        self.skipStepButton.setObjectName(u"skipStepButton")
        self.skipStepButton.setGeometry(QRect(720, 680, 88, 26))
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.skipStepButton.sizePolicy().hasHeightForWidth())
        self.skipStepButton.setSizePolicy(sizePolicy2)
        self.skipStepButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.skipCalibrationButton = QPushButton(self.visionTab)
        self.skipCalibrationButton.setObjectName(u"skipCalibrationButton")
        self.skipCalibrationButton.setGeometry(QRect(820, 680, 151, 26))
        self.skipCalibrationButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.stepper = QWidget(self.visionTab)
        self.stepper.setObjectName(u"stepper")
        self.stepper.setGeometry(QRect(10, 90, 981, 581))
        self.verticalLayout_3 = QVBoxLayout(self.stepper)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(-1, -1, 0, 0)
        self.stepperHeader = QHBoxLayout()
        self.stepperHeader.setObjectName(u"stepperHeader")
        self.cropFieldRadio = QGridLayout()
        self.cropFieldRadio.setObjectName(u"cropFieldRadio")
        self.cropFieldLabel = QLabel(self.stepper)
        self.cropFieldLabel.setObjectName(u"cropFieldLabel")

        self.cropFieldRadio.addWidget(self.cropFieldLabel, 0, 0, 1, 1)

        self.cropFieldButton = QRadioButton(self.stepper)
        self.cropFieldButton.setObjectName(u"cropFieldButton")
        sizePolicy.setHeightForWidth(self.cropFieldButton.sizePolicy().hasHeightForWidth())
        self.cropFieldButton.setSizePolicy(sizePolicy)
        self.cropFieldButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.cropFieldButton.setChecked(True)

        self.cropFieldRadio.addWidget(self.cropFieldButton, 1, 0, 1, 1)


        self.stepperHeader.addLayout(self.cropFieldRadio)

        self.cropInnerFieldStep = QGridLayout()
        self.cropInnerFieldStep.setObjectName(u"cropInnerFieldStep")
        self.cropInnFieldLabel = QLabel(self.stepper)
        self.cropInnFieldLabel.setObjectName(u"cropInnFieldLabel")

        self.cropInnerFieldStep.addWidget(self.cropInnFieldLabel, 0, 0, 1, 1)

        self.cropInnerFieldButton = QRadioButton(self.stepper)
        self.cropInnerFieldButton.setObjectName(u"cropInnerFieldButton")
        self.cropInnerFieldButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.cropInnerFieldButton.setChecked(False)

        self.cropInnerFieldStep.addWidget(self.cropInnerFieldButton, 1, 0, 1, 1)


        self.stepperHeader.addLayout(self.cropInnerFieldStep)

        self.segElementsStep = QGridLayout()
        self.segElementsStep.setObjectName(u"segElementsStep")
        self.segElementsLabel = QLabel(self.stepper)
        self.segElementsLabel.setObjectName(u"segElementsLabel")

        self.segElementsStep.addWidget(self.segElementsLabel, 0, 0, 1, 1)

        self.segElementsButton = QRadioButton(self.stepper)
        self.segElementsButton.setObjectName(u"segElementsButton")
        self.segElementsButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.segElementsButton.setChecked(False)

        self.segElementsStep.addWidget(self.segElementsButton, 1, 0, 1, 1)


        self.stepperHeader.addLayout(self.segElementsStep)

        self.segTeamStep = QGridLayout()
        self.segTeamStep.setObjectName(u"segTeamStep")
        self.segTeamLabel = QLabel(self.stepper)
        self.segTeamLabel.setObjectName(u"segTeamLabel")

        self.segTeamStep.addWidget(self.segTeamLabel, 0, 0, 1, 1)

        self.segTeamButton = QRadioButton(self.stepper)
        self.segTeamButton.setObjectName(u"segTeamButton")
        self.segTeamButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.segTeamButton.setChecked(False)

        self.segTeamStep.addWidget(self.segTeamButton, 1, 0, 1, 1)


        self.stepperHeader.addLayout(self.segTeamStep)

        self.segBallStep = QGridLayout()
        self.segBallStep.setObjectName(u"segBallStep")
        self.segBallLabel = QLabel(self.stepper)
        self.segBallLabel.setObjectName(u"segBallLabel")

        self.segBallStep.addWidget(self.segBallLabel, 0, 0, 1, 1)

        self.segBallButton = QRadioButton(self.stepper)
        self.segBallButton.setObjectName(u"segBallButton")
        self.segBallButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.segBallButton.setChecked(False)

        self.segBallStep.addWidget(self.segBallButton, 1, 0, 1, 1)


        self.stepperHeader.addLayout(self.segBallStep)

        self.genParamsStep = QGridLayout()
        self.genParamsStep.setObjectName(u"genParamsStep")
        self.genParamsLabel = QLabel(self.stepper)
        self.genParamsLabel.setObjectName(u"genParamsLabel")

        self.genParamsStep.addWidget(self.genParamsLabel, 0, 0, 1, 1)

        self.genParamsButton = QRadioButton(self.stepper)
        self.genParamsButton.setObjectName(u"genParamsButton")
        self.genParamsButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.genParamsButton.setChecked(False)

        self.genParamsStep.addWidget(self.genParamsButton, 1, 0, 1, 1)


        self.stepperHeader.addLayout(self.genParamsStep)


        self.verticalLayout_3.addLayout(self.stepperHeader)

        self.cropFieldStep = QFrame(self.stepper)
        self.cropFieldStep.setObjectName(u"cropFieldStep")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.cropFieldStep.sizePolicy().hasHeightForWidth())
        self.cropFieldStep.setSizePolicy(sizePolicy3)
        self.cropFieldStep.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropFieldStep.setFrameShadow(QFrame.Shadow.Raised)
        self.cropControlBox = QFrame(self.cropFieldStep)
        self.cropControlBox.setObjectName(u"cropControlBox")
        self.cropControlBox.setGeometry(QRect(540, 10, 421, 401))
        self.cropControlBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropControlBox.setFrameShadow(QFrame.Shadow.Raised)
        self.cropLabel = QLabel(self.cropControlBox)
        self.cropLabel.setObjectName(u"cropLabel")
        self.cropLabel.setGeometry(QRect(10, 10, 91, 18))
        self.nextStepButton = QPushButton(self.cropControlBox)
        self.nextStepButton.setObjectName(u"nextStepButton")
        self.nextStepButton.setGeometry(QRect(70, 150, 271, 26))
        self.widget4 = QWidget(self.cropControlBox)
        self.widget4.setObjectName(u"widget4")
        self.widget4.setGeometry(QRect(10, 40, 211, 20))
        self.showCrop = QHBoxLayout(self.widget4)
        self.showCrop.setObjectName(u"showCrop")
        self.showCrop.setContentsMargins(0, 0, 0, 0)
        self.showCropLabel = QLabel(self.widget4)
        self.showCropLabel.setObjectName(u"showCropLabel")

        self.showCrop.addWidget(self.showCropLabel)

        self.showCropSlider = QSlider(self.widget4)
        self.showCropSlider.setObjectName(u"showCropSlider")
        sizePolicy.setHeightForWidth(self.showCropSlider.sizePolicy().hasHeightForWidth())
        self.showCropSlider.setSizePolicy(sizePolicy)
        self.showCropSlider.setMaximumSize(QSize(30, 15))
        self.showCropSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.showCropSlider.setMaximum(1)
        self.showCropSlider.setOrientation(Qt.Orientation.Horizontal)

        self.showCrop.addWidget(self.showCropSlider)

        self.widget5 = QWidget(self.cropControlBox)
        self.widget5.setObjectName(u"widget5")
        self.widget5.setGeometry(QRect(10, 70, 211, 68))
        self.cropControls = QVBoxLayout(self.widget5)
        self.cropControls.setObjectName(u"cropControls")
        self.cropControls.setContentsMargins(0, 0, 0, 0)
        self.cropControlsLabel = QLabel(self.widget5)
        self.cropControlsLabel.setObjectName(u"cropControlsLabel")

        self.cropControls.addWidget(self.cropControlsLabel)

        self.cropControlButtons = QHBoxLayout()
        self.cropControlButtons.setObjectName(u"cropControlButtons")
        self.cropRedoButton = QPushButton(self.widget5)
        self.cropRedoButton.setObjectName(u"cropRedoButton")
        sizePolicy.setHeightForWidth(self.cropRedoButton.sizePolicy().hasHeightForWidth())
        self.cropRedoButton.setSizePolicy(sizePolicy)
        self.cropRedoButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon6 = QIcon()
        icon6.addFile(u"assets/icons/redo.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.cropRedoButton.setIcon(icon6)
        self.cropRedoButton.setIconSize(QSize(30, 38))

        self.cropControlButtons.addWidget(self.cropRedoButton)

        self.cropEraseButton = QPushButton(self.widget5)
        self.cropEraseButton.setObjectName(u"cropEraseButton")
        sizePolicy.setHeightForWidth(self.cropEraseButton.sizePolicy().hasHeightForWidth())
        self.cropEraseButton.setSizePolicy(sizePolicy)
        self.cropEraseButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon7 = QIcon()
        icon7.addFile(u"assets/icons/eraser.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.cropEraseButton.setIcon(icon7)
        self.cropEraseButton.setIconSize(QSize(30, 38))

        self.cropControlButtons.addWidget(self.cropEraseButton)


        self.cropControls.addLayout(self.cropControlButtons)

        self.widget6 = QWidget(self.cropFieldStep)
        self.widget6.setObjectName(u"widget6")
        self.widget6.setGeometry(QRect(10, 10, 521, 398))
        self.displayCrop = QVBoxLayout(self.widget6)
        self.displayCrop.setObjectName(u"displayCrop")
        self.displayCrop.setContentsMargins(0, 0, 0, 0)
        self.displayCropText = QLabel(self.widget6)
        self.displayCropText.setObjectName(u"displayCropText")

        self.displayCrop.addWidget(self.displayCropText)

        self.displayCropImage = QLabel(self.widget6)
        self.displayCropImage.setObjectName(u"displayCropImage")
        sizePolicy1.setHeightForWidth(self.displayCropImage.sizePolicy().hasHeightForWidth())
        self.displayCropImage.setSizePolicy(sizePolicy1)
        self.displayCropImage.setCursor(QCursor(Qt.PointingHandCursor))
        self.displayCropImage.setMouseTracking(True)
        self.displayCropImage.setLineWidth(0)
        self.displayCropImage.setPixmap(QPixmap(u"assets/display.png"))
        self.displayCropImage.setScaledContents(True)
        self.displayCropImage.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.displayCrop.addWidget(self.displayCropImage)


        self.verticalLayout_3.addWidget(self.cropFieldStep)

        self.widget7 = QWidget(self.visionTab)
        self.widget7.setObjectName(u"widget7")
        self.widget7.setGeometry(QRect(10, 10, 981, 71))
        self.visionTabHeader = QHBoxLayout(self.widget7)
        self.visionTabHeader.setObjectName(u"visionTabHeader")
        self.visionTabHeader.setContentsMargins(0, 0, 0, 0)
        self.visionControls = QFrame(self.widget7)
        self.visionControls.setObjectName(u"visionControls")
        self.visionControls.setFrameShape(QFrame.Shape.StyledPanel)
        self.visionControls.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.visionControls)
        self.horizontalLayout_5.setSpacing(5)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(3, 3, 3, 3)
        self.gameOptions_2 = QVBoxLayout()
        self.gameOptions_2.setObjectName(u"gameOptions_2")
        self.optionsLabel_2 = QLabel(self.visionControls)
        self.optionsLabel_2.setObjectName(u"optionsLabel_2")
        self.optionsLabel_2.setStyleSheet(u"")
        self.optionsLabel_2.setScaledContents(True)

        self.gameOptions_2.addWidget(self.optionsLabel_2)

        self.optionsDropdown_2 = QComboBox(self.visionControls)
        self.optionsDropdown_2.addItem("")
        self.optionsDropdown_2.addItem("")
        self.optionsDropdown_2.setObjectName(u"optionsDropdown_2")
        sizePolicy.setHeightForWidth(self.optionsDropdown_2.sizePolicy().hasHeightForWidth())
        self.optionsDropdown_2.setSizePolicy(sizePolicy)
        self.optionsDropdown_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.optionsDropdown_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.optionsDropdown_2.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        self.optionsDropdown_2.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.gameOptions_2.addWidget(self.optionsDropdown_2)


        self.horizontalLayout_5.addLayout(self.gameOptions_2)

        self.vision_2 = QVBoxLayout()
        self.vision_2.setObjectName(u"vision_2")
        self.visionLabel_2 = QLabel(self.visionControls)
        self.visionLabel_2.setObjectName(u"visionLabel_2")
        self.visionLabel_2.setStyleSheet(u"")
        self.visionLabel_2.setScaledContents(True)

        self.vision_2.addWidget(self.visionLabel_2)

        self.visionDropdown_2 = QComboBox(self.visionControls)
        self.visionDropdown_2.addItem("")
        self.visionDropdown_2.addItem("")
        self.visionDropdown_2.addItem("")
        self.visionDropdown_2.setObjectName(u"visionDropdown_2")
        sizePolicy.setHeightForWidth(self.visionDropdown_2.sizePolicy().hasHeightForWidth())
        self.visionDropdown_2.setSizePolicy(sizePolicy)
        self.visionDropdown_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.visionDropdown_2.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.visionDropdown_2.setStyleSheet(u"")
        self.visionDropdown_2.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        self.visionDropdown_2.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.vision_2.addWidget(self.visionDropdown_2)


        self.horizontalLayout_5.addLayout(self.vision_2)

        self.camera = QVBoxLayout()
        self.camera.setObjectName(u"camera")
        self.cameraLabel = QLabel(self.visionControls)
        self.cameraLabel.setObjectName(u"cameraLabel")

        self.camera.addWidget(self.cameraLabel)

        self.cameraDropdown = QComboBox(self.visionControls)
        self.cameraDropdown.addItem("")
        self.cameraDropdown.addItem("")
        self.cameraDropdown.setObjectName(u"cameraDropdown")
        sizePolicy.setHeightForWidth(self.cameraDropdown.sizePolicy().hasHeightForWidth())
        self.cameraDropdown.setSizePolicy(sizePolicy)
        self.cameraDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.camera.addWidget(self.cameraDropdown)


        self.horizontalLayout_5.addLayout(self.camera)


        self.visionTabHeader.addWidget(self.visionControls)

        self.highLevelVisionButton = QPushButton(self.widget7)
        self.highLevelVisionButton.setObjectName(u"highLevelVisionButton")
        sizePolicy.setHeightForWidth(self.highLevelVisionButton.sizePolicy().hasHeightForWidth())
        self.highLevelVisionButton.setSizePolicy(sizePolicy)
        self.highLevelVisionButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.highLevelVisionButton.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.highLevelVisionButton.setAutoFillBackground(False)
        self.highLevelVisionButton.setStyleSheet(u"")
        self.highLevelVisionButton.setCheckable(True)

        self.visionTabHeader.addWidget(self.highLevelVisionButton)

        self.tabWidget.addTab(self.visionTab, "")
        self.ballnetTab = QWidget()
        self.ballnetTab.setObjectName(u"ballnetTab")
        self.tabWidget.addTab(self.ballnetTab, "")
        self.layoutWidget8 = QWidget(self.centralwidget)
        self.layoutWidget8.setObjectName(u"layoutWidget8")
        self.layoutWidget8.setGeometry(QRect(870, 0, 128, 41))
        self.windowButtons = QHBoxLayout(self.layoutWidget8)
        self.windowButtons.setObjectName(u"windowButtons")
        self.windowButtons.setContentsMargins(0, 0, 0, 0)
        self.minButton = QPushButton(self.layoutWidget8)
        self.minButton.setObjectName(u"minButton")
        self.minButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.minButton.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.minButton.setStyleSheet(u"")
        icon8 = QIcon()
        icon8.addFile(u"assets/icons/min.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.minButton.setIcon(icon8)
        self.minButton.setIconSize(QSize(26, 26))
        self.minButton.setFlat(False)

        self.windowButtons.addWidget(self.minButton)

        self.resizeButton = QPushButton(self.layoutWidget8)
        self.resizeButton.setObjectName(u"resizeButton")
        self.resizeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.resizeButton.setStyleSheet(u"")
        icon9 = QIcon()
        icon9.addFile(u"assets/icons/max.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.resizeButton.setIcon(icon9)
        self.resizeButton.setIconSize(QSize(26, 26))

        self.windowButtons.addWidget(self.resizeButton)

        self.closeButton = QPushButton(self.layoutWidget8)
        self.closeButton.setObjectName(u"closeButton")
        self.closeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.closeButton.setStyleSheet(u"")
        icon10 = QIcon()
        icon10.addFile(u"assets/icons/close.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.closeButton.setIcon(icon10)
        self.closeButton.setIconSize(QSize(26, 26))

        self.windowButtons.addWidget(self.closeButton)

        self.layoutWidget9 = QWidget(self.centralwidget)
        self.layoutWidget9.setObjectName(u"layoutWidget9")
        self.layoutWidget9.setGeometry(QRect(0, 0, 871, 41))
        self.header = QHBoxLayout(self.layoutWidget9)
        self.header.setObjectName(u"header")
        self.header.setContentsMargins(0, 0, 0, 0)
        self.logo = QLabel(self.layoutWidget9)
        self.logo.setObjectName(u"logo")
        self.logo.setPixmap(QPixmap(u"assets/UnBall_Logo_Preto.svg"))

        self.header.addWidget(self.logo)

        self.titleLabel = QLabel(self.layoutWidget9)
        self.titleLabel.setObjectName(u"titleLabel")
        self.titleLabel.setScaledContents(True)

        self.header.addWidget(self.titleLabel)

        self.headerSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.header.addItem(self.headerSpacer)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.closeButton.clicked.connect(MainWindow.close)
        self.minButton.clicked.connect(MainWindow.showMinimized)
        self.teamSideSwitch.valueChanged.connect(self.teamSideName.setNum)
        self.teamColorFlag.clicked["bool"].connect(self.teamColorName.update)
        self.cropFieldButton.clicked["bool"].connect(self.cropFieldStep.setVisible)

        self.tabWidget.setCurrentIndex(1)
        self.sysTabWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.robotRole.setItemText(0, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.robotRole.setItemText(1, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.robotRole.setItemText(2, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.robotRole.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.commLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Comunica\u00e7\u00e3o:</span></p></body></html>", None))
        self.commStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; color:#003b22;\">OK</span></p></body></html>", None))
        self.robotImage.setText("")
        self.robotCharge.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700; color:#494848;\">Bateria:</span><span style=\" font-size:8pt; color:#494848;\"> 100%</span></p></body></html>", None))
        self.idLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">ID</span></p></body></html>", None))
        self.idValue.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">0</span></p></body></html>", None))
        self.posLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Posi\u00e7\u00e3o</span></p></body></html>", None))
        self.xPos.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">x: 0.0m</span></p></body></html>", None))
        self.yPos.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">y: 0.0m</span></p></body></html>", None))
        self.orientationLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Orienta\u00e7\u00e3o</span></p></body></html>", None))
        self.orientationValue.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">th: 0.0 graus</span></p></body></html>", None))
        self.rSpeedLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Velocidade lida</span></p></body></html>", None))
        self.rVSpeed.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">v: 0.0 m/s</span></p></body></html>", None))
        self.rWSpeed.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">w: 0.0 rad/s</span></p></body></html>", None))
        self.sSpeedLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Velocidade enviada</span></p></body></html>", None))
        self.sVSpeed.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">v: 0.0 m/s</span></p></body></html>", None))
        self.sWSpeed.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">w: 0.0 rad/s</span></p></body></html>", None))
        self.freqLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Frequ\u00eancia de envio</span></p></body></html>", None))
        self.freqValue.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">2 MHz</span></p></body></html>", None))
        self.debugTitle.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">Configura\u00e7\u00e3o dos rob\u00f4s</span></p></body></html>", None))
        self.nRobots.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">3 rob\u00f4s identificados</span></p></body></html>", None))
        self.robotRole_2.setItemText(0, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.robotRole_2.setItemText(1, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.robotRole_2.setItemText(2, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.robotRole_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.commLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Comunica\u00e7\u00e3o:</span></p></body></html>", None))
        self.commStatus_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; color:#003b22;\">OK</span></p></body></html>", None))
        self.robotImage_2.setText("")
        self.robotCharge_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700; color:#494848;\">Bateria:</span><span style=\" font-size:8pt; color:#494848;\"> 100%</span></p></body></html>", None))
        self.idLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">ID</span></p></body></html>", None))
        self.idValue_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">0</span></p></body></html>", None))
        self.posLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Posi\u00e7\u00e3o</span></p></body></html>", None))
        self.xPos_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">x: 0.0m</span></p></body></html>", None))
        self.yPos_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">y: 0.0m</span></p></body></html>", None))
        self.orientationLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Orienta\u00e7\u00e3o</span></p></body></html>", None))
        self.orientationValue_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">th: 0.0 graus</span></p></body></html>", None))
        self.rSpeedLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Velocidade lida</span></p></body></html>", None))
        self.rVSpeed_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">v: 0.0 m/s</span></p></body></html>", None))
        self.rWSpeed_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">w: 0.0 rad/s</span></p></body></html>", None))
        self.sSpeedLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Velocidade enviada</span></p></body></html>", None))
        self.sVSpeed_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">v: 0.0 m/s</span></p></body></html>", None))
        self.sWSpeed_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">w: 0.0 rad/s</span></p></body></html>", None))
        self.freqLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Frequ\u00eancia de envio</span></p></body></html>", None))
        self.freqValue_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">2 MHz</span></p></body></html>", None))
        self.sysTabWidget.setTabText(self.sysTabWidget.indexOf(self.debugTab), QCoreApplication.translate("MainWindow", u"Debug", None))
        self.viewUvfLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Visualizar Campo UVF</span></p></body></html>", None))
        self.pointsNumberLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; color:#494848;\">Quantidade de pontos</span></p></body></html>", None))
        self.uvfViewIcon.setText("")
        self.selectFieldLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Selecionar Campo</span></p></body></html>", None))
        self.selectFieldDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Nenhum", None))

        self.selectFieldDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Nenhum", None))
        self.robotUvfTitle.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700; color:#494848;\">UVF</span></p></body></html>", None))
        self.lastPointName.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Ponto final selecion\u00e1vel</span></p></body></html>", None))
        self.lastPointDescription.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; color:#494848;\">Habilita a sele\u00e7\u00e3o manual de ponto final das trajet\u00f3rias</span></p></body></html>", None))
        self.uvfRadiusLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Raio</span></p></body></html>", None))
        self.uvfConstLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Constante de suaviza\u00e7\u00e3o</span></p></body></html>", None))
        self.uvfUniConstLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Constante de suaviza\u00e7\u00e3o unidirecional</span></p></body></html>", None))
        self.robotUvfId.setItemText(0, QCoreApplication.translate("MainWindow", u"0", None))
        self.robotUvfId.setItemText(1, QCoreApplication.translate("MainWindow", u"1", None))
        self.robotUvfId.setItemText(2, QCoreApplication.translate("MainWindow", u"2", None))

        self.robotUvfId.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Rob\u00f4 ID", None))
        self.sysTabWidget.setTabText(self.sysTabWidget.indexOf(self.navigationTab), QCoreApplication.translate("MainWindow", u"Navega\u00e7\u00e3o", None))
        self.decisionTitle.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">Forma\u00e7\u00e3o das entidades</span></p></body></html>", None))
        self.decisionDescrption.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Selecione o tipo de forma\u00e7\u00e3o</span></p></body></html>", None))
        self.staticEntitiesRadio.setText(QCoreApplication.translate("MainWindow", u"Entidades Est\u00e1ticas", None))
        self.robot0RoleLabel.setText(QCoreApplication.translate("MainWindow", u"Rob\u00f4 0", None))
        self.robot0RoleDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.robot0RoleDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.robot0RoleDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.robot0RoleDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.robot1RoleLabel.setText(QCoreApplication.translate("MainWindow", u"Rob\u00f4 1", None))
        self.robot1RoleSpinner.setItemText(0, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.robot1RoleSpinner.setItemText(1, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.robot1RoleSpinner.setItemText(2, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.robot1RoleSpinner.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.robot2RoleLabel.setText(QCoreApplication.translate("MainWindow", u"Rob\u00f4  2", None))
        self.robot2RoleDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.robot2RoleDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.robot2RoleDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.robot2RoleDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.dynamicEntitiesRadio.setText(QCoreApplication.translate("MainWindow", u"Entidades Din\u00e2micas", None))
        self.virtualJudgePosLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Usar posicionamento do juiz virtual</span></p></body></html>", None))
        self.manualJudgePosLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Usar posicionamento manual</span></p></body></html>", None))
        self.selectPosLabel.setText(QCoreApplication.translate("MainWindow", u"Selecionar posicionamento", None))
        self.selectPosDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Free Ball", None))
        self.selectPosDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Kick Off", None))
        self.selectPosDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"Penalti", None))

        self.selectPosDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Free Ball", None))
        self.posTiming.setText(QCoreApplication.translate("MainWindow", u"Tempo tentando se posicionar: 8s", None))
        self.selectPosTitle.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">Posicionamento</span></p></body></html>", None))
        self.sysTabWidget.setTabText(self.sysTabWidget.indexOf(self.decisionTab), QCoreApplication.translate("MainWindow", u"Decis\u00e3o", None))
        self.ballPosLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Posi\u00e7\u00e3o</span></p></body></html>", None))
        self.xBallPos.setText(QCoreApplication.translate("MainWindow", u"x: 0.0 m", None))
        self.yBallPos.setText(QCoreApplication.translate("MainWindow", u"y: 0.0 m", None))
        self.speedInfoLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Velocidade</span></p></body></html>", None))
        self.speedValue.setText(QCoreApplication.translate("MainWindow", u"3 m/s", None))
        self.accLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Acelera\u00e7\u00e3o</span></p></body></html>", None))
        self.accValue.setText(QCoreApplication.translate("MainWindow", u"3 m/s\u00b2", None))
        self.ballTitle.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">Bola</span></p></body></html>", None))
        self.ballStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#003b22;\">Status</span></p></body></html>", None))
        self.logLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">Erros e Warnings</span></p></body></html>", None))
        self.logContent.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">[Fonte do erro]: descri\u00e7\u00e3o</span></p><p><span style=\" font-size:8pt;\">[Fonte do erro]: descri\u00e7\u00e3o</span></p><p><span style=\" font-size:8pt;\">[Fonte do erro]: descri\u00e7\u00e3o</span></p><p><span style=\" font-size:8pt;\">[Fonte do erro]: descri\u00e7\u00e3o</span></p></body></html>", None))
        self.commTitle.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">Comunica\u00e7\u00e3o</span></p></body></html>", None))
        self.visionCommLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Vis\u00e3o</span></p></body></html>", None))
        self.visionCommStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"right\"><span style=\" font-size:8pt; color:#003b22;\">Status</span></p></body></html>", None))
        self.visionPortValue.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Porta</p></body></html>", None))
        self.refereeCommLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Referee</span></p></body></html>", None))
        self.refereeCommStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"right\"><span style=\" font-size:8pt; color:#003b22;\">Status</span></p></body></html>", None))
        self.refereePortValue.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Porta</p></body></html>", None))
        self.transCommLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt; font-weight:700;\">Transmissor</span></p></body></html>", None))
        self.transCommStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"right\"><span style=\" font-size:8pt; color:#003b22;\">Status</span></p></body></html>", None))
        self.transPortValue.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Porta</p></body></html>", None))
        self.image.setText("")
        self.prevButton.setText("")
        self.stopButton.setText("")
        self.playButton.setText("")
        self.nextButton.setText("")
        self.displaySpeedSpinner.setSuffix(QCoreApplication.translate("MainWindow", u"x", None))
        self.teamSideDirection.setText(QCoreApplication.translate("MainWindow", u"Lado aliado", None))
        self.teamSideArrow.setText("")
        self.enemySideDirection.setText(QCoreApplication.translate("MainWindow", u"Lado inimigo", None))
        self.visionLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700; color:#494848;\">Vis\u00e3o</span></p></body></html>", None))
        self.visionDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"MainVision", None))
        self.visionDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"FiraSim", None))
        self.visionDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"YOLO", None))

        self.optionsLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700; color:#494848;\">Op\u00e7\u00f5es</span></p></body></html>", None))
        self.optionsDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"F\u00edsico", None))
        self.optionsDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Simulado", None))

        self.teamColorName.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Azul</span></p></body></html>", None))
        self.teamColorFlag.setText("")
        self.teamColorLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700; color:#494848;\">Cor do Time Aliado</span></p></body></html>", None))
        self.teamSideName.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#494848;\">Direito</span></p></body></html>", None))
        self.teamSideLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700; color:#494848;\">Lado Aliado</span></p></body></html>", None))
        self.execButton.setText(QCoreApplication.translate("MainWindow", u"Executar", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.sysTab), QCoreApplication.translate("MainWindow", u"Informa\u00e7\u00f5es do Sistema", None))
        self.skipStepButton.setText(QCoreApplication.translate("MainWindow", u"Pular etapa", None))
        self.skipCalibrationButton.setText(QCoreApplication.translate("MainWindow", u"Pular calibra\u00e7\u00e3o", None))
        self.cropFieldLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Cortar campo</p></body></html>", None))
        self.cropFieldButton.setText("")
        self.cropInnFieldLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Cortar campo interno</p></body></html>", None))
        self.cropInnerFieldButton.setText("")
        self.segElementsLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Segmentar elementos</p></body></html>", None))
        self.segElementsButton.setText("")
        self.segTeamLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Segmentar time</p></body></html>", None))
        self.segTeamButton.setText("")
        self.segBallLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Segmentar bola</p></body></html>", None))
        self.segBallButton.setText("")
        self.genParamsLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\">Par\u00e2metros gerais</p></body></html>", None))
        self.genParamsButton.setText("")
        self.cropLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">Ferramentas</span></p></body></html>", None))
        self.nextStepButton.setText(QCoreApplication.translate("MainWindow", u"Avan\u00e7ar", None))
        self.showCropLabel.setText(QCoreApplication.translate("MainWindow", u"Mostrar campo cortado", None))
        self.cropControlsLabel.setText(QCoreApplication.translate("MainWindow", u"A\u00e7\u00f5es:", None))
        self.cropRedoButton.setText("")
        self.cropEraseButton.setText("")
        self.displayCropText.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">Selecione 4 pontos</span></p></body></html>", None))
        self.displayCropImage.setText("")
        self.optionsLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700; color:#494848;\">Op\u00e7\u00f5es</span></p></body></html>", None))
        self.optionsDropdown_2.setItemText(0, QCoreApplication.translate("MainWindow", u"F\u00edsico", None))
        self.optionsDropdown_2.setItemText(1, QCoreApplication.translate("MainWindow", u"Simulado", None))

        self.visionLabel_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700; color:#494848;\">Vis\u00e3o</span></p></body></html>", None))
        self.visionDropdown_2.setItemText(0, QCoreApplication.translate("MainWindow", u"MainVision", None))
        self.visionDropdown_2.setItemText(1, QCoreApplication.translate("MainWindow", u"FiraSim", None))
        self.visionDropdown_2.setItemText(2, QCoreApplication.translate("MainWindow", u"YOLO", None))

        self.cameraLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-weight:700;\">C\u00e2mera</span></p></body></html>", None))
        self.cameraDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"LogiTech", None))
        self.cameraDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Outra", None))

        self.highLevelVisionButton.setText(QCoreApplication.translate("MainWindow", u"Vis\u00e3o de Alto N\u00edvel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.visionTab), QCoreApplication.translate("MainWindow", u"Calibra\u00e7\u00e3o da Vis\u00e3o", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ballnetTab), QCoreApplication.translate("MainWindow", u"Ballnet", None))
        self.minButton.setText("")
        self.resizeButton.setText("")
        self.closeButton.setText("")
        self.logo.setText("")
        self.titleLabel.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:20pt; color:#494848;\">Very Small Size - UnBall</span></p></body></html>", None))
    # retranslateUi

