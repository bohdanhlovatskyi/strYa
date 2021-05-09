'''
Contains containers for sensor's data. Classes to
represent rotations and determine one's position.

Should be run in a simulation, or in case one wants to test the system
could be used to analyse data written to a dataset.
'''

import numpy as np
import math
import serial
from typing import Dict, Tuple, List
from ahrs import Quaternion
from datetime import datetime
from time import time

from abc import ABCMeta, abstractmethod
from ahrs.filters import Mahony


class Buffer:

    def __init__(self, size: int = 25) -> None:
        self.data: List[float] = []
        self.size: int = size
        self.optimal: List[float] = None
        self.gyro_settings: Tuple[float] = None

    def push(self, quat: Tuple[float]) -> None:
        '''
        Puches an elements into buffer, while it is not filled.

        If it is, deletes the first element in order for buffer
        to remain of the same size.
        '''

        if self.is_filled():
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
        return optimal

    def count_gyro_drift(self) -> None:
        '''
        Finds the drift (bias) of gyro, based on the measurements
        that are in the filled buffer. Then applies them as settings in order
        to get rid of this bias later on
        '''

        # takes three args that represent gyro measuremnts
        gyro_data = np.array(self.data)
        bias = tuple(gyro_data.mean(axis=0))
        print(f'Gyro bias is calculated: {bias}')

        return bias

    def __str__(self) -> str:
        return str(self.data)


class Sensor(metaclass=ABCMeta):
    '''
    Abstract base class for a sensor values.
    Contains information, as well as setting of calibration
    that will allow to process its values in certain moment
    of time
    '''

    def __init__(self) -> None:
        self.buffer: Buffer = Buffer()
        self.current_value: Tuple[float] = None
        self.settings: Tuple[float] = None

    @abstractmethod
    def set_values(self):
        pass

    def __str__(self) -> str:
        return f'{type(self).__name__}({self.current_value})'

    @property
    def current_value_np(self) -> np.ndarray:
        return np.array(self.current_value)


class Accelerometer(Sensor):
    '''
    Accelerometer container class
    '''

    def set_values(self, values: Tuple[float]) -> None: 
        self.current_value = values

class Gyro(Sensor):

    def process_values(self, values: List[float]) -> Tuple[float]:
        '''
        Processes value due to the gyro setings.
        If there is no such, raises ValueError
        '''

        if self.settings is None:
            raise ValueError('There is no settings counted')

        for idx, value in enumerate(values):
            values[idx] = value - self.settings[idx]

        return values            

    def set_values(self, values: Tuple[float]) -> None:
        '''
        Assignes value to this gyro. Values go into buffer
        in order to have the bias counted
        '''

        if self.settings is not None:
            self.current_value = self.process_values(values)
            return
        if not self.buffer.is_filled():
            self.buffer.push(values)
            self.current_value = values
            return
        self.settings = self.buffer.count_gyro_drift()
        self.current_value = self.process_values(values)
        self.buffer = None
        return


class QuaternionContainer:
    
    def __init__(self, data: np.array) -> None:
        self.w, self.x, self.y, self.z = data

    def as_numpy_array(self) -> np.array:
        return np.array([self.w, self.x, self.y, self.z])

    def __str__(self) -> str:
        return str(self.as_numpy_array())

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

    def __init__(self, name: str = 'sensor_group') -> None:
        self.name = name
        self.acc = Accelerometer()
        self.gyro = Gyro()
        self.orientation = QuaternionContainer([1.0, 0.0, 0.0, 0.0])
        self.optimal_position = None
        self.buffer: Buffer = Buffer()
        self.filter = Mahony(frequency=5)

    def count_orientation(self, only_count: bool = False) -> None:
        if self.name == 'lower one':
            # print(f'{self.name}: {self.orientation}') - there is some prroblem, no idea what exactly
            # print(self.acc, self.gyro) -> this works fine to me
            pass

        self.orientation = QuaternionContainer(self.filter.updateIMU(self.orientation.as_numpy_array(),
                                                                     self.gyro.current_value_np,
                                                                     self.acc.current_value_np))

        if only_count:
            return

        if self.optimal_position is not None:
            return
        if not self.buffer.is_filled():
            self.buffer.push(self.orientation.to_euler())
            return
        if not self.optimal_position:
            self.optimal_position = self.buffer.optimal_position()
            print(self.buffer.data)
            print(f'Optimal position of {self.name} sensor grroup is estimated, it is: {self.optimal_position}\n')
            self.buffer = None
            return

    def check_current_posture(self, port: serial.Serial = None) -> None:
        # print(self.orientation.to_euler())
        try:
            x, y, z = self.orientation.to_euler()
        except TypeError:
            return
        except AttributeError: 
            return
        # determine_bad_posture(q)
        vertical_posture: bool = True
        horisontal_posture: bool = True
        posture_to_str: Dict[bool, str] = {True: 'OK', False: 'F'}
        if abs(y - self.optimal_position[1]) > 10:
            vertical_posture = False
        if abs(x - self.optimal_position[0]) > 10:
            horisontal_posture = False

        print(f'Sensor: {self.name} | Vertical: {posture_to_str[vertical_posture]}; \
Horisontal: {posture_to_str[horisontal_posture]}; {datetime.now()}')

        # in case the posture is bad, writes 1 to the serial port so
        # it would be handled and the led would be powered
        if port and (not vertical_posture or not horisontal_posture):
            port.write(bytearray(b'1'))


    def __str__(self) -> str:
        return f'{str(self.acc)} | {str(self.gyro)})'


class PosturePosition:

    def __init__(self) -> None:
        '''
        Should be used as container for certain variables that would be comfportable
        to use while analysing the user's posture
        '''

        self.upper_sensor_group = SensorGroup('upper one')
        self.lower_sensor_group = SensorGroup('lower one')
        self.sensor_groups = (self.upper_sensor_group, self.lower_sensor_group)
        self.num_of_groups: int = 2

    def get_sensor_data(self, port: serial.Serial) -> None:


        SENSOR_GROUP_SEPARATOR = '|'
        SENSOR_SEPARATOR = '; '
        COORDINATE_SEPARATOR = ', '
        line = port.readline()

        try:
            data = line.decode('utf-8').rstrip('\r\n').split(SENSOR_GROUP_SEPARATOR)
        except AttributeError:
            raise ValueError('The data cannot be readen')

        if len(data) != self.num_of_groups: # if there is not enought data  for 4 sensors
            raise ValueError('Number of data that is read does not match with the number\
    of given sensor groups to read into')

        for_obj_data = []
        for line, sensor_group in zip(data, self.sensor_groups):
            try:
                acc, gyro = line.split(SENSOR_SEPARATOR)
            except ValueError:
                return

            # time is saved at the time of creation of an object
            acc = [round(float(i), 2) for i in acc.split(COORDINATE_SEPARATOR)]
            gyro = [round(float(i), 2) for i in gyro.split(COORDINATE_SEPARATOR)]
            # print(sensor_group.name, acc, gyro)
            sensor_group.gyro.set_values(gyro)
            sensor_group.acc.set_values(acc)

    def establish_connection(self, baudrate: int = 115200) -> serial.Serial:
        '''
        Establishes a connection on available port on a given baudrate
        '''

        possible_ports = ['/dev/cu.usbserial-14120',
                        '/dev/cu.usbserial-14220', 
                        '/dev/cu.usbserial-14240'
                        'COM3']

        for port in possible_ports:
            try:
                return serial.Serial(port, baudrate)
            except serial.serialutil.SerialException as exc:
                continue
        raise ValueError('There is no available port to connect to')

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


    def set_optimal_position(self, optimal_position: Tuple[float]) -> None:
        self.optimal_position = optimal_position


if __name__ == '__main__':
    posture = PosturePosition()
    print(posture.upper_sensor_group.gyro)
    for i in range(26):
        posture.upper_sensor_group.gyro.set_values([i, i, i])
    print(posture.upper_sensor_group.gyro)
    print(posture.upper_sensor_group.gyro.settings)
