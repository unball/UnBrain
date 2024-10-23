from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy,
    QPushButton, 
)
from PySide6.QtCore import Qt, QSize, QPointF
from PySide6.QtGui import QPixmap, QFont, QCursor, QIcon
from core import SizePolicies
#############################################
# Header config
#############################################

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