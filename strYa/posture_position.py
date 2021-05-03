'''
Class for analysing dataset. Will be used in analytics
presented to user

! There is a point to calculate a middle value from three sensors
that would be useful to determine movement and so on.
'''

from typing import List, Tuple
from datetime import datetime
from strYa.adts import *
from ahrs import Quaternion

class PosturePosition:

    def __init__(self) -> None:
        '''
        Should be used as container for certain variables that would be comfportable
        to use while analysing the user's posture
        '''

        self.optimal_position = None
        self.__iters_without_movement: int = 0

    @staticmethod
    def _find_change(prev_orientation: Tuple[float],
                     current: Tuple[float]) ->\
                     Tuple[float, Tuple[float]]:
        '''
        Determines change between two orientation measurements.

        Returns tuple with (percentage_of_change, (relative change vector values))

        '''

        pass

    @staticmethod
    def _detects_movement(prev_orientation: Tuple[float],\
                          current: Tuple[float], precision: int = 10) -> bool:
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

    def check_current_posture(self, orientation: QuaternionContainer) -> None:
        x, y, z = orientation.to_euler()
        # determine_bad_posture(q)
        if (abs(y) - abs(self.optimal_position[1])) > 10:
            print(f'Bad posture {datetime.now()}')
        if abs(x - self.optimal_position[0]) > 10:
            print(f'Bad horisontal posture {datetime.now()}')


    def set_optimal_position(self, optimal_position: Tuple[float]) -> None:
        self.optimal_position = optimal_position

    def visualise_posture(self) -> None:
        '''
        Visualises the posture via matplotlib(???)
        '''

        pass

    def find_time_without_movement(self) -> float:
        pass

    def most_popular_position(self) -> Tuple[float]:
        pass

    def recommendations(self) -> str:
        '''
        Prints out some information
        '''
        
        pass
