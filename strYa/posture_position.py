'''
Class for analysing dataset. Will be used in analytics
presented to user

! There is a point to calculate a middle value from three sensors
that would be useful to determine movement and so on.
'''

from typing import List, Tuple
from adts import Orientation, SensorGroup
from ahrs import Quaternion

class PosturePosition:

    def __init__(self, data):
        self.data = data

    @staticmethod
    def _find_change(prev_orientation: Orientation,
                     current: Orientation) ->\
                     Tuple[float, Tuple[float]]:
        '''
        Determines change between two orientation measurements.

        Returns tuple with (percentage_of_change, (relative change vector values))

        '''

        pass

    @staticmethod
    def _detects_movement(prev_orientation: Orientation,\
                          current: Orientation, precision: int = 10) -> bool:
        '''
        determines whether object moves between two measurements.

        possible_usage: checks this for 10-15 measurement and
        if the majority the function return values are True,
        then the object is moving. This would be useful in determining
        time of sitting srteadily and so on
        '''

        change, _ = self._find_change(prev_orientation, current)

        if change > precision:
            return True 

        return False

    def __get_optimal_value(self) -> None:
        if not self.data.is_filled():
            raise ValueError()
        
        self.optimal_position = buf.optimal_value()

    def visualise_posture(self) -> None:
        '''
        Visualises the posture via matplotlib(???)
        '''

        pass

    def find_time_without_movement(self) -> float:
        pass

    def most_popular_position(self) -> Orientation:
        pass

    def recommendations(self) -> str:
        '''
        Prints out some information
        '''
        
        pass


class Buffer:

    def __init__(self, size: int = 10) -> None:
        self.positions = []
        self.size = size

    def add(self, pos: Orientation) -> None:
        self.positions.append(pos)

    def is_filled(self) -> bool:
        return len(self.positions) >= self.size

    def optimal_value(self) -> Orientation:
        pass

    def from_file(self, path: str ='test_set.txt', size: int = 100, sep: str = ', ') -> None:

        with open(path) as infile:
            lines = infile.readlines()

        for idx, line in enumerate(lines):
            line = line.rstrip().split(sep=sep)
            lines[idx] = [float(elm) for elm in line]

        return lines

'''
buf = pp.Buffer()
def plot_buf_from_file(buf: pp.Buffer, file_name: str, idx: int = 0) -> None:
    df = pd.DataFrame(buf.from_file(file_name))
    
    columns_mean: Dict[int, int] = {}
    for column in df.columns:
        columns_mean[column] = df[column].mean()
        
    for column in columns_mean:
        df[column] = df[column].apply(lambda x: x - columns_mean[column])
        
    pd.set_option('display.max_rows', 100)
    line1, line2 = df[idx].to_list(), [df[0].mean() for elm in df[idx]]
    # print(line1, line2)
    line3 = [(columns_mean[0] + line2[0])/4 for elm in line2]
    # print(line3)
    
    plt.plot(line1)
    plt.plot(line2)
    plt.plot(line3)
'''

if __name__ == '__main__':
    
    buf = Buffer()
    print(buf.from_file())
    # while not buf.is_filled():
        # acc, gyro, _ = read_data(filename='dataset.txt')
        # buf.add(Orientation(SensorGroup(acc, gyro)))
# 
    # pos_pos = PosturePosition(buf)
# 
    # while True:
        # acc, gyro, _ = read_data(filename='dataset.txt')
        # buf.pop(0)
        # orient = Orientation(SensorGroup(acc, gyro))
        # buf.append(orient)
