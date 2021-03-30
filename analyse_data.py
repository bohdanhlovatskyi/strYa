import matplotlib.pyplot as plt
import numpy
import pandas
from typing import Optional, List

class Sensor:
    
    def __init__(self, values: Optional[List]=[]) -> None:
        self.values = values

    def plot_values(self, values=[]) -> None:
        values = self.values if not values else values
        plt.plot(values, scalex=len(values))
        plt.show()


class Accelerometer(Sensor):
    pass

class Gyroscope(Sensor):
    pass

class Magnetometer(Sensor):
    pass

class OrientQuaternion(Sensor):
    pass