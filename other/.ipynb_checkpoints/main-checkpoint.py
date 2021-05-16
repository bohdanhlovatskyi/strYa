'''
Script module
'''
import csv
from time import time
from strYa.adts import SensorGroup, Accelerometer,\
                        Gyro, Buffer, QuaternionContainer,\
                        PosturePosition

def main(file_name=None) -> None:
    '''
    Script function
    '''

    # creates an instance of posture position class, which
    # allocates memory for 4 sensors (combined in two sensor groups)
    posture = PosturePosition()
    port = posture.establish_connection()
    file_csv = open(file_name, 'w')
    writer = csv.writer(file_csv)
    names_of_columns = ['human_time', 'computer_time', 'x_acc_1', 'y_acc_1', 'z_acc_1', 'x_gyro_1', 'y_gyro_1', 'z_gyro_1',\
        'x_acc_2', 'y_acc_2', 'z_acc_2', 'x_gyro_2', 'y_gyro_2', 'z_gyro_2']
    writer.writerow(names_of_columns)
    # file.write(', '.join(names_of_columns) + '\n')
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



# def main(file_name=None) -> None:
#     '''
#     Script function
#     '''

#     # creates an instance of posture position class, which
#     # allocates memory for 4 sensors (combined in two sensor groups)
#     posture = PosturePosition()
#     port = posture.establish_connection()
#     file_csv = open(file_name, 'w')
#     writer = csv.writer(file_csv)
#     names_of_columns = ['computer_time', 'x1', 'y1', 'z1', 'x2', 'y2', 'z2']
#     writer.writerow(names_of_columns)
#     # file.write(', '.join(names_of_columns) + '\n')
#     iteration: int = 0  
#     while True:
#         iteration += 1

#         posture.get_sensor_data(port, writer)
#         if not posture.lower_sensor_group.gyro.settings:
#             # waits for bias that will be then applied to each element
#             print('. . .')
#             continue
#         orientations = []
#         for sensor_group in posture.sensor_groups:
#             # skips some iteration so to the sensors could stabilise
#             if iteration < 100:
#                 sensor_group.count_orientation(only_count=True)
#             else:
#                 sensor_group.count_orientation()
#                 orientations += sensor_group.orientation.to_euler()
#             try:
#                 # port in which we will write in case if the posture is bad
#                 sensor_group.check_current_posture(port=port)
#             except TypeError: # while optimal position is not
#                 # calculated typeerror will be raised by check current pos func
#                 continue
#         if orientations:
#             print(orientations)
#             writer.writerow([time()] + orientations)


def process(raw_data):
    posture = PosturePosition()
    iteration: int = 0  
    while True:
        iteration += 1

        if not posture.lower_sensor_group.gyro.settings:
            sensor_group.gyro.set_values(gyro)
            sensor_group.acc.set_values(acc)
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

# if __name__ == '__main__':
#     main('steady.csv')
