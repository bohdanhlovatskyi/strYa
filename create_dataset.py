import serial
from strYa.adts import PosturePosition

posture = PosturePosition()

def from_port_to_file(posture: PosturePosition, filename: str) -> None:
    SENSOR_GROUP_SEPARATOR = '|'
    SENSOR_SEPARATOR = '; '
    COORDINATE_SEPARATOR = ', '
    
    port = posture.establish_connection()

    while True:
        line = port.readline()
        print(line)    
        try:      
            data = line.decode('utf-8').rstrip('\r\n').split(SENSOR_GROUP_SEPARATOR)      
        except AttributeError:    
            raise ValueError('The data cannot be readen')     
        if len(data) != posture.num_of_groups: # if there is not enought data  for 4 sensors      
            raise ValueError('Number of data that is read does not match with the number of given sensor groups to read into')     

        for_obj_data = []     
        for line, sensor_group in zip(data, posture.sensor_groups): 
            try:      
                acc, gyro = line.split(SENSOR_SEPARATOR)      
            except ValueError:    
                return    
            # time is saved at the time of creation of an object      
            acc = [round(float(i), 2) for i in acc.split(COORDINATE_SEPARATOR)  ] 
            gyro = [round(float(i), 2) for i in gyro.split(COORDINATE_SEPARATOR)]     
            # print(sensor_group.name, acc, gyro)     

            # print(acc, gyro)      

if __name__ == '__main__':
    from_port_to_file(posture, 'test.txt')
