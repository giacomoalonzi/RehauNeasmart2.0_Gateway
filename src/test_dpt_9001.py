import unittest
from dpt_9001 import pack_dpt9001, unpack_dpt9001, DPT9001Error


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
        with self.assertRaises(DPT9001Error):
            pack_dpt9001(700000.0)
        with self.assertRaises(DPT9001Error):
            pack_dpt9001(-700000.0)

    def test_invalid_input(self):
        # Test invalid input types
        with self.assertRaises(TypeError):
            pack_dpt9001("invalid")
        with self.assertRaises(TypeError):
            unpack_dpt9001("invalid")


if __name__ == "__main__":
    unittest.main()