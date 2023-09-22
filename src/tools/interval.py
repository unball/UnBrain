import time

class Interval:
    def __init__(self, filter=True, initial_dt=None):
        self._dt = initial_dt
        self.lastTime = None
        self.filter = filter

    def getInterval(self, update=True):
        if self.lastTime is not None:
            currentTime = time.time()
            dt = currentTime - self.lastTime
            if self.filter: self._dt = dt if self._dt is None else (0.999 * self._dt + 0.001 * dt)
            else: self._dt = dt
            
        self.lastTime = time.time()
        return 0.016#self._dt

    @property
    def dt(self):
        return 0.016#self._dt

    def update(self):
        self.lastTime = time.time()