import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

def plot_timeline(file_name, path):
    #data frame from rounded data file
    new = file_name.split('/')[-1]
    new = new.split('.')[0][7:] + '_timeline.png'
    new = path + new
    df = pd.read_csv(path + file_name)
    rounded = np.round(df)

    #find optimal and delete it from data frame
    optimal = df.tail(1)
    df = df.head(-1)

    #find all par for graphs
    time = df['computer_time']

    #plotting
    fig, (ax0, ax1, ax2, ax3) = plt.subplots(4, 1)
    ax0.plot(time, df['x1'].tolist())
    ax0.set_title('x1')

    ax1.plot(time, df['y1'].tolist())
    ax1.set_title('y1')

    ax2.plot(time, df['x2'].tolist())
    ax2.set_title('x2')

    ax3.plot(time, df['y2'].tolist())
    ax3.set_title('y2')

    fig.subplots_adjust(hspace=0.5)

    plt.show()
    #plt.savefig(new)