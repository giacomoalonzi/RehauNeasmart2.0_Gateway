#!/usr/bin/env python3

"""
Unit tests for constants refactoring.

This module tests the new constants and data transformation utilities
to ensure backward compatibility and proper functionality.
"""

import unittest
import warnings
from src import const
from src.utils.data_transformer import (
    to_camel_case, to_snake_case, transform_dict_to_camel_case,
    transform_dict_to_snake_case, transform_api_response, apply_field_mappings
)


class TestConstantsRefactoring(unittest.TestCase):
    """Test cases for constants refactoring."""
    
    def test_old_constants_deprecation_warnings(self):
        """Test that old constants trigger deprecation warnings."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Test deprecated constants
            _ = const.get_NEASMART_BASE_SLAVE_ADDR()
            _ = const.get_BASE_ZONE_ID()
            _ = const.get_OUTSIDE_TEMP_REG()
            _ = const.get_FILTERED_OUTSIDE_TEMP_REG()
            
            # Check that warnings were issued
            self.assertEqual(len(w), 4)
            for warning in w:
                self.assertIsInstance(warning.message, DeprecationWarning)
    
    def test_new_constants_values(self):
        """Test that new constants have correct values."""
        # Test address calculation constants
        self.assertEqual(const.ZONE_BASE_ID_MULTIPLIER, 1200)
        self.assertEqual(const.ZONE_ID_MULTIPLIER, 100)
        
        # Test temperature register constants
        self.assertEqual(const.OUTSIDE_TEMPERATURE_ADDR, 7)
        self.assertEqual(const.FILTERED_OUTSIDE_TEMPERATURE_ADDR, 8)
        
        # Test slave address constants
        self.assertEqual(const.NEASMART_SLAVE_ADDRESS_PRIMARY, 240)
        self.assertEqual(const.NEASMART_SLAVE_ADDRESS_SECONDARY, 241)
    
    def test_state_mapping_constants(self):
        """Test state mapping constants."""
        # Test state mapping
        self.assertEqual(const.STATE_MAPPING[0], "off")
        self.assertEqual(const.STATE_MAPPING[1], "normal")
        self.assertEqual(const.STATE_MAPPING[2], "reduced")
        
        # Test reverse mapping
        self.assertEqual(const.STATE_MAPPING_REVERSE["off"], 0)
        self.assertEqual(const.STATE_MAPPING_REVERSE["normal"], 1)
        self.assertEqual(const.STATE_MAPPING_REVERSE["reduced"], 2)
    
    def test_mode_mapping_constants(self):
        """Test mode mapping constants."""
        # Test mode mapping
        self.assertEqual(const.MODE_MAPPING[0], "off")
        self.assertEqual(const.MODE_MAPPING[1], "auto")
        self.assertEqual(const.MODE_MAPPING[2], "heating")
        
        # Test reverse mapping
        self.assertEqual(const.MODE_MAPPING_REVERSE["off"], 0)
        self.assertEqual(const.MODE_MAPPING_REVERSE["auto"], 1)
        self.assertEqual(const.MODE_MAPPING_REVERSE["heating"], 2)
    
    def test_zone_address_calculation(self):
        """Test zone address calculation with new constants."""
        base_id = 1
        zone_id = 5
        
        # Calculate using new constants
        new_addr = (base_id - 1) * const.ZONE_BASE_ID_MULTIPLIER + zone_id * const.ZONE_ID_MULTIPLIER
        
        # Calculate using old constants (should be same)
        old_addr = (base_id - 1) * const.NEASMART_BASE_SLAVE_ADDR + zone_id * const.BASE_ZONE_ID
        
        self.assertEqual(new_addr, old_addr)
        self.assertEqual(new_addr, 500)  # Expected result


class TestDataTransformation(unittest.TestCase):
    """Test cases for data transformation utilities."""
    
    def test_to_camel_case(self):
        """Test snake_case to camelCase conversion."""
        self.assertEqual(to_camel_case("operation_mode"), "operationMode")
        self.assertEqual(to_camel_case("outside_temperature"), "outsideTemperature")
        self.assertEqual(to_camel_case("filtered_outside_temperature"), "filteredOutsideTemperature")
        self.assertEqual(to_camel_case("relative_humidity"), "relativeHumidity")
    
    def test_to_snake_case(self):
        """Test camelCase to snake_case conversion."""
        self.assertEqual(to_snake_case("operationMode"), "operation_mode")
        self.assertEqual(to_snake_case("outsideTemperature"), "outside_temperature")
        self.assertEqual(to_snake_case("filteredOutsideTemperature"), "filtered_outside_temperature")
        self.assertEqual(to_snake_case("relativeHumidity"), "relative_humidity")
    
    def test_transform_dict_to_camel_case(self):
        """Test dictionary transformation to camelCase."""
        data = {
            "operation_mode": 1,
            "outside_temperature": 22.5,
            "nested_data": {
                "relative_humidity": 60
            }
        }
        
        expected = {
            "operationMode": 1,
            "outsideTemperature": 22.5,
            "nestedData": {
                "relativeHumidity": 60
            }
        }
        
        result = transform_dict_to_camel_case(data)
        self.assertEqual(result, expected)
    
    def test_transform_dict_to_snake_case(self):
        """Test dictionary transformation to snake_case."""
        data = {
            "operationMode": 1,
            "outsideTemperature": 22.5,
            "nestedData": {
                "relativeHumidity": 60
            }
        }
        
        expected = {
            "operation_mode": 1,
            "outside_temperature": 22.5,
            "nested_data": {
                "relative_humidity": 60
            }
        }
        
        result = transform_dict_to_snake_case(data)
        self.assertEqual(result, expected)
    
    def test_apply_field_mappings(self):
        """Test field mapping application."""
        data = {
            "operation_mode": 1,
            "outside_temperature": 22.5,
            "zone_id": 5
        }
        
        expected = {
            "operationMode": 1,
            "outsideTemperature": 22.5,
            "zoneId": 5
        }
        
        result = apply_field_mappings(data, reverse=False)
        self.assertEqual(result, expected)
    
    def test_apply_field_mappings_reverse(self):
        """Test reverse field mapping application."""
        data = {
            "operationMode": 1,
            "outsideTemperature": 22.5,
            "zoneId": 5
        }
        
        expected = {
            "operation_mode": 1,
            "outside_temperature": 22.5,
            "zone_id": 5
        }
        
        result = apply_field_mappings(data, reverse=True)
        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
