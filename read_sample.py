import serial
import numpy as np
import ahrs
from typing import List
from analyse_data import Gyroscope, OrientQuaternion


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

madgwick_obj = ahrs.filters.Madgwick()
Q = np.array([1., 0., 0., 0.])

if __name__ == '__main__':

    try:
        port = serial.Serial('/dev/cu.usbserial-14240', 9600)
    except serial.serialutil.SerialException:
        port = serial.Serial(PORTS[1], 9600)
    except:
        raise

    Qs = []
    gyro_datas = []
    for i in range(20):
        data = process_raw_data(port.readline())
        try: # first measurment is not ok, this should be changed btw
            data[1][1]
        except IndexError:
            continue
        print(data)
        acc_data, mag_data, gyro_data = data
        gyro_datas.append(gyro_data)
        # not sure whether this needs mora than one iteration data, need some testing
        Q = madgwick_obj.updateMARG(Q, gyr=gyro_data, acc=acc_data, mag=mag_data)
        Qs.append(Q)

    gyro = Gyroscope(gyro_data)
    q = OrientQuaternion(Qs)

