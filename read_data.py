import ahrs
import numpy as np
import serial

from visualisation import *

madgwick_obj = ahrs.filters.Madgwick()
Q = np.array([1., 0., 0., 0.])

def process_raw_data(data):
    data = data.split(';')
    #print(data)
    gyro_data = data[0].split()
    acc_data = data[1].split()
    mag_data = data[2].split()
    #print(gyro_data, acc_data, mag_data)
    for i in range(3):
        gyro_data[i] = float(gyro_data[i])
        acc_data[i] = float(acc_data[i])/1000
        mag_data[i] = float(mag_data[i])/100000
    return np.array(gyro_data), np.array(acc_data), np.array(mag_data)


if __name__ == "__main__":
    port = serial.Serial('COM3', 9600)
    while True:
        Q = main(port, Q)
