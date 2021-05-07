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
from ahrs import Quaternion
from datetime import datetime
from time import time


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
        optimal = list(data.mean(axis=0))
        print(f'Buffer is filled, optimal position is {optimal}')
        return optimal

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


class Sensor(metaclass=ABCMeta):
    '''
    Abstract base class for a sensor values.
    Contains information, as well as setting of calibration
    that will allow to process its values in certain moment
    of time
    '''

    def __init__(self, values_tuple: Tuple[float], settings: Dict = None) -> None:
        # higly unlikely that this class will be used by the user
        self.values = values_tuple
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
        return np.array(self.values)

    @property
    @abstractmethod
    def sensor_data(self) ->Tuple[float]:
        '''
        Procceeds the raw data depending on the given setting.
        For each sensor these setting are different
        '''

        return NotImplemented

    def as_numpy_array(self) -> np.array:
        return np.array(self.values)

    def __str__(self) -> str:
        return f'{type(self).__name__} Here should go your data'


class Accelerometer(Sensor):

    def sensor_data(self) -> Tuple[float]:
        '''
        Processes data depending on the given settings

        TODO: what exactly parameters affect the accelerometer values
        '''

        #if self.settings is None:
        return self.raw_data


class Gyro(Sensor):

    calibration_buffer = Buffer()
    settings = None
    idx_to_atr = {0: 'x', 1: 'y', 2: 'z'}

    def __new__(cls,  *args) -> 'Gyro':
        gyro = super(Gyro, cls).__new__(cls)
        # while creating a new instance of class,
        # fills the buffer to count gyro bias (drift)
        # that then will be reduced while creating a new instance
        if gyro.settings is not None:
            gyro.set_settings(Gyro.settings)
        elif not Gyro.calibration_buffer.is_filled():
            Gyro.calibration_buffer.push(args[0])
        # calculates actual bias from the filled buffer
        elif not Gyro.settings:
            print(Gyro.calibration_buffer)
            Gyro.settings = {Gyro.idx_to_atr[idx]: value for idx, value in\
                            enumerate(Gyro.calibration_buffer.optimal_position())}
            print(Gyro.settings)
            gyro.set_settings(Gyro.settings)
            Gyro.calibration_buffer = None

        return gyro
    
    def sensor_data(self) -> Tuple[float]:
        '''
        Processes data depending on the given settings
        '''

        if not Gyro.settings:
            return self.raw_data
        try:
            corrected_data = [value - getattr(self, Gyro.idx_to_atr[idx]) \
                            for idx, value in enumerate(self.values)]
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

class SensorGroup:
    '''
    Sensor group container. Contains sensors info
    that will be processed in some class that will represent
    rotation and relative position
    '''

    def __init__(self, acc: Accelerometer = None, gyro: Gyro = None) -> None:
        self.acc = Accelerometer
        self.gyro = Gyro
        self.orientation = QuaternionContainer(np.array([1, 0, 0, 0]))

    def set_current_orientation(sefl, orientation: np.ndarray) -> None: 
        self.orientation = QuaternionContainer(list(orientation))


    @property
    def optimal_position(self) -> Tuple[float]:
        '''
        We can pass the logic of determining the optimal postiion here as well
        '''

        return self.orientation

    def set_sensors(self, acc: Accelerometer, gyro: Gyro):
        self.acc = acc
        self.gyro = gyro

    def __str__(self) -> str:
        return f'{str(self.acc)} | {str(self.gyro)})'


class PosturePosition:

    def __init__(self, sensor_groups: Tuple[SensorGroup] = None) -> None:
        '''
        Should be used as container for certain variables that would be comfportable
        to use while analysing the user's posture
        '''

        self.sensor_groups = sensor_groups

    @staticmethod
    def _find_change(prev_orientation: Tuple[float],
                     current: Tuple[float]) ->\
                     Tuple[float, Tuple[float]]:
        '''
        Determines change between two orientation measurements.

        Returns tuple with (percentage_of_change, (relative change vector values))

        '''

        pass

    @staticmethod
    def _detects_movement(prev_orientation: Tuple[float],\
                          current: Tuple[float], precision: int = 10) -> bool:
        '''
        determines whether object moves between two measurements.

        possible_usage: checks this for 10-15 measurement and
        if the majority the function return values are True,
        then the object is moving. This would be useful in determining
        time of sitting srteadily and so on
        '''

        change, _ = self._find_change(prev_orientation, current)

        if change > precision:
            return True 

        return False

    def check_current_posture(self, orientation: QuaternionContainer) -> None:
        x, y, z = orientation.to_euler()
        # determine_bad_posture(q)
        if (abs(y) - abs(self.optimal_position[1])) > 10:
            print(f'Bad posture {datetime.now()}')
        if abs(x - self.optimal_position[0]) > 10:
            print(f'Bad horisontal posture {datetime.now()}')


    def set_optimal_position(self, optimal_position: Tuple[float]) -> None:
        self.optimal_position = optimal_position

    def visualise_posture(self) -> None:
        '''
        Visualises the posture via matplotlib(???)
        '''

        pass

    def find_time_without_movement(self) -> float:
        pass

    def most_popular_position(self) -> Tuple[float]:
        pass

    def recommendations(self) -> str:
        '''
        Prints out some information
        '''
        
        pass

if __name__ == '__main__':
    g = Gyro((1, 1, 1))
    print(g)
    print(Gyro.calibration_buffer)
    g1 = Gyro((2, 2, 2))
    print(Gyro.calibration_buffer)
    for i in range(25):
        Gyro((i, i, i))
    print(Gyro((15, 15, 15)).sensor_data())
    
