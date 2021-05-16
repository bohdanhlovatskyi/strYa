'''
Contains containers for sensor's data. Classes to
represent rotations and determine one's position.

Should be run in a simulation, or in case one wants to test the system
could be used to analyse data written to a dataset.
'''

import numpy as np
import math
import serial
from typing import Dict, Tuple, List, Union
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

    def count_orientation(self, only_count: bool = False) -> None:

        self.orientation = QuaternionContainer(self.filter.updateIMU(self.orientation.as_numpy_array(),
                                                                     self.gyro.current_value_np,
                                                                     self.acc.current_value_np))
        if only_count:
            return

        self.buffer.push(self.orientation.to_euler())
        if not self.optimal_position:
            self.optimal_position = self.buffer.optimal_position()
            print(f'Optimal position of {self.name} sensor grroup is estimated, it is: {self.optimal_position}\n')
            return

    def deviation_from_optimal(self) -> Tuple[float]:
        try:
            x, y, z = self.orientation.to_euler()
        except TypeError:
            return
        except AttributeError: 
            return

        return (abs(x - self.optimal_position[0]), 
                abs(y - self.optimal_position[1]),
                abs(z - self.optimal_position[2]))

    def _check_current_posture_one_sensor(self, port: serial.Serial = None) -> None:
        '''
        This function is kinda deprecated because works well
        only with logic compatable with one sensor, though
        it might be useful to know on which sensor exactly does it
        not work ok
        '''

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
        # if port and (not vertical_posture or not horisontal_posture):
        #     port.write(bytearray(b'1'))

    def __str__(self) -> str:
        return f'{str(self.acc)} | {str(self.gyro)})'


class PosturePosition:

    BAD_POSTURE_DEGREE: int = 5

    def __init__(self) -> None:
        '''
        Should be used as container for certain variables that would be comfportable
        to use while analysing the user's posture
        '''

        self.upper_sensor_group = SensorGroup('upper one')
        self.lower_sensor_group = SensorGroup('lower one')
        self.sensor_groups = (self.upper_sensor_group, self.lower_sensor_group)
        self.num_of_groups: int = 2
        self.num_of_bad_posture_measurements: int = 0
        # not efficient realisation, can be rewritten via bytearray ot sth
        self.posture_state_buffer = Buffer(10)


    def check_current_posture(self, port: serial.Serial = None) -> None:
        '''
        Checks the posture based on reading from two sensors
        '''

        changes = zip(self.upper_sensor_group.deviation_from_optimal(),
                      self.lower_sensor_group.deviation_from_optimal())
        changes = list(map(lambda x: abs(abs(x[0]) - abs(x[1])), changes))

        # omits one of angles because it does not work yet
        changes = changes[:2]

        idx_to_dimenstion = {0: 'x', 1: 'y', 2: 'z'}
        posture_to_str: Dict[bool, str] = {False: 'OK', True: 'F'}

        bad_posture: bool = False
        for idx, elm in enumerate(changes):
            if elm > self.BAD_POSTURE_DEGREE:
                bad_posture = True
                break

<<<<<<< HEAD
    def get_sensor_data(self, port: serial.Serial, writer=None) -> None:
=======
        # for analysing variables incrementation
        self.posture_state_buffer.push(bad_posture)
        # imcrements variable of bad_posture_masurement
        # handy in funciton of recalibration, as well
        if bad_posture:
            self.num_of_bad_posture_measurements += 1
>>>>>>> cb9ab5cdb24fa7782635b66d32410d347511818e

        outstr = f'Posture in {datetime.now()} is {posture_to_str[bad_posture]}. '
        if bad_posture:
            outstr += f'There is a problem with {idx_to_dimenstion[idx]}'
        print(outstr)

        # in case the posture is bad, writes 1 to the serial port so
        # it would be handled and the led would be powered
        if port and all(self.posture_state_buffer.data):
            port.write(bytearray(b'1'))


    def set_sensor_data(self, data: List[List[List[float]]], file_obj=None) -> None:
        '''
        Receives a list of data with measurements: [[[acc], [gyro]], [[acc], [gyro]]]
        Sets it into allocated memory for it (created instance of class so to make
        it go to its calibratio buffer etc.)
        '''

        outstr: str = ''
        for line, sensor_group in zip(data, self.sensor_groups):
            acc, gyro = line
            outstr += ', '.join([str(elm) for elm in [*acc, *gyro]]) + ', '
            sensor_group.gyro.set_values(gyro)
            sensor_group.acc.set_values(acc)

        if file_obj:
            outstr = str(datetime.now()) + ', ' + str(time()) + ', ' + \
                    outstr.rstrip(', ') + '\n'
            file_obj.write(outstr)

    def preprocess_data_from_file(self, line: str) -> List[List[List[float]]]:
        '''
        Preprocesses data from csv file, in ordet ro return it 
        in such outlook: [[[acc], [gyro]], [[acc], [gyro]]]
        '''

        line = line.split(', ')[2:] # ommits the human and machine time
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
            sensor_name = sensor_group.name
            if writer:
                if sensor_name == 'upper one':
                    data = [datetime.now()]+[time()]+acc+gyro
                else:
                    data += acc + gyro
                    writer.writerow(data)
            sensor_group.gyro.set_values(gyro)
            sensor_group.acc.set_values(acc)
            outdata.append([acc, gyro])

        return outdata

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
    def process_data_from_file(self, from_file):
        to_file = 'angles_' + from_file
        file_to_write = open(to_file, 'w')
        writer = csv.writer(to_file)
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

class Analyzer:
    def read_data(self, path):

        #data frame from rounded data file
        df = pd.read_csv(path)
        rounded = np.round(df)

        #find optimal and delete it from data frame
        optimal = df.tail(1)
        x1_optimal = optimal['x1'].tolist()[0]
        y1_optimal = optimal['y1'].tolist()[0]
        # # print(x_optimal, y_optimal)
        #print(optimal)
        x2_optimal = optimal['x2'].tolist()[0]
        y2_optimal = optimal['y2'].tolist()[0]
        df = df.head(-1)

        #find all par for graphs
        time = df['computer_time'].tolist()
        start_time = time[0]
        time = [i-start_time for i in time]
        x1 = df['x1'].tolist()
        x1 = [i+x1_optimal for i in x1]
        y1 = df['y1'].tolist()
        y1 = [i-y1_optimal for i in y1]
        # z1 = df['z1'].tolist()

        x2 = df['x2'].tolist()
        x2 = [i+x2_optimal for i in x2]
        y2 = df['y2'].tolist()
        y2 = [i-y2_optimal for i in y2]
        # z2 = df['z2'].tolist()
        return x1, y1, x2, y2

    @staticmethod
    def steady(orient_1, orient_2):
        for orientation in [orient_1, orient_2]:
            for axis in orientation:
                if abs(axis) > 5:
                    return False
        return True
    @staticmethod
    def forward_rotation(orient_1, orient_2):
        y1 = orient_1[1]
        y2 = orient_2[1]
        if 30 < abs(y1) < 70 and 30 < abs(y2) < 70:
            if abs(y1-y1) < 20:
                return True
        return False
    @staticmethod
    def forward_tilt(orient_1, orient_2):
        y1 = orient_1[1]
        y2 = orient_2[1]
        if 10 < abs(y1) < 25 and abs(y2) < 7:
            return True
        #chack sitting
        if 10 < abs(y1) < 15 and 25 < abc(y2) < 30:
            return True
        return False

    @staticmethod
    def side_tilt(orient_1, orient_2):      
        x1 = orient_1[0]
        x2 = orient_2[0]
        if 10 < abs(x1) < 30 or 10 < abs(x2) < 30:
                return True
        return False
    

    def check_mode(self, x1, y1, x2, y2):
        orient_1 = (x1, y1)
        orient_2 = (x2, y2)
        if self.steady(orient_1, orient_2):
            print('Steady.')
        if self.forward_rotation(orient_1, orient_2):
            print('Forward rotation.')
        elif self.forward_tilt(orient_1, orient_2):
            print('Forward tilt.')
        elif self.side_tilt(orient_1, orient_2):
            print('Side tilt')


    def check_data(self, path):
        x1, y1, x2, y2 = self.read_data(path)
        for i in range(len(x1)):
            self.check_mode(x1[i], y1[i], x2[i], y2[i])


if __name__ == '__main__':
    analyze = Analyzer()
    analyze.check_data('angles_sitting_2.csv')
#     posture = PosturePosition()
#     posture.process_data_from_file('steady.csv')
