'''
TODO: Tests for analyser, posture position and sensor group
'''

import unittest
import sys
sys.path.append('..')
import adts

class TestBuffer(unittest.TestCase):

    def setUp(self) -> None:
        self.buffer = adts.Buffer(size=25)
        for i in range(25):
            self.buffer.push((i, i, i))

    def test_is_filled(self):
        self.assertTrue(self.buffer.is_filled())

    def test_pushing(self):
        del_elm = self.buffer.data[0]
        self.buffer.push((26, 26, 26))
        new_elm = self.buffer.data[0]
        self.assertNotEqual(del_elm, new_elm)
        self.assertTrue(self.buffer.is_filled())

    def test_optimal_position(self):
        '''
        TODO: This will be depricated, because we will use comparisson via sin and cos
        '''

        # 12 - is a mean number from 0 to 24 included - mean is counted fine
        self.assertEqual(self.buffer.optimal_position(), [12, 12, 12])

    def test_gyro_drift_counting(self):
        # TODO: if we assume that it is ok to count mean for gyro, it works
        # thouhg it is worth discussing whether we actually need this mean or not
        self.assertEqual(self.buffer.count_gyro_drift(), (12, 12, 12))


# ---- there is no point in testing acc, because it is simply a container -----


class TestGyro(unittest.TestCase):

    def setUp(self) -> None:
        self.gyro = adts.Gyro()

    def test_set_values(self):
        for i in range(30):
            # to remember that gyro should take list, because
            # it will be then changed
            self.gyro.set_values([i, i, i])
        # tests that the bias is calculated correctly (as a mean)
        # TODO: in case switching to sins it won't work
        self.assertEqual(self.gyro.settings, (12, 12, 12))
        # tests that thebuffer is cleaned after the calibration is done
        with self.assertRaises(AttributeError):
            self.assertEqual(self.gyro.buffer.data)

    def test_process_values(self):
        for i in range(30):
            # in order for bufffer to calibrate
            self.gyro.set_values([i, i, i])
        # mean of the buffer - bias - is equal to [12, 12, 12]
        # checks that the buffer bias is applied to the measurements
        self.assertEqual(self.gyro.process_values([15, 15, 15]), [3, 3, 3])


class TestQuaternionContainer(unittest.TestCase):

    def setUp(self) -> None:
        self.orientation = adts.QuaternionContainer([1, 0, 0, 0])
    
    def test_to_euler(self):
        # zero quaternion of state is passed, so the euler angles should
        # also look in the same way
        self.assertEqual(self.orientation.to_euler(), (0, 0, 0))


class TestSensorGroup(unittest.TestCase):
    
    def setUp(self) -> None:
        self.sg = adts.SensorGroup('test_group')
        for i in range(40):
            self.sg.acc.set_values([i, i, i])
            self.sg.gyro.set_values([1, 1, 1])
            self.sg.count_orientation()

    # --- block of TODO funcs --- (should be changed after sin and cos would be rewritten)
    def test_count_orientation(self):
        # TODO: ??? IDK how to test this propeprly. For now this function
        # only works as an verbose that we did not broke anything
        self.assertEqual([int(elm) for elm in self.sg.optimal_position], [12, 10, 12])

    def test_deviation(self):
        self.assertEqual([int(elm) for elm in self.sg.deviation_from_optimal()], [32, 45, 101])


if __name__ == '__main__':
    unittest.main()
