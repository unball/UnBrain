from .area import Area
import numpy as np

class AvoidRect(Area):
    def __init__(self, ra, rb):
        super().__init__()
        self.ra = np.array(ra)
        self.rb = np.array(rb)

    def P(self, t):
        #ra = ra / (np.sqrt(ra[0]**2 + ra[1]**2))
        #rb = rb / (np.sqrt(rb[0]**2 + rb[1]**2))
        ra = self.ra
        rb = self.rb
        if(t >= 0 and t < 1/4):
            x = 4*t
            return np.array([rb[0], ra[1]+x*(rb[1]-ra[1])])
        elif(t >= 1/4 and t < 2/4):
            x = 4*t - 1
            return np.array([(1-x)*rb[0] + x*ra[0], rb[1]])
        elif(t >= 2/4 and t < 3/4):
            x = 4*t - 2
            return np.array([ra[0], rb[1]-x*(rb[1]-ra[1])])
        elif(t >= 3/4 and t <= 1):
            x = 4*t - 3
            return np.array([(1-x)*ra[0] + x*rb[0], ra[1]])