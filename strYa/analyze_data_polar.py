from math import radians
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

def plot_polar(file_name, path):
     #data frame from rounded data file
     new = file_name.split('/')[-1]
     new = new.split('.')[0][7:] + '_polar.png'
     new = path + new
     df = pd.read_csv(path + file_name)
     rounded = np.round(df)

     #find optimal and delete it from data frame
     optimal = df.tail(1)
     df = df.head(-1)

     #find all par for graphs
     angles = []
     luxes = []
     for axis in ['x1', 'y1', 'x2', 'y2']:
          dups = rounded.pivot_table(index=[axis], aggfunc='size')
          angle = dups.axes[0].tolist()
          angle.append(optimal[axis])
          angle = [radians(a*10) for a in angle]
          lux = dups.tolist()
          lux.append(max(lux) * 1.5)
          angles.append(angle)
          luxes.append(lux)

     #plotting
     fig, ((ax0, ax1), (ax2, ax3)) = plt.subplots(2, 2, subplot_kw=dict(projection='polar'))
     ax0.plot(angles[0], luxes[0])
     ax0.set_theta_zero_location('N')
     ax0.set_title('x1')

     ax1.plot(angles[1], luxes[1])
     ax1.set_theta_zero_location('N')
     ax1.set_title('y1')

     ax2.plot(angles[2], luxes[2])
     ax2.set_theta_zero_location('N')
     ax2.set_title('x2')

     ax3.plot(angles[3], luxes[3])
     ax3.set_theta_zero_location('N')
     ax3.set_title('y2')

     fig.subplots_adjust(hspace=0.5)

     # plt.show()
     plt.savefig(new)
