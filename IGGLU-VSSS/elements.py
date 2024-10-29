from dataclasses import dataclass

@dataclass
class Robot:
    id: str = '0'
    x: float = 0.0
    y: float = 0.0
    orientation: float = 0.0
    status: str = 'OFF'
    battery: int = 0
    linearSpeed: float = 0.0
    angularSpeed: float = 0.0
    frequency: float = 0.0

class Ball:
    x: float = 0.0
    y: float = 0.0