from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform, QPen)
from PySide6.QtWidgets import (QAbstractScrollArea, QAbstractSpinBox, QComboBox,
    QDoubleSpinBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLayout, QMainWindow, QPushButton,
    QRadioButton, QScrollArea, QSizePolicy, QSlider,
    QSpacerItem, QSpinBox, QTabWidget, QVBoxLayout,
    QWidget)

from editor import CropEditor, SegmentEditor
from core import SizePolicies, Fonts
from header import QHeader
from layouts import RobotLayout, Robot

class Ui_MainWindow(object):
    def setupUi(self, MainWindow: QWidget, robots: list[Robot]):
        self.robots = robots        
        ############################################
        # Icons
        ############################################
        icon = QIcon()
        icon.addFile(u"assets/icons/UnBall_Logo_Preto.svg", QSize(), QIcon.Normal, QIcon.Off)
        blueFlagIcon = QIcon()
        blueFlagIcon.addFile(u"assets/icons/blue_flag.svg", QSize(), QIcon.Normal, QIcon.Off)
        playIcon = QIcon()
        playIcon.addFile(u"assets/icons/play.svg", QSize(), QIcon.Normal, QIcon.Off)
        prevIcon = QIcon()
        prevIcon.addFile(u"assets/icons/prev.svg", QSize(), QIcon.Normal, QIcon.Off)
        redStopIcon = QIcon()
        redStopIcon.addFile(u"assets/icons/stop_red.svg", QSize(), QIcon.Normal, QIcon.Off)
        
        #############################################
        # Main Window
        #############################################
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(900, 700)
        MainWindow.setMinimumSize(QSize(800, 600))
        MainWindow.setMaximumSize(QSize(1366, 1166))
        MainWindow.setWindowIcon(icon)

        
        ############################################
        # Central Widget
        ############################################
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        
        
        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(SizePolicies["Expanding_Preferred"])
        
        self.centralwidget.setMinimumSize(QSize(800, 600))
        self.centralwidget.setMaximumSize(QSize(1366, 1166))
        self.centralwidget.setMouseTracking(True)
        self.centralwidget.setStyleSheet(u"* {\n"
"	padding: 0px;\n"
"	margin: 0px;\n"
"	color: #494848;\n"
"	background: #a5a5a5;\n"
"	font-family: \"Roboto\", sans-serif;\n"
"}\n"
"")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        
        #############################################
        # Header Widget
        #############################################
        self.header = QHeader(self.centralwidget)
        self.verticalLayout.addWidget(self.header, 0, Qt.AlignmentFlag.AlignTop)
        
        ###################################
        # Body Section
        ###################################
        self.body = QFrame(self.centralwidget)
        self.body.setObjectName(u"body")
        self.body.setFrameShape(QFrame.Shape.StyledPanel)
        self.body.setFrameShadow(QFrame.Shadow.Raised)
        

        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.body.sizePolicy().hasHeightForWidth())
        self.body.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.verticalLayout_2 = QVBoxLayout(self.body)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        
        self.appContents = QTabWidget(self.body)
        self.appContents.setObjectName(u"appContents")
        self.appContents.setCursor(QCursor(Qt.ArrowCursor))
        self.appContents.setStyleSheet(u"")
        self.appContents.setTabPosition(QTabWidget.TabPosition.West)
        self.appContents.setTabShape(QTabWidget.TabShape.Rounded)
        self.appContents.setIconSize(QSize(24, 24))
        
        ############################################
        # System Information Tab
        ############################################
        self.sysInfoTab = QWidget()
        self.sysInfoTab.setObjectName(u"sysInfoTab")
        
        self.sysInfoHeader = QFrame(self.sysInfoTab)
        self.sysInfoHeader.setObjectName(u"sysInfoHeader")
        self.sysInfoHeader.setGeometry(QRect(0, 0, 861, 71))
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.sysInfoHeader.sizePolicy().hasHeightForWidth())
        self.sysInfoHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.sysInfoHeader.setMinimumSize(QSize(761, 0))
        self.sysInfoHeader.setMaximumSize(QSize(1332, 16777215))
        self.sysInfoHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.sysInfoHeader.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_9 = QHBoxLayout(self.sysInfoHeader)
        self.horizontalLayout_9.setSpacing(10)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(10, 10, 10, 10)
        
        self.gameSettings = QFrame(self.sysInfoHeader)
        self.gameSettings.setObjectName(u"gameSettings")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.gameSettings.sizePolicy().hasHeightForWidth())
        self.gameSettings.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.gameSettings.setMinimumSize(QSize(0, 51))
        self.gameSettings.setMaximumSize(QSize(350, 51))
        self.gameSettings.setFrameShape(QFrame.Shape.StyledPanel)
        self.gameSettings.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_4 = QHBoxLayout(self.gameSettings)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(3, 3, 3, 3)
        
        self.gameOptions = QVBoxLayout()
        self.gameOptions.setSpacing(0)
        self.gameOptions.setObjectName(u"gameOptions")
        
        self.gameOptionsLabel = QLabel(self.gameSettings)
        self.gameOptionsLabel.setObjectName(u"gameOptionsLabel")
        
        self.gameOptionsLabel.setFont(Fonts["font2"])
        self.gameOptionsLabel.setScaledContents(True)
        self.gameOptionsLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gameOptions.addWidget(self.gameOptionsLabel)

        self.gameOptionsDropdown = QComboBox(self.gameSettings)
        self.gameOptionsDropdown.setObjectName(u"gameOptionsDropdown")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.gameOptionsDropdown.sizePolicy().hasHeightForWidth())
        self.gameOptionsDropdown.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.gameOptionsDropdown.setFont(Fonts["font3"])
        self.gameOptionsDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.gameOptionsDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.gameOptionsDropdown.setFrame(True)
        self.gameOptionsDropdown.addItem("")
        self.gameOptionsDropdown.addItem("")

        self.gameOptions.addWidget(self.gameOptionsDropdown)

        self.horizontalLayout_4.addLayout(self.gameOptions)

        self.visionOptions = QVBoxLayout()
        self.visionOptions.setSpacing(0)
        self.visionOptions.setObjectName(u"visionOptions")
        
        self.visionOptionsLabel = QLabel(self.gameSettings)
        self.visionOptionsLabel.setObjectName(u"visionOptionsLabel")
        self.visionOptionsLabel.setFont(Fonts["font2"])

        self.visionOptions.addWidget(self.visionOptionsLabel)

        self.visionOptionsDropdown = QComboBox(self.gameSettings)
        self.visionOptionsDropdown.setObjectName(u"visionOptionsDropdown")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.visionOptionsDropdown.sizePolicy().hasHeightForWidth())
        self.visionOptionsDropdown.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.visionOptionsDropdown.setFont(Fonts["font3"])
        self.visionOptionsDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.visionOptionsDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.visionOptionsDropdown.setFrame(True)
        self.visionOptionsDropdown.addItem("")
        self.visionOptionsDropdown.addItem("")
        self.visionOptionsDropdown.addItem("")

        self.visionOptions.addWidget(self.visionOptionsDropdown)

        self.horizontalLayout_4.addLayout(self.visionOptions)

        self.horizontalLayout_9.addWidget(self.gameSettings)

        self.myTeamInfo = QFrame(self.sysInfoHeader)
        self.myTeamInfo.setObjectName(u"myTeamInfo")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.myTeamInfo.sizePolicy().hasHeightForWidth())
        self.myTeamInfo.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.myTeamInfo.setMaximumSize(QSize(350, 16777215))
        
        self.myTeamInfo.setFrameShape(QFrame.Shape.StyledPanel)
        self.myTeamInfo.setFrameShadow(QFrame.Shadow.Raised)
        
        self.verticalLayout_5 = QVBoxLayout(self.myTeamInfo)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(3, 3, 3, 3)
        
        self.myTeamColor = QFrame(self.myTeamInfo)
        self.myTeamColor.setObjectName(u"myTeamColor")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.myTeamColor.sizePolicy().hasHeightForWidth())
        self.myTeamColor.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.myTeamColor.setFrameShape(QFrame.Shape.NoFrame)
        self.myTeamColor.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_8 = QHBoxLayout(self.myTeamColor)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        
        self.myTeamSideText = QLabel(self.myTeamColor)
        self.myTeamSideText.setObjectName(u"myTeamSideText")
        self.myTeamSideText.setFont(Fonts["font2"])
        self.myTeamSideText.setScaledContents(True)

        self.horizontalLayout_8.addWidget(self.myTeamSideText)

        self.colorSpacer = QSpacerItem(207, 16, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.colorSpacer)

        self.teamColorControls = QFrame(self.myTeamColor)
        self.teamColorControls.setObjectName(u"teamColorControls")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.teamColorControls.sizePolicy().hasHeightForWidth())
        self.teamColorControls.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.teamColorControls.setFrameShape(QFrame.Shape.NoFrame)
        self.teamColorControls.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_5 = QHBoxLayout(self.teamColorControls)
        self.horizontalLayout_5.setSpacing(3)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        
        self.switchTeamColorButton = QPushButton(self.teamColorControls)
        self.switchTeamColorButton.setObjectName(u"switchTeamColorButton")
        self.switchTeamColorButton.setCursor(QCursor(Qt.PointingHandCursor))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.switchTeamColorButton.sizePolicy().hasHeightForWidth())
        self.switchTeamColorButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.switchTeamColorButton.setIcon(blueFlagIcon)
        self.switchTeamColorButton.setIconSize(QSize(24, 22))
        self.switchTeamColorButton.setCheckable(True)
        self.switchTeamColorButton.setFlat(True)

        self.horizontalLayout_5.addWidget(self.switchTeamColorButton)

        self.myTeamColorLabel = QLabel(self.teamColorControls)
        self.myTeamColorLabel.setObjectName(u"myTeamColorLabel")
        self.myTeamColorLabel.setFont(Fonts["font3"])

        self.horizontalLayout_5.addWidget(self.myTeamColorLabel)

        self.horizontalLayout_8.addWidget(self.teamColorControls)

        self.verticalLayout_5.addWidget(self.myTeamColor)

        self.myTeamSide = QFrame(self.myTeamInfo)
        self.myTeamSide.setObjectName(u"myTeamSide")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.myTeamSide.sizePolicy().hasHeightForWidth())
        self.myTeamSide.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.myTeamSide.setFrameShape(QFrame.Shape.NoFrame)
        self.myTeamSide.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_7 = QHBoxLayout(self.myTeamSide)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        
        self.myTeamSideTitle = QLabel(self.myTeamSide)
        self.myTeamSideTitle.setObjectName(u"myTeamSideTitle")
        self.myTeamSideTitle.setFont(Fonts["font2"])

        self.horizontalLayout_7.addWidget(self.myTeamSideTitle)

        self.sideSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.sideSpacer)

        self.myTeamSideControl = QFrame(self.myTeamSide)
        self.myTeamSideControl.setObjectName(u"myTeamSideControl")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.myTeamSideControl.sizePolicy().hasHeightForWidth())
        self.myTeamSideControl.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.myTeamSideControl.setFrameShape(QFrame.Shape.NoFrame)
        self.myTeamSideControl.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_6 = QHBoxLayout(self.myTeamSideControl)
        self.horizontalLayout_6.setSpacing(10)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        
        self.myTeamSideSwitch = QSlider(self.myTeamSideControl)
        self.myTeamSideSwitch.setObjectName(u"myTeamSideSwitch")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.myTeamSideSwitch.sizePolicy().hasHeightForWidth())
        self.myTeamSideSwitch.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.myTeamSideSwitch.setMinimumSize(QSize(41, 0))
        self.myTeamSideSwitch.setMaximumSize(QSize(41, 16777215))
        self.myTeamSideSwitch.setCursor(QCursor(Qt.PointingHandCursor))
        self.myTeamSideSwitch.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.myTeamSideSwitch.setMaximum(1)
        self.myTeamSideSwitch.setValue(1)
        self.myTeamSideSwitch.setSliderPosition(1)
        self.myTeamSideSwitch.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_6.addWidget(self.myTeamSideSwitch)

        self.myTeamSideLabel = QLabel(self.myTeamSideControl)
        self.myTeamSideLabel.setObjectName(u"myTeamSideLabel")
        self.myTeamSideLabel.setFont(Fonts["font3"])

        self.horizontalLayout_6.addWidget(self.myTeamSideLabel)

        self.horizontalLayout_7.addWidget(self.myTeamSideControl)

        self.verticalLayout_5.addWidget(self.myTeamSide)

        self.horizontalLayout_9.addWidget(self.myTeamInfo)

        self.sysInfoSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.sysInfoSpacer)

        self.execStart = QFrame(self.sysInfoHeader)
        self.execStart.setObjectName(u"execStart")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.execStart.sizePolicy().hasHeightForWidth())
        self.execStart.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.execStart.setMinimumSize(QSize(105, 35))
        self.execStart.setMaximumSize(QSize(105, 35))
        self.execStart.setCursor(QCursor(Qt.PointingHandCursor))
        self.execStart.setFrameShape(QFrame.Shape.NoFrame)
        self.execStart.setFrameShadow(QFrame.Shadow.Raised)
        
        self.execButton = QPushButton(self.execStart)
        self.execButton.setObjectName(u"execButton")
        self.execButton.setGeometry(QRect(0, 0, 101, 31))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.execButton.sizePolicy().hasHeightForWidth())
        self.execButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.execButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.execButton.setStyleSheet(u"color: #fff; background: #3E7239;")
        
        self.execButton.setIcon(playIcon)
        self.execButton.setIconSize(QSize(16, 16))
        self.execButton.setCheckable(True)
        
        self.execButtonShadow = QFrame(self.execStart)
        self.execButtonShadow.setObjectName(u"execButtonShadow")
        self.execButtonShadow.setGeometry(QRect(3, 3, 101, 31))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.execButtonShadow.sizePolicy().hasHeightForWidth())
        self.execButtonShadow.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.execButtonShadow.setStyleSheet(u"background: #8D8D8D; border-radius: 6px;")
        self.execButtonShadow.setFrameShape(QFrame.Shape.NoFrame)
        self.execButtonShadow.setFrameShadow(QFrame.Shadow.Plain)
        self.execButtonShadow.raise_()
        self.execButton.raise_()

        self.horizontalLayout_9.addWidget(self.execStart)
        self.horizontalLayout_9.setStretch(0, 1)
        self.horizontalLayout_9.setStretch(1, 2)
        
        self.displayBox = QFrame(self.sysInfoTab)
        self.displayBox.setObjectName(u"displayBox")
        self.displayBox.setGeometry(QRect(10, 80, 401, 301))
        self.displayBox.setMinimumSize(QSize(351, 265))
        self.displayBox.setMaximumSize(QSize(560, 419))
        self.displayBox.setFrameShape(QFrame.Shape.NoFrame)
        self.displayBox.setFrameShadow(QFrame.Shadow.Raised)
        
        self.verticalLayout_7 = QVBoxLayout(self.displayBox)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        
        self.imageLayout = QFrame(self.displayBox)
        self.imageLayout.setObjectName(u"imageLayout")
        self.imageLayout.setMinimumSize(QSize(351, 265))
        self.imageLayout.setMaximumSize(QSize(560, 419))
        self.imageLayout.setFrameShape(QFrame.Shape.NoFrame)
        self.imageLayout.setFrameShadow(QFrame.Shadow.Raised)
        
        self.verticalLayout_6 = QVBoxLayout(self.imageLayout)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        
        self.imageDisplay = QLabel(self.imageLayout)
        self.imageDisplay.setObjectName(u"imageDisplay")
        
        SizePolicies["Preferred_Preferred"].setHeightForWidth(self.imageDisplay.sizePolicy().hasHeightForWidth())
        self.imageDisplay.setSizePolicy(SizePolicies["Preferred_Preferred"])
        
        self.imageDisplay.setMinimumSize(QSize(351, 265))
        self.imageDisplay.setMaximumSize(QSize(560, 445))
        self.imageDisplay.setBaseSize(QSize(351, 265))
        self.imageDisplay.setPixmap(QPixmap(u"assets/display.png"))
        self.imageDisplay.setScaledContents(True)
        self.imageDisplay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_6.addWidget(self.imageDisplay)

        self.verticalLayout_7.addWidget(self.imageLayout)

        self.displaySettings = QFrame(self.displayBox)
        self.displaySettings.setObjectName(u"displaySettings")
        
        SizePolicies["Preferred_Fixed"].setHeightForWidth(self.displaySettings.sizePolicy().hasHeightForWidth())
        self.displaySettings.setSizePolicy(SizePolicies["Preferred_Fixed"])
        
        self.displaySettings.setMinimumSize(QSize(351, 0))
        self.displaySettings.setFrameShape(QFrame.Shape.NoFrame)
        self.displaySettings.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_3 = QHBoxLayout(self.displaySettings)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        
        self.controlButtons = QHBoxLayout()
        self.controlButtons.setSpacing(0)
        self.controlButtons.setObjectName(u"controlButtons")
        
        self.prevButton = QPushButton(self.displaySettings)
        self.prevButton.setObjectName(u"prevButton")
        self.prevButton.setCursor(QCursor(Qt.PointingHandCursor))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.prevButton.sizePolicy().hasHeightForWidth())
        self.prevButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.prevButton.setIcon(prevIcon)
        self.prevButton.setFlat(True)

        self.controlButtons.addWidget(self.prevButton)

        self.stopButton = QPushButton(self.displaySettings)
        self.stopButton.setObjectName(u"stopButton")
        self.stopButton.setCursor(QCursor(Qt.PointingHandCursor))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.stopButton.setIcon(redStopIcon)
        self.stopButton.setFlat(True)

        self.controlButtons.addWidget(self.stopButton)

        self.playButton = QPushButton(self.displaySettings)
        self.playButton.setObjectName(u"playButton")
        self.playButton.setCursor(QCursor(Qt.PointingHandCursor))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.playButton.sizePolicy().hasHeightForWidth())
        self.playButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        icon8 = QIcon()
        icon8.addFile(u"assets/icons/play_gray.svg", QSize(), QIcon.Normal, QIcon.Off)
        
        self.playButton.setIcon(icon8)
        self.playButton.setFlat(True)

        self.controlButtons.addWidget(self.playButton)

        self.nextButton = QPushButton(self.displaySettings)
        self.nextButton.setObjectName(u"nextButton")
        self.nextButton.setCursor(QCursor(Qt.PointingHandCursor))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.nextButton.sizePolicy().hasHeightForWidth())
        self.nextButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        icon9 = QIcon()
        icon9.addFile(u"assets/icons/next.svg", QSize(), QIcon.Normal, QIcon.Off)
        
        self.nextButton.setIcon(icon9)
        self.nextButton.setFlat(True)

        self.controlButtons.addWidget(self.nextButton)

        self.horizontalLayout_3.addLayout(self.controlButtons)

        self.speedSpinBox = QDoubleSpinBox(self.displaySettings)
        self.speedSpinBox.setObjectName(u"speedSpinBox")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.speedSpinBox.sizePolicy().hasHeightForWidth())
        self.speedSpinBox.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.speedSpinBox.setMinimumSize(QSize(43, 20))
        self.speedSpinBox.setMaximumSize(QSize(45, 20))
        self.speedSpinBox.setFont(Fonts["font3"])
        self.speedSpinBox.setCursor(QCursor(Qt.PointingHandCursor))
        self.speedSpinBox.setWrapping(False)
        self.speedSpinBox.setFrame(True)
        self.speedSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.speedSpinBox.setProperty("showGroupSeparator", False)
        self.speedSpinBox.setDecimals(1)
        self.speedSpinBox.setMinimum(1.0)
        self.speedSpinBox.setMaximum(3.0)
        self.speedSpinBox.setSingleStep(0.5)

        self.horizontalLayout_3.addWidget(self.speedSpinBox)

        self.displaySpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.displaySpacer)

        self.fieldSideDisplay = QFrame(self.displaySettings)
        self.fieldSideDisplay.setObjectName(u"fieldSideDisplay")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.fieldSideDisplay.sizePolicy().hasHeightForWidth())
        self.fieldSideDisplay.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.fieldSideDisplay.setMinimumSize(QSize(216, 26))
        self.fieldSideDisplay.setMaximumSize(QSize(560, 26))
        self.fieldSideDisplay.setFrameShape(QFrame.Shape.NoFrame)
        self.fieldSideDisplay.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_2 = QHBoxLayout(self.fieldSideDisplay)
        self.horizontalLayout_2.setSpacing(3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        
        self.leftTeamSideLabel = QLabel(self.fieldSideDisplay)
        self.leftTeamSideLabel.setObjectName(u"leftTeamSideLabel")
        self.leftTeamSideLabel.setFont(Fonts["font3"])
        self.leftTeamSideLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.leftTeamSideLabel)

        self.fieldSideDirection = QLabel(self.fieldSideDisplay)
        self.fieldSideDirection.setObjectName(u"fieldSideDirection")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.fieldSideDirection.sizePolicy().hasHeightForWidth())
        self.fieldSideDirection.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.fieldSideDirection.setPixmap(QPixmap(u"assets/icons/arrow_left.svg"))
        self.fieldSideDirection.setScaledContents(True)
        self.fieldSideDirection.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.fieldSideDirection)

        self.rightTeamSideLabel = QLabel(self.fieldSideDisplay)
        self.rightTeamSideLabel.setObjectName(u"rightTeamSideLabel")
        
        SizePolicies["Preferred_Preferred"].setHeightForWidth(self.rightTeamSideLabel.sizePolicy().hasHeightForWidth())
        self.rightTeamSideLabel.setSizePolicy(SizePolicies["Preferred_Preferred"])
        
        self.rightTeamSideLabel.setFont(Fonts["font3"])
        self.rightTeamSideLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_2.addWidget(self.rightTeamSideLabel)

        self.horizontalLayout_3.addWidget(self.fieldSideDisplay)

        self.verticalLayout_7.addWidget(self.displaySettings)

        self.tabWidget = QTabWidget(self.sysInfoTab)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(420, 80, 431, 301))
        self.tabWidget.setMinimumSize(QSize(310, 0))
        self.tabWidget.setFont(Fonts["font3"])
        
        self.debugTab = QWidget()
        self.debugTab.setObjectName(u"debugTab")
        
        self.debugScrollArea = QScrollArea(self.debugTab)
        self.debugScrollArea.setObjectName(u"debugScrollArea")
        self.debugScrollArea.setGeometry(QRect(0, 0, 441, 271))
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.debugScrollArea.sizePolicy().hasHeightForWidth())
        self.debugScrollArea.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.debugScrollArea.setMinimumSize(QSize(310, 0))
        self.debugScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.debugScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.debugScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.debugScrollArea.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.debugScrollArea.setWidgetResizable(True)
        self.debugScrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.debugScrollContents = QWidget()
        self.debugScrollContents.setObjectName(u"debugScrollContents")
        self.debugScrollContents.setGeometry(QRect(0, 0, 427, 515))
        
        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.debugScrollContents.sizePolicy().hasHeightForWidth())
        self.debugScrollContents.setSizePolicy(SizePolicies["Expanding_Preferred"])
        
        self.verticalLayout_17 = QVBoxLayout(self.debugScrollContents)
        self.verticalLayout_17.setSpacing(6)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.verticalLayout_17.setContentsMargins(6, 6, 6, 6)
        
        self.configHeader = QFrame(self.debugScrollContents)
        self.configHeader.setObjectName(u"configHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.configHeader.sizePolicy().hasHeightForWidth())
        self.configHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.configHeader.setMinimumSize(QSize(350, 0))
        self.configHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.configHeader.setFrameShadow(QFrame.Shadow.Raised)
        
        self.horizontalLayout_23 = QHBoxLayout(self.configHeader)
        self.horizontalLayout_23.setSpacing(0)
        self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
        self.horizontalLayout_23.setContentsMargins(0, 0, 0, 0)
        
        self.debugTabTitle = QLabel(self.configHeader)
        self.debugTabTitle.setObjectName(u"debugTabTitle")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.debugTabTitle.sizePolicy().hasHeightForWidth())
        self.debugTabTitle.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.debugTabTitle.setFont(Fonts["font2"])
        self.debugTabTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_23.addWidget(self.debugTabTitle)

        self.configHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_23.addItem(self.configHeaderSpacer)

        self.robotsFound = QLabel(self.configHeader)
        self.robotsFound.setObjectName(u"robotsFound")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.robotsFound.sizePolicy().hasHeightForWidth())
        self.robotsFound.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.robotsFound.setMinimumSize(QSize(110, 0))
        self.robotsFound.setMaximumSize(QSize(110, 16777215))
        self.robotsFound.setFont(Fonts["font3"])
        self.robotsFound.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_23.addWidget(self.robotsFound)

        self.verticalLayout_17.addWidget(self.configHeader)
        
        #######################################
        # Robot Layouts
        #######################################
        
        self.robotLayouts = {}

        for i, robot in enumerate(self.robots):
                robotInfoBox = RobotLayout(self.debugScrollContents, robot)
                self.robotLayouts[f"robot{i}Layout"] = robotInfoBox
                self.verticalLayout_17.addWidget(robotInfoBox)
        ########################################
        
        self.debugSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_17.addItem(self.debugSpacer)

        self.debugScrollArea.setWidget(self.debugScrollContents)
        self.tabWidget.addTab(self.debugTab, "")
        self.navTab = QWidget()
        self.navTab.setObjectName(u"navTab")
        self.navScrollArea = QScrollArea(self.navTab)
        self.navScrollArea.setObjectName(u"navScrollArea")
        self.navScrollArea.setGeometry(QRect(0, 0, 441, 271))
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.navScrollArea.sizePolicy().hasHeightForWidth())
        self.navScrollArea.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.navScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.navScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.navScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.navScrollArea.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored)
        self.navScrollArea.setWidgetResizable(True)
        self.navScrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.navScrollContents = QWidget()
        self.navScrollContents.setObjectName(u"navScrollContents")
        self.navScrollContents.setGeometry(QRect(0, 0, 427, 341))
        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.navScrollContents.sizePolicy().hasHeightForWidth())
        self.navScrollContents.setSizePolicy(SizePolicies["Expanding_Preferred"])
        self.verticalLayout_25 = QVBoxLayout(self.navScrollContents)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.verticalLayout_25.setContentsMargins(6, 6, 6, 6)
        self.navHeader = QFrame(self.navScrollContents)
        self.navHeader.setObjectName(u"navHeader")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.navHeader.sizePolicy().hasHeightForWidth())
        self.navHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.navHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.navHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_21 = QHBoxLayout(self.navHeader)
        self.horizontalLayout_21.setSpacing(0)
        self.horizontalLayout_21.setObjectName(u"horizontalLayout_21")
        self.horizontalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.navRobotId = QComboBox(self.navHeader)
        self.navRobotId.addItem("")
        self.navRobotId.addItem("")
        self.navRobotId.addItem("")
        self.navRobotId.addItem("")
        self.navRobotId.setObjectName(u"navRobotId")
        self.navRobotId.setFont(Fonts["font3"])
        self.navRobotId.setCursor(QCursor(Qt.PointingHandCursor))
        self.navRobotId.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.horizontalLayout_21.addWidget(self.navRobotId)

        self.navRobotSpacer = QSpacerItem(276, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_21.addItem(self.navRobotSpacer)


        self.verticalLayout_25.addWidget(self.navHeader)

        self.uvfTitle = QFrame(self.navScrollContents)
        self.uvfTitle.setObjectName(u"uvfTitle")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.uvfTitle.sizePolicy().hasHeightForWidth())
        self.uvfTitle.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.uvfTitle.setFrameShape(QFrame.Shape.NoFrame)
        self.uvfTitle.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_24 = QHBoxLayout(self.uvfTitle)
        self.horizontalLayout_24.setSpacing(0)
        self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
        self.horizontalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.uvfLabel = QLabel(self.uvfTitle)
        self.uvfLabel.setObjectName(u"uvfLabel")
        
        self.uvfLabel.setFont(Fonts["font4"])
        self.uvfLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_24.addWidget(self.uvfLabel)

        self.uvfTitleSpacer = QSpacerItem(310, 16, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_24.addItem(self.uvfTitleSpacer)


        self.verticalLayout_25.addWidget(self.uvfTitle)

        self.viewUvf = QFrame(self.navScrollContents)
        self.viewUvf.setObjectName(u"viewUvf")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.viewUvf.sizePolicy().hasHeightForWidth())
        self.viewUvf.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.viewUvf.setFrameShape(QFrame.Shape.StyledPanel)
        self.viewUvf.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_22 = QHBoxLayout(self.viewUvf)
        self.horizontalLayout_22.setSpacing(0)
        self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
        self.horizontalLayout_22.setContentsMargins(3, 3, 3, 3)
        self.viewUvfFieldLabel = QLabel(self.viewUvf)
        self.viewUvfFieldLabel.setObjectName(u"viewUvfFieldLabel")
        self.viewUvfFieldLabel.setFont(Fonts["font3"])
        self.viewUvfFieldLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_22.addWidget(self.viewUvfFieldLabel)

        self.viewUvfSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_22.addItem(self.viewUvfSpacer)

        self.pointsNumber = QVBoxLayout()
        self.pointsNumber.setObjectName(u"pointsNumber")
        self.pointsLabel = QLabel(self.viewUvf)
        self.pointsLabel.setObjectName(u"pointsLabel")
        
        self.pointsLabel.setFont(Fonts["font5"])
        self.pointsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.pointsNumber.addWidget(self.pointsLabel)

        self.pointsSpinBox = QSpinBox(self.viewUvf)
        self.pointsSpinBox.setObjectName(u"pointsSpinBox")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.pointsSpinBox.sizePolicy().hasHeightForWidth())
        self.pointsSpinBox.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.pointsSpinBox.setCursor(QCursor(Qt.PointingHandCursor))
        self.pointsSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pointsSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.pointsSpinBox.setMaximum(10)

        self.pointsNumber.addWidget(self.pointsSpinBox)


        self.horizontalLayout_22.addLayout(self.pointsNumber)

        self.viewUvfButton = QPushButton(self.viewUvf)
        self.viewUvfButton.setObjectName(u"viewUvfButton")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.viewUvfButton.sizePolicy().hasHeightForWidth())
        self.viewUvfButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.viewUvfButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon10 = QIcon()
        icon10.addFile(u"assets/icons/mdi_eye.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.viewUvfButton.setIcon(icon10)
        self.viewUvfButton.setIconSize(QSize(24, 24))
        self.viewUvfButton.setCheckable(True)
        self.viewUvfButton.setFlat(True)

        self.horizontalLayout_22.addWidget(self.viewUvfButton, 0, Qt.AlignmentFlag.AlignBottom)


        self.verticalLayout_25.addWidget(self.viewUvf)

        self.finalPoint = QFrame(self.navScrollContents)
        self.finalPoint.setObjectName(u"finalPoint")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.finalPoint.sizePolicy().hasHeightForWidth())
        self.finalPoint.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.finalPoint.setFrameShape(QFrame.Shape.StyledPanel)
        self.finalPoint.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_35 = QHBoxLayout(self.finalPoint)
        self.horizontalLayout_35.setSpacing(3)
        self.horizontalLayout_35.setObjectName(u"horizontalLayout_35")
        self.horizontalLayout_35.setContentsMargins(3, 3, 3, 3)
        self.finalPointLabel = QLabel(self.finalPoint)
        self.finalPointLabel.setObjectName(u"finalPointLabel")
        self.finalPointLabel.setFont(Fonts["font3"])
        self.finalPointLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_35.addWidget(self.finalPointLabel)

        self.finalPointSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_35.addItem(self.finalPointSpacer)

        self.finalPointSwitch = QSlider(self.finalPoint)
        self.finalPointSwitch.setObjectName(u"finalPointSwitch")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.finalPointSwitch.sizePolicy().hasHeightForWidth())
        self.finalPointSwitch.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.finalPointSwitch.setMinimumSize(QSize(41, 0))
        self.finalPointSwitch.setMaximumSize(QSize(41, 16777215))
        self.finalPointSwitch.setCursor(QCursor(Qt.PointingHandCursor))
        self.finalPointSwitch.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.finalPointSwitch.setMaximum(1)
        self.finalPointSwitch.setPageStep(1)
        self.finalPointSwitch.setValue(0)
        self.finalPointSwitch.setSliderPosition(0)
        self.finalPointSwitch.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_35.addWidget(self.finalPointSwitch)


        self.verticalLayout_25.addWidget(self.finalPoint)

        self.selectField = QFrame(self.navScrollContents)
        self.selectField.setObjectName(u"selectField")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.selectField.sizePolicy().hasHeightForWidth())
        self.selectField.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.selectField.setFrameShape(QFrame.Shape.StyledPanel)
        self.selectField.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_34 = QHBoxLayout(self.selectField)
        self.horizontalLayout_34.setSpacing(3)
        self.horizontalLayout_34.setObjectName(u"horizontalLayout_34")
        self.horizontalLayout_34.setContentsMargins(3, 3, 3, 3)
        self.selectFieldLabel = QLabel(self.selectField)
        self.selectFieldLabel.setObjectName(u"selectFieldLabel")
        self.selectFieldLabel.setFont(Fonts["font3"])
        self.selectFieldLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_34.addWidget(self.selectFieldLabel)

        self.selectFieldSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_34.addItem(self.selectFieldSpacer)

        self.selectFieldDropdown = QComboBox(self.selectField)
        self.selectFieldDropdown.addItem("")
        self.selectFieldDropdown.setObjectName(u"selectFieldDropdown")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.selectFieldDropdown.sizePolicy().hasHeightForWidth())
        self.selectFieldDropdown.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.selectFieldDropdown.setFont(Fonts["font3"])
        self.selectFieldDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.selectFieldDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.selectFieldDropdown.setFrame(True)
        self.selectFieldDropdown.setModelColumn(0)

        self.horizontalLayout_34.addWidget(self.selectFieldDropdown)


        self.verticalLayout_25.addWidget(self.selectField)

        self.uvfSettings = QGridLayout()
        self.uvfSettings.setObjectName(u"uvfSettings")
        self.uvfSettings.setHorizontalSpacing(0)
        self.uvfSettings.setVerticalSpacing(6)
        self.uvfSettings.setContentsMargins(3, 3, 3, 3)
        self.radius = QFrame(self.navScrollContents)
        self.radius.setObjectName(u"radius")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.radius.sizePolicy().hasHeightForWidth())
        self.radius.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.radius.setFrameShape(QFrame.Shape.NoFrame)
        self.radius.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_15 = QVBoxLayout(self.radius)
        self.verticalLayout_15.setSpacing(0)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.radiusHeader = QHBoxLayout()
        self.radiusHeader.setSpacing(0)
        self.radiusHeader.setObjectName(u"radiusHeader")
        self.radiusHeaderLabel = QLabel(self.radius)
        self.radiusHeaderLabel.setObjectName(u"radiusHeaderLabel")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.radiusHeaderLabel.sizePolicy().hasHeightForWidth())
        self.radiusHeaderLabel.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.radiusHeaderLabel.setFont(Fonts["font3"])
        self.radiusHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.radiusHeader.addWidget(self.radiusHeaderLabel)

        self.radiusHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.radiusHeader.addItem(self.radiusHeaderSpacer)


        self.verticalLayout_15.addLayout(self.radiusHeader)

        self.radiusSpinBox = QSpinBox(self.radius)
        self.radiusSpinBox.setObjectName(u"radiusSpinBox")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.radiusSpinBox.sizePolicy().hasHeightForWidth())
        self.radiusSpinBox.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.radiusSpinBox.setCursor(QCursor(Qt.PointingHandCursor))
        self.radiusSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.radiusSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.radiusSpinBox.setMaximum(10)

        self.verticalLayout_15.addWidget(self.radiusSpinBox)


        self.uvfSettings.addWidget(self.radius, 0, 0, 1, 1)

        self.kSmooth = QFrame(self.navScrollContents)
        self.kSmooth.setObjectName(u"kSmooth")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.kSmooth.sizePolicy().hasHeightForWidth())
        self.kSmooth.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.kSmooth.setFrameShape(QFrame.Shape.NoFrame)
        self.kSmooth.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_16 = QVBoxLayout(self.kSmooth)
        self.verticalLayout_16.setSpacing(0)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.kSmoothHeader = QHBoxLayout()
        self.kSmoothHeader.setSpacing(0)
        self.kSmoothHeader.setObjectName(u"kSmoothHeader")
        self.kSmoothHeaderLabel = QLabel(self.kSmooth)
        self.kSmoothHeaderLabel.setObjectName(u"kSmoothHeaderLabel")
        self.kSmoothHeaderLabel.setFont(Fonts["font3"])
        self.kSmoothHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.kSmoothHeader.addWidget(self.kSmoothHeaderLabel)

        self.kSmoothHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.kSmoothHeader.addItem(self.kSmoothHeaderSpacer)


        self.verticalLayout_16.addLayout(self.kSmoothHeader)

        self.kSmoothSpinBox = QSpinBox(self.kSmooth)
        self.kSmoothSpinBox.setObjectName(u"kSmoothSpinBox")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.kSmoothSpinBox.sizePolicy().hasHeightForWidth())
        self.kSmoothSpinBox.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.kSmoothSpinBox.setCursor(QCursor(Qt.PointingHandCursor))
        self.kSmoothSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.kSmoothSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.kSmoothSpinBox.setMaximum(10)

        self.verticalLayout_16.addWidget(self.kSmoothSpinBox)


        self.uvfSettings.addWidget(self.kSmooth, 0, 1, 1, 1)

        self.uniKSmooth = QFrame(self.navScrollContents)
        self.uniKSmooth.setObjectName(u"uniKSmooth")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.uniKSmooth.sizePolicy().hasHeightForWidth())
        self.uniKSmooth.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.uniKSmooth.setFrameShape(QFrame.Shape.NoFrame)
        self.uniKSmooth.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_24 = QVBoxLayout(self.uniKSmooth)
        self.verticalLayout_24.setSpacing(0)
        self.verticalLayout_24.setObjectName(u"verticalLayout_24")
        self.verticalLayout_24.setContentsMargins(0, 0, 0, 0)
        self.uniKSmoothHeader = QHBoxLayout()
        self.uniKSmoothHeader.setSpacing(0)
        self.uniKSmoothHeader.setObjectName(u"uniKSmoothHeader")
        self.uniKSmoothHeaderLabel = QLabel(self.uniKSmooth)
        self.uniKSmoothHeaderLabel.setObjectName(u"uniKSmoothHeaderLabel")
        self.uniKSmoothHeaderLabel.setFont(Fonts["font3"])
        self.uniKSmoothHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.uniKSmoothHeader.addWidget(self.uniKSmoothHeaderLabel)

        self.uniKSmoothHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.uniKSmoothHeader.addItem(self.uniKSmoothHeaderSpacer)


        self.verticalLayout_24.addLayout(self.uniKSmoothHeader)

        self.uniKSmoothSpinBox = QSpinBox(self.uniKSmooth)
        self.uniKSmoothSpinBox.setObjectName(u"uniKSmoothSpinBox")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.uniKSmoothSpinBox.sizePolicy().hasHeightForWidth())
        self.uniKSmoothSpinBox.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.uniKSmoothSpinBox.setCursor(QCursor(Qt.PointingHandCursor))
        self.uniKSmoothSpinBox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.uniKSmoothSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.uniKSmoothSpinBox.setMaximum(10)

        self.verticalLayout_24.addWidget(self.uniKSmoothSpinBox)


        self.uvfSettings.addWidget(self.uniKSmooth, 1, 0, 1, 2)


        self.verticalLayout_25.addLayout(self.uvfSettings)

        self.allUvf = QFrame(self.navScrollContents)
        self.allUvf.setObjectName(u"allUvf")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.allUvf.sizePolicy().hasHeightForWidth())
        self.allUvf.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.allUvf.setFrameShape(QFrame.Shape.StyledPanel)
        self.allUvf.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_36 = QHBoxLayout(self.allUvf)
        self.horizontalLayout_36.setSpacing(0)
        self.horizontalLayout_36.setObjectName(u"horizontalLayout_36")
        self.horizontalLayout_36.setContentsMargins(3, 3, 3, 3)
        self.allUvfLabel = QLabel(self.allUvf)
        self.allUvfLabel.setObjectName(u"allUvfLabel")
        self.allUvfLabel.setFont(Fonts["font3"])
        self.allUvfLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_36.addWidget(self.allUvfLabel)

        self.allUvfSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_36.addItem(self.allUvfSpacer)

        self.allUvfSiwtch = QSlider(self.allUvf)
        self.allUvfSiwtch.setObjectName(u"allUvfSiwtch")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.allUvfSiwtch.sizePolicy().hasHeightForWidth())
        self.allUvfSiwtch.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.allUvfSiwtch.setMinimumSize(QSize(41, 0))
        self.allUvfSiwtch.setMaximumSize(QSize(41, 16777215))
        self.allUvfSiwtch.setCursor(QCursor(Qt.PointingHandCursor))
        self.allUvfSiwtch.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.allUvfSiwtch.setMaximum(1)
        self.allUvfSiwtch.setPageStep(1)
        self.allUvfSiwtch.setValue(0)
        self.allUvfSiwtch.setSliderPosition(0)
        self.allUvfSiwtch.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_36.addWidget(self.allUvfSiwtch)


        self.verticalLayout_25.addWidget(self.allUvf)

        self.navScrollArea.setWidget(self.navScrollContents)
        self.tabWidget.addTab(self.navTab, "")
        self.decisionTab = QWidget()
        self.decisionTab.setObjectName(u"decisionTab")
        self.decScrollArea = QScrollArea(self.decisionTab)
        self.decScrollArea.setObjectName(u"decScrollArea")
        self.decScrollArea.setGeometry(QRect(0, 0, 441, 271))
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.decScrollArea.sizePolicy().hasHeightForWidth())
        self.decScrollArea.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.decScrollArea.setMinimumSize(QSize(310, 0))
        self.decScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.decScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.decScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.decScrollArea.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.decScrollArea.setWidgetResizable(True)
        self.decScrollArea.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.decScrollContents = QWidget()
        self.decScrollContents.setObjectName(u"decScrollContents")
        self.decScrollContents.setGeometry(QRect(0, 0, 427, 271))
        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.decScrollContents.sizePolicy().hasHeightForWidth())
        self.decScrollContents.setSizePolicy(SizePolicies["Expanding_Preferred"])
        self.verticalLayout_26 = QVBoxLayout(self.decScrollContents)
        self.verticalLayout_26.setSpacing(6)
        self.verticalLayout_26.setObjectName(u"verticalLayout_26")
        self.verticalLayout_26.setContentsMargins(6, 6, 6, 6)
        self.decHeader = QFrame(self.decScrollContents)
        self.decHeader.setObjectName(u"decHeader")
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.decHeader.sizePolicy().hasHeightForWidth())
        self.decHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        self.decHeader.setMinimumSize(QSize(350, 0))
        self.decHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.decHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_38 = QHBoxLayout(self.decHeader)
        self.horizontalLayout_38.setSpacing(0)
        self.horizontalLayout_38.setObjectName(u"horizontalLayout_38")
        self.horizontalLayout_38.setContentsMargins(0, 0, 0, 0)
        self.decTabTitle = QLabel(self.decHeader)
        self.decTabTitle.setObjectName(u"decTabTitle")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.decTabTitle.sizePolicy().hasHeightForWidth())
        self.decTabTitle.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.decTabTitle.setFont(Fonts["font2"])
        self.decTabTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_38.addWidget(self.decTabTitle)

        self.decHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_38.addItem(self.decHeaderSpacer)

        self.verticalLayout_26.addWidget(self.decHeader)

        self.staticEntitiesContents = QHBoxLayout()
        self.staticEntitiesContents.setSpacing(0)
        self.staticEntitiesContents.setObjectName(u"staticEntitiesContents")
        self.chooseEntitites = QVBoxLayout()
        self.chooseEntitites.setObjectName(u"chooseEntitites")
        self.staticEntitiesRadio = QRadioButton(self.decScrollContents)
        self.staticEntitiesRadio.setObjectName(u"staticEntitiesRadio")
        self.staticEntitiesRadio.setFont(Fonts["font3"])

        self.chooseEntitites.addWidget(self.staticEntitiesRadio)

        self.dynEntitiesRadio = QRadioButton(self.decScrollContents)
        self.dynEntitiesRadio.setObjectName(u"dynEntitiesRadio")
        self.dynEntitiesRadio.setFont(Fonts["font3"])
        self.dynEntitiesRadio.setChecked(True)

        self.chooseEntitites.addWidget(self.dynEntitiesRadio)


        self.staticEntitiesContents.addLayout(self.chooseEntitites)

        self.staticRobotsBox = QFrame(self.decScrollContents)
        self.staticRobotsBox.setObjectName(u"staticRobotsBox")
        self.staticRobotsBox.setFrameShape(QFrame.Shape.NoFrame)
        self.staticRobotsBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_33 = QVBoxLayout(self.staticRobotsBox)
        self.verticalLayout_33.setObjectName(u"verticalLayout_33")
        self.verticalLayout_33.setContentsMargins(0, 0, 0, 0)
        self.staticRobot = QHBoxLayout()
        self.staticRobot.setObjectName(u"staticRobot")
        self.staticRobotLabel = QLabel(self.staticRobotsBox)
        self.staticRobotLabel.setObjectName(u"staticRobotLabel")
        self.staticRobotLabel.setFont(Fonts["font2"])
        self.staticRobotLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.staticRobot.addWidget(self.staticRobotLabel)

        self.staticRobotDropdown = QComboBox(self.staticRobotsBox)
        self.staticRobotDropdown.addItem("")
        self.staticRobotDropdown.addItem("")
        self.staticRobotDropdown.addItem("")
        self.staticRobotDropdown.addItem("")
        self.staticRobotDropdown.setObjectName(u"staticRobotDropdown")
        self.staticRobotDropdown.setFont(Fonts["font3"])
        self.staticRobotDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.staticRobotDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.staticRobot.addWidget(self.staticRobotDropdown)

        self.verticalLayout_33.addLayout(self.staticRobot)

        self.staticRobot_2 = QHBoxLayout()
        self.staticRobot_2.setObjectName(u"staticRobot_2")
        self.staticRobotLabel_2 = QLabel(self.staticRobotsBox)
        self.staticRobotLabel_2.setObjectName(u"staticRobotLabel_2")
        self.staticRobotLabel_2.setFont(Fonts["font2"])
        self.staticRobotLabel_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.staticRobot_2.addWidget(self.staticRobotLabel_2)

        self.staticRobotDropdown_2 = QComboBox(self.staticRobotsBox)
        self.staticRobotDropdown_2.addItem("")
        self.staticRobotDropdown_2.addItem("")
        self.staticRobotDropdown_2.addItem("")
        self.staticRobotDropdown_2.addItem("")
        self.staticRobotDropdown_2.setObjectName(u"staticRobotDropdown_2")
        self.staticRobotDropdown_2.setFont(Fonts["font3"])
        self.staticRobotDropdown_2.setCursor(QCursor(Qt.PointingHandCursor))
        self.staticRobotDropdown_2.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.staticRobot_2.addWidget(self.staticRobotDropdown_2)

        self.verticalLayout_33.addLayout(self.staticRobot_2)

        self.staticRobot3 = QHBoxLayout()
        self.staticRobot3.setObjectName(u"staticRobot3")
        self.staticRobotLabel_3 = QLabel(self.staticRobotsBox)
        self.staticRobotLabel_3.setObjectName(u"staticRobotLabel_3")
        self.staticRobotLabel_3.setFont(Fonts["font2"])
        self.staticRobotLabel_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.staticRobot3.addWidget(self.staticRobotLabel_3)

        self.staticRobotDropdown_3 = QComboBox(self.staticRobotsBox)
        self.staticRobotDropdown_3.addItem("")
        self.staticRobotDropdown_3.addItem("")
        self.staticRobotDropdown_3.addItem("")
        self.staticRobotDropdown_3.addItem("")
        self.staticRobotDropdown_3.setObjectName(u"staticRobotDropdown_3")
        self.staticRobotDropdown_3.setFont(Fonts["font3"])
        self.staticRobotDropdown_3.setCursor(QCursor(Qt.PointingHandCursor))
        self.staticRobotDropdown_3.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.staticRobot3.addWidget(self.staticRobotDropdown_3)

        self.verticalLayout_33.addLayout(self.staticRobot3)

        self.staticEntitiesContents.addWidget(self.staticRobotsBox)

        self.verticalLayout_26.addLayout(self.staticEntitiesContents)
        
        self.staticRobotsBox.hide()

        self.decHLine = QFrame(self.decScrollContents)
        self.decHLine.setObjectName(u"decHLine")
        self.decHLine.setFrameShape(QFrame.HLine)
        self.decHLine.setFrameShadow(QFrame.Sunken)

        self.verticalLayout_26.addWidget(self.decHLine)

        self.positioning = QVBoxLayout()
        self.positioning.setObjectName(u"positioning")
        self.posLabel = QLabel(self.decScrollContents)
        self.posLabel.setObjectName(u"posLabel")
        self.posLabel.setFont(Fonts["font2"])

        self.positioning.addWidget(self.posLabel)

        self.posContents = QFrame(self.decScrollContents)
        self.posContents.setObjectName(u"posContents")
        self.posContents.setFrameShape(QFrame.Shape.StyledPanel)
        self.posContents.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_34 = QVBoxLayout(self.posContents)
        self.verticalLayout_34.setObjectName(u"verticalLayout_34")
        self.verticalLayout_34.setContentsMargins(0, 0, 0, 0)
        
        ###################################
        # Position Source
        ###################################
        self.posSource = QHBoxLayout()
        self.posSource.setObjectName(u"posSource")
        
        self.posSourceLabel = QLabel(self.posContents)
        self.posSourceLabel.setObjectName(u"posSourceLabel")
        self.posSourceLabel.setFont(Fonts["font3"])
        
        self.posSource.addWidget(self.posSourceLabel)
        
        self.posSourceSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.posSource.addItem(self.posSourceSpacer)

        self.posSourceSwitch = QSlider(self.posContents)
        self.posSourceSwitch.setObjectName(u"posSourceSwitch")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.posSourceSwitch.sizePolicy().hasHeightForWidth())
        self.posSourceSwitch.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.posSourceSwitch.setMinimumSize(QSize(41, 0))
        self.posSourceSwitch.setMaximumSize(QSize(41, 16777215))
        self.posSourceSwitch.setCursor(QCursor(Qt.PointingHandCursor))
        self.posSourceSwitch.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.posSourceSwitch.setSliderPosition(1)
        self.posSourceSwitch.setValue(1)
        self.posSourceSwitch.setMaximum(1)
        self.posSourceSwitch.setOrientation(Qt.Orientation.Horizontal)

        self.posSource.addWidget(self.posSourceSwitch)

        self.verticalLayout_34.addLayout(self.posSource)
        

        self.selectPos = QHBoxLayout()
        self.selectPos.setObjectName(u"selectPos")
        self.selectPosLabel = QLabel(self.posContents)
        self.selectPosLabel.setObjectName(u"selectPosLabel")
        
        self.selectPosLabel.setFont(Fonts["font6"])
        self.selectPosLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.selectPos.addWidget(self.selectPosLabel)

        self.selectPosSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.selectPos.addItem(self.selectPosSpacer)

        self.selectPosDropdown = QComboBox(self.posContents)
        self.selectPosDropdown.addItem("")
        self.selectPosDropdown.addItem("")
        self.selectPosDropdown.addItem("")
        self.selectPosDropdown.setObjectName(u"selectPosDropdown")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.selectPosDropdown.sizePolicy().hasHeightForWidth())
        self.selectPosDropdown.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.selectPosDropdown.setFont(Fonts["font3"])
        self.selectPosDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.selectPosDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.selectPos.addWidget(self.selectPosDropdown)

        self.verticalLayout_34.addLayout(self.selectPos)

        self.posTime = QHBoxLayout()
        self.posTime.setObjectName(u"posTime")
        self.posTimeLabel = QLabel(self.posContents)
        self.posTimeLabel.setObjectName(u"posTimeLabel")
        self.posTimeLabel.setFont(Fonts["font6"])
        self.posTimeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.posTime.addWidget(self.posTimeLabel)

        self.posTimeSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.posTime.addItem(self.posTimeSpacer)

        self.posTimeValue = QLabel(self.posContents)
        self.posTimeValue.setObjectName(u"posTimeValue")
        self.posTimeValue.setFont(Fonts["font6"])
        self.posTimeValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.posTime.addWidget(self.posTimeValue)

        self.verticalLayout_34.addLayout(self.posTime)

        self.positioning.addWidget(self.posContents)

        self.verticalLayout_26.addLayout(self.positioning)

        self.decSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_26.addItem(self.decSpacer)

        self.decScrollArea.setWidget(self.decScrollContents)
        self.tabWidget.addTab(self.decisionTab, "")
        self.layoutWidget = QWidget(self.sysInfoTab)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 390, 841, 251))
        self.sysInfoFooter = QVBoxLayout(self.layoutWidget)
        self.sysInfoFooter.setObjectName(u"sysInfoFooter")
        self.sysInfoFooter.setContentsMargins(0, 0, 0, 0)
        self.sysInfoBox = QFrame(self.layoutWidget)
        self.sysInfoBox.setObjectName(u"sysInfoBox")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.sysInfoBox.sizePolicy().hasHeightForWidth())
        self.sysInfoBox.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.sysInfoBox.setFrameShape(QFrame.Shape.NoFrame)
        self.sysInfoBox.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_17 = QHBoxLayout(self.sysInfoBox)
        self.horizontalLayout_17.setSpacing(9)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.ballInfo = QFrame(self.sysInfoBox)
        self.ballInfo.setObjectName(u"ballInfo")
        
        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.ballInfo.sizePolicy().hasHeightForWidth())
        self.ballInfo.setSizePolicy(SizePolicies["Expanding_Preferred"])
        
        self.ballInfo.setMinimumSize(QSize(251, 0))
        self.ballInfo.setFrameShape(QFrame.Shape.StyledPanel)
        self.ballInfo.setFrameShadow(QFrame.Shadow.Raised)
        self.ballInfo.setLineWidth(1)
        self.verticalLayout_9 = QVBoxLayout(self.ballInfo)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(-1, 3, -1, -1)
        self.ballInfoHeader = QFrame(self.ballInfo)
        self.ballInfoHeader.setObjectName(u"ballInfoHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.ballInfoHeader.sizePolicy().hasHeightForWidth())
        self.ballInfoHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.ballInfoHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.ballInfoHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.ballInfoHeader)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.ballInfoTitle = QLabel(self.ballInfoHeader)
        self.ballInfoTitle.setObjectName(u"ballInfoTitle")
        self.ballInfoTitle.setFont(Fonts["font2"])
        self.ballInfoTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_10.addWidget(self.ballInfoTitle)

        self.ballInfoSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.ballInfoSpacer)

        self.ballInfoStatus = QLabel(self.ballInfoHeader)
        self.ballInfoStatus.setObjectName(u"ballInfoStatus")
        self.ballInfoStatus.setFont(Fonts["font6"])
        self.ballInfoStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_10.addWidget(self.ballInfoStatus)

        self.verticalLayout_9.addWidget(self.ballInfoHeader)

        self.ballInfoBox = QFrame(self.ballInfo)
        self.ballInfoBox.setObjectName(u"ballInfoBox")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.ballInfoBox.sizePolicy().hasHeightForWidth())
        self.ballInfoBox.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.ballInfoBox.setFrameShape(QFrame.Shape.NoFrame)
        self.ballInfoBox.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.ballInfoBox)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.ballPos = QVBoxLayout()
        self.ballPos.setObjectName(u"ballPos")
        self.ballPosHeader = QFrame(self.ballInfoBox)
        self.ballPosHeader.setObjectName(u"ballPosHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.ballPosHeader.sizePolicy().hasHeightForWidth())
        self.ballPosHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.ballPosHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.ballPosHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_18 = QHBoxLayout(self.ballPosHeader)
        self.horizontalLayout_18.setSpacing(0)
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.ballPosLabel = QLabel(self.ballPosHeader)
        self.ballPosLabel.setObjectName(u"ballPosLabel")
        self.ballPosLabel.setFont(Fonts["font2"])
        self.ballPosLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_18.addWidget(self.ballPosLabel)

        self.ballPosSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_18.addItem(self.ballPosSpacer)

        self.ballPos.addWidget(self.ballPosHeader)

        self.ballPosBox = QFrame(self.ballInfoBox)
        self.ballPosBox.setObjectName(u"ballPosBox")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.ballPosBox.sizePolicy().hasHeightForWidth())
        self.ballPosBox.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.ballPosBox.setMinimumSize(QSize(86, 0))
        self.ballPosBox.setStyleSheet(u"")
        self.ballPosBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.ballPosBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.ballPosBox)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(3, 3, 3, 3)
        self.ballPosValue = QLabel(self.ballPosBox)
        self.ballPosValue.setObjectName(u"ballPosValue")
        self.ballPosValue.setFont(Fonts["font6"])
        self.ballPosValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_3.addWidget(self.ballPosValue)

        self.ballPos.addWidget(self.ballPosBox)

        self.horizontalLayout_11.addLayout(self.ballPos)

        self.ballSpeed = QVBoxLayout()
        self.ballSpeed.setObjectName(u"ballSpeed")
        self.ballSpeedLabel = QLabel(self.ballInfoBox)
        self.ballSpeedLabel.setObjectName(u"ballSpeedLabel")
        self.ballSpeedLabel.setFont(Fonts["font2"])
        self.ballSpeedLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ballSpeed.addWidget(self.ballSpeedLabel)

        self.ballSpeedBox = QFrame(self.ballInfoBox)
        self.ballSpeedBox.setObjectName(u"ballSpeedBox")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.ballSpeedBox.sizePolicy().hasHeightForWidth())
        self.ballSpeedBox.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.ballSpeedBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.ballSpeedBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.ballSpeedBox)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(3, 3, 3, 3)
        self.ballSpeedValue = QLabel(self.ballSpeedBox)
        self.ballSpeedValue.setObjectName(u"ballSpeedValue")
        self.ballSpeedValue.setFont(Fonts["font3"])

        self.verticalLayout_4.addWidget(self.ballSpeedValue)

        self.ballSpeed.addWidget(self.ballSpeedBox)

        self.horizontalLayout_11.addLayout(self.ballSpeed)

        self.ballAcc = QVBoxLayout()
        self.ballAcc.setObjectName(u"ballAcc")
        self.ballAccLabel = QLabel(self.ballInfoBox)
        self.ballAccLabel.setObjectName(u"ballAccLabel")
        self.ballAccLabel.setFont(Fonts["font2"])
        self.ballAccLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.ballAcc.addWidget(self.ballAccLabel)

        self.ballAccBox = QFrame(self.ballInfoBox)
        self.ballAccBox.setObjectName(u"ballAccBox")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.ballAccBox.sizePolicy().hasHeightForWidth())
        self.ballAccBox.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.ballAccBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.ballAccBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.ballAccBox)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(3, 3, 3, 3)
        self.ballAccValue = QLabel(self.ballAccBox)
        self.ballAccValue.setObjectName(u"ballAccValue")
        self.ballAccValue.setFont(Fonts["font3"])
        self.ballAccValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_8.addWidget(self.ballAccValue)

        self.ballAcc.addWidget(self.ballAccBox)

        self.horizontalLayout_11.addLayout(self.ballAcc)

        self.verticalLayout_9.addWidget(self.ballInfoBox)

        self.horizontalLayout_17.addWidget(self.ballInfo)

        self.comm = QFrame(self.sysInfoBox)
        self.comm.setObjectName(u"comm")
        
        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.comm.sizePolicy().hasHeightForWidth())
        self.comm.setSizePolicy(SizePolicies["Expanding_Preferred"])
        
        self.comm.setMinimumSize(QSize(397, 0))
        self.comm.setFrameShape(QFrame.Shape.StyledPanel)
        self.comm.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.comm)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(-1, 3, -1, -1)
        self.commHeader = QFrame(self.comm)
        self.commHeader.setObjectName(u"commHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.commHeader.sizePolicy().hasHeightForWidth())
        self.commHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.commHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.commHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_19 = QHBoxLayout(self.commHeader)
        self.horizontalLayout_19.setSpacing(0)
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.commTitle = QLabel(self.commHeader)
        self.commTitle.setObjectName(u"commTitle")
        self.commTitle.setFont(Fonts["font2"])
        self.commTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_19.addWidget(self.commTitle)

        self.commSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_19.addItem(self.commSpacer)

        self.verticalLayout_13.addWidget(self.commHeader)

        self.commInfoBox = QFrame(self.comm)
        self.commInfoBox.setObjectName(u"commInfoBox")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.commInfoBox.sizePolicy().hasHeightForWidth())
        self.commInfoBox.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.commInfoBox.setFrameShape(QFrame.Shape.NoFrame)
        self.commInfoBox.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_15 = QHBoxLayout(self.commInfoBox)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.visionComm = QVBoxLayout()
        self.visionComm.setObjectName(u"visionComm")
        self.visionCommHeader = QFrame(self.commInfoBox)
        self.visionCommHeader.setObjectName(u"visionCommHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.visionCommHeader.sizePolicy().hasHeightForWidth())
        self.visionCommHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.visionCommHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.visionCommHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.visionCommHeader)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.visionCommLabel = QLabel(self.visionCommHeader)
        self.visionCommLabel.setObjectName(u"visionCommLabel")
        self.visionCommLabel.setFont(Fonts["font2"])
        self.visionCommLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_12.addWidget(self.visionCommLabel)

        self.visionCommSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.visionCommSpacer)

        self.visionCommStatus = QLabel(self.visionCommHeader)
        self.visionCommStatus.setObjectName(u"visionCommStatus")
        self.visionCommStatus.setFont(Fonts["font6"])
        self.visionCommStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_12.addWidget(self.visionCommStatus)

        self.visionComm.addWidget(self.visionCommHeader)

        self.visionCommPortBox = QFrame(self.commInfoBox)
        self.visionCommPortBox.setObjectName(u"visionCommPortBox")
        self.visionCommPortBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.visionCommPortBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_10 = QVBoxLayout(self.visionCommPortBox)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(3, 3, 3, 3)
        self.visionCommPortValue = QLabel(self.visionCommPortBox)
        self.visionCommPortValue.setObjectName(u"visionCommPortValue")
        self.visionCommPortValue.setFont(Fonts["font3"])
        self.visionCommPortValue.setScaledContents(False)
        self.visionCommPortValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_10.addWidget(self.visionCommPortValue, 0, Qt.AlignmentFlag.AlignVCenter)

        self.visionComm.addWidget(self.visionCommPortBox)

        self.horizontalLayout_15.addLayout(self.visionComm)

        self.refComm = QVBoxLayout()
        self.refComm.setObjectName(u"refComm")
        self.refCommHeader = QFrame(self.commInfoBox)
        self.refCommHeader.setObjectName(u"refCommHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.refCommHeader.sizePolicy().hasHeightForWidth())
        self.refCommHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.refCommHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.refCommHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_13 = QHBoxLayout(self.refCommHeader)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.refCommLabel = QLabel(self.refCommHeader)
        self.refCommLabel.setObjectName(u"refCommLabel")
        self.refCommLabel.setFont(Fonts["font2"])
        self.refCommLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_13.addWidget(self.refCommLabel)

        self.refCommSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.refCommSpacer)

        self.refCommStatus = QLabel(self.refCommHeader)
        self.refCommStatus.setObjectName(u"refCommStatus")
        self.refCommStatus.setFont(Fonts["font6"])
        self.refCommStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_13.addWidget(self.refCommStatus)


        self.refComm.addWidget(self.refCommHeader)

        self.refCommPortBox = QFrame(self.commInfoBox)
        self.refCommPortBox.setObjectName(u"refCommPortBox")
        self.refCommPortBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.refCommPortBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_11 = QVBoxLayout(self.refCommPortBox)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(3, 3, 3, 3)
        self.refCommPortValue = QLabel(self.refCommPortBox)
        self.refCommPortValue.setObjectName(u"refCommPortValue")
        self.refCommPortValue.setFont(Fonts["font3"])
        self.refCommPortValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.refCommPortValue, 0, Qt.AlignmentFlag.AlignVCenter)

        self.refComm.addWidget(self.refCommPortBox)

        self.horizontalLayout_15.addLayout(self.refComm)

        self.transComm = QVBoxLayout()
        self.transComm.setObjectName(u"transComm")
        self.transCommHeader = QFrame(self.commInfoBox)
        self.transCommHeader.setObjectName(u"transCommHeader")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.transCommHeader.sizePolicy().hasHeightForWidth())
        self.transCommHeader.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.transCommHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.transCommHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_14 = QHBoxLayout(self.transCommHeader)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.transCommLabel = QLabel(self.transCommHeader)
        self.transCommLabel.setObjectName(u"transCommLabel")
        self.transCommLabel.setFont(Fonts["font2"])
        self.transCommLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_14.addWidget(self.transCommLabel)

        self.transCommSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.transCommSpacer)

        self.transCommStatus = QLabel(self.transCommHeader)
        self.transCommStatus.setObjectName(u"transCommStatus")
        self.transCommStatus.setFont(Fonts["font6"])
        self.transCommStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_14.addWidget(self.transCommStatus)

        self.transComm.addWidget(self.transCommHeader)

        self.transCommPortBox = QFrame(self.commInfoBox)
        self.transCommPortBox.setObjectName(u"transCommPortBox")
        self.transCommPortBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.transCommPortBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_12 = QVBoxLayout(self.transCommPortBox)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(3, 3, 3, 3)
        self.transCommPortValue = QLabel(self.transCommPortBox)
        self.transCommPortValue.setObjectName(u"transCommPortValue")
        self.transCommPortValue.setFont(Fonts["font3"])
        self.transCommPortValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_12.addWidget(self.transCommPortValue, 0, Qt.AlignmentFlag.AlignVCenter)

        self.transComm.addWidget(self.transCommPortBox)

        self.horizontalLayout_15.addLayout(self.transComm)

        self.verticalLayout_13.addWidget(self.commInfoBox)

        self.commButtons = QFrame(self.comm)
        self.commButtons.setObjectName(u"commButtons")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.commButtons.sizePolicy().hasHeightForWidth())
        self.commButtons.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.commButtons.setFrameShape(QFrame.Shape.NoFrame)
        self.commButtons.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_20 = QHBoxLayout(self.commButtons)
        self.horizontalLayout_20.setSpacing(6)
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.horizontalLayout_20.setContentsMargins(0, 0, 0, 0)
        self.commButtonsSpacer = QSpacerItem(172, 16, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_20.addItem(self.commButtonsSpacer)

        self.commCancelButton = QPushButton(self.commButtons)
        self.commCancelButton.setObjectName(u"commCancelButton")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.commCancelButton.sizePolicy().hasHeightForWidth())
        self.commCancelButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.commCancelButton.setMinimumSize(QSize(70, 20))
        
        self.commCancelButton.setFont(Fonts["font3"])
        self.commCancelButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.commCancelButton.setStyleSheet(u"")

        self.horizontalLayout_20.addWidget(self.commCancelButton)

        self.commAlterButton = QPushButton(self.commButtons)
        self.commAlterButton.setObjectName(u"commAlterButton")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.commAlterButton.sizePolicy().hasHeightForWidth())
        self.commAlterButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.commAlterButton.setMinimumSize(QSize(120, 20))
        
        self.commAlterButton.setFont(Fonts["font3"])
        self.commAlterButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.commAlterButton.setStyleSheet(u"")

        self.horizontalLayout_20.addWidget(self.commAlterButton)

        self.verticalLayout_13.addWidget(self.commButtons)

        self.horizontalLayout_17.addWidget(self.comm)

        self.infoSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_17.addItem(self.infoSpacer)

        self.sysInfoFooter.addWidget(self.sysInfoBox)

        self.logging = QHBoxLayout()
        self.logging.setSpacing(0)
        self.logging.setObjectName(u"logging")
        self.logBox = QFrame(self.layoutWidget)
        self.logBox.setObjectName(u"logBox")
        
        SizePolicies["Expanding_Preferred"].setHeightForWidth(self.logBox.sizePolicy().hasHeightForWidth())
        self.logBox.setSizePolicy(SizePolicies["Expanding_Preferred"])
        
        self.logBox.setMinimumSize(QSize(656, 0))
        self.logBox.setFrameShape(QFrame.Shape.StyledPanel)
        self.logBox.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_14 = QVBoxLayout(self.logBox)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(-1, 3, -1, -1)
        self.logHeader = QFrame(self.logBox)
        self.logHeader.setObjectName(u"logHeader")
        self.logHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.logHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_16 = QHBoxLayout(self.logHeader)
        self.horizontalLayout_16.setSpacing(0)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.logHeaderLabel = QLabel(self.logHeader)
        self.logHeaderLabel.setObjectName(u"logHeaderLabel")
        self.logHeaderLabel.setFont(Fonts["font2"])
        self.logHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_16.addWidget(self.logHeaderLabel)

        self.logHeaderSpacer = QSpacerItem(284, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.logHeaderSpacer)

        self.verticalLayout_14.addWidget(self.logHeader)

        self.logScrollArea = QScrollArea(self.logBox)
        self.logScrollArea.setObjectName(u"logScrollArea")
        self.logScrollArea.setWidgetResizable(True)
        self.logScrollContents = QWidget()
        self.logScrollContents.setObjectName(u"logScrollContents")
        self.logScrollContents.setGeometry(QRect(0, 0, 634, 87))
        self.logMessages = QLabel(self.logScrollContents)
        self.logMessages.setObjectName(u"logMessages")
        self.logMessages.setGeometry(QRect(0, 0, 641, 141))
        self.logScrollArea.setWidget(self.logScrollContents)

        self.verticalLayout_14.addWidget(self.logScrollArea)

        self.logging.addWidget(self.logBox)

        self.logSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.logging.addItem(self.logSpacer)

        self.sysInfoFooter.addLayout(self.logging)

        icon11 = QIcon()
        icon11.addFile(u"assets/icons/mdi_cog-outline.svg", QSize(), QIcon.Normal, QIcon.Off)
        
        ############################################
        # Vision Settings Tab
        ############################################
        self.appContents.addTab(self.sysInfoTab, icon11, "")
        self.visionSettingsTab = QWidget()
        self.visionSettingsTab.setObjectName(u"visionSettingsTab")
        self.visionSettings = QFrame(self.visionSettingsTab)
        self.visionSettings.setObjectName(u"visionSettings")
        self.visionSettings.setGeometry(QRect(10, 10, 551, 51))
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.visionSettings.sizePolicy().hasHeightForWidth())
        self.visionSettings.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.visionSettings.setMinimumSize(QSize(551, 51))
        self.visionSettings.setMaximumSize(QSize(16777215, 51))
        self.visionSettings.setFrameShape(QFrame.Shape.StyledPanel)
        self.visionSettings.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_37 = QHBoxLayout(self.visionSettings)
        self.horizontalLayout_37.setObjectName(u"horizontalLayout_37")
        self.horizontalLayout_37.setContentsMargins(3, 3, 3, 3)
        self.visGameOptions = QVBoxLayout()
        self.visGameOptions.setSpacing(0)
        self.visGameOptions.setObjectName(u"visGameOptions")
        self.visGameOptionsLabel = QLabel(self.visionSettings)
        self.visGameOptionsLabel.setObjectName(u"visGameOptionsLabel")
        self.visGameOptionsLabel.setFont(Fonts["font2"])
        self.visGameOptionsLabel.setScaledContents(True)
        self.visGameOptionsLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.visGameOptions.addWidget(self.visGameOptionsLabel)

        self.visGameOptionsDropdown = QComboBox(self.visionSettings)
        self.visGameOptionsDropdown.addItem("")
        self.visGameOptionsDropdown.addItem("")
        self.visGameOptionsDropdown.setObjectName(u"visGameOptionsDropdown")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.visGameOptionsDropdown.sizePolicy().hasHeightForWidth())
        self.visGameOptionsDropdown.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.visGameOptionsDropdown.setFont(Fonts["font3"])
        self.visGameOptionsDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.visGameOptionsDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.visGameOptionsDropdown.setFrame(True)

        self.visGameOptions.addWidget(self.visGameOptionsDropdown)

        self.horizontalLayout_37.addLayout(self.visGameOptions)

        self.deviceOptions = QVBoxLayout()
        self.deviceOptions.setSpacing(0)
        self.deviceOptions.setObjectName(u"deviceOptions")
        self.deviceOptionsLabel = QLabel(self.visionSettings)
        self.deviceOptionsLabel.setObjectName(u"deviceOptionsLabel")
        self.deviceOptionsLabel.setFont(Fonts["font2"])

        self.deviceOptions.addWidget(self.deviceOptionsLabel)

        self.deviceOptionsDropdown = QComboBox(self.visionSettings)
        self.deviceOptionsDropdown.addItem("")
        self.deviceOptionsDropdown.setObjectName(u"deviceOptionsDropdown")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.deviceOptionsDropdown.sizePolicy().hasHeightForWidth())
        self.deviceOptionsDropdown.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.deviceOptionsDropdown.setFont(Fonts["font3"])
        self.deviceOptionsDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.deviceOptionsDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.deviceOptionsDropdown.setFrame(True)

        self.deviceOptions.addWidget(self.deviceOptionsDropdown)

        self.horizontalLayout_37.addLayout(self.deviceOptions)

        self.selectVisionOptions = QVBoxLayout()
        self.selectVisionOptions.setSpacing(0)
        self.selectVisionOptions.setObjectName(u"selectVisionOptions")
        self.selectVisionOptionsLabel = QLabel(self.visionSettings)
        self.selectVisionOptionsLabel.setObjectName(u"selectVisionOptionsLabel")
        self.selectVisionOptionsLabel.setFont(Fonts["font2"])

        self.selectVisionOptions.addWidget(self.selectVisionOptionsLabel)

        self.selectVisionOptionsDropdown = QComboBox(self.visionSettings)
        self.selectVisionOptionsDropdown.addItem("")
        self.selectVisionOptionsDropdown.addItem("")
        self.selectVisionOptionsDropdown.setObjectName(u"selectVisionOptionsDropdown")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.selectVisionOptionsDropdown.sizePolicy().hasHeightForWidth())
        self.selectVisionOptionsDropdown.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.selectVisionOptionsDropdown.setFont(Fonts["font3"])
        self.selectVisionOptionsDropdown.setCursor(QCursor(Qt.PointingHandCursor))
        self.selectVisionOptionsDropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.selectVisionOptionsDropdown.setFrame(True)

        self.selectVisionOptions.addWidget(self.selectVisionOptionsDropdown)

        self.horizontalLayout_37.addLayout(self.selectVisionOptions)

        self.highLevelVision = QFrame(self.visionSettingsTab)
        self.highLevelVision.setObjectName(u"highLevelVision")
        self.highLevelVision.setGeometry(QRect(630, 10, 161, 35))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.highLevelVision.sizePolicy().hasHeightForWidth())
        self.highLevelVision.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.highLevelVision.setMinimumSize(QSize(105, 35))
        self.highLevelVision.setCursor(QCursor(Qt.PointingHandCursor))
        self.highLevelVision.setFrameShape(QFrame.Shape.NoFrame)
        self.highLevelVision.setFrameShadow(QFrame.Shadow.Raised)
        self.highLevelVisionButton = QPushButton(self.highLevelVision)
        self.highLevelVisionButton.setObjectName(u"highLevelVisionButton")
        self.highLevelVisionButton.setGeometry(QRect(0, 0, 161, 31))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.highLevelVisionButton.sizePolicy().hasHeightForWidth())
        self.highLevelVisionButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.highLevelVisionButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.highLevelVisionButton.setAutoFillBackground(False)
        self.highLevelVisionButton.setStyleSheet(u"color: #494848; background: #a5a5a5;")
        self.highLevelVisionButton.setIconSize(QSize(16, 16))
        self.highLevelVisionButton.setCheckable(True)
        self.highLevelVisionShadow = QFrame(self.highLevelVision)
        self.highLevelVisionShadow.setObjectName(u"highLevelVisionShadow")
        self.highLevelVisionShadow.setGeometry(QRect(3, 3, 161, 31))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.highLevelVisionShadow.sizePolicy().hasHeightForWidth())
        self.highLevelVisionShadow.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.highLevelVisionShadow.setStyleSheet(u"background: #8D8D8D; border-radius: 6px;")
        self.highLevelVisionShadow.setFrameShape(QFrame.Shape.NoFrame)
        self.highLevelVisionShadow.setFrameShadow(QFrame.Shadow.Plain)
        self.highLevelVisionShadow.raise_()
        self.highLevelVisionButton.raise_()
        self.highLevelVisionContents = QFrame(self.visionSettingsTab)
        self.highLevelVisionContents.setObjectName(u"highLevelVisionContents")
        self.highLevelVisionContents.setGeometry(QRect(10, 100, 841, 404))
        
        SizePolicies["Expanding_Expanding"].setHeightForWidth(self.highLevelVisionContents.sizePolicy().hasHeightForWidth())
        self.highLevelVisionContents.setSizePolicy(SizePolicies["Expanding_Expanding"])
        
        self.highLevelVisionContents.setMinimumSize(QSize(737, 402))
        self.highLevelVisionContents.setFrameShape(QFrame.Shape.NoFrame)
        self.highLevelVisionContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_134 = QHBoxLayout(self.highLevelVisionContents)
        self.horizontalLayout_134.setObjectName(u"horizontalLayout_134")
        self.horizontalLayout_134.setContentsMargins(6, 6, 6, 6)
        self.highLevelVisionDisplay = QFrame(self.highLevelVisionContents)
        self.highLevelVisionDisplay.setObjectName(u"highLevelVisionDisplay")
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.highLevelVisionDisplay.sizePolicy().hasHeightForWidth())
        self.highLevelVisionDisplay.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.highLevelVisionDisplay.setCursor(QCursor(Qt.PointingHandCursor))
        self.highLevelVisionDisplay.setFrameShape(QFrame.Shape.NoFrame)
        self.highLevelVisionDisplay.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_105 = QVBoxLayout(self.highLevelVisionDisplay)
        self.verticalLayout_105.setSpacing(0)
        self.verticalLayout_105.setObjectName(u"verticalLayout_105")
        self.verticalLayout_105.setContentsMargins(0, 0, 0, 0)
        self.highLevelVisionFrame = QLabel(self.highLevelVisionDisplay)
        self.highLevelVisionFrame.setObjectName(u"highLevelVisionFrame")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.highLevelVisionFrame.sizePolicy().hasHeightForWidth())
        self.highLevelVisionFrame.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.highLevelVisionFrame.setMinimumSize(QSize(486, 390))
        self.highLevelVisionFrame.setMaximumSize(QSize(486, 390))
        self.highLevelVisionFrame.setPixmap(QPixmap(u"assets/highLevelVision.png"))
        self.highLevelVisionFrame.setScaledContents(True)
        self.highLevelVisionFrame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_105.addWidget(self.highLevelVisionFrame)

        self.horizontalLayout_134.addWidget(self.highLevelVisionDisplay)

        self.highLevelVisionTools = QFrame(self.highLevelVisionContents)
        self.highLevelVisionTools.setObjectName(u"highLevelVisionTools")
        
        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.highLevelVisionTools.sizePolicy().hasHeightForWidth())
        self.highLevelVisionTools.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.highLevelVisionTools.setMinimumSize(QSize(0, 392))
        self.highLevelVisionTools.setBaseSize(QSize(0, 0))
        self.highLevelVisionTools.setFrameShape(QFrame.Shape.StyledPanel)
        self.highLevelVisionTools.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_106 = QVBoxLayout(self.highLevelVisionTools)
        self.verticalLayout_106.setObjectName(u"verticalLayout_106")
        self.verticalLayout_106.setContentsMargins(6, 6, 6, 6)
        self.highLevelVisionToolsHeader = QFrame(self.highLevelVisionTools)
        self.highLevelVisionToolsHeader.setObjectName(u"highLevelVisionToolsHeader")
        self.highLevelVisionToolsHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.highLevelVisionToolsHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_135 = QHBoxLayout(self.highLevelVisionToolsHeader)
        self.horizontalLayout_135.setSpacing(0)
        self.horizontalLayout_135.setObjectName(u"horizontalLayout_135")
        self.horizontalLayout_135.setContentsMargins(0, 0, 0, 0)
        self.highLevelVisionToolsLabel = QLabel(self.highLevelVisionToolsHeader)
        self.highLevelVisionToolsLabel.setObjectName(u"highLevelVisionToolsLabel")
        
        self.highLevelVisionToolsLabel.setFont(Fonts["font7"])
        self.highLevelVisionToolsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_135.addWidget(self.highLevelVisionToolsLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.highLevelVisionHeaderSpacer = QSpacerItem(73, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_135.addItem(self.highLevelVisionHeaderSpacer)

        self.verticalLayout_106.addWidget(self.highLevelVisionToolsHeader)

        self.vRobotsContents = QFrame(self.highLevelVisionTools)
        self.vRobotsContents.setObjectName(u"vRobotsContents")
        self.vRobotsContents.setFrameShape(QFrame.Shape.StyledPanel)
        self.vRobotsContents.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_107 = QVBoxLayout(self.vRobotsContents)
        self.verticalLayout_107.setSpacing(0)
        self.verticalLayout_107.setObjectName(u"verticalLayout_107")
        self.verticalLayout_107.setContentsMargins(0, 0, 0, 0)
        self.xRobots = QFrame(self.vRobotsContents)
        self.xRobots.setObjectName(u"xRobots")
        self.xRobots.setFrameShape(QFrame.Shape.NoFrame)
        self.xRobots.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_136 = QHBoxLayout(self.xRobots)
        self.horizontalLayout_136.setSpacing(0)
        self.horizontalLayout_136.setObjectName(u"horizontalLayout_136")
        self.horizontalLayout_136.setContentsMargins(0, 0, 0, 0)
        self.xRobotsLabel = QLabel(self.xRobots)
        self.xRobotsLabel.setObjectName(u"xRobotsLabel")
        self.xRobotsLabel.setFont(Fonts["font2"])
        self.xRobotsLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_136.addWidget(self.xRobotsLabel)

        self.xRobotsSpacer = QSpacerItem(271, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_136.addItem(self.xRobotsSpacer)


        self.verticalLayout_107.addWidget(self.xRobots)

        self.vRobots = QVBoxLayout()
        self.vRobots.setObjectName(u"vRobots")
        self.vRobotContents = QHBoxLayout()
        self.vRobotContents.setObjectName(u"vRobotContents")
        self.vRobotIdLabel = QLabel(self.vRobotsContents)
        self.vRobotIdLabel.setObjectName(u"vRobotIdLabel")
        
        self.vRobotIdLabel.setFont(Fonts["font8"])
        self.vRobotIdLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vRobotContents.addWidget(self.vRobotIdLabel, 0, Qt.AlignmentFlag.AlignVCenter)

        self.vRobotInfo = QVBoxLayout()
        self.vRobotInfo.setObjectName(u"vRobotInfo")
        self.vRobotStatus = QLabel(self.vRobotsContents)
        self.vRobotStatus.setObjectName(u"vRobotStatus")
        self.vRobotStatus.setFont(Fonts["font3"])

        self.vRobotInfo.addWidget(self.vRobotStatus)

        self.vRobotPos = QLabel(self.vRobotsContents)
        self.vRobotPos.setObjectName(u"vRobotPos")
        self.vRobotPos.setFont(Fonts["font3"])

        self.vRobotInfo.addWidget(self.vRobotPos)

        self.vRobotAngle = QLabel(self.vRobotsContents)
        self.vRobotAngle.setObjectName(u"vRobotAngle")
        self.vRobotAngle.setFont(Fonts["font3"])

        self.vRobotInfo.addWidget(self.vRobotAngle)

        self.vRobotContents.addLayout(self.vRobotInfo)

        self.vRobots.addLayout(self.vRobotContents)

        self.vRobotContents_2 = QHBoxLayout()
        self.vRobotContents_2.setObjectName(u"vRobotContents_2")
        self.vRobotIdLabel_2 = QLabel(self.vRobotsContents)
        self.vRobotIdLabel_2.setObjectName(u"vRobotIdLabel_2")
        self.vRobotIdLabel_2.setFont(Fonts["font8"])
        self.vRobotIdLabel_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vRobotContents_2.addWidget(self.vRobotIdLabel_2, 0, Qt.AlignmentFlag.AlignVCenter)

        self.vRobotInfo_2 = QVBoxLayout()
        self.vRobotInfo_2.setObjectName(u"vRobotInfo_2")
        self.vRobotStatus_2 = QLabel(self.vRobotsContents)
        self.vRobotStatus_2.setObjectName(u"vRobotStatus_2")
        self.vRobotStatus_2.setFont(Fonts["font3"])

        self.vRobotInfo_2.addWidget(self.vRobotStatus_2)

        self.vRobotPos_2 = QLabel(self.vRobotsContents)
        self.vRobotPos_2.setObjectName(u"vRobotPos_2")
        self.vRobotPos_2.setFont(Fonts["font3"])

        self.vRobotInfo_2.addWidget(self.vRobotPos_2)

        self.vRobotAngle_2 = QLabel(self.vRobotsContents)
        self.vRobotAngle_2.setObjectName(u"vRobotAngle_2")
        self.vRobotAngle_2.setFont(Fonts["font3"])

        self.vRobotInfo_2.addWidget(self.vRobotAngle_2)

        self.vRobotContents_2.addLayout(self.vRobotInfo_2)

        self.vRobots.addLayout(self.vRobotContents_2)

        self.vRobotContents_3 = QHBoxLayout()
        self.vRobotContents_3.setObjectName(u"vRobotContents_3")
        self.vRobotIdLabel_3 = QLabel(self.vRobotsContents)
        self.vRobotIdLabel_3.setObjectName(u"vRobotIdLabel_3")
        self.vRobotIdLabel_3.setFont(Fonts["font8"])
        self.vRobotIdLabel_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vRobotContents_3.addWidget(self.vRobotIdLabel_3, 0, Qt.AlignmentFlag.AlignVCenter)

        self.vRobotInfo_3 = QVBoxLayout()
        self.vRobotInfo_3.setObjectName(u"vRobotInfo_3")
        self.vRobotStatus_3 = QLabel(self.vRobotsContents)
        self.vRobotStatus_3.setObjectName(u"vRobotStatus_3")
        self.vRobotStatus_3.setFont(Fonts["font3"])

        self.vRobotInfo_3.addWidget(self.vRobotStatus_3)

        self.vRobotPos_3 = QLabel(self.vRobotsContents)
        self.vRobotPos_3.setObjectName(u"vRobotPos_3")
        self.vRobotPos_3.setFont(Fonts["font3"])

        self.vRobotInfo_3.addWidget(self.vRobotPos_3)

        self.vRobotAngle_3 = QLabel(self.vRobotsContents)
        self.vRobotAngle_3.setObjectName(u"vRobotAngle_3")
        self.vRobotAngle_3.setFont(Fonts["font3"])

        self.vRobotInfo_3.addWidget(self.vRobotAngle_3)

        self.vRobotContents_3.addLayout(self.vRobotInfo_3)

        self.vRobots.addLayout(self.vRobotContents_3)

        self.verticalLayout_107.addLayout(self.vRobots)

        self.verticalLayout_106.addWidget(self.vRobotsContents)

        self.vBall = QVBoxLayout()
        self.vBall.setObjectName(u"vBall")
        self.vBallInfoHeader = QFrame(self.highLevelVisionTools)
        self.vBallInfoHeader.setObjectName(u"vBallInfoHeader")
        self.vBallInfoHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.vBallInfoHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_137 = QHBoxLayout(self.vBallInfoHeader)
        self.horizontalLayout_137.setSpacing(0)
        self.horizontalLayout_137.setObjectName(u"horizontalLayout_137")
        self.horizontalLayout_137.setContentsMargins(0, 0, 0, 0)
        self.vBallInfoLabel = QLabel(self.vBallInfoHeader)
        self.vBallInfoLabel.setObjectName(u"vBallInfoLabel")
        self.vBallInfoLabel.setFont(Fonts["font2"])
        self.vBallInfoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_137.addWidget(self.vBallInfoLabel)

        self.vBallInfoSpacer = QSpacerItem(117, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_137.addItem(self.vBallInfoSpacer)

        self.vBall.addWidget(self.vBallInfoHeader)

        self.vBallContents = QHBoxLayout()
        self.vBallContents.setObjectName(u"vBallContents")
        self.vBallLabel = QLabel(self.highLevelVisionTools)
        self.vBallLabel.setObjectName(u"vBallLabel")
        self.vBallLabel.setFont(Fonts["font8"])
        self.vBallLabel.setPixmap(QPixmap(u"assets/icons/volleyball-ball.svg"))
        self.vBallLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vBallContents.addWidget(self.vBallLabel, 0, Qt.AlignmentFlag.AlignVCenter)

        self.vBallInfo = QVBoxLayout()
        self.vBallInfo.setObjectName(u"vBallInfo")
        self.vBallStatus = QLabel(self.highLevelVisionTools)
        self.vBallStatus.setObjectName(u"vBallStatus")
        self.vBallStatus.setFont(Fonts["font3"])

        self.vBallInfo.addWidget(self.vBallStatus)

        self.vBallPos = QLabel(self.highLevelVisionTools)
        self.vBallPos.setObjectName(u"vBallPos")
        self.vBallPos.setFont(Fonts["font3"])

        self.vBallInfo.addWidget(self.vBallPos)

        self.vBallContents.addLayout(self.vBallInfo)

        self.vBall.addLayout(self.vBallContents)

        self.verticalLayout_106.addLayout(self.vBall)

        self.nextStepVision = QFrame(self.highLevelVisionTools)
        self.nextStepVision.setObjectName(u"nextStepVision")
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.nextStepVision.sizePolicy().hasHeightForWidth())
        self.nextStepVision.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.nextStepVision.setMinimumSize(QSize(105, 35))
        self.nextStepVision.setCursor(QCursor(Qt.PointingHandCursor))
        self.nextStepVision.setFrameShape(QFrame.Shape.NoFrame)
        self.nextStepVision.setFrameShadow(QFrame.Shadow.Raised)
        self.nextStepVisionButton = QPushButton(self.nextStepVision)
        self.nextStepVisionButton.setObjectName(u"nextStepVisionButton")
        self.nextStepVisionButton.setGeometry(QRect(0, 0, 321, 31))
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.nextStepVisionButton.sizePolicy().hasHeightForWidth())
        self.nextStepVisionButton.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.nextStepVisionButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.nextStepVisionButton.setAutoFillBackground(False)
        self.nextStepVisionButton.setStyleSheet(u"color: #fff; background: #3E7239;")
        self.nextStepVisionButton.setIconSize(QSize(16, 16))
        self.nextStepVisionButton.setCheckable(False)
        self.nextStepVisionLabel = QFrame(self.nextStepVision)
        self.nextStepVisionLabel.setObjectName(u"nextStepVisionLabel")
        self.nextStepVisionLabel.setGeometry(QRect(3, 3, 321, 31))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.nextStepVisionLabel.sizePolicy().hasHeightForWidth())
        self.nextStepVisionLabel.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.nextStepVisionLabel.setStyleSheet(u"background: #8D8D8D; border-radius: 6px;")
        self.nextStepVisionLabel.setFrameShape(QFrame.Shape.NoFrame)
        self.nextStepVisionLabel.setFrameShadow(QFrame.Shadow.Plain)
        self.nextStepVisionLabel.raise_()
        self.nextStepVisionButton.raise_()

        self.verticalLayout_106.addWidget(self.nextStepVision)

        self.highLevelVisionToolsSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_106.addItem(self.highLevelVisionToolsSpacer)

        self.horizontalLayout_134.addWidget(self.highLevelVisionTools)

        self.visionSteps = QTabWidget(self.visionSettingsTab)
        self.visionSteps.setObjectName(u"visionSteps")
        self.visionSteps.setGeometry(QRect(10, 70, 841, 491))
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.visionSteps.sizePolicy().hasHeightForWidth())
        self.visionSteps.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.visionSteps.setFont(Fonts["font3"])
        self.visionSteps.setCursor(QCursor(Qt.ArrowCursor))
        self.visionSteps.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.cropFieldTab = QWidget()
        self.cropFieldTab.setObjectName(u"cropFieldTab")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropFieldTab.sizePolicy().hasHeightForWidth())
        self.cropFieldTab.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropFieldContents = QFrame(self.cropFieldTab)
        self.cropFieldContents.setObjectName(u"cropFieldContents")
        self.cropFieldContents.setGeometry(QRect(0, 0, 831, 451))
        
        SizePolicies["Expanding_Expanding"].setHeightForWidth(self.cropFieldContents.sizePolicy().hasHeightForWidth())
        self.cropFieldContents.setSizePolicy(SizePolicies["Expanding_Expanding"])
        
        self.cropFieldContents.setMinimumSize(QSize(737, 402))
        self.cropFieldContents.setFrameShape(QFrame.Shape.NoFrame)
        self.cropFieldContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_138 = QHBoxLayout(self.cropFieldContents)
        self.horizontalLayout_138.setObjectName(u"horizontalLayout_138")
        self.horizontalLayout_138.setContentsMargins(6, 6, 6, 6)
        
        self.visionCropFrame = CropEditor(self.cropFieldContents, QPixmap(u"assets/defaultFrame.png"))
        self.visionCropFrame.setObjectName(u"visionCropFrame")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.visionCropFrame.sizePolicy().hasHeightForWidth())
        self.visionCropFrame.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.visionCropFrame.setScaledContents(True)
        self.visionCropFrame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visionCropFrame.setCursor(QCursor(Qt.PointingHandCursor))


        self.horizontalLayout_138.addWidget(self.visionCropFrame, 0, Qt.AlignmentFlag.AlignTop)

        self.cropFieldTools = QFrame(self.cropFieldContents)
        self.cropFieldTools.setObjectName(u"cropFieldTools")
        
        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.cropFieldTools.sizePolicy().hasHeightForWidth())
        self.cropFieldTools.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.cropFieldTools.setMinimumSize(QSize(0, 392))
        self.cropFieldTools.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropFieldTools.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_110 = QVBoxLayout(self.cropFieldTools)
        self.verticalLayout_110.setObjectName(u"verticalLayout_110")
        self.verticalLayout_110.setContentsMargins(6, 6, 6, 6)
        self.cropFieldToolsHeader = QFrame(self.cropFieldTools)
        self.cropFieldToolsHeader.setObjectName(u"cropFieldToolsHeader")
        self.cropFieldToolsHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.cropFieldToolsHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_139 = QHBoxLayout(self.cropFieldToolsHeader)
        self.horizontalLayout_139.setSpacing(0)
        self.horizontalLayout_139.setObjectName(u"horizontalLayout_139")
        self.horizontalLayout_139.setContentsMargins(0, 0, 0, 0)
        self.cropFieldToolsHeaderLabel = QLabel(self.cropFieldToolsHeader)
        self.cropFieldToolsHeaderLabel.setObjectName(u"cropFieldToolsHeaderLabel")
        self.cropFieldToolsHeaderLabel.setFont(Fonts["font7"])
        self.cropFieldToolsHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_139.addWidget(self.cropFieldToolsHeaderLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.cropFieldToolsHeaderSpacer = QSpacerItem(73, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_139.addItem(self.cropFieldToolsHeaderSpacer)


        self.verticalLayout_110.addWidget(self.cropFieldToolsHeader)

        self.showCropField = QHBoxLayout()
        self.showCropField.setSpacing(0)
        self.showCropField.setObjectName(u"showCropField")
        self.showCropFieldLabel = QLabel(self.cropFieldTools)
        self.showCropFieldLabel.setObjectName(u"showCropFieldLabel")
        self.showCropFieldLabel.setFont(Fonts["font3"])
        self.showCropFieldLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.showCropField.addWidget(self.showCropFieldLabel)

        self.showCropFieldSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.showCropField.addItem(self.showCropFieldSpacer)

        self.showCropFieldSwitch = QSlider(self.cropFieldTools)
        self.showCropFieldSwitch.setObjectName(u"showCropFieldSwitch")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.showCropFieldSwitch.sizePolicy().hasHeightForWidth())
        self.showCropFieldSwitch.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.showCropFieldSwitch.setMinimumSize(QSize(41, 0))
        self.showCropFieldSwitch.setMaximumSize(QSize(41, 16777215))
        self.showCropFieldSwitch.setCursor(QCursor(Qt.PointingHandCursor))
        self.showCropFieldSwitch.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.showCropFieldSwitch.setMaximum(1)
        self.showCropFieldSwitch.setPageStep(1)
        self.showCropFieldSwitch.setValue(0)
        self.showCropFieldSwitch.setSliderPosition(0)
        self.showCropFieldSwitch.setOrientation(Qt.Orientation.Horizontal)

        self.showCropField.addWidget(self.showCropFieldSwitch)


        self.verticalLayout_110.addLayout(self.showCropField)

        self.cropFieldActions = QVBoxLayout()
        self.cropFieldActions.setObjectName(u"cropFieldActions")
        self.cropFieldActionHeader = QFrame(self.cropFieldTools)
        self.cropFieldActionHeader.setObjectName(u"cropFieldActionHeader")
        self.cropFieldActionHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.cropFieldActionHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_140 = QHBoxLayout(self.cropFieldActionHeader)
        self.horizontalLayout_140.setSpacing(0)
        self.horizontalLayout_140.setObjectName(u"horizontalLayout_140")
        self.horizontalLayout_140.setContentsMargins(0, 0, 0, 0)
        self.cropFieldActionHeaderLabel = QLabel(self.cropFieldActionHeader)
        self.cropFieldActionHeaderLabel.setObjectName(u"cropFieldActionHeaderLabel")
        self.cropFieldActionHeaderLabel.setFont(Fonts["font3"])
        self.cropFieldActionHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_140.addWidget(self.cropFieldActionHeaderLabel)

        self.cropFieldActionHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_140.addItem(self.cropFieldActionHeaderSpacer)

        self.cropFieldActions.addWidget(self.cropFieldActionHeader)

        self.cropFieldActionButtons = QFrame(self.cropFieldTools)
        self.cropFieldActionButtons.setObjectName(u"cropFieldActionButtons")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.cropFieldActionButtons.sizePolicy().hasHeightForWidth())
        self.cropFieldActionButtons.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.cropFieldActionButtons.setSizeIncrement(QSize(5, 0))
        self.cropFieldActionButtons.setFrameShape(QFrame.Shape.NoFrame)
        self.cropFieldActionButtons.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_141 = QHBoxLayout(self.cropFieldActionButtons)
        self.horizontalLayout_141.setSpacing(0)
        self.horizontalLayout_141.setObjectName(u"horizontalLayout_141")
        self.horizontalLayout_141.setContentsMargins(0, 0, 0, 0)
        self.cropFieldSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_141.addItem(self.cropFieldSpacerLeft)

        self.cropFieldRedoTool = QFrame(self.cropFieldActionButtons)
        self.cropFieldRedoTool.setObjectName(u"cropFieldRedoTool")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropFieldRedoTool.sizePolicy().hasHeightForWidth())
        self.cropFieldRedoTool.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropFieldRedoTool.setMinimumSize(QSize(49, 49))
        self.cropFieldRedoTool.setMaximumSize(QSize(49, 49))
        self.cropFieldRedoTool.setFrameShape(QFrame.Shape.NoFrame)
        self.cropFieldRedoTool.setFrameShadow(QFrame.Shadow.Raised)
        self.cropFieldRedoButtonShadow = QFrame(self.cropFieldRedoTool)
        self.cropFieldRedoButtonShadow.setObjectName(u"cropFieldRedoButtonShadow")
        self.cropFieldRedoButtonShadow.setGeometry(QRect(3, 3, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropFieldRedoButtonShadow.sizePolicy().hasHeightForWidth())
        self.cropFieldRedoButtonShadow.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropFieldRedoButtonShadow.setStyleSheet(u"background: #8D8D8D; border-radius: 6px;")
        self.cropFieldRedoButtonShadow.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropFieldRedoButtonShadow.setFrameShadow(QFrame.Shadow.Raised)
        self.cropFieldRedoButton = QPushButton(self.cropFieldRedoTool)
        self.cropFieldRedoButton.setObjectName(u"cropFieldRedoButton")
        self.cropFieldRedoButton.setGeometry(QRect(0, 0, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropFieldRedoButton.sizePolicy().hasHeightForWidth())
        self.cropFieldRedoButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropFieldRedoButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon12 = QIcon()
        icon12.addFile(u"assets/icons/redo.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.cropFieldRedoButton.setIcon(icon12)
        self.cropFieldRedoButton.setIconSize(QSize(36, 36))
        self.cropFieldRedoButton.setFlat(False)

        self.horizontalLayout_141.addWidget(self.cropFieldRedoTool)

        self.cropFieldActionButtonsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_141.addItem(self.cropFieldActionButtonsSpacer)

        self.cropFieldEraseTool = QFrame(self.cropFieldActionButtons)
        self.cropFieldEraseTool.setObjectName(u"cropFieldEraseTool")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropFieldEraseTool.sizePolicy().hasHeightForWidth())
        self.cropFieldEraseTool.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropFieldEraseTool.setMinimumSize(QSize(49, 49))
        self.cropFieldEraseTool.setMaximumSize(QSize(49, 49))
        self.cropFieldEraseTool.setFrameShape(QFrame.Shape.NoFrame)
        self.cropFieldEraseTool.setFrameShadow(QFrame.Shadow.Raised)
        self.cropFieldEraseButtonShadow = QFrame(self.cropFieldEraseTool)
        self.cropFieldEraseButtonShadow.setObjectName(u"cropFieldEraseButtonShadow")
        self.cropFieldEraseButtonShadow.setGeometry(QRect(3, 3, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropFieldEraseButtonShadow.sizePolicy().hasHeightForWidth())
        self.cropFieldEraseButtonShadow.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropFieldEraseButtonShadow.setStyleSheet(u"background: #8D8D8D; border-radius: 6px;")
        self.cropFieldEraseButtonShadow.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropFieldEraseButtonShadow.setFrameShadow(QFrame.Shadow.Raised)
        self.cropFieldEraseButton = QPushButton(self.cropFieldEraseTool)
        self.cropFieldEraseButton.setObjectName(u"cropFieldEraseButton")
        self.cropFieldEraseButton.setGeometry(QRect(0, 0, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropFieldEraseButton.sizePolicy().hasHeightForWidth())
        self.cropFieldEraseButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropFieldEraseButton.setMinimumSize(QSize(46, 46))
        self.cropFieldEraseButton.setMaximumSize(QSize(46, 46))
        self.cropFieldEraseButton.setCursor(QCursor(Qt.PointingHandCursor))
        icon13 = QIcon()
        icon13.addFile(u"assets/icons/eraser.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.cropFieldEraseButton.setIcon(icon13)
        self.cropFieldEraseButton.setIconSize(QSize(36, 36))
        self.cropFieldEraseButton.setFlat(False)

        self.horizontalLayout_141.addWidget(self.cropFieldEraseTool)

        self.cropFieldSpacerRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_141.addItem(self.cropFieldSpacerRight)

        self.cropFieldActions.addWidget(self.cropFieldActionButtons)

        self.verticalLayout_110.addLayout(self.cropFieldActions)

        self.cropFieldSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_110.addItem(self.cropFieldSpacer)

        self.horizontalLayout_138.addWidget(self.cropFieldTools)

        icon14 = QIcon()
        icon14.addFile(u"assets/icons/radio_unchecked.svg", QSize(), QIcon.Normal, QIcon.Off)
        icon14.addFile(u"assets/icons/radio_checked.svg", QSize(), QIcon.Normal, QIcon.On)
        self.visionSteps.addTab(self.cropFieldTab, icon14, "")
        self.cropInnerFieldTab = QWidget()
        self.cropInnerFieldTab.setObjectName(u"cropInnerFieldTab")
        self.cropInnerFieldContents = QFrame(self.cropInnerFieldTab)
        self.cropInnerFieldContents.setObjectName(u"cropInnerFieldContents")
        self.cropInnerFieldContents.setGeometry(QRect(0, 0, 831, 451))
        
        SizePolicies["Expanding_Expanding"].setHeightForWidth(self.cropInnerFieldContents.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldContents.setSizePolicy(SizePolicies["Expanding_Expanding"])
        
        self.cropInnerFieldContents.setMinimumSize(QSize(737, 402))
        self.cropInnerFieldContents.setFrameShape(QFrame.Shape.NoFrame)
        self.cropInnerFieldContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_142 = QHBoxLayout(self.cropInnerFieldContents)
        self.horizontalLayout_142.setObjectName(u"horizontalLayout_142")
        self.horizontalLayout_142.setContentsMargins(6, 6, 6, 6)
        self.visionInnerCropDisplay = QFrame(self.cropInnerFieldContents)
        self.visionInnerCropDisplay.setObjectName(u"visionInnerCropDisplay")
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.visionInnerCropDisplay.sizePolicy().hasHeightForWidth())
        self.visionInnerCropDisplay.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.visionInnerCropDisplay.setCursor(QCursor(Qt.PointingHandCursor))
        self.visionInnerCropDisplay.setFrameShape(QFrame.Shape.NoFrame)
        self.visionInnerCropDisplay.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_111 = QVBoxLayout(self.visionInnerCropDisplay)
        self.verticalLayout_111.setSpacing(0)
        self.verticalLayout_111.setObjectName(u"verticalLayout_111")
        self.verticalLayout_111.setContentsMargins(0, 0, 0, 0)
        self.visionInnerCropFrame = QLabel(self.visionInnerCropDisplay)
        self.visionInnerCropFrame.setObjectName(u"visionInnerCropFrame")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.visionInnerCropFrame.sizePolicy().hasHeightForWidth())
        self.visionInnerCropFrame.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.visionInnerCropFrame.setPixmap(QPixmap(u"assets/defaultFrame.png"))
        self.visionInnerCropFrame.setScaledContents(True)
        self.visionInnerCropFrame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_111.addWidget(self.visionInnerCropFrame)


        self.horizontalLayout_142.addWidget(self.visionInnerCropDisplay, 0, Qt.AlignmentFlag.AlignTop)

        self.cropInnerFieldTools = QFrame(self.cropInnerFieldContents)
        self.cropInnerFieldTools.setObjectName(u"cropInnerFieldTools")
        
        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.cropInnerFieldTools.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldTools.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.cropInnerFieldTools.setMinimumSize(QSize(0, 392))
        self.cropInnerFieldTools.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropInnerFieldTools.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_112 = QVBoxLayout(self.cropInnerFieldTools)
        self.verticalLayout_112.setObjectName(u"verticalLayout_112")
        self.verticalLayout_112.setContentsMargins(6, 6, 6, 6)
        self.cropInnerFieldToolsHeader = QFrame(self.cropInnerFieldTools)
        self.cropInnerFieldToolsHeader.setObjectName(u"cropInnerFieldToolsHeader")
        self.cropInnerFieldToolsHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.cropInnerFieldToolsHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_143 = QHBoxLayout(self.cropInnerFieldToolsHeader)
        self.horizontalLayout_143.setSpacing(0)
        self.horizontalLayout_143.setObjectName(u"horizontalLayout_143")
        self.horizontalLayout_143.setContentsMargins(0, 0, 0, 0)
        self.cropInnerFieldToolsHeaderLabel = QLabel(self.cropInnerFieldToolsHeader)
        self.cropInnerFieldToolsHeaderLabel.setObjectName(u"cropInnerFieldToolsHeaderLabel")
        self.cropInnerFieldToolsHeaderLabel.setFont(Fonts["font7"])
        self.cropInnerFieldToolsHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_143.addWidget(self.cropInnerFieldToolsHeaderLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.cropInnerFieldToolsHeaderSpacer = QSpacerItem(73, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_143.addItem(self.cropInnerFieldToolsHeaderSpacer)


        self.verticalLayout_112.addWidget(self.cropInnerFieldToolsHeader)

        self.showInnerCropField = QHBoxLayout()
        self.showInnerCropField.setSpacing(0)
        self.showInnerCropField.setObjectName(u"showInnerCropField")
        self.showInnerCropFieldLabel = QLabel(self.cropInnerFieldTools)
        self.showInnerCropFieldLabel.setObjectName(u"showInnerCropFieldLabel")
        self.showInnerCropFieldLabel.setFont(Fonts["font3"])
        self.showInnerCropFieldLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.showInnerCropField.addWidget(self.showInnerCropFieldLabel)

        self.showInnerCropFieldSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.showInnerCropField.addItem(self.showInnerCropFieldSpacer)

        self.showInnerCropFieldSwitch = QSlider(self.cropInnerFieldTools)
        self.showInnerCropFieldSwitch.setObjectName(u"showInnerCropFieldSwitch")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.showInnerCropFieldSwitch.sizePolicy().hasHeightForWidth())
        self.showInnerCropFieldSwitch.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.showInnerCropFieldSwitch.setMinimumSize(QSize(41, 0))
        self.showInnerCropFieldSwitch.setMaximumSize(QSize(41, 16777215))
        self.showInnerCropFieldSwitch.setCursor(QCursor(Qt.PointingHandCursor))
        self.showInnerCropFieldSwitch.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.showInnerCropFieldSwitch.setMaximum(1)
        self.showInnerCropFieldSwitch.setPageStep(1)
        self.showInnerCropFieldSwitch.setValue(0)
        self.showInnerCropFieldSwitch.setSliderPosition(0)
        self.showInnerCropFieldSwitch.setOrientation(Qt.Orientation.Horizontal)

        self.showInnerCropField.addWidget(self.showInnerCropFieldSwitch)

        self.verticalLayout_112.addLayout(self.showInnerCropField)

        self.cropInnerFieldActions = QVBoxLayout()
        self.cropInnerFieldActions.setObjectName(u"cropInnerFieldActions")
        self.cropInnerFieldActionHeader = QFrame(self.cropInnerFieldTools)
        self.cropInnerFieldActionHeader.setObjectName(u"cropInnerFieldActionHeader")
        self.cropInnerFieldActionHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.cropInnerFieldActionHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_144 = QHBoxLayout(self.cropInnerFieldActionHeader)
        self.horizontalLayout_144.setSpacing(0)
        self.horizontalLayout_144.setObjectName(u"horizontalLayout_144")
        self.horizontalLayout_144.setContentsMargins(0, 0, 0, 0)
        self.cropInnerFieldActionHeaderLabel = QLabel(self.cropInnerFieldActionHeader)
        self.cropInnerFieldActionHeaderLabel.setObjectName(u"cropInnerFieldActionHeaderLabel")
        self.cropInnerFieldActionHeaderLabel.setFont(Fonts["font3"])
        self.cropInnerFieldActionHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_144.addWidget(self.cropInnerFieldActionHeaderLabel)

        self.cropInnerFieldActionHeaderSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_144.addItem(self.cropInnerFieldActionHeaderSpacer)

        self.cropInnerFieldActions.addWidget(self.cropInnerFieldActionHeader)

        self.cropInnerFieldActionButtons = QFrame(self.cropInnerFieldTools)
        self.cropInnerFieldActionButtons.setObjectName(u"cropInnerFieldActionButtons")
        
        SizePolicies["Expanding_Fixed"].setHeightForWidth(self.cropInnerFieldActionButtons.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldActionButtons.setSizePolicy(SizePolicies["Expanding_Fixed"])
        
        self.cropInnerFieldActionButtons.setSizeIncrement(QSize(5, 0))
        self.cropInnerFieldActionButtons.setFrameShape(QFrame.Shape.NoFrame)
        self.cropInnerFieldActionButtons.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_145 = QHBoxLayout(self.cropInnerFieldActionButtons)
        self.horizontalLayout_145.setSpacing(0)
        self.horizontalLayout_145.setObjectName(u"horizontalLayout_145")
        self.horizontalLayout_145.setContentsMargins(0, 0, 0, 0)
        self.cropInnerFieldSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_145.addItem(self.cropInnerFieldSpacerLeft)

        self.cropInnerFieldRedoTool = QFrame(self.cropInnerFieldActionButtons)
        self.cropInnerFieldRedoTool.setObjectName(u"cropInnerFieldRedoTool")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropInnerFieldRedoTool.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldRedoTool.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropInnerFieldRedoTool.setMinimumSize(QSize(49, 49))
        self.cropInnerFieldRedoTool.setMaximumSize(QSize(49, 49))
        self.cropInnerFieldRedoTool.setFrameShape(QFrame.Shape.NoFrame)
        self.cropInnerFieldRedoTool.setFrameShadow(QFrame.Shadow.Raised)
        self.cropInnerFieldRedoButtonShadow = QFrame(self.cropInnerFieldRedoTool)
        self.cropInnerFieldRedoButtonShadow.setObjectName(u"cropInnerFieldRedoButtonShadow")
        self.cropInnerFieldRedoButtonShadow.setGeometry(QRect(3, 3, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropInnerFieldRedoButtonShadow.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldRedoButtonShadow.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropInnerFieldRedoButtonShadow.setStyleSheet(u"background: #8D8D8D; border-radius: 6px;")
        self.cropInnerFieldRedoButtonShadow.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropInnerFieldRedoButtonShadow.setFrameShadow(QFrame.Shadow.Raised)
        self.cropInnerFieldRedoButton = QPushButton(self.cropInnerFieldRedoTool)
        self.cropInnerFieldRedoButton.setObjectName(u"cropInnerFieldRedoButton")
        self.cropInnerFieldRedoButton.setGeometry(QRect(0, 0, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropInnerFieldRedoButton.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldRedoButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropInnerFieldRedoButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.cropInnerFieldRedoButton.setIcon(icon12)
        self.cropInnerFieldRedoButton.setIconSize(QSize(36, 36))
        self.cropInnerFieldRedoButton.setFlat(False)

        self.horizontalLayout_145.addWidget(self.cropInnerFieldRedoTool)

        self.cropInnerFieldActionButtonsSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_145.addItem(self.cropInnerFieldActionButtonsSpacer)

        self.cropInnerFieldEraseTool = QFrame(self.cropInnerFieldActionButtons)
        self.cropInnerFieldEraseTool.setObjectName(u"cropInnerFieldEraseTool")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropInnerFieldEraseTool.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldEraseTool.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropInnerFieldEraseTool.setMinimumSize(QSize(49, 49))
        self.cropInnerFieldEraseTool.setMaximumSize(QSize(49, 49))
        self.cropInnerFieldEraseTool.setFrameShape(QFrame.Shape.NoFrame)
        self.cropInnerFieldEraseTool.setFrameShadow(QFrame.Shadow.Raised)
        self.cropInnerFieldEraseButtonShadow = QFrame(self.cropInnerFieldEraseTool)
        self.cropInnerFieldEraseButtonShadow.setObjectName(u"cropInnerFieldEraseButtonShadow")
        self.cropInnerFieldEraseButtonShadow.setGeometry(QRect(3, 3, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropInnerFieldEraseButtonShadow.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldEraseButtonShadow.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropInnerFieldEraseButtonShadow.setStyleSheet(u"background: #8D8D8D; border-radius: 6px;")
        self.cropInnerFieldEraseButtonShadow.setFrameShape(QFrame.Shape.StyledPanel)
        self.cropInnerFieldEraseButtonShadow.setFrameShadow(QFrame.Shadow.Raised)
        self.cropInnerFieldEraseButton = QPushButton(self.cropInnerFieldEraseTool)
        self.cropInnerFieldEraseButton.setObjectName(u"cropInnerFieldEraseButton")
        self.cropInnerFieldEraseButton.setGeometry(QRect(0, 0, 46, 46))
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.cropInnerFieldEraseButton.sizePolicy().hasHeightForWidth())
        self.cropInnerFieldEraseButton.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.cropInnerFieldEraseButton.setMinimumSize(QSize(46, 46))
        self.cropInnerFieldEraseButton.setMaximumSize(QSize(46, 46))
        self.cropInnerFieldEraseButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.cropInnerFieldEraseButton.setIcon(icon13)
        self.cropInnerFieldEraseButton.setIconSize(QSize(36, 36))
        self.cropInnerFieldEraseButton.setFlat(False)

        self.horizontalLayout_145.addWidget(self.cropInnerFieldEraseTool)

        self.cropInnerFieldSpacerRight = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_145.addItem(self.cropInnerFieldSpacerRight)

        self.cropInnerFieldActions.addWidget(self.cropInnerFieldActionButtons)

        self.verticalLayout_112.addLayout(self.cropInnerFieldActions)

        self.cropInnerFieldSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_112.addItem(self.cropInnerFieldSpacer)

        self.horizontalLayout_142.addWidget(self.cropInnerFieldTools)

        self.visionSteps.addTab(self.cropInnerFieldTab, icon14, "")
        self.segTab = QWidget()
        self.segTab.setObjectName(u"segTab")
        self.segContents = QFrame(self.segTab)
        self.segContents.setObjectName(u"segContents")
        self.segContents.setGeometry(QRect(0, 0, 831, 451))
        
        SizePolicies["Expanding_Expanding"].setHeightForWidth(self.segContents.sizePolicy().hasHeightForWidth())
        self.segContents.setSizePolicy(SizePolicies["Expanding_Expanding"])
        
        self.segContents.setMinimumSize(QSize(737, 402))
        self.segContents.setFrameShape(QFrame.Shape.NoFrame)
        self.segContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_146 = QHBoxLayout(self.segContents)
        self.horizontalLayout_146.setObjectName(u"horizontalLayout_146")
        self.horizontalLayout_146.setContentsMargins(6, 6, 6, 6)
        
#####################
        self.segFrame = SegmentEditor(self.segContents, QPixmap(u"assets/defaultFrame.png"))
        self.segFrame.setObjectName(u"segFrame")
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.segFrame.sizePolicy().hasHeightForWidth())
        self.segFrame.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.segFrame.setScaledContents(True)
        self.segFrame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_146.addWidget(self.segFrame, 0, Qt.AlignmentFlag.AlignTop)

#####################
        self.segTools = QFrame(self.segContents)
        self.segTools.setObjectName(u"segTools")
        
        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.segTools.sizePolicy().hasHeightForWidth())
        self.segTools.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.segTools.setMinimumSize(QSize(0, 392))
        self.segTools.setBaseSize(QSize(0, 0))
        self.segTools.setFrameShape(QFrame.Shape.StyledPanel)
        self.segTools.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_114 = QVBoxLayout(self.segTools)
        self.verticalLayout_114.setObjectName(u"verticalLayout_114")
        self.verticalLayout_114.setContentsMargins(6, 6, 6, 6)
        self.segToolsHeader = QFrame(self.segTools)
        self.segToolsHeader.setObjectName(u"segToolsHeader")
        self.segToolsHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.segToolsHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_147 = QHBoxLayout(self.segToolsHeader)
        self.horizontalLayout_147.setSpacing(0)
        self.horizontalLayout_147.setObjectName(u"horizontalLayout_147")
        self.horizontalLayout_147.setContentsMargins(0, 0, 0, 0)
        self.segToolsHeaderLabel = QLabel(self.segToolsHeader)
        self.segToolsHeaderLabel.setObjectName(u"segToolsHeaderLabel")
        self.segToolsHeaderLabel.setFont(Fonts["font7"])
        self.segToolsHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_147.addWidget(self.segToolsHeaderLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.segToolsHeaderSpacer = QSpacerItem(73, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_147.addItem(self.segToolsHeaderSpacer)


        self.verticalLayout_114.addWidget(self.segToolsHeader)

        self.segToolsContents = QFrame(self.segTools)
        self.segToolsContents.setObjectName(u"segToolsContents")
        self.segToolsContents.setFrameShape(QFrame.Shape.StyledPanel)
        self.segToolsContents.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_115 = QVBoxLayout(self.segToolsContents)
        self.verticalLayout_115.setSpacing(0)
        self.verticalLayout_115.setObjectName(u"verticalLayout_115")
        self.verticalLayout_115.setContentsMargins(0, 0, 0, 0)
        self.hue = QFrame(self.segToolsContents)
        self.hue.setObjectName(u"hue")
        self.hue.setFrameShape(QFrame.Shape.NoFrame)
        self.hue.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_116 = QVBoxLayout(self.hue)
        self.verticalLayout_116.setSpacing(0)
        self.verticalLayout_116.setObjectName(u"verticalLayout_116")
        self.verticalLayout_116.setContentsMargins(0, 0, 0, 0)
        self.hueHeader = QFrame(self.hue)
        self.hueHeader.setObjectName(u"hueHeader")
        self.hueHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.hueHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_148 = QHBoxLayout(self.hueHeader)
        self.horizontalLayout_148.setSpacing(0)
        self.horizontalLayout_148.setObjectName(u"horizontalLayout_148")
        self.horizontalLayout_148.setContentsMargins(0, 0, 0, 0)
        self.hueTitle = QLabel(self.hueHeader)
        self.hueTitle.setObjectName(u"hueTitle")
        self.hueTitle.setFont(Fonts["font2"])
        self.hueTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_148.addWidget(self.hueTitle)

        self.hueHeaderSlider = QSpacerItem(242, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_148.addItem(self.hueHeaderSlider)


        self.verticalLayout_116.addWidget(self.hueHeader)

        self.hueValues = QFrame(self.hue)
        self.hueValues.setObjectName(u"hueValues")
        self.hueValues.setFrameShape(QFrame.Shape.NoFrame)
        self.hueValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_117 = QVBoxLayout(self.hueValues)
        self.verticalLayout_117.setObjectName(u"verticalLayout_117")
        self.verticalLayout_117.setContentsMargins(6, 6, 6, 6)
        self.hueMin = QVBoxLayout()
        self.hueMin.setObjectName(u"hueMin")
        self.hueMinLabel = QLabel(self.hueValues)
        self.hueMinLabel.setObjectName(u"hueMinLabel")
        self.hueMinLabel.setFont(Fonts["font3"])
        self.hueMinLabel.setScaledContents(True)
        self.hueMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hueMin.addWidget(self.hueMinLabel)

        self.hueMinContents = QFrame(self.hueValues)
        self.hueMinContents.setObjectName(u"hueMinContents")
        self.hueMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.hueMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_149 = QHBoxLayout(self.hueMinContents)
        self.horizontalLayout_149.setSpacing(6)
        self.horizontalLayout_149.setObjectName(u"horizontalLayout_149")
        self.horizontalLayout_149.setContentsMargins(0, 0, 0, 0)
        self.hueMinSlider = QSlider(self.hueMinContents)
        self.hueMinSlider.setObjectName(u"hueMinSlider")
        self.hueMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.hueMinSlider.setMaximum(180)
        self.hueMinSlider.setValue(0)
        self.hueMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.hueMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hueMinSlider.setTickInterval(10)

        self.horizontalLayout_149.addWidget(self.hueMinSlider)

        self.hueMinValue = QLabel(self.hueMinContents)
        self.hueMinValue.setObjectName(u"hueMinValue")
        self.hueMinValue.setScaledContents(True)
        self.hueMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_149.addWidget(self.hueMinValue)


        self.hueMin.addWidget(self.hueMinContents)


        self.verticalLayout_117.addLayout(self.hueMin)

        self.hueMax = QVBoxLayout()
        self.hueMax.setObjectName(u"hueMax")
        self.hueMaxLabel = QLabel(self.hueValues)
        self.hueMaxLabel.setObjectName(u"hueMaxLabel")
        self.hueMaxLabel.setFont(Fonts["font3"])
        self.hueMaxLabel.setScaledContents(True)
        self.hueMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hueMax.addWidget(self.hueMaxLabel)

        self.hueMaxContents = QFrame(self.hueValues)
        self.hueMaxContents.setObjectName(u"hueMaxContents")
        self.hueMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.hueMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_150 = QHBoxLayout(self.hueMaxContents)
        self.horizontalLayout_150.setSpacing(6)
        self.horizontalLayout_150.setObjectName(u"horizontalLayout_150")
        self.horizontalLayout_150.setContentsMargins(0, 0, 0, 0)
        self.hueMaxSlider = QSlider(self.hueMaxContents)
        self.hueMaxSlider.setObjectName(u"hueMaxSlider")
        self.hueMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.hueMaxSlider.setMaximum(180)
        self.hueMaxSlider.setValue(180)
        self.hueMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.hueMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hueMaxSlider.setTickInterval(10)

        self.horizontalLayout_150.addWidget(self.hueMaxSlider)

        self.hueMaxValue = QLabel(self.hueMaxContents)
        self.hueMaxValue.setObjectName(u"hueMaxValue")
        self.hueMaxValue.setScaledContents(True)
        self.hueMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_150.addWidget(self.hueMaxValue)


        self.hueMax.addWidget(self.hueMaxContents)


        self.verticalLayout_117.addLayout(self.hueMax)


        self.verticalLayout_116.addWidget(self.hueValues)


        self.verticalLayout_115.addWidget(self.hue)

        self.saturation = QFrame(self.segToolsContents)
        self.saturation.setObjectName(u"saturation")
        self.saturation.setFrameShape(QFrame.Shape.NoFrame)
        self.saturation.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_118 = QVBoxLayout(self.saturation)
        self.verticalLayout_118.setSpacing(0)
        self.verticalLayout_118.setObjectName(u"verticalLayout_118")
        self.verticalLayout_118.setContentsMargins(0, 0, 0, 0)
        self.satHeader = QFrame(self.saturation)
        self.satHeader.setObjectName(u"satHeader")
        self.satHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.satHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_151 = QHBoxLayout(self.satHeader)
        self.horizontalLayout_151.setSpacing(0)
        self.horizontalLayout_151.setObjectName(u"horizontalLayout_151")
        self.horizontalLayout_151.setContentsMargins(0, 0, 0, 0)
        self.satTitle = QLabel(self.satHeader)
        self.satTitle.setObjectName(u"satTitle")
        self.satTitle.setFont(Fonts["font2"])
        self.satTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_151.addWidget(self.satTitle)

        self.satHeaderSlider = QSpacerItem(191, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_151.addItem(self.satHeaderSlider)


        self.verticalLayout_118.addWidget(self.satHeader)

        self.satValues = QFrame(self.saturation)
        self.satValues.setObjectName(u"satValues")
        self.satValues.setFrameShape(QFrame.Shape.NoFrame)
        self.satValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_119 = QVBoxLayout(self.satValues)
        self.verticalLayout_119.setObjectName(u"verticalLayout_119")
        self.verticalLayout_119.setContentsMargins(6, 6, 6, 6)
        self.satMin = QVBoxLayout()
        self.satMin.setObjectName(u"satMin")
        self.satMinLabel = QLabel(self.satValues)
        self.satMinLabel.setObjectName(u"satMinLabel")
        self.satMinLabel.setFont(Fonts["font3"])
        self.satMinLabel.setScaledContents(True)
        self.satMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.satMin.addWidget(self.satMinLabel)

        self.satMinContents = QFrame(self.satValues)
        self.satMinContents.setObjectName(u"satMinContents")
        self.satMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.satMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_152 = QHBoxLayout(self.satMinContents)
        self.horizontalLayout_152.setSpacing(6)
        self.horizontalLayout_152.setObjectName(u"horizontalLayout_152")
        self.horizontalLayout_152.setContentsMargins(0, 0, 0, 0)
        self.satMinSlider = QSlider(self.satMinContents)
        self.satMinSlider.setObjectName(u"satMinSlider")
        self.satMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.satMinSlider.setMaximum(255)
        self.satMinSlider.setValue(38)
        self.satMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.satMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.satMinSlider.setTickInterval(10)

        self.horizontalLayout_152.addWidget(self.satMinSlider)

        self.satMinValue = QLabel(self.satMinContents)
        self.satMinValue.setObjectName(u"satMinValue")
        self.satMinValue.setScaledContents(True)
        self.satMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_152.addWidget(self.satMinValue)


        self.satMin.addWidget(self.satMinContents)


        self.verticalLayout_119.addLayout(self.satMin)

        self.satMax = QVBoxLayout()
        self.satMax.setObjectName(u"satMax")
        self.satMaxLabel = QLabel(self.satValues)
        self.satMaxLabel.setObjectName(u"satMaxLabel")
        self.satMaxLabel.setFont(Fonts["font3"])
        self.satMaxLabel.setScaledContents(True)
        self.satMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.satMax.addWidget(self.satMaxLabel)

        self.satMaxContents = QFrame(self.satValues)
        self.satMaxContents.setObjectName(u"satMaxContents")
        self.satMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.satMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_153 = QHBoxLayout(self.satMaxContents)
        self.horizontalLayout_153.setSpacing(6)
        self.horizontalLayout_153.setObjectName(u"horizontalLayout_153")
        self.horizontalLayout_153.setContentsMargins(0, 0, 0, 0)
        self.satMaxSlider = QSlider(self.satMaxContents)
        self.satMaxSlider.setObjectName(u"satMaxSlider")
        self.satMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.satMaxSlider.setMaximum(255)
        self.satMaxSlider.setValue(255)
        self.satMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.satMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.satMaxSlider.setTickInterval(10)

        self.horizontalLayout_153.addWidget(self.satMaxSlider)

        self.satMaxValue = QLabel(self.satMaxContents)
        self.satMaxValue.setObjectName(u"satMaxValue")
        self.satMaxValue.setScaledContents(True)
        self.satMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_153.addWidget(self.satMaxValue)


        self.satMax.addWidget(self.satMaxContents)


        self.verticalLayout_119.addLayout(self.satMax)


        self.verticalLayout_118.addWidget(self.satValues)


        self.verticalLayout_115.addWidget(self.saturation)

        self.value = QFrame(self.segToolsContents)
        self.value.setObjectName(u"value")
        self.value.setFrameShape(QFrame.Shape.NoFrame)
        self.value.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_120 = QVBoxLayout(self.value)
        self.verticalLayout_120.setSpacing(0)
        self.verticalLayout_120.setObjectName(u"verticalLayout_120")
        self.verticalLayout_120.setContentsMargins(0, 0, 0, 0)
        self.valueHeader = QFrame(self.value)
        self.valueHeader.setObjectName(u"valueHeader")
        self.valueHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.valueHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_154 = QHBoxLayout(self.valueHeader)
        self.horizontalLayout_154.setSpacing(0)
        self.horizontalLayout_154.setObjectName(u"horizontalLayout_154")
        self.horizontalLayout_154.setContentsMargins(0, 0, 0, 0)
        self.valueTitle = QLabel(self.valueHeader)
        self.valueTitle.setObjectName(u"valueTitle")
        self.valueTitle.setFont(Fonts["font2"])
        self.valueTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_154.addWidget(self.valueTitle)

        self.valueHeaderSlider = QSpacerItem(191, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_154.addItem(self.valueHeaderSlider)


        self.verticalLayout_120.addWidget(self.valueHeader)

        self.valueValues = QFrame(self.value)
        self.valueValues.setObjectName(u"valueValues")
        self.valueValues.setFrameShape(QFrame.Shape.NoFrame)
        self.valueValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_121 = QVBoxLayout(self.valueValues)
        self.verticalLayout_121.setObjectName(u"verticalLayout_121")
        self.verticalLayout_121.setContentsMargins(6, 6, 6, 6)
        self.valueMin = QVBoxLayout()
        self.valueMin.setObjectName(u"valueMin")
        self.valueMinLabel = QLabel(self.valueValues)
        self.valueMinLabel.setObjectName(u"valueMinLabel")
        self.valueMinLabel.setFont(Fonts["font3"])
        self.valueMinLabel.setScaledContents(True)
        self.valueMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.valueMin.addWidget(self.valueMinLabel)

        self.valueMinContents = QFrame(self.valueValues)
        self.valueMinContents.setObjectName(u"valueMinContents")
        self.valueMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.valueMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_155 = QHBoxLayout(self.valueMinContents)
        self.horizontalLayout_155.setSpacing(6)
        self.horizontalLayout_155.setObjectName(u"horizontalLayout_155")
        self.horizontalLayout_155.setContentsMargins(0, 0, 0, 0)
        self.valueMinSlider = QSlider(self.valueMinContents)
        self.valueMinSlider.setObjectName(u"valueMinSlider")
        self.valueMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.valueMinSlider.setMaximum(255)
        self.valueMinSlider.setValue(198)
        self.valueMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.valueMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.valueMinSlider.setTickInterval(10)

        self.horizontalLayout_155.addWidget(self.valueMinSlider)

        self.valueMinValue = QLabel(self.valueMinContents)
        self.valueMinValue.setObjectName(u"valueMinValue")
        self.valueMinValue.setScaledContents(True)
        self.valueMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_155.addWidget(self.valueMinValue)


        self.valueMin.addWidget(self.valueMinContents)


        self.verticalLayout_121.addLayout(self.valueMin)

        self.valueMax = QVBoxLayout()
        self.valueMax.setObjectName(u"valueMax")
        self.valueMaxLabel = QLabel(self.valueValues)
        self.valueMaxLabel.setObjectName(u"valueMaxLabel")
        self.valueMaxLabel.setFont(Fonts["font3"])
        self.valueMaxLabel.setScaledContents(True)
        self.valueMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.valueMax.addWidget(self.valueMaxLabel)

        self.valueMaxContents = QFrame(self.valueValues)
        self.valueMaxContents.setObjectName(u"valueMaxContents")
        self.valueMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.valueMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_156 = QHBoxLayout(self.valueMaxContents)
        self.horizontalLayout_156.setSpacing(6)
        self.horizontalLayout_156.setObjectName(u"horizontalLayout_156")
        self.horizontalLayout_156.setContentsMargins(0, 0, 0, 0)
        self.valueMaxSlider = QSlider(self.valueMaxContents)
        self.valueMaxSlider.setObjectName(u"valueMaxSlider")
        self.valueMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.valueMaxSlider.setMaximum(255)
        self.valueMaxSlider.setValue(255)
        self.valueMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.valueMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.valueMaxSlider.setTickInterval(10)

        self.horizontalLayout_156.addWidget(self.valueMaxSlider)

        self.valueMaxValue = QLabel(self.valueMaxContents)
        self.valueMaxValue.setObjectName(u"valueMaxValue")
        self.valueMaxValue.setScaledContents(True)
        self.valueMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_156.addWidget(self.valueMaxValue)


        self.valueMax.addWidget(self.valueMaxContents)


        self.verticalLayout_121.addLayout(self.valueMax)


        self.verticalLayout_120.addWidget(self.valueValues)


        self.verticalLayout_115.addWidget(self.value)


        self.verticalLayout_114.addWidget(self.segToolsContents)

        self.segSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_114.addItem(self.segSpacer)


        self.horizontalLayout_146.addWidget(self.segTools)

        self.visionSteps.addTab(self.segTab, icon14, "")
        self.segTeamTab = QWidget()
        self.segTeamTab.setObjectName(u"segTeamTab")
        self.segTeamContents = QFrame(self.segTeamTab)
        self.segTeamContents.setObjectName(u"segTeamContents")
        self.segTeamContents.setGeometry(QRect(0, 0, 831, 451))
        
        SizePolicies["Expanding_Expanding"].setHeightForWidth(self.segTeamContents.sizePolicy().hasHeightForWidth())
        self.segTeamContents.setSizePolicy(SizePolicies["Expanding_Expanding"])
        
        self.segTeamContents.setMinimumSize(QSize(737, 402))
        self.segTeamContents.setFrameShape(QFrame.Shape.NoFrame)
        self.segTeamContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_157 = QHBoxLayout(self.segTeamContents)
        self.horizontalLayout_157.setObjectName(u"horizontalLayout_157")
        self.horizontalLayout_157.setContentsMargins(6, 6, 6, 6)
        
        self.segTeamFrame = SegmentEditor(self.segTeamContents, QPixmap(u"assets/defaultFrame.png"))
        self.segTeamFrame.setObjectName(u"segTeamFrame")
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.segTeamFrame.sizePolicy().hasHeightForWidth())
        self.segTeamFrame.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.segTeamFrame.setScaledContents(True)
        self.segTeamFrame.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.horizontalLayout_157.addWidget(self.segTeamFrame, 0, Qt.AlignmentFlag.AlignTop)

        self.segTeamTools = QFrame(self.segTeamContents)
        self.segTeamTools.setObjectName(u"segTeamTools")
        
        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.segTeamTools.sizePolicy().hasHeightForWidth())
        self.segTeamTools.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.segTeamTools.setMinimumSize(QSize(0, 392))
        self.segTeamTools.setBaseSize(QSize(0, 0))
        self.segTeamTools.setFrameShape(QFrame.Shape.StyledPanel)
        self.segTeamTools.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_123 = QVBoxLayout(self.segTeamTools)
        self.verticalLayout_123.setObjectName(u"verticalLayout_123")
        self.verticalLayout_123.setContentsMargins(6, 6, 6, 6)
        self.segTeamToolsHeader = QFrame(self.segTeamTools)
        self.segTeamToolsHeader.setObjectName(u"segTeamToolsHeader")
        self.segTeamToolsHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.segTeamToolsHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_158 = QHBoxLayout(self.segTeamToolsHeader)
        self.horizontalLayout_158.setSpacing(0)
        self.horizontalLayout_158.setObjectName(u"horizontalLayout_158")
        self.horizontalLayout_158.setContentsMargins(0, 0, 0, 0)
        self.segTeamToolsHeaderLabel = QLabel(self.segTeamToolsHeader)
        self.segTeamToolsHeaderLabel.setObjectName(u"segTeamToolsHeaderLabel")
        self.segTeamToolsHeaderLabel.setFont(Fonts["font7"])
        self.segTeamToolsHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_158.addWidget(self.segTeamToolsHeaderLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.segTeamToolsHeaderSpacer = QSpacerItem(73, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_158.addItem(self.segTeamToolsHeaderSpacer)


        self.verticalLayout_123.addWidget(self.segTeamToolsHeader)

        self.segTeamToolsContents = QFrame(self.segTeamTools)
        self.segTeamToolsContents.setObjectName(u"segTeamToolsContents")
        self.segTeamToolsContents.setFrameShape(QFrame.Shape.StyledPanel)
        self.segTeamToolsContents.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_124 = QVBoxLayout(self.segTeamToolsContents)
        self.verticalLayout_124.setSpacing(0)
        self.verticalLayout_124.setObjectName(u"verticalLayout_124")
        self.verticalLayout_124.setContentsMargins(0, 0, 0, 0)
        self.hueTeam = QFrame(self.segTeamToolsContents)
        self.hueTeam.setObjectName(u"hueTeam")
        self.hueTeam.setFrameShape(QFrame.Shape.NoFrame)
        self.hueTeam.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_125 = QVBoxLayout(self.hueTeam)
        self.verticalLayout_125.setSpacing(0)
        self.verticalLayout_125.setObjectName(u"verticalLayout_125")
        self.verticalLayout_125.setContentsMargins(0, 0, 0, 0)
        self.hueTeamHeader = QFrame(self.hueTeam)
        self.hueTeamHeader.setObjectName(u"hueTeamHeader")
        self.hueTeamHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.hueTeamHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_159 = QHBoxLayout(self.hueTeamHeader)
        self.horizontalLayout_159.setSpacing(0)
        self.horizontalLayout_159.setObjectName(u"horizontalLayout_159")
        self.horizontalLayout_159.setContentsMargins(0, 0, 0, 0)
        self.hueTeamTitle = QLabel(self.hueTeamHeader)
        self.hueTeamTitle.setObjectName(u"hueTeamTitle")
        self.hueTeamTitle.setFont(Fonts["font2"])
        self.hueTeamTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_159.addWidget(self.hueTeamTitle)

        self.hueTeamHeaderSlider = QSpacerItem(242, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_159.addItem(self.hueTeamHeaderSlider)


        self.verticalLayout_125.addWidget(self.hueTeamHeader)

        self.hueTeamValues = QFrame(self.hueTeam)
        self.hueTeamValues.setObjectName(u"hueTeamValues")
        self.hueTeamValues.setFrameShape(QFrame.Shape.NoFrame)
        self.hueTeamValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_126 = QVBoxLayout(self.hueTeamValues)
        self.verticalLayout_126.setObjectName(u"verticalLayout_126")
        self.verticalLayout_126.setContentsMargins(6, 6, 6, 6)
        self.hueTeamMin = QVBoxLayout()
        self.hueTeamMin.setObjectName(u"hueTeamMin")
        self.hueTeamMinLabel = QLabel(self.hueTeamValues)
        self.hueTeamMinLabel.setObjectName(u"hueTeamMinLabel")
        self.hueTeamMinLabel.setFont(Fonts["font3"])
        self.hueTeamMinLabel.setScaledContents(True)
        self.hueTeamMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hueTeamMin.addWidget(self.hueTeamMinLabel)

        self.hueTeamMinContents = QFrame(self.hueTeamValues)
        self.hueTeamMinContents.setObjectName(u"hueTeamMinContents")
        self.hueTeamMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.hueTeamMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_160 = QHBoxLayout(self.hueTeamMinContents)
        self.horizontalLayout_160.setSpacing(6)
        self.horizontalLayout_160.setObjectName(u"horizontalLayout_160")
        self.horizontalLayout_160.setContentsMargins(0, 0, 0, 0)
        self.hueTeamMinSlider = QSlider(self.hueTeamMinContents)
        self.hueTeamMinSlider.setObjectName(u"hueTeamMinSlider")
        self.hueTeamMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.hueTeamMinSlider.setMaximum(180)
        self.hueTeamMinSlider.setValue(0)
        self.hueTeamMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.hueTeamMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hueTeamMinSlider.setTickInterval(10)

        self.horizontalLayout_160.addWidget(self.hueTeamMinSlider)

        self.hueTeamMinValue = QLabel(self.hueTeamMinContents)
        self.hueTeamMinValue.setObjectName(u"hueTeamMinValue")
        self.hueTeamMinValue.setScaledContents(True)
        self.hueTeamMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_160.addWidget(self.hueTeamMinValue)


        self.hueTeamMin.addWidget(self.hueTeamMinContents)


        self.verticalLayout_126.addLayout(self.hueTeamMin)

        self.hueTeamMax = QVBoxLayout()
        self.hueTeamMax.setObjectName(u"hueTeamMax")
        self.hueTeamMaxLabel = QLabel(self.hueTeamValues)
        self.hueTeamMaxLabel.setObjectName(u"hueTeamMaxLabel")
        self.hueTeamMaxLabel.setFont(Fonts["font3"])
        self.hueTeamMaxLabel.setScaledContents(True)
        self.hueTeamMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hueTeamMax.addWidget(self.hueTeamMaxLabel)

        self.hueTeamMaxContents = QFrame(self.hueTeamValues)
        self.hueTeamMaxContents.setObjectName(u"hueTeamMaxContents")
        self.hueTeamMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.hueTeamMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_161 = QHBoxLayout(self.hueTeamMaxContents)
        self.horizontalLayout_161.setSpacing(6)
        self.horizontalLayout_161.setObjectName(u"horizontalLayout_161")
        self.horizontalLayout_161.setContentsMargins(0, 0, 0, 0)
        self.hueTeamMaxSlider = QSlider(self.hueTeamMaxContents)
        self.hueTeamMaxSlider.setObjectName(u"hueTeamMaxSlider")
        self.hueTeamMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.hueTeamMaxSlider.setMaximum(180)
        self.hueTeamMaxSlider.setValue(180)
        self.hueTeamMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.hueTeamMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hueTeamMaxSlider.setTickInterval(10)

        self.horizontalLayout_161.addWidget(self.hueTeamMaxSlider)

        self.hueTeamMaxValue = QLabel(self.hueTeamMaxContents)
        self.hueTeamMaxValue.setObjectName(u"hueTeamMaxValue")
        self.hueTeamMaxValue.setScaledContents(True)
        self.hueTeamMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_161.addWidget(self.hueTeamMaxValue)


        self.hueTeamMax.addWidget(self.hueTeamMaxContents)


        self.verticalLayout_126.addLayout(self.hueTeamMax)


        self.verticalLayout_125.addWidget(self.hueTeamValues)


        self.verticalLayout_124.addWidget(self.hueTeam)

        self.sTeam = QFrame(self.segTeamToolsContents)
        self.sTeam.setObjectName(u"sTeam")
        self.sTeam.setFrameShape(QFrame.Shape.NoFrame)
        self.sTeam.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_127 = QVBoxLayout(self.sTeam)
        self.verticalLayout_127.setSpacing(0)
        self.verticalLayout_127.setObjectName(u"verticalLayout_127")
        self.verticalLayout_127.setContentsMargins(0, 0, 0, 0)
        self.sTeamHeader = QFrame(self.sTeam)
        self.sTeamHeader.setObjectName(u"sTeamHeader")
        self.sTeamHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.sTeamHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_162 = QHBoxLayout(self.sTeamHeader)
        self.horizontalLayout_162.setSpacing(0)
        self.horizontalLayout_162.setObjectName(u"horizontalLayout_162")
        self.horizontalLayout_162.setContentsMargins(0, 0, 0, 0)
        self.sTeamTitle = QLabel(self.sTeamHeader)
        self.sTeamTitle.setObjectName(u"sTeamTitle")
        self.sTeamTitle.setFont(Fonts["font2"])
        self.sTeamTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_162.addWidget(self.sTeamTitle)

        self.sTeamHeaderSlider = QSpacerItem(191, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_162.addItem(self.sTeamHeaderSlider)


        self.verticalLayout_127.addWidget(self.sTeamHeader)

        self.sTeamValues = QFrame(self.sTeam)
        self.sTeamValues.setObjectName(u"sTeamValues")
        self.sTeamValues.setFrameShape(QFrame.Shape.NoFrame)
        self.sTeamValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_128 = QVBoxLayout(self.sTeamValues)
        self.verticalLayout_128.setObjectName(u"verticalLayout_128")
        self.verticalLayout_128.setContentsMargins(6, 6, 6, 6)
        self.sTeamMin = QVBoxLayout()
        self.sTeamMin.setObjectName(u"sTeamMin")
        self.sTeamMinLabel = QLabel(self.sTeamValues)
        self.sTeamMinLabel.setObjectName(u"sTeamMinLabel")
        self.sTeamMinLabel.setFont(Fonts["font3"])
        self.sTeamMinLabel.setScaledContents(True)
        self.sTeamMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sTeamMin.addWidget(self.sTeamMinLabel)

        self.sTeamMinContents = QFrame(self.sTeamValues)
        self.sTeamMinContents.setObjectName(u"sTeamMinContents")
        self.sTeamMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.sTeamMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_163 = QHBoxLayout(self.sTeamMinContents)
        self.horizontalLayout_163.setSpacing(6)
        self.horizontalLayout_163.setObjectName(u"horizontalLayout_163")
        self.horizontalLayout_163.setContentsMargins(0, 0, 0, 0)
        self.sTeamMinSlider = QSlider(self.sTeamMinContents)
        self.sTeamMinSlider.setObjectName(u"sTeamMinSlider")
        self.sTeamMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.sTeamMinSlider.setMaximum(180)
        self.sTeamMinSlider.setValue(38)
        self.sTeamMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.sTeamMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sTeamMinSlider.setTickInterval(10)

        self.horizontalLayout_163.addWidget(self.sTeamMinSlider)

        self.sTeamMinValue = QLabel(self.sTeamMinContents)
        self.sTeamMinValue.setObjectName(u"sTeamMinValue")
        self.sTeamMinValue.setScaledContents(True)
        self.sTeamMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_163.addWidget(self.sTeamMinValue)


        self.sTeamMin.addWidget(self.sTeamMinContents)


        self.verticalLayout_128.addLayout(self.sTeamMin)

        self.sTeamMax = QVBoxLayout()
        self.sTeamMax.setObjectName(u"sTeamMax")
        self.sTeamMaxLabel = QLabel(self.sTeamValues)
        self.sTeamMaxLabel.setObjectName(u"sTeamMaxLabel")
        self.sTeamMaxLabel.setFont(Fonts["font3"])
        self.sTeamMaxLabel.setScaledContents(True)
        self.sTeamMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sTeamMax.addWidget(self.sTeamMaxLabel)

        self.sTeamMaxContents = QFrame(self.sTeamValues)
        self.sTeamMaxContents.setObjectName(u"sTeamMaxContents")
        self.sTeamMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.sTeamMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_164 = QHBoxLayout(self.sTeamMaxContents)
        self.horizontalLayout_164.setSpacing(6)
        self.horizontalLayout_164.setObjectName(u"horizontalLayout_164")
        self.horizontalLayout_164.setContentsMargins(0, 0, 0, 0)
        self.sTeamMaxSlider = QSlider(self.sTeamMaxContents)
        self.sTeamMaxSlider.setObjectName(u"sTeamMaxSlider")
        self.sTeamMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.sTeamMaxSlider.setMaximum(255)
        self.sTeamMaxSlider.setValue(255)
        self.sTeamMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.sTeamMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sTeamMaxSlider.setTickInterval(10)

        self.horizontalLayout_164.addWidget(self.sTeamMaxSlider)

        self.sTeamMaxValue = QLabel(self.sTeamMaxContents)
        self.sTeamMaxValue.setObjectName(u"sTeamMaxValue")
        self.sTeamMaxValue.setScaledContents(True)
        self.sTeamMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_164.addWidget(self.sTeamMaxValue)


        self.sTeamMax.addWidget(self.sTeamMaxContents)


        self.verticalLayout_128.addLayout(self.sTeamMax)


        self.verticalLayout_127.addWidget(self.sTeamValues)


        self.verticalLayout_124.addWidget(self.sTeam)

        self.vTeam = QFrame(self.segTeamToolsContents)
        self.vTeam.setObjectName(u"vTeam")
        self.vTeam.setFrameShape(QFrame.Shape.NoFrame)
        self.vTeam.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_129 = QVBoxLayout(self.vTeam)
        self.verticalLayout_129.setSpacing(0)
        self.verticalLayout_129.setObjectName(u"verticalLayout_129")
        self.verticalLayout_129.setContentsMargins(0, 0, 0, 0)
        self.vTeamHeader = QFrame(self.vTeam)
        self.vTeamHeader.setObjectName(u"vTeamHeader")
        self.vTeamHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.vTeamHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_165 = QHBoxLayout(self.vTeamHeader)
        self.horizontalLayout_165.setSpacing(0)
        self.horizontalLayout_165.setObjectName(u"horizontalLayout_165")
        self.horizontalLayout_165.setContentsMargins(0, 0, 0, 0)
        self.vTeamTitle = QLabel(self.vTeamHeader)
        self.vTeamTitle.setObjectName(u"vTeamTitle")
        self.vTeamTitle.setFont(Fonts["font2"])
        self.vTeamTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_165.addWidget(self.vTeamTitle)

        self.vTeamHeaderSlider = QSpacerItem(191, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_165.addItem(self.vTeamHeaderSlider)


        self.verticalLayout_129.addWidget(self.vTeamHeader)

        self.vTeamValues = QFrame(self.vTeam)
        self.vTeamValues.setObjectName(u"vTeamValues")
        self.vTeamValues.setFrameShape(QFrame.Shape.NoFrame)
        self.vTeamValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_130 = QVBoxLayout(self.vTeamValues)
        self.verticalLayout_130.setObjectName(u"verticalLayout_130")
        self.verticalLayout_130.setContentsMargins(6, 6, 6, 6)
        self.vTeamMin = QVBoxLayout()
        self.vTeamMin.setObjectName(u"vTeamMin")
        self.vTeamMinLabel = QLabel(self.vTeamValues)
        self.vTeamMinLabel.setObjectName(u"vTeamMinLabel")
        self.vTeamMinLabel.setFont(Fonts["font3"])
        self.vTeamMinLabel.setScaledContents(True)
        self.vTeamMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vTeamMin.addWidget(self.vTeamMinLabel)

        self.vTeamMinContents = QFrame(self.vTeamValues)
        self.vTeamMinContents.setObjectName(u"vTeamMinContents")
        self.vTeamMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.vTeamMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_166 = QHBoxLayout(self.vTeamMinContents)
        self.horizontalLayout_166.setSpacing(6)
        self.horizontalLayout_166.setObjectName(u"horizontalLayout_166")
        self.horizontalLayout_166.setContentsMargins(0, 0, 0, 0)
        self.vTeamMinSlider = QSlider(self.vTeamMinContents)
        self.vTeamMinSlider.setObjectName(u"vTeamMinSlider")
        self.vTeamMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.vTeamMinSlider.setMaximum(255)
        self.vTeamMinSlider.setValue(198)
        self.vTeamMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.vTeamMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.vTeamMinSlider.setTickInterval(10)

        self.horizontalLayout_166.addWidget(self.vTeamMinSlider)

        self.vTeamMinValue = QLabel(self.vTeamMinContents)
        self.vTeamMinValue.setObjectName(u"vTeamMinValue")
        self.vTeamMinValue.setScaledContents(True)
        self.vTeamMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_166.addWidget(self.vTeamMinValue)


        self.vTeamMin.addWidget(self.vTeamMinContents)


        self.verticalLayout_130.addLayout(self.vTeamMin)

        self.vTeamMax = QVBoxLayout()
        self.vTeamMax.setObjectName(u"vTeamMax")
        self.vTeamMaxLabel = QLabel(self.vTeamValues)
        self.vTeamMaxLabel.setObjectName(u"vTeamMaxLabel")
        self.vTeamMaxLabel.setFont(Fonts["font3"])
        self.vTeamMaxLabel.setScaledContents(True)
        self.vTeamMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vTeamMax.addWidget(self.vTeamMaxLabel)

        self.vTeamMaxContents = QFrame(self.vTeamValues)
        self.vTeamMaxContents.setObjectName(u"vTeamMaxContents")
        self.vTeamMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.vTeamMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_167 = QHBoxLayout(self.vTeamMaxContents)
        self.horizontalLayout_167.setSpacing(6)
        self.horizontalLayout_167.setObjectName(u"horizontalLayout_167")
        self.horizontalLayout_167.setContentsMargins(0, 0, 0, 0)
        self.vTeamMaxSlider = QSlider(self.vTeamMaxContents)
        self.vTeamMaxSlider.setObjectName(u"vTeamMaxSlider")
        self.vTeamMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.vTeamMaxSlider.setMaximum(255)
        self.vTeamMaxSlider.setValue(255)
        self.vTeamMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.vTeamMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.vTeamMaxSlider.setTickInterval(10)

        self.horizontalLayout_167.addWidget(self.vTeamMaxSlider)

        self.vTeamMaxValue = QLabel(self.vTeamMaxContents)
        self.vTeamMaxValue.setObjectName(u"vTeamMaxValue")
        self.vTeamMaxValue.setScaledContents(True)
        self.vTeamMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_167.addWidget(self.vTeamMaxValue)


        self.vTeamMax.addWidget(self.vTeamMaxContents)


        self.verticalLayout_130.addLayout(self.vTeamMax)


        self.verticalLayout_129.addWidget(self.vTeamValues)


        self.verticalLayout_124.addWidget(self.vTeam)


        self.verticalLayout_123.addWidget(self.segTeamToolsContents)

        self.segTeamSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_123.addItem(self.segTeamSpacer)


        self.horizontalLayout_157.addWidget(self.segTeamTools)

        self.visionSteps.addTab(self.segTeamTab, icon14, "")
        #############################################
        self.segBallTab = QWidget()
        self.segBallTab.setObjectName(u"segBallTab")
        self.segBallContents = QFrame(self.segBallTab)
        self.segBallContents.setObjectName(u"segBallContents")
        self.segBallContents.setGeometry(QRect(0, 0, 831, 451))
        
        SizePolicies["Expanding_Expanding"].setHeightForWidth(self.segBallContents.sizePolicy().hasHeightForWidth())
        self.segBallContents.setSizePolicy(SizePolicies["Expanding_Expanding"])
        
        self.segBallContents.setMinimumSize(QSize(737, 402))
        self.segBallContents.setFrameShape(QFrame.Shape.NoFrame)
        self.segBallContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_168 = QHBoxLayout(self.segBallContents)
        self.horizontalLayout_168.setObjectName(u"horizontalLayout_168")
        self.horizontalLayout_168.setContentsMargins(6, 6, 6, 6)
       
        self.segBallFrame = SegmentEditor(self.segBallContents, QPixmap(u"assets/defaultFrame.png"))
        self.segBallFrame.setObjectName(u"segBallFrame")
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.segBallFrame.sizePolicy().hasHeightForWidth())
        self.segBallFrame.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.segBallFrame.setScaledContents(True)
        self.segBallFrame.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.horizontalLayout_168.addWidget(self.segBallFrame, 0, Qt.AlignmentFlag.AlignTop)

        self.segBallTools = QFrame(self.segBallContents)
        self.segBallTools.setObjectName(u"segBallTools")
        
        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.segBallTools.sizePolicy().hasHeightForWidth())
        self.segBallTools.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.segBallTools.setMinimumSize(QSize(0, 392))
        self.segBallTools.setBaseSize(QSize(0, 0))
        self.segBallTools.setFrameShape(QFrame.Shape.StyledPanel)
        self.segBallTools.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_132 = QVBoxLayout(self.segBallTools)
        self.verticalLayout_132.setObjectName(u"verticalLayout_132")
        self.verticalLayout_132.setContentsMargins(6, 6, 6, 6)
        self.ballToolsHeader = QFrame(self.segBallTools)
        self.ballToolsHeader.setObjectName(u"ballToolsHeader")
        self.ballToolsHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.ballToolsHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_169 = QHBoxLayout(self.ballToolsHeader)
        self.horizontalLayout_169.setSpacing(0)
        self.horizontalLayout_169.setObjectName(u"horizontalLayout_169")
        self.horizontalLayout_169.setContentsMargins(0, 0, 0, 0)
        self.ballToolsHeaderLabel = QLabel(self.ballToolsHeader)
        self.ballToolsHeaderLabel.setObjectName(u"ballToolsHeaderLabel")
        self.ballToolsHeaderLabel.setFont(Fonts["font7"])
        self.ballToolsHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_169.addWidget(self.ballToolsHeaderLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.ballToolsHeaderSpacer = QSpacerItem(73, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_169.addItem(self.ballToolsHeaderSpacer)


        self.verticalLayout_132.addWidget(self.ballToolsHeader)

        self.ballToolsContents = QFrame(self.segBallTools)
        self.ballToolsContents.setObjectName(u"ballToolsContents")
        self.ballToolsContents.setFrameShape(QFrame.Shape.StyledPanel)
        self.ballToolsContents.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_133 = QVBoxLayout(self.ballToolsContents)
        self.verticalLayout_133.setSpacing(0)
        self.verticalLayout_133.setObjectName(u"verticalLayout_133")
        self.verticalLayout_133.setContentsMargins(0, 0, 0, 0)
        self.hueBall = QFrame(self.ballToolsContents)
        self.hueBall.setObjectName(u"hueBall")
        self.hueBall.setFrameShape(QFrame.Shape.NoFrame)
        self.hueBall.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_134 = QVBoxLayout(self.hueBall)
        self.verticalLayout_134.setSpacing(0)
        self.verticalLayout_134.setObjectName(u"verticalLayout_134")
        self.verticalLayout_134.setContentsMargins(0, 0, 0, 0)
        self.hueBallHeader = QFrame(self.hueBall)
        self.hueBallHeader.setObjectName(u"hueBallHeader")
        self.hueBallHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.hueBallHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_170 = QHBoxLayout(self.hueBallHeader)
        self.horizontalLayout_170.setSpacing(0)
        self.horizontalLayout_170.setObjectName(u"horizontalLayout_170")
        self.horizontalLayout_170.setContentsMargins(0, 0, 0, 0)
        self.hueBallTitle = QLabel(self.hueBallHeader)
        self.hueBallTitle.setObjectName(u"hueBallTitle")
        self.hueBallTitle.setFont(Fonts["font2"])
        self.hueBallTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_170.addWidget(self.hueBallTitle)

        self.hueBallHeaderSlider = QSpacerItem(242, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_170.addItem(self.hueBallHeaderSlider)


        self.verticalLayout_134.addWidget(self.hueBallHeader)

        self.hueBallValues = QFrame(self.hueBall)
        self.hueBallValues.setObjectName(u"hueBallValues")
        self.hueBallValues.setFrameShape(QFrame.Shape.NoFrame)
        self.hueBallValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_135 = QVBoxLayout(self.hueBallValues)
        self.verticalLayout_135.setObjectName(u"verticalLayout_135")
        self.verticalLayout_135.setContentsMargins(6, 6, 6, 6)
        self.hueBallMin = QVBoxLayout()
        self.hueBallMin.setObjectName(u"hueBallMin")
        self.hueBallMinLabel = QLabel(self.hueBallValues)
        self.hueBallMinLabel.setObjectName(u"hueBallMinLabel")
        self.hueBallMinLabel.setFont(Fonts["font3"])
        self.hueBallMinLabel.setScaledContents(True)
        self.hueBallMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hueBallMin.addWidget(self.hueBallMinLabel)

        self.hueBallMinContents = QFrame(self.hueBallValues)
        self.hueBallMinContents.setObjectName(u"hueBallMinContents")
        self.hueBallMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.hueBallMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_171 = QHBoxLayout(self.hueBallMinContents)
        self.horizontalLayout_171.setSpacing(6)
        self.horizontalLayout_171.setObjectName(u"horizontalLayout_171")
        self.horizontalLayout_171.setContentsMargins(0, 0, 0, 0)
        self.hueBallMinSlider = QSlider(self.hueBallMinContents)
        self.hueBallMinSlider.setObjectName(u"hueBallMinSlider")
        self.hueBallMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.hueBallMinSlider.setMaximum(180)
        self.hueBallMinSlider.setValue(0)
        self.hueBallMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.hueBallMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hueBallMinSlider.setTickInterval(10)

        self.horizontalLayout_171.addWidget(self.hueBallMinSlider)

        self.hueBallMinValue = QLabel(self.hueBallMinContents)
        self.hueBallMinValue.setObjectName(u"hueBallMinValue")
        self.hueBallMinValue.setScaledContents(True)
        self.hueBallMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_171.addWidget(self.hueBallMinValue)


        self.hueBallMin.addWidget(self.hueBallMinContents)


        self.verticalLayout_135.addLayout(self.hueBallMin)

        self.hueBallMax = QVBoxLayout()
        self.hueBallMax.setObjectName(u"hueBallMax")
        self.hueBallMaxLabel = QLabel(self.hueBallValues)
        self.hueBallMaxLabel.setObjectName(u"hueBallMaxLabel")
        self.hueBallMaxLabel.setFont(Fonts["font3"])
        self.hueBallMaxLabel.setScaledContents(True)
        self.hueBallMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hueBallMax.addWidget(self.hueBallMaxLabel)

        self.hueBallMaxContents = QFrame(self.hueBallValues)
        self.hueBallMaxContents.setObjectName(u"hueBallMaxContents")
        self.hueBallMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.hueBallMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_172 = QHBoxLayout(self.hueBallMaxContents)
        self.horizontalLayout_172.setSpacing(6)
        self.horizontalLayout_172.setObjectName(u"horizontalLayout_172")
        self.horizontalLayout_172.setContentsMargins(0, 0, 0, 0)
        self.hueBallMaxSlider = QSlider(self.hueBallMaxContents)
        self.hueBallMaxSlider.setObjectName(u"hueBallMaxSlider")
        self.hueBallMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.hueBallMaxSlider.setMaximum(180)
        self.hueBallMaxSlider.setValue(180)
        self.hueBallMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.hueBallMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.hueBallMaxSlider.setTickInterval(10)

        self.horizontalLayout_172.addWidget(self.hueBallMaxSlider)

        self.hueBallMaxValue = QLabel(self.hueBallMaxContents)
        self.hueBallMaxValue.setObjectName(u"hueBallMaxValue")
        self.hueBallMaxValue.setScaledContents(True)
        self.hueBallMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_172.addWidget(self.hueBallMaxValue)


        self.hueBallMax.addWidget(self.hueBallMaxContents)


        self.verticalLayout_135.addLayout(self.hueBallMax)


        self.verticalLayout_134.addWidget(self.hueBallValues)


        self.verticalLayout_133.addWidget(self.hueBall)

        self.sBall = QFrame(self.ballToolsContents)
        self.sBall.setObjectName(u"sBall")
        self.sBall.setFrameShape(QFrame.Shape.NoFrame)
        self.sBall.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_136 = QVBoxLayout(self.sBall)
        self.verticalLayout_136.setSpacing(0)
        self.verticalLayout_136.setObjectName(u"verticalLayout_136")
        self.verticalLayout_136.setContentsMargins(0, 0, 0, 0)
        self.sBallHeader = QFrame(self.sBall)
        self.sBallHeader.setObjectName(u"sBallHeader")
        self.sBallHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.sBallHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_173 = QHBoxLayout(self.sBallHeader)
        self.horizontalLayout_173.setSpacing(0)
        self.horizontalLayout_173.setObjectName(u"horizontalLayout_173")
        self.horizontalLayout_173.setContentsMargins(0, 0, 0, 0)
        self.sBallTitle = QLabel(self.sBallHeader)
        self.sBallTitle.setObjectName(u"sBallTitle")
        self.sBallTitle.setFont(Fonts["font2"])
        self.sBallTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_173.addWidget(self.sBallTitle)

        self.sBallHeaderSlider = QSpacerItem(191, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_173.addItem(self.sBallHeaderSlider)


        self.verticalLayout_136.addWidget(self.sBallHeader)

        self.sBallValues = QFrame(self.sBall)
        self.sBallValues.setObjectName(u"sBallValues")
        self.sBallValues.setFrameShape(QFrame.Shape.NoFrame)
        self.sBallValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_137 = QVBoxLayout(self.sBallValues)
        self.verticalLayout_137.setObjectName(u"verticalLayout_137")
        self.verticalLayout_137.setContentsMargins(6, 6, 6, 6)
        self.sBallMin = QVBoxLayout()
        self.sBallMin.setObjectName(u"sBallMin")
        self.sBallMinLabel = QLabel(self.sBallValues)
        self.sBallMinLabel.setObjectName(u"sBallMinLabel")
        self.sBallMinLabel.setFont(Fonts["font3"])
        self.sBallMinLabel.setScaledContents(True)
        self.sBallMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sBallMin.addWidget(self.sBallMinLabel)

        self.sBallMinContents = QFrame(self.sBallValues)
        self.sBallMinContents.setObjectName(u"sBallMinContents")
        self.sBallMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.sBallMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_174 = QHBoxLayout(self.sBallMinContents)
        self.horizontalLayout_174.setSpacing(6)
        self.horizontalLayout_174.setObjectName(u"horizontalLayout_174")
        self.horizontalLayout_174.setContentsMargins(0, 0, 0, 0)
        self.sBallMinSlider = QSlider(self.sBallMinContents)
        self.sBallMinSlider.setObjectName(u"sBallMinSlider")
        self.sBallMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.sBallMinSlider.setMaximum(180)
        self.sBallMinSlider.setValue(38)
        self.sBallMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.sBallMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sBallMinSlider.setTickInterval(10)

        self.horizontalLayout_174.addWidget(self.sBallMinSlider)

        self.sBallMinValue = QLabel(self.sBallMinContents)
        self.sBallMinValue.setObjectName(u"sBallMinValue")
        self.sBallMinValue.setScaledContents(True)
        self.sBallMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_174.addWidget(self.sBallMinValue)


        self.sBallMin.addWidget(self.sBallMinContents)


        self.verticalLayout_137.addLayout(self.sBallMin)

        self.sBallMax = QVBoxLayout()
        self.sBallMax.setObjectName(u"sBallMax")
        self.sBallMaxLabel = QLabel(self.sBallValues)
        self.sBallMaxLabel.setObjectName(u"sBallMaxLabel")
        self.sBallMaxLabel.setFont(Fonts["font3"])
        self.sBallMaxLabel.setScaledContents(True)
        self.sBallMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.sBallMax.addWidget(self.sBallMaxLabel)

        self.sBallMaxContents = QFrame(self.sBallValues)
        self.sBallMaxContents.setObjectName(u"sBallMaxContents")
        self.sBallMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.sBallMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_175 = QHBoxLayout(self.sBallMaxContents)
        self.horizontalLayout_175.setSpacing(6)
        self.horizontalLayout_175.setObjectName(u"horizontalLayout_175")
        self.horizontalLayout_175.setContentsMargins(0, 0, 0, 0)
        self.sBallMaxSlider = QSlider(self.sBallMaxContents)
        self.sBallMaxSlider.setObjectName(u"sBallMaxSlider")
        self.sBallMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.sBallMaxSlider.setMaximum(255)
        self.sBallMaxSlider.setValue(255)
        self.sBallMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.sBallMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sBallMaxSlider.setTickInterval(10)

        self.horizontalLayout_175.addWidget(self.sBallMaxSlider)

        self.sBallMaxValue = QLabel(self.sBallMaxContents)
        self.sBallMaxValue.setObjectName(u"sBallMaxValue")
        self.sBallMaxValue.setScaledContents(True)
        self.sBallMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_175.addWidget(self.sBallMaxValue)


        self.sBallMax.addWidget(self.sBallMaxContents)


        self.verticalLayout_137.addLayout(self.sBallMax)


        self.verticalLayout_136.addWidget(self.sBallValues)


        self.verticalLayout_133.addWidget(self.sBall)

        self.valBall = QFrame(self.ballToolsContents)
        self.valBall.setObjectName(u"valBall")
        self.valBall.setFrameShape(QFrame.Shape.NoFrame)
        self.valBall.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_138 = QVBoxLayout(self.valBall)
        self.verticalLayout_138.setSpacing(0)
        self.verticalLayout_138.setObjectName(u"verticalLayout_138")
        self.verticalLayout_138.setContentsMargins(0, 0, 0, 0)
        self.valBallHeader = QFrame(self.valBall)
        self.valBallHeader.setObjectName(u"valBallHeader")
        self.valBallHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.valBallHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_176 = QHBoxLayout(self.valBallHeader)
        self.horizontalLayout_176.setSpacing(0)
        self.horizontalLayout_176.setObjectName(u"horizontalLayout_176")
        self.horizontalLayout_176.setContentsMargins(0, 0, 0, 0)
        self.vBallTitle = QLabel(self.valBallHeader)
        self.vBallTitle.setObjectName(u"vBallTitle")
        self.vBallTitle.setFont(Fonts["font2"])
        self.vBallTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_176.addWidget(self.vBallTitle)

        self.vBallHeaderSlider = QSpacerItem(191, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_176.addItem(self.vBallHeaderSlider)


        self.verticalLayout_138.addWidget(self.valBallHeader)

        self.vBallValues = QFrame(self.valBall)
        self.vBallValues.setObjectName(u"vBallValues")
        self.vBallValues.setFrameShape(QFrame.Shape.NoFrame)
        self.vBallValues.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_139 = QVBoxLayout(self.vBallValues)
        self.verticalLayout_139.setObjectName(u"verticalLayout_139")
        self.verticalLayout_139.setContentsMargins(6, 6, 6, 6)
        self.vBallMin = QVBoxLayout()
        self.vBallMin.setObjectName(u"vBallMin")
        self.valBallMinLabel = QLabel(self.vBallValues)
        self.valBallMinLabel.setObjectName(u"valBallMinLabel")
        self.valBallMinLabel.setFont(Fonts["font3"])
        self.valBallMinLabel.setScaledContents(True)
        self.valBallMinLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vBallMin.addWidget(self.valBallMinLabel)

        self.vBallMinContents = QFrame(self.vBallValues)
        self.vBallMinContents.setObjectName(u"vBallMinContents")
        self.vBallMinContents.setFrameShape(QFrame.Shape.NoFrame)
        self.vBallMinContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_177 = QHBoxLayout(self.vBallMinContents)
        self.horizontalLayout_177.setSpacing(6)
        self.horizontalLayout_177.setObjectName(u"horizontalLayout_177")
        self.horizontalLayout_177.setContentsMargins(0, 0, 0, 0)
        self.vBallMinSlider = QSlider(self.vBallMinContents)
        self.vBallMinSlider.setObjectName(u"vBallMinSlider")
        self.vBallMinSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.vBallMinSlider.setMaximum(255)
        self.vBallMinSlider.setValue(198)
        self.vBallMinSlider.setOrientation(Qt.Orientation.Horizontal)
        self.vBallMinSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.vBallMinSlider.setTickInterval(10)

        self.horizontalLayout_177.addWidget(self.vBallMinSlider)

        self.vBallMinValue = QLabel(self.vBallMinContents)
        self.vBallMinValue.setObjectName(u"vBallMinValue")
        self.vBallMinValue.setScaledContents(True)
        self.vBallMinValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_177.addWidget(self.vBallMinValue)


        self.vBallMin.addWidget(self.vBallMinContents)


        self.verticalLayout_139.addLayout(self.vBallMin)

        self.vBallMax = QVBoxLayout()
        self.vBallMax.setObjectName(u"vBallMax")
        self.vBallMaxLabel = QLabel(self.vBallValues)
        self.vBallMaxLabel.setObjectName(u"vBallMaxLabel")
        self.vBallMaxLabel.setFont(Fonts["font3"])
        self.vBallMaxLabel.setScaledContents(True)
        self.vBallMaxLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vBallMax.addWidget(self.vBallMaxLabel)

        self.vBallMaxContents = QFrame(self.vBallValues)
        self.vBallMaxContents.setObjectName(u"vBallMaxContents")
        self.vBallMaxContents.setFrameShape(QFrame.Shape.NoFrame)
        self.vBallMaxContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_178 = QHBoxLayout(self.vBallMaxContents)
        self.horizontalLayout_178.setSpacing(6)
        self.horizontalLayout_178.setObjectName(u"horizontalLayout_178")
        self.horizontalLayout_178.setContentsMargins(0, 0, 0, 0)
        self.vBallMaxSlider = QSlider(self.vBallMaxContents)
        self.vBallMaxSlider.setObjectName(u"vBallMaxSlider")
        self.vBallMaxSlider.setCursor(QCursor(Qt.PointingHandCursor))
        self.vBallMaxSlider.setMaximum(255)
        self.vBallMaxSlider.setValue(255)
        self.vBallMaxSlider.setOrientation(Qt.Orientation.Horizontal)
        self.vBallMaxSlider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.vBallMaxSlider.setTickInterval(10)

        self.horizontalLayout_178.addWidget(self.vBallMaxSlider)

        self.vBallMaxValue = QLabel(self.vBallMaxContents)
        self.vBallMaxValue.setObjectName(u"vBallMaxValue")
        self.vBallMaxValue.setScaledContents(True)
        self.vBallMaxValue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_178.addWidget(self.vBallMaxValue)


        self.vBallMax.addWidget(self.vBallMaxContents)


        self.verticalLayout_139.addLayout(self.vBallMax)


        self.verticalLayout_138.addWidget(self.vBallValues)


        self.verticalLayout_133.addWidget(self.valBall)


        self.verticalLayout_132.addWidget(self.ballToolsContents)

        self.ballSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_132.addItem(self.ballSpacer)


        self.horizontalLayout_168.addWidget(self.segBallTools)

        self.visionSteps.addTab(self.segBallTab, icon14, "")
        self.genParamsTab = QWidget()
        self.genParamsTab.setObjectName(u"genParamsTab")
        self.genParamsContents = QFrame(self.genParamsTab)
        self.genParamsContents.setObjectName(u"genParamsContents")
        self.genParamsContents.setGeometry(QRect(0, 0, 831, 451))
        
        SizePolicies["Expanding_Expanding"].setHeightForWidth(self.genParamsContents.sizePolicy().hasHeightForWidth())
        self.genParamsContents.setSizePolicy(SizePolicies["Expanding_Expanding"])
        
        self.genParamsContents.setMinimumSize(QSize(737, 402))
        self.genParamsContents.setFrameShape(QFrame.Shape.NoFrame)
        self.genParamsContents.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_179 = QHBoxLayout(self.genParamsContents)
        self.horizontalLayout_179.setObjectName(u"horizontalLayout_179")
        self.horizontalLayout_179.setContentsMargins(6, 6, 6, 6)
        self.genParamsDisplay = QFrame(self.genParamsContents)
        self.genParamsDisplay.setObjectName(u"genParamsDisplay")
        
        SizePolicies["MinExpanding_Fixed"].setHeightForWidth(self.genParamsDisplay.sizePolicy().hasHeightForWidth())
        self.genParamsDisplay.setSizePolicy(SizePolicies["MinExpanding_Fixed"])
        
        self.genParamsDisplay.setCursor(QCursor(Qt.PointingHandCursor))
        self.genParamsDisplay.setFrameShape(QFrame.Shape.NoFrame)
        self.genParamsDisplay.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_140 = QVBoxLayout(self.genParamsDisplay)
        self.verticalLayout_140.setSpacing(0)
        self.verticalLayout_140.setObjectName(u"verticalLayout_140")
        self.verticalLayout_140.setContentsMargins(0, 0, 0, 0)
        self.genParamsFrame = QLabel(self.genParamsDisplay)
        self.genParamsFrame.setObjectName(u"genParamsFrame")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.genParamsFrame.sizePolicy().hasHeightForWidth())
        self.genParamsFrame.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.genParamsFrame.setMinimumSize(QSize(479, 0))
        self.genParamsFrame.setPixmap(QPixmap(u"assets/segImage.png"))
        self.genParamsFrame.setScaledContents(True)
        self.genParamsFrame.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_140.addWidget(self.genParamsFrame)


        self.horizontalLayout_179.addWidget(self.genParamsDisplay)

        self.genParamsTools = QFrame(self.genParamsContents)
        self.genParamsTools.setObjectName(u"genParamsTools")
        
        SizePolicies["MinExpanding_Expanding"].setHeightForWidth(self.genParamsTools.sizePolicy().hasHeightForWidth())
        self.genParamsTools.setSizePolicy(SizePolicies["MinExpanding_Expanding"])
        
        self.genParamsTools.setMinimumSize(QSize(0, 392))
        self.genParamsTools.setBaseSize(QSize(0, 0))
        self.genParamsTools.setFrameShape(QFrame.Shape.StyledPanel)
        self.genParamsTools.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_141 = QVBoxLayout(self.genParamsTools)
        self.verticalLayout_141.setObjectName(u"verticalLayout_141")
        self.verticalLayout_141.setContentsMargins(6, 6, 6, 6)
        self.segBallToolsHeader = QFrame(self.genParamsTools)
        self.segBallToolsHeader.setObjectName(u"segBallToolsHeader")
        self.segBallToolsHeader.setFrameShape(QFrame.Shape.NoFrame)
        self.segBallToolsHeader.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_180 = QHBoxLayout(self.segBallToolsHeader)
        self.horizontalLayout_180.setSpacing(0)
        self.horizontalLayout_180.setObjectName(u"horizontalLayout_180")
        self.horizontalLayout_180.setContentsMargins(0, 0, 0, 0)
        self.segBallToolsHeaderLabel = QLabel(self.segBallToolsHeader)
        self.segBallToolsHeaderLabel.setObjectName(u"segBallToolsHeaderLabel")
        self.segBallToolsHeaderLabel.setFont(Fonts["font7"])
        self.segBallToolsHeaderLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_180.addWidget(self.segBallToolsHeaderLabel, 0, Qt.AlignmentFlag.AlignTop)

        self.segBallToolsHeaderSpacer = QSpacerItem(73, 15, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_180.addItem(self.segBallToolsHeaderSpacer)


        self.verticalLayout_141.addWidget(self.segBallToolsHeader)

        self.segBallToolsContents = QFrame(self.genParamsTools)
        self.segBallToolsContents.setObjectName(u"segBallToolsContents")
        self.segBallToolsContents.setFrameShape(QFrame.Shape.StyledPanel)
        self.segBallToolsContents.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_142 = QVBoxLayout(self.segBallToolsContents)
        self.verticalLayout_142.setSpacing(0)
        self.verticalLayout_142.setObjectName(u"verticalLayout_142")
        self.verticalLayout_142.setContentsMargins(0, 0, 0, 0)
        self.minAreaInnerContour = QVBoxLayout()
        self.minAreaInnerContour.setObjectName(u"minAreaInnerContour")
        self.minAreaInnerContourLabel = QLabel(self.segBallToolsContents)
        self.minAreaInnerContourLabel.setObjectName(u"minAreaInnerContourLabel")
        self.minAreaInnerContourLabel.setFont(Fonts["font3"])
        self.minAreaInnerContourLabel.setScaledContents(True)
        self.minAreaInnerContourLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.minAreaInnerContour.addWidget(self.minAreaInnerContourLabel)

        self.minAreaInnerContourSpinner = QSpinBox(self.segBallToolsContents)
        self.minAreaInnerContourSpinner.setObjectName(u"minAreaInnerContourSpinner")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.minAreaInnerContourSpinner.sizePolicy().hasHeightForWidth())
        self.minAreaInnerContourSpinner.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.minAreaInnerContourSpinner.setCursor(QCursor(Qt.PointingHandCursor))
        self.minAreaInnerContourSpinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minAreaInnerContourSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.minAreaInnerContourSpinner.setMaximum(10)
        self.minAreaInnerContourSpinner.setValue(10)

        self.minAreaInnerContour.addWidget(self.minAreaInnerContourSpinner)


        self.verticalLayout_142.addLayout(self.minAreaInnerContour)


        self.verticalLayout_141.addWidget(self.segBallToolsContents)

        self.minAreaContour = QVBoxLayout()
        self.minAreaContour.setObjectName(u"minAreaContour")
        self.minAreaContourLabel = QLabel(self.genParamsTools)
        self.minAreaContourLabel.setObjectName(u"minAreaContourLabel")
        self.minAreaContourLabel.setFont(Fonts["font3"])
        self.minAreaContourLabel.setScaledContents(True)
        self.minAreaContourLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.minAreaContour.addWidget(self.minAreaContourLabel)

        self.minAreaContourSpinner = QSpinBox(self.genParamsTools)
        
        self.minAreaContourSpinner.setObjectName(u"minAreaContourSpinner")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.minAreaContourSpinner.sizePolicy().hasHeightForWidth())
        
        self.minAreaContourSpinner.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.minAreaContourSpinner.setCursor(QCursor(Qt.PointingHandCursor))
        self.minAreaContourSpinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.minAreaContourSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.minAreaContourSpinner.setMaximum(10)
        self.minAreaContourSpinner.setValue(10)

        self.minAreaContour.addWidget(self.minAreaContourSpinner)


        self.verticalLayout_141.addLayout(self.minAreaContour)

        self.areaRectRatio = QVBoxLayout()
        self.areaRectRatio.setObjectName(u"areaRectRatio")
        self.areaRectRatioLabel = QLabel(self.genParamsTools)
        self.areaRectRatioLabel.setObjectName(u"areaRectRatioLabel")
        self.areaRectRatioLabel.setFont(Fonts["font3"])
        self.areaRectRatioLabel.setScaledContents(True)
        self.areaRectRatioLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.areaRectRatio.addWidget(self.areaRectRatioLabel)

        self.areaRectRatioSpinner = QSpinBox(self.genParamsTools)
        self.areaRectRatioSpinner.setObjectName(u"areaRectRatioSpinner")
        
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.areaRectRatioSpinner.sizePolicy().hasHeightForWidth())
        self.areaRectRatioSpinner.setSizePolicy(SizePolicies["Fixed_Fixed"])
        
        self.areaRectRatioSpinner.setCursor(QCursor(Qt.PointingHandCursor))
        self.areaRectRatioSpinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.areaRectRatioSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.areaRectRatioSpinner.setMaximum(10)
        self.areaRectRatioSpinner.setValue(10)

        self.areaRectRatio.addWidget(self.areaRectRatioSpinner)


        self.verticalLayout_141.addLayout(self.areaRectRatio)

        self.stabilityParam = QVBoxLayout()
        self.stabilityParam.setObjectName(u"stabilityParam")
        self.stabilityParamLabel = QLabel(self.genParamsTools)
        self.stabilityParamLabel.setObjectName(u"stabilityParamLabel")
        self.stabilityParamLabel.setFont(Fonts["font3"])
        self.stabilityParamLabel.setScaledContents(True)
        self.stabilityParamLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.stabilityParam.addWidget(self.stabilityParamLabel)

        self.stabilityParamSpinner = QSpinBox(self.genParamsTools)
        self.stabilityParamSpinner.setObjectName(u"stabilityParamSpinner")
        SizePolicies["Fixed_Fixed"].setHeightForWidth(self.stabilityParamSpinner.sizePolicy().hasHeightForWidth())
        self.stabilityParamSpinner.setSizePolicy(SizePolicies["Fixed_Fixed"])
        self.stabilityParamSpinner.setCursor(QCursor(Qt.PointingHandCursor))
        self.stabilityParamSpinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stabilityParamSpinner.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        self.stabilityParamSpinner.setMaximum(10)
        self.stabilityParamSpinner.setValue(10)

        self.stabilityParam.addWidget(self.stabilityParamSpinner)

        self.verticalLayout_141.addLayout(self.stabilityParam)

        self.segBallSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_141.addItem(self.segBallSpacer)


        self.horizontalLayout_179.addWidget(self.genParamsTools)

        self.visionSteps.addTab(self.genParamsTab, icon14, "")
        icon15 = QIcon()
        icon15.addFile(u"assets/icons/mdi_camera-iris.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.appContents.addTab(self.visionSettingsTab, icon15, "")
        self.visionAiTab = QWidget()
        self.visionAiTab.setObjectName(u"visionAiTab")
        icon16 = QIcon()
        icon16.addFile(u"assets/icons/mdi_bullseye-arrow.svg", QSize(), QIcon.Normal, QIcon.Off)
        ############################################
        # AI Vision Tab
        ############################################
        self.appContents.addTab(self.visionAiTab, icon16, "")

        self.verticalLayout_2.addWidget(self.appContents)

        self.verticalLayout.addWidget(self.body)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        
        ##########################################
        # Connect Slots and Signals
        ##########################################
        # Header
        self.header.closeButton.clicked.connect(MainWindow.close)
        self.header.minButton.clicked.connect(MainWindow.showMinimized)
        
        # System Info Signals
        
        self.showCropFieldSwitch.valueChanged.connect(MainWindow.showCropField)
        self.myTeamSideSwitch.valueChanged.connect(MainWindow.changeFieldSideArrow)
        self.switchTeamColorButton.clicked["bool"].connect(MainWindow.changeTeamColor)
        self.viewUvfButton.clicked["bool"].connect(MainWindow.enableViewUvf)
        self.staticEntitiesRadio.clicked["bool"].connect(self.staticRobotsBox.setVisible)
        self.dynEntitiesRadio.clicked["bool"].connect(self.staticRobotsBox.setHidden)
        self.highLevelVisionButton.clicked["bool"].connect(self.visionSteps.setHidden)
        self.execButton.clicked.connect(MainWindow.executeUnbrain)
        
        # Position Source
        self.posSourceSwitch.valueChanged.connect(self.posSourceLabel.setNum)
        self.posSourceSwitch.valueChanged.connect(MainWindow.updatePosSourceLabel)
        
        # Elements Saturation Sliders
        self.satMinSlider.valueChanged.connect(self.satMinValue.setNum)
        self.satMinSlider.valueChanged.connect(self.segFrame.updateMinSaturation)
        self.satMaxSlider.valueChanged.connect(self.satMaxValue.setNum)
        self.satMinSlider.valueChanged.connect(self.segFrame.updateMaxSaturation)
        
        # Ball Saturation Sliders
        self.sBallMinSlider.valueChanged.connect(self.sBallMinValue.setNum)
        self.sBallMinSlider.valueChanged.connect(self.segBallFrame.updateMinSaturation)
        self.sBallMaxSlider.valueChanged.connect(self.sBallMaxValue.setNum)
        self.sBallMaxSlider.valueChanged.connect(self.segBallFrame.updateMaxSaturation)
        
        # Team Saturation Sliders
        self.sTeamMinSlider.valueChanged.connect(self.segTeamFrame.updateMinSaturation)
        self.sTeamMaxSlider.valueChanged.connect(self.segTeamFrame.updateMaxSaturation)
        self.sTeamMinSlider.valueChanged.connect(self.sTeamMinValue.setNum)
        self.sTeamMaxSlider.valueChanged.connect(self.sTeamMaxValue.setNum)
        
        # Elements Value Sliders 
        self.valueMaxSlider.valueChanged.connect(self.valueMaxValue.setNum)
        self.valueMaxSlider.valueChanged.connect(self.segFrame.updateMaxValue)
        self.valueMinSlider.valueChanged.connect(self.valueMinValue.setNum)
        self.valueMinSlider.valueChanged.connect(self.segFrame.updateMinValue)
        
        # Team Value Sliders
        self.vTeamMinSlider.valueChanged.connect(self.segTeamFrame.updateMinValue)
        self.vTeamMinSlider.valueChanged.connect(self.vTeamMinValue.setNum)
        self.vTeamMaxSlider.valueChanged.connect(self.vTeamMaxValue.setNum)
        self.vTeamMaxSlider.valueChanged.connect(self.segTeamFrame.updateMaxValue)
        
        # Ball Value Sliders
        self.vBallMinSlider.valueChanged.connect(self.vBallMinValue.setNum)
        self.vBallMinSlider.valueChanged.connect(self.segBallFrame.updateMinValue)
        self.vBallMaxSlider.valueChanged.connect(self.vBallMaxValue.setNum)
        self.vBallMaxSlider.valueChanged.connect(self.segBallFrame.updateMaxValue)
        
        # Ball Hue Sliders
        self.hueBallMinSlider.valueChanged.connect(self.hueBallMinValue.setNum)
        self.hueBallMinSlider.valueChanged.connect(self.segBallFrame.updateMinHue)
        self.hueBallMaxSlider.valueChanged.connect(self.hueBallMaxValue.setNum)
        
        
        # Team Hue Sliders
        self.hueTeamMinSlider.valueChanged.connect(self.hueTeamMinValue.setNum)
        self.hueTeamMaxSlider.valueChanged.connect(self.hueTeamMaxValue.setNum)
        self.hueTeamMinSlider.valueChanged.connect(self.segTeamFrame.updateMinHue)
        self.hueTeamMaxSlider.valueChanged.connect(self.segTeamFrame.updateMaxHue)
        
        # Elements Hue Sliders
        self.hueMaxSlider.valueChanged.connect(self.hueMaxValue.setNum)
        self.hueMaxSlider.valueChanged.connect(self.segBallFrame.updateMaxHue)
        self.hueMinSlider.valueChanged.connect(self.hueMinValue.setNum)
        self.hueMinSlider.valueChanged.connect(self.segFrame.updateMinHue)

        ####################################
        # Tab Initialization
        ####################################
        self.appContents.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        self.visionSteps.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"VSSS - UnBall", None))
        self.header.appName.setText(QCoreApplication.translate("MainWindow", u"Very Small Size - UnBall", None))
        self.gameOptionsLabel.setText(QCoreApplication.translate("MainWindow", u"Op\u00e7\u00f5es", None))
        self.gameOptionsDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"F\u00edsico", None))
        self.gameOptionsDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Simulado", None))

        self.gameOptionsDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"F\u00edsico", None))
        self.visionOptionsLabel.setText(QCoreApplication.translate("MainWindow", u"Vis\u00e3o", None))
        self.visionOptionsDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"MainVision", None))
        self.visionOptionsDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"FiraSim", None))

        self.visionOptionsDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"MainVision", None))
        self.myTeamSideText.setText(QCoreApplication.translate("MainWindow", u"Cor do time aliado:", None))
        self.switchTeamColorButton.setText("")
        self.myTeamColorLabel.setText(QCoreApplication.translate("MainWindow", u"Azul", None))
        self.myTeamSideTitle.setText(QCoreApplication.translate("MainWindow", u"Lado aliado:", None))
        self.myTeamSideLabel.setText(QCoreApplication.translate("MainWindow", u"Direito", None))
        self.execButton.setText(QCoreApplication.translate("MainWindow", u"Executar", None))
        self.imageDisplay.setText("")
        self.prevButton.setText("")
        self.stopButton.setText("")
        self.playButton.setText("")
        self.nextButton.setText("")
        self.speedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u"x", None))
        self.leftTeamSideLabel.setText(QCoreApplication.translate("MainWindow", u"Lado inimigo", None))
        self.fieldSideDirection.setText("")
        self.rightTeamSideLabel.setText(QCoreApplication.translate("MainWindow", u"Lado aliado", None))
        self.debugTabTitle.setText(QCoreApplication.translate("MainWindow", u"Configura\u00e7\u00e3o dos rob\u00f4s", None))
        self.robotsFound.setText(QCoreApplication.translate("MainWindow", u"3 rob\u00f4s identificados", None))
        
        for layout in self.robotLayouts:
                self.robotLayouts[layout].retranslateUi()
        
       
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.debugTab), QCoreApplication.translate("MainWindow", u"Debug", None))
        self.navRobotId.setItemText(0, QCoreApplication.translate("MainWindow", u"Rob\u00f4 ID", None))
        self.navRobotId.setItemText(1, QCoreApplication.translate("MainWindow", u"0", None))
        self.navRobotId.setItemText(2, QCoreApplication.translate("MainWindow", u"1", None))
        self.navRobotId.setItemText(3, QCoreApplication.translate("MainWindow", u"2", None))

        self.navRobotId.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Rob\u00f4 ID", None))
        self.uvfLabel.setText(QCoreApplication.translate("MainWindow", u"UVF", None))
        self.viewUvfFieldLabel.setText(QCoreApplication.translate("MainWindow", u"Visualizar campo UVF", None))
        self.pointsLabel.setText(QCoreApplication.translate("MainWindow", u"Quantidade de pontos", None))
        self.viewUvfButton.setText("")
#if QT_CONFIG(tooltip)
        self.finalPoint.setToolTip(QCoreApplication.translate("MainWindow", u"Habilita a sele\u00e7\u00e3o manual de ponto final das trajet\u00f3rias", None))
#endif // QT_CONFIG(tooltip)
        self.finalPointLabel.setText(QCoreApplication.translate("MainWindow", u"Ponto final selecion\u00e1vel", None))
        self.selectFieldLabel.setText(QCoreApplication.translate("MainWindow", u"Selecionar campo", None))
        self.selectFieldDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Nenhum", None))

        self.selectFieldDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Nenhum", None))
        self.radiusHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Raio:", None))
        self.kSmoothHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Constante de suaviza\u00e7\u00e3o:", None))
        self.uniKSmoothHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Constante de suaviza\u00e7\u00e3o unidirecional:", None))
#if QT_CONFIG(tooltip)
        self.allUvf.setToolTip(QCoreApplication.translate("MainWindow", u"Habilita visualiza\u00e7\u00e3o dos campos de todos os rob\u00f4s", None))
#endif // QT_CONFIG(tooltip)
        self.allUvfLabel.setText(QCoreApplication.translate("MainWindow", u"Visualizar todos os campos UVF", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.navTab), QCoreApplication.translate("MainWindow", u"Navega\u00e7\u00e3o", None))
#if QT_CONFIG(tooltip)
        self.decTabTitle.setToolTip(QCoreApplication.translate("MainWindow", u"Selecione o tipo de forma\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.decTabTitle.setText(QCoreApplication.translate("MainWindow", u"Forma\u00e7\u00e3o das entidades", None))
        self.staticEntitiesRadio.setText(QCoreApplication.translate("MainWindow", u"Entidades est\u00e1ticas", None))
        self.dynEntitiesRadio.setText(QCoreApplication.translate("MainWindow", u"Entidades din\u00e2micas", None))
        self.staticRobotLabel.setText(QCoreApplication.translate("MainWindow", u"Rob\u00f4 0:", None))
        self.staticRobotDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.staticRobotDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.staticRobotDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.staticRobotDropdown.setItemText(3, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.staticRobotDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.staticRobotLabel_2.setText(QCoreApplication.translate("MainWindow", u"Rob\u00f4 1:", None))
        self.staticRobotDropdown_2.setItemText(0, QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.staticRobotDropdown_2.setItemText(1, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.staticRobotDropdown_2.setItemText(2, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.staticRobotDropdown_2.setItemText(3, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.staticRobotDropdown_2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.staticRobotLabel_3.setText(QCoreApplication.translate("MainWindow", u"Rob\u00f4 2:", None))
        self.staticRobotDropdown_3.setItemText(0, QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        self.staticRobotDropdown_3.setItemText(1, QCoreApplication.translate("MainWindow", u"Atacante", None))
        self.staticRobotDropdown_3.setItemText(2, QCoreApplication.translate("MainWindow", u"Zagueiro", None))
        self.staticRobotDropdown_3.setItemText(3, QCoreApplication.translate("MainWindow", u"Goleiro", None))

        self.staticRobotDropdown_3.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Papel do rob\u00f4", None))
        
        self.posLabel.setText(QCoreApplication.translate("MainWindow", u"Posicionamento", None))
        self.posSourceLabel.setText(QCoreApplication.translate("MainWindow", u"Posicionamento com juiz virtual", None))
        
        self.selectPosLabel.setText(QCoreApplication.translate("MainWindow", u"Selecionar posicionamento", None))
        self.selectPosDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"Free Ball", None))
        self.selectPosDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Kick Off", None))
        self.selectPosDropdown.setItemText(2, QCoreApplication.translate("MainWindow", u"P\u00eanalti", None))

        self.selectPosDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Free Ball", None))
        self.posTimeLabel.setText(QCoreApplication.translate("MainWindow", u"Tempo tentando se posicionar:", None))
        self.posTimeValue.setText(QCoreApplication.translate("MainWindow", u"8s", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.decisionTab), QCoreApplication.translate("MainWindow", u"Decis\u00e3o", None))
        self.ballInfoTitle.setText(QCoreApplication.translate("MainWindow", u"Bola", None))
        self.ballInfoStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#3e7239;\">Status</span></p></body></html>", None))
        self.ballPosLabel.setText(QCoreApplication.translate("MainWindow", u"Posi\u00e7\u00e3o", None))
        self.ballPosValue.setText(QCoreApplication.translate("MainWindow", u"x: 0.0 m y: 0.0 m", None))
        self.ballSpeedLabel.setText(QCoreApplication.translate("MainWindow", u"Velocidade", None))
        self.ballSpeedValue.setText(QCoreApplication.translate("MainWindow", u"3 m/s", None))
        self.ballAccLabel.setText(QCoreApplication.translate("MainWindow", u"Acelera\u00e7\u00e3o", None))
        self.ballAccValue.setText(QCoreApplication.translate("MainWindow", u"3 m/s\u00b2", None))
        self.commTitle.setText(QCoreApplication.translate("MainWindow", u"Comunica\u00e7\u00e3o", None))
        self.visionCommLabel.setText(QCoreApplication.translate("MainWindow", u"Vis\u00e3o", None))
        self.visionCommStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#3e7239;\">Status</span></p></body></html>", None))
        self.visionCommPortValue.setText(QCoreApplication.translate("MainWindow", u"Porta", None))
        self.refCommLabel.setText(QCoreApplication.translate("MainWindow", u"Referee", None))
        self.refCommStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#3e7239;\">Status</span></p></body></html>", None))
        self.refCommPortValue.setText(QCoreApplication.translate("MainWindow", u"Porta", None))
        self.transCommLabel.setText(QCoreApplication.translate("MainWindow", u"Transmissor", None))
        self.transCommStatus.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" color:#3e7239;\">Status</span></p></body></html>", None))
        self.transCommPortValue.setText(QCoreApplication.translate("MainWindow", u"Porta", None))
        self.commCancelButton.setText(QCoreApplication.translate("MainWindow", u"Cancelar", None))
        self.commAlterButton.setText(QCoreApplication.translate("MainWindow", u"Aplicar Altera\u00e7\u00f5es", None))
        self.logHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Erros e Warnings", None))
        self.logMessages.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:8pt;\">[Fonte do erro]: descri\u00e7\u00e3o</span></p><p><span style=\" font-size:8pt;\">[Fonte do erro]: descri\u00e7\u00e3o</span></p><p><span style=\" font-size:8pt;\">[Fonte do erro]: descri\u00e7\u00e3o</span></p><p><span style=\" font-size:8pt;\">...</span></p></body></html>", None))
        self.appContents.setTabText(self.appContents.indexOf(self.sysInfoTab), "")
#if QT_CONFIG(tooltip)
        self.appContents.setTabToolTip(self.appContents.indexOf(self.sysInfoTab), QCoreApplication.translate("MainWindow", u"Informa\u00e7\u00f5es do Sistema", None))
#endif // QT_CONFIG(tooltip)
        self.visGameOptionsLabel.setText(QCoreApplication.translate("MainWindow", u"Op\u00e7\u00f5es", None))
        self.visGameOptionsDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"F\u00edsico", None))
        self.visGameOptionsDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"Simulado", None))

        self.visGameOptionsDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"F\u00edsico", None))
        self.deviceOptionsLabel.setText(QCoreApplication.translate("MainWindow", u"C\u00e2mera", None))
        self.deviceOptionsDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"LogiTech", None))

        self.deviceOptionsDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"MainVision", None))
        self.selectVisionOptionsLabel.setText(QCoreApplication.translate("MainWindow", u"Vis\u00e3o", None))
        self.selectVisionOptionsDropdown.setItemText(0, QCoreApplication.translate("MainWindow", u"MainVision", None))
        self.selectVisionOptionsDropdown.setItemText(1, QCoreApplication.translate("MainWindow", u"FiraSim", None))

        self.selectVisionOptionsDropdown.setPlaceholderText(QCoreApplication.translate("MainWindow", u"MainVision", None))
        self.highLevelVisionButton.setText(QCoreApplication.translate("MainWindow", u"Vis\u00e3o de alto n\u00edvel", None))
#if QT_CONFIG(tooltip)
        self.highLevelVisionDisplay.setToolTip(QCoreApplication.translate("MainWindow", u"Selecione 4 pontos", None))
#endif // QT_CONFIG(tooltip)
        self.highLevelVisionFrame.setText("")
        self.highLevelVisionToolsLabel.setText(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
        self.xRobotsLabel.setText(QCoreApplication.translate("MainWindow", u"X Rob\u00f4s ", None))
        self.vRobotIdLabel.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.vRobotStatus.setText(QCoreApplication.translate("MainWindow", u"N\u00e3o identificado", None))
        self.vRobotPos.setText(QCoreApplication.translate("MainWindow", u"Posi\u00e7\u00e3o: (0.00, 0.00) m", None))
        self.vRobotAngle.setText(QCoreApplication.translate("MainWindow", u"\u00c2ngulo: 0.0", None))
        self.vRobotIdLabel_2.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.vRobotStatus_2.setText(QCoreApplication.translate("MainWindow", u"N\u00e3o identificado", None))
        self.vRobotPos_2.setText(QCoreApplication.translate("MainWindow", u"Posi\u00e7\u00e3o: (0.00, 0.00) m", None))
        self.vRobotAngle_2.setText(QCoreApplication.translate("MainWindow", u"\u00c2ngulo: 0.0", None))
        self.vRobotIdLabel_3.setText(QCoreApplication.translate("MainWindow", u"2", None))
        self.vRobotStatus_3.setText(QCoreApplication.translate("MainWindow", u"N\u00e3o identificado", None))
        self.vRobotPos_3.setText(QCoreApplication.translate("MainWindow", u"Posi\u00e7\u00e3o: (0.00, 0.00) m", None))
        self.vRobotAngle_3.setText(QCoreApplication.translate("MainWindow", u"\u00c2ngulo: 0.0", None))
        self.vBallInfoLabel.setText(QCoreApplication.translate("MainWindow", u"Bola", None))
        self.vBallLabel.setText("")
        self.vBallStatus.setText(QCoreApplication.translate("MainWindow", u"N\u00e3o identificado", None))
        self.vBallPos.setText(QCoreApplication.translate("MainWindow", u"Posi\u00e7\u00e3o: (0.00, 0.00) m", None))
        self.nextStepVisionButton.setText(QCoreApplication.translate("MainWindow", u"Avan\u00e7ar para executar", None))

        self.cropFieldToolsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
        self.showCropFieldLabel.setText(QCoreApplication.translate("MainWindow", u"Mostrar campo cortado", None))
        self.cropFieldActionHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"A\u00e7\u00f5es:", None))
        self.cropFieldRedoButton.setText("")
        self.cropFieldEraseButton.setText("")
        self.visionSteps.setTabText(self.visionSteps.indexOf(self.cropFieldTab), QCoreApplication.translate("MainWindow", u"Cortar campo", None))
#if QT_CONFIG(tooltip)
        self.visionInnerCropDisplay.setToolTip(QCoreApplication.translate("MainWindow", u"Verifique  o desenho do campo interno. Se necess\u00e1rio, refa\u00e7a a marca\u00e7\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.visionInnerCropFrame.setText("")
        self.cropInnerFieldToolsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
        self.showInnerCropFieldLabel.setText(QCoreApplication.translate("MainWindow", u"Mostrar campo cortado", None))
        self.cropInnerFieldActionHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"A\u00e7\u00f5es:", None))
        self.cropInnerFieldRedoButton.setText("")
        self.cropInnerFieldEraseButton.setText("")
        self.visionSteps.setTabText(self.visionSteps.indexOf(self.cropInnerFieldTab), QCoreApplication.translate("MainWindow", u"Cortar campo interno", None))
#if QT_CONFIG(tooltip)
        self.segFrame.setToolTip(QCoreApplication.translate("MainWindow", u"Selecione o filtro por intervalo (espaço HSV)", None))
#endif // QT_CONFIG(tooltip)
        self.segFrame.segmentImage()
        self.segToolsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
        self.hueTitle.setText(QCoreApplication.translate("MainWindow", u"Hue", None))
        self.hueMinLabel.setText(QCoreApplication.translate("MainWindow", u"Hmin", None))
        self.hueMinValue.setText(QCoreApplication.translate("MainWindow", str(self.hueMinSlider.value()), None))
        self.hueMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Hmax", None))
        self.hueMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.hueMaxSlider.value()), None))
        self.satTitle.setText(QCoreApplication.translate("MainWindow", u"Saturation", None))
        self.satMinLabel.setText(QCoreApplication.translate("MainWindow", u"Smin", None))
        self.satMinValue.setText(QCoreApplication.translate("MainWindow", str(self.satMinSlider.value()), None))
        self.satMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Smax", None))
        self.satMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.satMaxSlider.value()), None))
        self.valueTitle.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.valueMinLabel.setText(QCoreApplication.translate("MainWindow", u"Vmin", None))
        self.valueMinValue.setText(QCoreApplication.translate("MainWindow", str(self.valueMinSlider.value()), None))
        self.valueMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Vmax", None))
        self.valueMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.valueMaxSlider.value()), None))
        self.visionSteps.setTabText(self.visionSteps.indexOf(self.segTab), QCoreApplication.translate("MainWindow", u"Segmentar Elementos", None))
#if QT_CONFIG(tooltip)
        self.segTeamFrame.setToolTip(QCoreApplication.translate("MainWindow", u"Selecione o filtro por intervalo (espaço HSV)", None))
#endif // QT_CONFIG(tooltip)
        self.segTeamFrame.segmentImage()
        self.segTeamToolsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
        self.hueTeamTitle.setText(QCoreApplication.translate("MainWindow", u"Hue", None))
        self.hueTeamMinLabel.setText(QCoreApplication.translate("MainWindow", u"Hmin", None))
        self.hueTeamMinValue.setText(QCoreApplication.translate("MainWindow", str(self.hueTeamMinSlider.value()), None))
        self.hueTeamMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Hmax", None))
        self.hueTeamMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.hueTeamMaxSlider.value()), None))
        self.sTeamTitle.setText(QCoreApplication.translate("MainWindow", u"Saturation", None))
        self.sTeamMinLabel.setText(QCoreApplication.translate("MainWindow", u"Smin", None))
        self.sTeamMinValue.setText(QCoreApplication.translate("MainWindow", str(self.sTeamMinSlider.value()), None))
        self.sTeamMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Smax", None))
        self.sTeamMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.sTeamMaxSlider.value()), None))
        self.vTeamTitle.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.vTeamMinLabel.setText(QCoreApplication.translate("MainWindow", u"Vmin", None))
        self.vTeamMinValue.setText(QCoreApplication.translate("MainWindow", str(self.vTeamMinSlider.value()), None))
        self.vTeamMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Vmax", None))
        self.vTeamMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.vTeamMaxSlider.value()), None))
        self.visionSteps.setTabText(self.visionSteps.indexOf(self.segTeamTab), QCoreApplication.translate("MainWindow", u"Segmentar time", None))
#if QT_CONFIG(tooltip)
        self.segBallFrame.setToolTip(QCoreApplication.translate("MainWindow", u"Selecione o filtro por intervalo (espaço HSV)", None))
#endif // QT_CONFIG(tooltip)
        self.segBallFrame.segmentImage()
        self.ballToolsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
        self.hueBallTitle.setText(QCoreApplication.translate("MainWindow", u"Hue", None))
        self.hueBallMinLabel.setText(QCoreApplication.translate("MainWindow", u"Hmin", None))
        self.hueBallMinValue.setText(QCoreApplication.translate("MainWindow", str(self.hueBallMinSlider.value()), None))
        self.hueBallMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Hmax", None))
        self.hueBallMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.hueBallMaxSlider.value()), None))
        self.sBallTitle.setText(QCoreApplication.translate("MainWindow", u"Saturation", None))
        self.sBallMinLabel.setText(QCoreApplication.translate("MainWindow", u"Smin", None))
        self.sBallMinValue.setText(QCoreApplication.translate("MainWindow", str(self.sBallMinSlider.value()), None))
        self.sBallMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Smax", None))
        self.sBallMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.sBallMaxSlider.value()), None))
        self.vBallTitle.setText(QCoreApplication.translate("MainWindow", u"Value", None))
        self.valBallMinLabel.setText(QCoreApplication.translate("MainWindow", u"Vmin", None))
        self.vBallMinValue.setText(QCoreApplication.translate("MainWindow", str(self.vBallMinSlider.value()), None))
        self.vBallMaxLabel.setText(QCoreApplication.translate("MainWindow", u"Vmax", None))
        self.vBallMaxValue.setText(QCoreApplication.translate("MainWindow", str(self.vBallMaxSlider.value()), None))
        self.visionSteps.setTabText(self.visionSteps.indexOf(self.segBallTab), QCoreApplication.translate("MainWindow", u"Segmentar bola", None))
#if QT_CONFIG(tooltip)
        self.genParamsDisplay.setToolTip(QCoreApplication.translate("MainWindow", u"Selecione 4 pontos", None))
#endif // QT_CONFIG(tooltip)
        self.genParamsFrame.setText("")
        self.segBallToolsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Ferramentas", None))
        self.minAreaInnerContourLabel.setText(QCoreApplication.translate("MainWindow", u"\u00c1rea m\u00ednima de contorno interno", None))
        self.minAreaContourLabel.setText(QCoreApplication.translate("MainWindow", u"\u00c1rea m\u00ednima de contorno externo", None))
        self.areaRectRatioLabel.setText(QCoreApplication.translate("MainWindow", u"Raz\u00e3o \u00e1rea contorno/ret\u00e2ngulo", None))
        self.stabilityParamLabel.setText(QCoreApplication.translate("MainWindow", u"Par\u00e2metro de estabilidade", None))
        self.visionSteps.setTabText(self.visionSteps.indexOf(self.genParamsTab), QCoreApplication.translate("MainWindow", u"Par\u00e2metros Gerais", None))
        self.appContents.setTabText(self.appContents.indexOf(self.visionSettingsTab), "")
#if QT_CONFIG(tooltip)
        self.appContents.setTabToolTip(self.appContents.indexOf(self.visionSettingsTab), QCoreApplication.translate("MainWindow", u"Caibra\u00e7\u00e3o da Vis\u00e3o", None))
#endif // QT_CONFIG(tooltip)
        self.appContents.setTabText(self.appContents.indexOf(self.visionAiTab), "")
#if QT_CONFIG(tooltip)
        self.appContents.setTabToolTip(self.appContents.indexOf(self.visionAiTab), QCoreApplication.translate("MainWindow", u"Detec\u00e7\u00e3o com IA", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

