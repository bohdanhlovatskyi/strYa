'''
Posture-data-receiving-implementaiton-free implementation of its analysis.
Analyser class is an convenient analysis function storage.
Its main function - check mode - prints out the logs on the
current posture position.

TODO: make it work for online port data receivnig so to actually print
out the logs 
- write an init that will receive current state and print out its qualities
- it shoult though still work with one reading of dataset - and rreturing
all the stats on it - so to visualise it in dash or sth
- TODO: each of function should correspond to bool variable withing
a class in order to make then a log message in an convenient way
(we can get rid of ifs - function modify allocated variables within a class
and on each iteration they are changed and then via dicts can be created nice log)
'''

import pandas as pd
import numpy as np


class Analyzer:
        
    def read_data(self, path):
        #data frame from rounded data file
        df = pd.read_csv(path)
        rounded = np.round(df)

        #find optimal and delete it from data frame
        optimal = df.tail(1)
        x1_optimal = optimal['x1'].tolist()[0]
        y1_optimal = optimal['y1'].tolist()[0]
        # # print(x_optimal, y_optimal)
        #print(optimal)
        x2_optimal = optimal['x2'].tolist()[0]
        y2_optimal = optimal['y2'].tolist()[0]
        df = df.head(-1)

        #find all par for graphs
        time = df['computer_time'].tolist()
        start_time = time[0]
        time = [i-start_time for i in time]
        x1 = df['x1'].tolist()
        x1 = [i+x1_optimal for i in x1]
        y1 = df['y1'].tolist()
        y1 = [i-y1_optimal for i in y1]
        # z1 = df['z1'].tolist()

        x2 = df['x2'].tolist()
        x2 = [i+x2_optimal for i in x2]
        y2 = df['y2'].tolist()
        y2 = [i-y2_optimal for i in y2]
        # z2 = df['z2'].tolist()
        return x1, y1, x2, y2

    @staticmethod
    def steady(orient_1, orient_2):
        for orientation in [orient_1, orient_2]:
            for axis in orientation:
                if abs(axis) > 5:
                    return False
        return True
    @staticmethod
    def forward_rotation(orient_1, orient_2):
        y1 = orient_1[1]
        y2 = orient_2[1]
        if 30 < abs(y1) < 70 and 30 < abs(y2) < 70:
            if abs(y1-y1) < 20:
                return True
        return False
    @staticmethod
    def forward_tilt(orient_1, orient_2):
        y1 = orient_1[1]
        y2 = orient_2[1]
        if 10 < abs(y1) < 25 and abs(y2) < 7:
            return True
        #check sitting
        if 10 < abs(y1) < 15 and 25 < abc(y2) < 30:
            return True
        return False

    @staticmethod
    def side_tilt(orient_1, orient_2):      
        x1 = orient_1[0]
        x2 = orient_2[0]
        if 10 < abs(x1) < 30 or 10 < abs(x2) < 30:
                return True
        return False
    

    def check_mode(self, x1, y1, x2, y2):
        orient_1 = (x1, y1)
        orient_2 = (x2, y2)
        if self.steady(orient_1, orient_2):
            print('Steady.')
        if self.forward_rotation(orient_1, orient_2):
            print('Forward rotation.')
        elif self.forward_tilt(orient_1, orient_2):
            print('Forward tilt.')
        elif self.side_tilt(orient_1, orient_2):
            print('Side tilt')
        

    def check_data(self, path):
        x1, y1, x2, y2 = self.read_data(path)
        for i in range(len(x1)):
            self.check_mode(x1[i], y1[i], x2[i], y2[i])


if __name__ == '__main__':
    analyze = Analyzer()
    analyze.check_data('angles_sitting_2.csv')
