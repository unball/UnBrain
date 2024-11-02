from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QFont, QFontDatabase
############################
# Base classes
############################

SizePolicies = {
    #genExpPrefPolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    "Expanding_Preferred": QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred),
    # expPrefPolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    "Expanding_Fixed": QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed),
    # fixFixPolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    "Fixed_Fixed": QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed),
    # minExpGenExpPolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
    "MinExpanding_Expanding": QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding),
    # prefPrefPolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    "Preferred_Preferred": QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred),
    # prefFixPolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
    "Preferred_Fixed": QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed),
    # genExpGenExpPolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    "Expanding_Expanding": QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding),
    # minExpFixPolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
    "MinExpanding_Fixed": QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
}

############################################
# Fonts
############################################
font2 = QFont()
font2.setFamilies([u"Roboto"])
font2.setPointSize(8)
font2.setBold(True)       

font3 = QFont()
font3.setFamilies([u"Roboto"])
font3.setPointSize(8)

font4 = QFont()
font4.setFamilies([u"Roboto"])
font4.setBold(True)

font5 = QFont()
font5.setFamilies([u"Roboto"])
font5.setPointSize(7)

font6 = QFont()
font6.setFamilies([u"Roboto"])
font6.setPointSize(8)

font7 = QFont()
font7.setFamilies([u"Roboto"])
font7.setPointSize(11)
font7.setBold(True)

font8 = QFont()
font8.setFamilies([u"Roboto"])
font8.setPointSize(20)

font9 = QFont()
font9.setFamilies([u"Roboto"])
font9.setPointSize(8)
font9.setWeight(QFont.Thin)

Fonts = {
    #"font1": font1,
    "font2": font2,
    "font3": font3,
    "font4": font4,
    "font5": font5,
    "font6": font6,
    "font7": font7,
    "font8": font8,
    "font9": font9
}


class AppWidget:
    def __init__(self):
        ...