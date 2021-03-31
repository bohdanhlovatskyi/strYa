import serial
import numpy as np
import ahrs
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d
from typing import List
from analyse_data import Gyroscope, OrientQuaternion

try:
    port = serial.Serial('/dev/cu.usbserial-14240', 9600)
except serial.serialutil.SerialException:
    port = serial.Serial('/dev/cu.usbserial-14120', 9600)
except:
    raise


madgwick_obj = ahrs.filters.Madgwick()
Q = np.array([1., 0., 0., 0.])


def process_raw_data(line: str, sep: str='//') -> np.array:
    # converts a given line from byte-string to str, removes some junk from it and splits by sep
    line = line.decode('utf-8').rstrip('\r\n').split(sep)

    return np.array([__float_iter(subline) for subline in line])


def __float_iter(num_str: str, sep: str = '/') -> List[float]:
    '''
    Converts string such as 123/123/123 into list of floats by sep
    '''

    out = []
    for char in num_str.split(sep):
        try:
            char = float(char)
        except ValueError:
            continue
        else:
            out.append(char)

    return np.array(out)


def animate(sensor: List[float]) -> None:
    '''
    Simple animation

    Bad realisation, but it is handy
    '''

    ax = plt.gca()
    plt.style.use('fivethirtyeight')

    time_values = range(len(sensor))

    sensor_xs, sensor_ys, sensor_zs = zip(*sensor)

    plt.cla()
    plt.plot(time_values[-20:], sensor_xs[-20:], linestyle='-', color='red')
    plt.plot(time_values[-20:], sensor_ys[-20:], linestyle='--', color='blue')
    plt.plot(time_values[-20:], sensor_zs[-20:], linestyle='solid', color='black')

    ax.legend(["x","y","z"])
    ax.set_xlabel("Time")
    ax.set_ylabel("Values for sensor")

    plt.draw()
    plt.pause(0.01)


if __name__ == '__main__':

    acc_data = []
    mag_data = []
    gyro_data = []
    Qs = []
    for i in range(100): # gets n measurments (can be replaces with while True loop)
        data = process_raw_data(port.readline())
        try: # first measurment is not ok, this should be changed btw
            data[1][1]
        except IndexError:
            continue
        # not sure whether this needs mora than one iteration data, needs some testing
        Qs.append([*Q])
        Q = madgwick_obj.updateMARG(Q, gyr=data[2], acc=data[0], mag=data[1])
        acc_data.append(data[0])
        mag_data.append(data[1])
        gyro_data.append(data[2])
        Qs_to_vis = [elm[1:] for elm in Qs]
        animate(Qs_to_vis)
