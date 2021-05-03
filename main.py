import pygame
import math
import time
import serial
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

from ahrs.filters import Madgwick, Mahony
from typing import Tuple

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

def get_sensor_data(port: serial.Serial) -> SensorGroup:
    '''
    Gets info from sensors
    '''

    return __process_info(port.readline())

def __process_info(line: str, debug: bool = False) -> Tuple[Tuple[float]]:
    try:
        line = line.decode('utf-8').rstrip('\r\n').split(';')
    except AttributeError:
        line = line.rstrip('\r\n').split(';')

    try:
        acc, gyro = line
    except ValueError:
        return

    # time is saved at the time of creation of an object
    sep = ', ' if debug else ' '
    acc = [float(i) for i in acc.split(sep)]
    gyro = [float(i) for i in gyro.split(sep)]

    return acc, gyro

def get_data_from_file(path: str) -> SensorGroup:
    '''
    DEBUG: reads info from file as if it is sensor.
    '''

    with open(path) as infile:
        data = infile.readlines()

    for idx, line in enumerate(data):
        data[idx] = __process_info(line, debug=True)

    return data

def main(debug: bool = False):
    if not debug:
        port = establish_connection()
    else:
        data = get_data_from_file('euler_angles_3.txt')

    mahony = Mahony(frequency=5)
    q = QuaternionContainer([1, 0.0, 0.0, 0.0])

    posture = PosturePosition()

    vis = Visualiser()
    vis.main_init()

    buf = Buffer()
    calibration_buffer = Buffer()

    # outfile = open('euler_angles_3.txt', 'w')
    iteration: int = 0
    while True:
        iteration += 1

        acc, gyro = data[i] if debug else get_sensor_data(port)

        if not calibration_buffer.is_filled():
            calibration_buffer.push([*acc, *gyro])
            continue
        
        if not calibration_buffer.gyro_settings:
            print('Wait for it...')
            calibration_buffer.count_gyro_drift()

        # N.B it is important to process some quaternions here, because we
        # start from [1, 0, 0, 0] quaternion and therefore they need some
        # time to stabilize
        acc, gyro = Accelerometer(acc), Gyro(gyro, calibration_buffer.gyro_settings)
        q = QuaternionContainer(mahony.updateIMU(q.as_numpy_array(),
                                                 gyro.sensor_data(),
                                                 acc.sensor_data()))

        if iteration < 15 + calibration_buffer.size:
            print(f'. . .')
            continue

        if not buf.is_filled():
            buf.push(q.to_euler())
            continue

        if not buf.optimal:
            posture.set_optimal_position(buf.optimal_position())

        # main logic is within this function
        posture.check_current_posture(q)
        # x, y, z = q.as_euler()
        # outfile.write(f'{time.time()}, {x}, {y}, {z}\n')

        # some pygame events that should be handled here
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        pygame.display.flip()
        vis.draw(*q.to_euler())

    # outfile.close()

if __name__ == '__main__':
    main(debug=False)
