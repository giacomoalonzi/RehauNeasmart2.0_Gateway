import unittest
import math
from dpt_9001 import (
    pack_dpt9001, unpack_dpt9001, DPT9001Error, DPT9001ValidationError,
    is_valid_dpt9001_value, get_dpt9001_range, DPT9001_MIN_VALUE, DPT9001_MAX_VALUE
)


class TestDPT9001(unittest.TestCase):

    def test_pack_and_unpack(self):
        # Test a range of values
        test_values = [-671088.64, -5000.0, 0.0, 5000.0, 670760.96]
        for value in test_values:
            with self.subTest(value=value):
                encoded = pack_dpt9001(value)
                decoded = unpack_dpt9001(encoded)
                self.assertAlmostEqual(decoded, value, delta=2.5)

    def test_out_of_range(self):
        # Test values out of range
        with self.assertRaises(DPT9001ValidationError):
            pack_dpt9001(700000.0)
        with self.assertRaises(DPT9001ValidationError):
            pack_dpt9001(-700000.0)

    def test_invalid_input(self):
        # Test invalid input types
        with self.assertRaises(TypeError):
            pack_dpt9001("invalid")
        with self.assertRaises(TypeError):
            unpack_dpt9001("invalid")
    
    def test_nan_and_infinity(self):
        # Test NaN and infinity handling
        with self.assertRaises(DPT9001ValidationError):
            pack_dpt9001(float('nan'))
        with self.assertRaises(DPT9001ValidationError):
            pack_dpt9001(float('inf'))
        with self.assertRaises(DPT9001ValidationError):
            pack_dpt9001(float('-inf'))
    
    def test_validation_functions(self):
        # Test is_valid_dpt9001_value function
        self.assertTrue(is_valid_dpt9001_value(0.0))
        self.assertTrue(is_valid_dpt9001_value(100.0))
        self.assertTrue(is_valid_dpt9001_value(-100.0))
        self.assertFalse(is_valid_dpt9001_value(700000.0))
        self.assertFalse(is_valid_dpt9001_value(-700000.0))
        self.assertFalse(is_valid_dpt9001_value(float('nan')))
        self.assertFalse(is_valid_dpt9001_value(float('inf')))
        self.assertFalse(is_valid_dpt9001_value("invalid"))
        
        # Test get_dpt9001_range function
        min_val, max_val = get_dpt9001_range()
        self.assertEqual(min_val, DPT9001_MIN_VALUE)
        self.assertEqual(max_val, DPT9001_MAX_VALUE)
    
    def test_unpack_validation(self):
        # Test unpack validation
        with self.assertRaises(DPT9001ValidationError):
            unpack_dpt9001(-1)
        with self.assertRaises(DPT9001ValidationError):
            unpack_dpt9001(0x10000)  # 65536, out of 16-bit range


if __name__ == "__main__":
    unittest.main()