'''
Script module

TODO: check current posture block is obviously bad one,
should work with analyser class
'''
import csv
from time import time, sleep
from typing import List, Tuple
from strYa.adts import SensorGroup, Accelerometer,\
                        Gyro, Buffer, QuaternionContainer,\
                        PosturePosition
from strYa.analyser import Analyzer

COLUMNS_NAMES = ['human_time', 'computer_time', 'x_acc_1', 'y_acc_1',\
            'z_acc_1', 'x_gyro_1', 'y_gyro_1', 'z_gyro_1', 'x_acc_2', \
            'y_acc_2', 'z_acc_2', 'x_gyro_2', 'y_gyro_2', 'z_gyro_2']

def main(from_file: str = None, to_file: str = None) -> None:
    '''
    Script function. Allows to write the info info file in txt format
    (containing row data that then would be useful for prototyping), 
    if the filename is specified.

    Has two modes of working:
    - direct when the user uses the devise that transmits some data
    through the serial port
    - if the from_file param is specified, reads data from datasets
    and displays in the terminal how the system would behave with
    such measurements. Useful for degub and test writing
    '''

    # creates an instance of posture position class, which
    # allocates memory for 4 sensors (combined in two sensor groups)
    posture = PosturePosition()
    analyser = Analyzer()

    if from_file:
        file = open(from_file)
        from_file_data = file.readlines()[1:]
        from_file_data = [line for line in from_file_data if line]
        port = None # so not to write separate handler of it later on
    else:
        port = posture.establish_connection()

    if to_file:
        # TODO: The keyboard interupt should handle its closing
        file = open(to_file, 'w')
        writer = csv.writer(file)
        writer.writerow(COLUMNS_NAMES)
    else:
        # so not to write separate handler of it later on
        writer = None

    iteration: int = 0  
    while True:
        iteration += 1

        # implemets some kind of recalibration
        # TODO: this should be rewritten when analyser class would be
        # implemented in in live code
        if iteration < 200 and posture.bad_posture_iters > 30:
            # function will end its execution and called one more time
            # so to make the calibration one more time
            print('Oooh, somethig has gone wrong... Wait for recalibration...')
            return -1

        if not from_file:
            line = port.readline()
            data = posture.preprocess_data(line)
        else:
            sleep(0.1) # because there are 200ms delays in data receiving from port
            try:
                line = from_file_data[iteration].rstrip()
                if not line: continue
            except IndexError:
                print(analyser.info_on_user)
                break
            data = posture.preprocess_data_from_file(line, sep=',')

        posture.set_sensor_data(data, writer)
        if not posture.lower_sensor_group.gyro.settings:
            # waits for bias that will be then applied to each element
            print('. . .')
            continue

        current_angles: List[Tuple[float]] = []
        for sensor_group in posture.sensor_groups:
            # skips some iteration so to the sensors could stabilise
            if iteration < 100:
                sensor_group.count_orientation(only_count=True)
            else:
                sensor_group.count_orientation()

            if sensor_group.has_optimal_position():
                # port in which we will write in case if the posture is bad
                # for test func: displays info about separate sensors groups
                # sensor_group.check_current_posture(port=port)
                current_angles.append(sensor_group.orientation.to_euler()[:-1])

        if not current_angles: continue
        analyser.check_mode(*current_angles)

if __name__ == '__main__':
    filename = 'datasets/row_data/side_tilt.csv'
    # filename = None
    # to_file = 'test.csv'
    to_file = None
    while main(from_file=filename, to_file=to_file) == -1:
        main(from_file=filename)
