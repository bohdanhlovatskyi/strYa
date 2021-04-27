'''
Contains containers for sensor's data. Classes to
represent rotations and determine one's position.

Should be run in a simulation, or in case one wants to test the system
could be used to analyse data written to a dataset.
'''

from typing import Dict, Tuple, List
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from time import time

class Sensor(metaclass=ABCMeta):
    '''
    Abstract base class for a sensor values.
    Contains information, as well as setting of calibration
    that will allow to process its values in certain moment
    of time
    '''

    def __init__(self, values_tuple: Tuple[float], settings: Dict = None) -> None:
        # higly unlikely that this class will be used by the user
        self._values = values_tuple
        self.set_settings(settings)
        self.init_time = time() # not sure whether we really need this here
        # because it will be called in the orientation class, which seems kinda more
        # handy

    def set_settings(self, settings: Dict) -> None:
        if settings is None:
            return

        for setting in settings:
            self.__setattr__(setting, settings[setting])

    @property
    def raw_data(self) -> Tuple[float]:
        return self._values

    @abstractmethod
    def sensor_data(self) ->Tuple[float]:
        '''
        Procceeds the raw data depending on the given setting.
        For each sensor these setting are different
        '''

        return NotImplemented

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.raw_data}'


class Accelerometer(Sensor):

    def sensor_data(self) -> Tuple[float]:
        '''
        Processes data depending on the given settings

        TODO: what exactly parameters affect the accelerometer values
        '''

        if settings is None:
            return self.raw_data

        pass

class Gyro(Sensor):
    
    def sensor_data(self) -> Tuple[float]:
        '''
        Processes data depending on the given settings
        '''

        if settings is None:
            return self.raw_data

        pass

class Magnetometer(Sensor):
    
    def sensor_data(self) -> Tuple[float]:
        '''
        Processes data depending on the given settings
        '''

        if settings is None:
            return self.raw_data

        pass


class Quaternion:
    
    def __init__(self, sensor_group: SensorGroup) -> None:
        angle, vector_x, vector_y, vector_z = self.proccess_group(sensor_group)
        self.angle = angle
        self.x = vector_x
        self.y = vector_y
        self.z = vector_z

    def proccess_group(self, group: SensorGroup) -> Tuple[float]:
        pass

@dataclass
class SensorGroup:
    '''
    Sensor group container. Contains three sensors info
    that will be processed in some class that will represent
    rotation and relative position

    TODO: rewrite for fusion of 3 sensors !!!! ! ! ! ! ! 
    '''

    acc: Accelerometer
    gyro: Gyro
    mag: Magnetometer

class Orientation:
    '''
    Main class that will contain all the info on the
    orientation of a person based on sensor fusion.

    TODO: not sure whether we need this at all
    '''

    def __init__(self, sensor_group: SensorGroup) -> None:
        self.orientation = Quaternion(sensor_group)
        self.time = time()


if __name__ == '__main__':
    acc = Accelerometer((10, 11, 12))
    print(acc)
    print(acc.raw_data)
    print(acc.set_settings({'lol': 3}))
    print(acc.lol)
