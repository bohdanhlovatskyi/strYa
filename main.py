'''
Script module
'''

from strYa.adts import SensorGroup, Accelerometer,\
                        Gyro, Buffer, QuaternionContainer,\
                        PosturePosition

def main() -> None:
    '''
    Script function
    '''

    # creates an instance of posture position class, which
    # allocates memory for 4 sensors (combined in two sensor groups)
    posture = PosturePosition()
    port = posture.establish_connection()

    iteration: int = 0  
    while True:
        iteration += 1

        posture.get_sensor_data(port)
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


if __name__ == '__main__':
    main()
