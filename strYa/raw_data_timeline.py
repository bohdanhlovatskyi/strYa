'''
Module that makes timeline graphs from csv data.
'''
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd


def plot_timeline(file_name):
    '''
    Makes timeline graphs from csv data.
    '''
    # data frame from rounded data file
    df = pd.read_csv(file_name)

    # find all par for graphs
    time = df['computer_time']

    # plotting
    fig, (x_acc_1, y_acc_1, x_gyro_1, y_gyro_1, x_acc_2,
          y_acc_2, x_gyro_2, y_gyro_2) = plt.subplots(8, 1)

    x_acc_1.plot(time, df['x_acc_1'].tolist())
    x_acc_1.set_title('x_acc_1')

    y_acc_1.plot(time, df['y_acc_1'].tolist())
    y_acc_1.set_title('y_acc_1')

    x_gyro_1.plot(time, df['x_gyro_1'].tolist())
    x_gyro_1.set_title('x_gyro_1')

    y_gyro_1.plot(time, df['y_gyro_1'].tolist())
    y_gyro_1.set_title('y_gyro_1')

    x_acc_2.plot(time, df['x_acc_2'].tolist())
    x_acc_2.set_title('x_acc_2')

    y_acc_2.plot(time, df['y_acc_2'].tolist())
    y_acc_2.set_title('y_acc_2')

    x_gyro_2.plot(time, df['x_gyro_2'].tolist())
    x_gyro_2.set_title('x_gyro_2')

    y_gyro_2.plot(time, df['y_gyro_2'].tolist())
    y_gyro_2.set_title('y_gyro_2')

    fig.subplots_adjust(hspace=0.5)

    plt.show()
    # plt.savefig(new)

# if __name__ == "__main__":
    # plot_timeline('walking.csv')
