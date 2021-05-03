'''
Contains containers for sensor's data. Classes to
represent rotations and determine one's position.

Should be run in a simulation, or in case one wants to test the system
could be used to analyse data written to a dataset.
'''

import numpy as np
import math
from typing import Dict, Tuple, List
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
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
        self.init_time = time() # not sure whether we really need this here
        # because it will be called in the orientation class, which
        # seems kinda more handy
        if not settings:
            self.settings = None
        else:
            self.set_settings(settings)

    def set_settings(self, user_settings: Dict[str, float]) -> None:
        for setting in user_settings:
            self.__setattr__(setting, user_settings[setting])

    @property
    def raw_data(self) -> Tuple[float]:
        return np.array(self._values)

    @property
    @abstractmethod
    def sensor_data(self) ->Tuple[float]:
        '''
        Procceeds the raw data depending on the given setting.
        For each sensor these setting are different
        '''

        return NotImplemented

    def as_numpy_array(self) -> np.array:
        return np.array(self._values)

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.raw_data}'


class Accelerometer(Sensor):

    def sensor_data(self) -> Tuple[float]:
        '''
        Processes data depending on the given settings

        TODO: what exactly parameters affect the accelerometer values
        '''

        #if self.settings is None:
        return self.raw_data


class Gyro(Sensor):
    
    def sensor_data(self) -> Tuple[float]:
        '''
        Processes data depending on the given settings
        '''

        idx_to_atr = {0: 'x', 1: 'y', 2: 'z'}
        try:
            corrected_data = [value - getattr(self, idx_to_atr[idx]) \
                            for idx, value in enumerate(self._values)]
        except AttributeError as err:
            raise ValueError('You shoule specify settings for gyro')

        return np.array(corrected_data)


class QuaternionContainer:
    
    def __init__(self, data: np.array) -> None:
        self.w, self.x, self.y, self.z = data

    def as_numpy_array(self) -> np.array:
        return np.array([self.w, self.x, self.y, self.z])

    def to_euler(self) -> Tuple[float]:
        '''
        Turns the Quaternion readings into Euler Angles for projection
        '''

        t0 = +2.0 * (self.w * self.x + self.y * self.z)
        t1 = +1.0 - 2.0 * (self.x * self.x + self.y * self.y)
        X = math.degrees(math.atan2(t0, t1))

        t2 = +2.0 * (self.w * self.y - self.z * self.x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        Y = math.degrees(math.asin(t2))

        t3 = +2.0 * (self.w * self.z + self.x * self.y)
        t4 = +1.0 - 2.0 * (self.y * self.y + self.z * self.z)
        Z = math.degrees(math.atan2(t3, t4))

        return X, Y, Z

@dataclass
class SensorGroup:
    '''
    Sensor group container. Contains sensors info
    that will be processed in some class that will represent
    rotation and relative position
    '''

    acc: Accelerometer
    gyro: Gyro


class Buffer:

    def __init__(self, size: int = 25) -> None:
        self.data = []
        self.size = size
        self.optimal = None
        self.gyro_settings = None

    def push(self, quat: Tuple[float]) -> None:
        '''
        Puches an elements into buffer, while it is not filled.

        If it is, deletes the first element in order for buffer
        to remain of the same size.
        '''

        if len(self.data) == self.size:
            self.data.pop(0)
        self.data.append(quat)

    def is_filled(self) -> bool:
        '''
        Checks whether buffer is filled
        '''

        return len(self.data) == self.size

    def optimal_position(self) -> Tuple[float]:
        '''
        Based on measurments, determines user's optimal position.
        '''

        data = np.array(self.data)
        self.optimal = list(data.mean(axis=0))
        print(f'Buffer is filled, optimal position is {self.optimal}')
        return self.optimal

    def count_gyro_drift(self) -> None:
        '''
        Finds the drift (bias) of gyro, based on the measurements
        that are in the filled buffer. Then applies them as settings in order
        to get rid of this bias later on
        '''

        # takes three args that represent gyro measuremnts
        gyro_data = np.array([msr[3:] for msr in self.data])
        drift = gyro_data.mean(axis=0)
        settings = {
            'x': drift[0],
            'y': drift[1],
            'z': drift[2] 
        }

        self.gyro_settings = settings

    def __str__(self) -> str:
        return str(self.data)

