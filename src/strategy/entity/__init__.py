from abc import ABC, abstractmethod, abstractproperty

class Entity(ABC):
    def __init__(self, world, robot):
        ABC.__init__(self)
        
        self.world = world
        self.robot = robot

    @abstractproperty
    def control(self):
        pass

    @abstractmethod
    def fieldDecider(self):
        pass

    @abstractmethod
    def directionDecider(self):
        pass

    @abstractmethod
    def equalsTo(self, otherEntityOfSameClass):
        pass

    @abstractmethod
    def onExit(self):
        pass

    def isLocked(self):
        return False
    
    