import serial
import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
import ahrs
from typing import List

PORTS = ['/dev/cu.usbserial-14120', '/dev/cu.usbserial-14140']


def process_raw_data(line: str) -> np.array:

    line = line.decode('utf-8').rstrip('\r\n').split('//')

    return np.array([__float_iter(subline) for subline in line])


def __float_iter(num_str: str, sep: str = '/') -> List[float]:
    out = []
    for char in num_str.split(sep):
        try:
            char = float(char)
        except ValueError:
            continue
        else:
            out.append(char)

    return np.array(out)

madgwick_obj = ahrs.filters.Madgwick()
Q = np.array([1., 0., 0., 0.])

if __name__ == '__main__':

    try:
        port = serial.Serial('/dev/cu.usbserial-14240', 9600)
    except serial.serialutil.SerialException:
        port = serial.Serial(PORTS[1], 9600)
    except:
        raise

    while True:
        data = process_raw_data(port.readline())
        try: # first measurment is not ok, this should be changed btw
            data[1][1]
        except IndexError:
            continue
        print(data)
        acc_data, mag_data, gyro_data = data
        Q = madgwick_obj.updateMARG(Q, gyr=gyro_data, acc=acc_data, mag=mag_data)
        print(Q)
