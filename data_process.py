import numpy as np
import matplotlib.pyplot as plt


class ProcessInfo:

    def __init__(self, filename: str) -> None:
        self.filename = filename
        if not self.filename:
            raise ValueError('You should specify file name')
        self.data = self.__read_data()

    def __read_data(self) -> np.matrix:

        with open(self.filename) as file:
            data = file.readlines()

        return list(map(np.matrix, data))

    def raw_acc_data(self):
        return [np.array(mtx[0]).flatten() for mtx in self.data]

    def raw_mgt_data(self):
        return [np.array(mtx[1]).flatten() for mtx in self.data]

    def raw_gyro_data(self):
        return [np.array(mtx[2]).flatten() for mtx in self.data]

    def show_two_dimesions(self, sensor: str, dimension: str):
        get_sensor_data = {'a': self.raw_acc_data, 'm': self.raw_mgt_data, 'g': self.raw_gyro_data}
        get_dimension = {'xy': [0, 1], 'yz': [1, 2], 'xz': [0, 2]}

        data = get_sensor_data[sensor]()
        dimension = get_dimension[dimension]
    
        data = [np.array([arr[dimension[0]], arr[dimension[1]]]) for arr in data]
        
        for idx, arr in enumerate(data):
            coord_1, _ = arr
            # 96/60 - n of point in one second
            plt.scatter(idx * 96/60, coord_1)
        plt.show()

if __name__ == '__main__':
    processor = ProcessInfo('data.txt')
    print(processor.show_two_dimesions('g', 'xy'))








    '''
    for mtx in data:
    xdata, ydata, zdata = mtx[0]

fig = plt.figure(figsize=(9, 6))
# Create 3D container
ax = plt.axes(projection = '3d')
# Visualize 3D scatter plot
for mtx in data:
    xdata, ydata, zdata = mtx[0]


    ax.scatter3D(xdata, ydata, zdata)
    # Give labels
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
# Save figure
plt.savefig('3d_scatter.png', dpi = 300);
    '''