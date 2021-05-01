import serial

try:
    port = serial.Serial('/dev/cu.usbserial-14240', 9600)
except serial.serialutil.SerialException:
    port = serial.Serial('/dev/cu.usbserial-14120', 9600)
except:
    raise

def read_into_file(path: str, num_of_lines: int = 100, skip_first: int = 25, sep: str = ', ') -> None:

    for i in range(skip_first):
        port.readline()

    data =  []
    for i in range(num_of_lines):
        line = port.readline()
        line = line.decode('utf-8').rstrip('\r\n').split(sep)
        print(i, line)
        data.append(line)

    with open(path, 'w') as outfile:
        for line in data:
            outfile.write(', '.join([elm for elm in line]) + '\n') 

if __name__ == '__main__':
    read_into_file('test_set_4.txt', num_of_lines=50, skip_first=10, sep=', ')
