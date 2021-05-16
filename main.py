'''
Script module

TODO: these should be merged into one function
TODO: check current posture block is obviously bad one,
should work with analyser class
'''
import csv
from time import time, sleep
from strYa.adts import SensorGroup, Accelerometer,\
                        Gyro, Buffer, QuaternionContainer,\
                        PosturePosition
from strYa.analyser import Analyzer

COLUMNS_NAMES = ['human_time', 'computer_time', 'x_acc_1', 'y_acc_1', 'z_acc_1', 'x_gyro_1', 'y_gyro_1', 'z_gyro_1',\
        'x_acc_2', 'y_acc_2', 'z_acc_2', 'x_gyro_2', 'y_gyro_2', 'z_gyro_2']

def main(from_file: str = None, to_file: str = None) -> None:
    '''
    Script function. Allows to write the info info file, if the filename is
    specified.

    Has two modes of working:
    - direct when the user uses the devise that transmits some data
    through the serial port
    - if the from_file param is specified, reads data from datasets
    and displays in the terminal how the system would behave with
    such measurements. Useful for degub and test writing
    '''
    posture = PosturePosition()
    port = posture.establish_connection()
    if to_file:
        file_csv = open(to_file, 'w')
        writer = csv.writer(file_csv)
        names_of_columns = ['human_time', 'computer_time', 'x_acc_1', 'y_acc_1', 'z_acc_1', 'x_gyro_1', 'y_gyro_1', 'z_gyro_1',\
            'x_acc_2', 'y_acc_2', 'z_acc_2', 'x_gyro_2', 'y_gyro_2', 'z_gyro_2']
        writer.writerow(names_of_columns)
    else:
        writer = None
    iteration: int = 0  
    while True:
        iteration += 1

        posture.get_sensor_data(port, writer)
        if not posture.lower_sensor_group.gyro.settings:
            # waits for bias that will be then applied to each element
            print('. . .')
            continue

        for sensor_group in posture.sensor_groups:

            # skips some iteration so to the sensors could stabilise
            if iteration < 100:
                sensor_group.count_orientation(only_count=True)
            else:
                sensor_group.count_orientation()
            try:
                # port in which we will write in case if the posture is bad
                sensor_group.check_current_posture(port=port)
            except TypeError: # while optimal position is not
                # calculated typeerror will be raised by check current pos func
                continue


def process(raw_data):
    posture = PosturePosition()
    iteration: int = 0  
    while True:
        iteration += 1

        if iteration < 100 and posture.num_of_bad_posture_measurements > 30:
            # function will end its execution and called one more time
            # so to make the calibration one more time
            print('Oooh, somethig has gone wrong... Wait for recalibration...')
            return -1

        # handles one iterational data receiving both from
        # serial port and user given file with dataset
        if not from_file:
            line = port.readline()
            data = posture.preprocess_data(line)
        else:
            sleep(0.1)
            try:
                line = file_data[iteration]
            except IndexError:
                break
            data = posture.preprocess_data_from_file(line)

        # because data from port works with different separator
        posture.set_sensor_data(data, file)
        if not posture.lower_sensor_group.gyro.settings:
            # waits for bias that will be then applied to each element
            print('. . .')
            continue

        for sensor_group in posture.sensor_groups:

            # skips some iteration so to the sensors could stabilise
            if iteration < 100:
                sensor_group.count_orientation(only_count=True)
            else:
                sensor_group.count_orientation()

            # this allows to see the comparison on both sensors
            try:
                sensor_group._check_current_posture_one_sensor(port=port)
            except TypeError:
                continue

if __name__ == '__main__':
    main()