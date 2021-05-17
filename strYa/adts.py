'''
Contains containers for sensor's data. Classes to
represent rotations and determine one's position.
Should be run in a simulation, or in case one wants to test the system
could be used to analyse data written to a dataset.
'''

import numpy as np
import math
from numpy.lib.function_base import angle
import serial
from typing import Any, Dict, Tuple, List, Union
from ahrs import Quaternion
from datetime import datetime
from time import time
import pandas as pd
from scipy.spatial.transform import Rotation as R
import csv

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
        print(data)
        optimal = list(data.mean(axis=0))
        print('optimal')
        print(optimal)
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
        self.num_of_bad_posture_measurements: int = 0

    def normalised_angles(self) -> List[float]:
        angles = self.orientation.to_euler()
        optimal = self.optimal_position
        # print(angles, optimal)
        return [angles[0] - optimal[0], angles[1] - optimal[1]]

    def count_orientation(self, only_count: bool = False) -> None:

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
        if abs(y - self.optimal_position[1]) > 5:
            vertical_posture = False
        if abs(x - self.optimal_position[0]) > 5:
            horisontal_posture = False

        print(f'Sensor: {self.name} | Vertical: {posture_to_str[vertical_posture]}; \
Horisontal: {posture_to_str[horisontal_posture]}; {datetime.now()}')

        # in case the posture is bad, writes 1 to the serial port so
        # it would be handled and the led would be powered
        if port and (not vertical_posture or not horisontal_posture):
            port.write(bytearray(b'1'))
            self.num_of_bad_posture_measurements += 1

    
    def has_optimal_position(self) -> bool:
        '''
        Bool function that is convenient to check
        whether optimal posistion is counte 
        '''

        return bool(self.optimal_position)


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

    
    def set_sensor_data(self, data: List[List[List[float]]], writer=None) -> None:
        '''
        Receives a list of data with measurements: [[[acc], [gyro]], [[acc], [gyro]]]
        Sets it into allocated memory for it (created instance of class so to make
        it go to its calibratio buffer etc.)
        '''

        outstr_info: List[Any] = [datetime.now()]+[time()]
        for line, sensor_group in zip(data, self.sensor_groups):
            acc, gyro = line
            outstr_info = outstr_info + acc + gyro
            sensor_group.gyro.set_values(gyro)
            sensor_group.acc.set_values(acc)

        if writer:
            writer.writerow(outstr_info)


    def preprocess_data_from_file(self, line: str, sep: str =',') -> List[List[List[float]]]:
        '''
        Preprocesses data from csv file, in ordet ro return it 
        in such outlook: [[[acc], [gyro]], [[acc], [gyro]]]
        '''

        line = line.split(sep)[2:] # ommits the human and machine time
        line = [float(elm) for elm in line]
        outlst = []
        for sensor_group in (line[:6], line[6:]):
            outlst.append([sensor_group[:3], sensor_group[3:]])

        return outlst

    def preprocess_data(self, line: bytes) -> List[List[List[float]]]:
        '''
        Converts line of data from str or byte string into somekind of lists
        Line looks like acc_x, acc_y, acc_z; gyro_x, gyro_y, gyro_z|\
        acc_x, acc_y, acc_z; gyro_x, gyro_y, gyro_z
        '''

        SENSOR_GROUP_SEPARATOR = '|'
        SENSOR_SEPARATOR = '; '
        COORDINATE_SEPARATOR = ', '

        try:
            data = line.decode('utf-8').rstrip('\r\n').split(SENSOR_GROUP_SEPARATOR)
        except AttributeError:
            raise ValueError('The data cannot be readen')

        if len(data) != self.num_of_groups: # if there is not enought data  for 4 sensors
            raise ValueError('Number of data that is read does not match with the number\
of given sensor groups to read into')

        outdata = []
        for line, sensor_group in zip(data, self.sensor_groups):
            try:
                acc, gyro = line.split(SENSOR_SEPARATOR)
            except ValueError:
                return

            # time is saved at the time of creation of an object
            acc = [round(float(i), 2) for i in acc.split(COORDINATE_SEPARATOR)]
            gyro = [round(float(i), 2) for i in gyro.split(COORDINATE_SEPARATOR)]
            outdata.append([acc, gyro])

        return outdata

    @property
    def bad_posture_iters(self) -> int:
        return max(self.upper_sensor_group.num_of_bad_posture_measurements,
                    self.lower_sensor_group.num_of_bad_posture_measurements)
            

    def establish_connection(self, baudrate: int = 115200) -> serial.Serial:
        '''
        Establishes a connection on available port on a given baudrate
        '''

        possible_ports = ['COM3',\
                        '/dev/cu.usbserial-14120',\
                        '/dev/cu.usbserial-14220',\
                        '/dev/cu.usbserial-14240']

        for port in possible_ports:
            try:
                return serial.Serial(port, baudrate)
            except serial.serialutil.SerialException as exc:
                continue
        raise ValueError('There is no available port to connect to')


    def set_optimal_position(self, optimal_position: Tuple[float]) -> None:
        self.optimal_position = optimal_position


    def process_data_from_file(self, from_file):
        to_file = 'angles_' + from_file
        file_to_write = open(to_file, 'w')
        writer = csv.writer(file_to_write)
        writer.writerow(['human_time', 'computer_time', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2'])
        df = pd.read_csv(from_file)
        human_time = df['human_time'].tolist()
        computer_time = df['computer_time'].tolist()
        x_acc_1 = df['x_acc_1'].tolist()
        y_acc_1 = df['y_acc_1'].tolist()
        z_acc_1 = df['z_acc_1'].tolist()
        x_gyro_1 = df['x_gyro_1'].tolist()
        y_gyro_1 = df['y_gyro_1'].tolist()
        z_gyro_1 = df['z_gyro_1'].tolist()
        x_acc_2 = df['x_acc_2'].tolist()
        y_acc_2 = df['y_acc_2'].tolist()
        z_acc_2 = df['z_acc_2'].tolist()
        x_gyro_2 = df['x_gyro_2'].tolist()
        y_gyro_2 = df['y_gyro_2'].tolist()
        z_gyro_2 = df['z_gyro_2'].tolist()
        for i in range(len(x_acc_1)):
            acc1 = [x_acc_1[i], y_acc_1[i], z_acc_1[i]]
            acc2 = [x_acc_2[i], y_acc_2[i], z_acc_2[i]]
            gyro1 = [x_gyro_1[i], y_gyro_1[i], z_gyro_1[i]]
            gyro2 = [x_gyro_2[i], y_gyro_2[i], z_gyro_2[i]]
            data = [[acc1, gyro1], [acc2, gyro2]]
            for index, sensor_group in enumerate(self.sensor_groups):
                sensor_group.acc.set_values(data[index][0])
                sensor_group.gyro.set_values(data[index][1])
            if not self.lower_sensor_group.gyro.settings:
                print('. . .')
                continue
            orientations = []
            for sensor_group in self.sensor_groups:
                sensor_group.count_orientation()
                if sensor_group.optimal_position is None:
                    continue
                orientations.extend(sensor_group.orientation.to_euler())
            if orientations:
                orientations = [human_time[i], computer_time[i]] + orientations
                writer.writerow(orientations)
        optimal_orientations = []
        for sensor_group in self.sensor_groups:
            optimal_orientations.extend([str(i) for i in sensor_group.optimal_position])
        writer.writerow(['0', '0'] + optimal_orientations)
        file_to_write.close()

posture = PosturePosition()
posture.process_data_from_file('main_two.csv')