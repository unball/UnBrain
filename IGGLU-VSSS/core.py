from PySide6.QtWidgets import QSizePolicy
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

class AppWidget:
    def __init__(self):
        ...