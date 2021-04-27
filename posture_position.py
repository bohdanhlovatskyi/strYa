'''
Class for analysing dataset. Will be used in analytics
presented to user

! There is a point to calculate a middle value from three sensors
that would be useful to determine movement and so on.
'''

from typing import List, Tuple
from adts import Orientation

class PosturePosition:

    def __init__(self, data: List[Orientation]):
        self.data = data

    @staticmethod
    def _find_change(prev_orientation: Orientation,
                     current: Orientation) ->
                     Tuple[float, Tuple[float]]:
        '''
        Determines change between two orientation measurements.

        Returns tuple with (percentage_of_change, (relative change vector values))

        '''

        pass

    @staticmethod
    def _detects_movement(prev_orientation: Orientation,
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

