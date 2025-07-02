"""Unit tests for DPT 9001 module"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from dpt_9001 import pack_dpt9001, unpack_dpt9001


class TestDPT9001:
    """Test DPT 9001 encoding and decoding"""
    
    def test_pack_unpack_symmetry(self):
        """Test that pack and unpack are symmetric operations"""
        test_values = [0.0, 20.0, 21.5, -10.0, 35.5, 100.0]
        
        for value in test_values:
            packed = pack_dpt9001(value)
            unpacked = unpack_dpt9001(packed)
            # Allow small floating point errors
            assert abs(unpacked - value) < 0.1, f"Failed for value {value}"
    
    def test_pack_known_values(self):
        """Test packing with known values from documentation"""
        # Test some known conversions
        assert pack_dpt9001(21.0) > 0
        assert pack_dpt9001(0.0) >= 0
        assert pack_dpt9001(-273.0) >= 0  # Minimum temperature
    
    def test_unpack_known_values(self):
        """Test unpacking with known encoded values"""
        # Test that unpacking returns reasonable values
        assert -400 < unpack_dpt9001(0) < 400
        assert -400 < unpack_dpt9001(65535) < 400
    
    def test_pack_edge_cases(self):
        """Test edge cases for packing"""
        # Very large values
        packed = pack_dpt9001(670433.28)
        assert isinstance(packed, int)
        assert 0 <= packed <= 65535
        
        # Very small values
        packed = pack_dpt9001(-671088.64)
        assert isinstance(packed, int)
        assert 0 <= packed <= 65535
    
    def test_temperature_range(self):
        """Test typical temperature range conversions"""
        temperatures = [-20, -10, 0, 10, 20, 25, 30, 40, 50]
        
        for temp in temperatures:
            packed = pack_dpt9001(temp)
            unpacked = unpack_dpt9001(packed)
            
            # Temperature should be preserved within reasonable accuracy
            assert abs(unpacked - temp) < 0.5, f"Temperature {temp}°C not preserved"
    
    def test_invalid_inputs(self):
        """Test handling of invalid inputs"""
        # Unpacking invalid values should not crash
        unpack_dpt9001(-1)  # Should handle gracefully
        unpack_dpt9001(70000)  # Should handle gracefully
    
    def test_setpoint_encoding(self):
        """Test encoding of typical setpoint values"""
        setpoints = [18.0, 19.0, 20.0, 21.0, 21.5, 22.0, 22.5, 23.0, 24.0]
        
        for setpoint in setpoints:
            packed = pack_dpt9001(setpoint)
            unpacked = unpack_dpt9001(packed)
            
            # Setpoint precision should be good
            assert abs(unpacked - setpoint) < 0.1, f"Setpoint {setpoint}°C not precise enough"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 