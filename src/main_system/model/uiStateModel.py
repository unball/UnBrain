from main_system.model import ModelContext

class UIStateModel(ModelContext):
    """Persiste configurações de sessão da UI"""
    def __init__(self):
        ModelContext.__init__(self, {
            "n_robots": ("ui_n_robots", 3),
            "field_side": ("ui_field_side", 1),
        })
