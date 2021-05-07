import pygame
import math
import time
import serial
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from ahrs.filters import Madgwick, Mahony
from typing import Tuple, Union

from strYa.adts import SensorGroup, Accelerometer, Gyro, Buffer, QuaternionContainer
from strYa.visualisation import Visualiser
from strYa.posture_position import PosturePosition
# from strYa.posture_position import PosturePosition

def establish_connection(baudrate: int = 115200) -> serial.Serial:
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
    raise

def get_sensor_data(port: serial.Serial, sensor_groups: Tuple[SensorGroup]) -> SensorGroup:
    '''
    Gets info from sensors
    '''

    return __process_info(port.readline(), sensor_groups)

def __process_info(line: str, sensor_groups: Tuple[SensorGroup],
                   debug: bool = False, sensor_sep: str = '|') -> None:
    '''
    Processes info either from serial port of from file with dataset 
    '''

    sep = ', ' if debug else ' '
    try:
        data = line.decode('utf-8').rstrip('\r\n').split(sensor_sep)
    except AttributeError:
        data = line.rstrip('\r\n').split(sensor_sep)

    if len(data) != len(sensor_groups):
        raise ValueError('Number of data that is read does not match with the number\
of given sensor groups to read into')

    for_obj_data = []
    for line, sensor_group in zip(data, sensor_groups):
        try:
            acc, gyro = line.split('; ')
        except ValueError:
            return

        # time is saved at the time of creation of an object
        acc = [float(i) for i in acc.split(', ')]
        gyro = [float(i) for i in gyro.split(', ')]
        sensor_group.set_sensors(Accelerometer(acc), Gyro(gyro))

def get_data_from_file(path: str) -> SensorGroup:
    '''
    DEBUG: reads info from file as if it is sensor.
    '''

    with open(path) as infile:
        data = infile.readlines()

    for idx, line in enumerate(data):
        data[idx] = __process_info(line, debug=True)

    return data

def process_measurement(data_source: Union[Tuple[Tuple[float]], serial.Serial],
                            current_position: QuaternionContainer,
                            posture: PosturePosition, iteration: int = 0,) -> QuaternionContainer:
    '''
    Function that will be used for iterating through data source.
    '''

    pass



def main(debug: bool = False):
    # it is here where we get source of data that will be used
    # while iterating
    if not debug:
        port = establish_connection()
    else:
        data = get_data_from_file('euler_angles_2.txt')

    mahony = Mahony(frequency=5)

    upper_sensor_group = SensorGroup()
    lower_sensor_group = SensorGroup()
    # sensor_groups = (upper_sensor_group, lower_sensor_group)
    # posture = PosturePosition(sensor_groups)

    # vis = Visualiser()
    # vis.main_init()

    buf = Buffer()

    # outfile = open('euler_angles_3.txt', 'w')
    
    iteration: int = 0  
    while True:
        iteration += 1

        get_sensor_data(port, (upper_sensor_group, lower_sensor_group))

        # print(upper_sensor_group.gyro, lower_sensor_group.gyro)
        while not Gyro.settings: # waits for quaterion to calculate the
            # bias that will be then applied to each element
            # print(Gyro.calibration_buffer)
            continue

        print(Gyro.settings)

        # N.B it is important to process some quaternions here, because we
        # start from [1, 0, 0, 0] quaternion and therefore they need some
        # time to stabilize
        verbose = False
        for sensor_group in sensor_groups:
            if verbose:
                verbose = False
                continue
            q = mahony.updateIMU(sensor_group.orientation.as_numpy_array(),
                                sensor_group.gyro.sensor_data(),
                                sensor_group.acc.sensor_data())
            print(q)
            sensor_group.set_current_orientation(q)

            if iteration < 35:
                print(f'. . .')
                verbose = True
                continue

            if not buf.is_filled():
                buf.push(q.to_euler())
                verbose = True
                continue

            if not buf.optimal:
                posture.set_optimal_position(buf.optimal_position())

        # main logic is within this function
            # posture.check_current_posture(q)
        # x, y, z = q.as_euler()
        # outfile.write(f'{time.time()}, {x}, {y}, {z}\n')

        # some pygame events that should be handled here
        # event = pygame.event.poll()
        # if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
        #     break
        # pygame.display.flip()
        # vis.draw(*q.to_euler())

    # outfile.close()

if __name__ == '__main__':
    # main()
    port = establish_connection()
    for i in range(20):
        get_sensor_data(port, (SensorGroup(), SensorGroup()))

