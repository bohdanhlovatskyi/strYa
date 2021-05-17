'''
Posture-data-receiving-implementaiton-free implementation of its analysis.
Analyser class is an convenient analysis function storage.
Its main function - check mode - prints out the logs on the
current posture position.
'''

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import List

class Analyzer:
    '''
    Analyser class. Should be created once in order to keep track of the user
    posture description. Should be related to other classes as an agregator class

    Main function is check_mode, which is based on some amount of static methods,
    that could be also useful for testing the system
    '''

    def __init__(self) -> None:
        '''
        Contains attributes that would be used as verboses
        '''

        self.info_on_user: defaultdict = defaultdict(int)
        
    def __read_data(self, path: str) -> List[List[float]]:
        '''
        Prepapares some lists of data from dataset. Is useful if
        onw wants to faslty get the stats on whole dataset (in a 
        wrapper function)
        '''

        #data frame from rounded data file
        df = pd.read_csv(path)
        rounded = np.round(df)

        #find optimal and delete it from data frame
        optimal = df.tail(1)
        print(optimal)
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
    def steady(orient_1: List[float], orient_2: List[float]) -> bool:
        '''
        Determines whether the posture of user is
        ok in the current moment of time
        '''

        for orientation in [orient_1, orient_2]:
            for axis in orientation:
                if abs(axis) > 5:
                    return False
        return True

    @staticmethod
    def forward_rotation(orient_1: List[float], orient_2: List[float]) -> bool:
        '''
        Checks whether the user bent down (so not to count it
        as a bad posture)
        '''

        y1, y2 = orient_1[1], orient_2[1]
        if 30 < abs(y1) < 70 and 30 < abs(y2) < 70:
            if abs(y1-y1) < 20:
                return True
        return False

    @staticmethod
    def forward_tilt(orient_1: List[float], orient_2: List[float]) -> bool:
        '''
        Checks whehter the user over-bends to the side
        '''

        y1 = orient_1[1]
        y2 = orient_2[1]
        if 10 < abs(y1) < 25 and abs(y2) < 7:
            return True
        #check sitting
        if 10 < abs(y1) < 15 and 25 < abs(y2) < 30:
            return True
        return False

    @staticmethod
    def side_tilt(orient_1: List[float], orient_2: List[float]) -> bool:      
        '''
        Checks whehter the user over-bends to the side
        '''

        x1 = orient_1[0]
        x2 = orient_2[0]
        if 10 < abs(x1) < 30 or 10 < abs(x2) < 30:
                return True
        return False
    

    def check_mode(self, *args) -> None:
        '''
        Main funciton of class. Checks current posture represented in angles for
        each type of analyser-function and print out the trend on the screen.
        '''

        upper_sensor_group, lower_sensor_group = args
        self.info_on_user['num_of_iterations'] += 1
        funcs = [self.steady, self.forward_rotation,  self.forward_tilt, self.side_tilt]

        for func in funcs:
            if not func(upper_sensor_group, lower_sensor_group):
                continue

            self.info_on_user[func.__name__] += 1
            print(f"On {self.info_on_user['num_of_iterations']} iteration, the trend in position is {func.__name__}")
            return
        # print(f"On {self.info_on_user['num_of_iterations']} iteration, the posture seems OK")


    def check_data(self, path):
        '''
        Function to check data from file
        '''

        x1, y1, x2, y2 = self.__read_data(path)
        for i in range(len(x1)):
            self.check_mode((x1[i], y1[i]), (x2[i], y2[i]))


if __name__ == '__main__':
    analyze = Analyzer()
    analyze.check_data('datasets/angles/angles_side_tilt.csv')
