#!/usr/bin/env python3

import time
import requests
import pytest
from app_factory import create_app


class TestZonesSetpoint:
    """Integration tests for zones setpoint functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_test(self):
        """Setup test environment."""
        # Create test app with test configuration
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Test endpoint URL
        self.zone_url = "/api/zones/1/2"
        
    def test_setpoint_set_and_get(self):
        """
        Test setting a setpoint to 20 and verifying it after 10 seconds.
        
        This test:
        1. Sets setpoint to 20 using POST
        2. Waits 10 seconds
        3. Gets zone data using GET
        4. Verifies setpoint is 20
        """
        # Step 1: Set setpoint to 20
        setpoint_data = {
            "setpoint": 20
        }
        
        response = self.client.post(
            self.zone_url,
            json=setpoint_data,
            content_type='application/json'
        )
        
        # Verify POST response
        assert response.status_code == 202, f"Expected status 202, got {response.status_code}: {response.get_data(as_text=True)}"
        
        response_data = response.get_json()
        assert "message" in response_data, "Response should contain message"
        assert response_data["message"] == "Zone updated successfully", "Unexpected message"
        
        # Step 2: Wait 10 seconds
        print("Waiting 10 seconds before checking setpoint...")
        time.sleep(10)
        
        # Step 3: Get zone data
        response = self.client.get(self.zone_url)
        
        # Verify GET response
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}: {response.get_data(as_text=True)}"
        
        zone_data = response.get_json()
        
        # Step 4: Verify setpoint is 20
        assert "setpoint" in zone_data, "Response should contain setpoint field"
        assert zone_data["setpoint"] == 20, f"Expected setpoint 20, got {zone_data['setpoint']}"
        
        print(f"✅ Test passed! Setpoint successfully set to {zone_data['setpoint']}")
        
        # Additional verification - check that other fields are present
        expected_fields = ["state", "setpoint", "temperature", "relativeHumidity"]
        for field in expected_fields:
            assert field in zone_data, f"Response should contain {field} field"
        
        print(f"✅ All expected fields present: {list(zone_data.keys())}")
    
    def test_setpoint_validation(self):
        """Test setpoint validation with invalid values."""
        # Test with invalid setpoint type
        invalid_data = {
            "setpoint": "invalid"
        }
        
        response = self.client.post(
            self.zone_url,
            json=invalid_data,
            content_type='application/json'
        )
        
        assert response.status_code == 400, "Should return 400 for invalid setpoint"
        
        response_data = response.get_json()
        assert "error" in response_data, "Error response should contain error field"
    
    def test_zone_parameters_validation(self):
        """Test zone parameter validation."""
        # Test with invalid base_id
        invalid_url = "/api/zones/5/2"  # base_id > 4
        
        response = self.client.get(invalid_url)
        assert response.status_code == 400, "Should return 400 for invalid base_id"
        
        # Test with invalid zone_id
        invalid_url = "/api/zones/1/13"  # zone_id > 12
        
        response = self.client.get(invalid_url)
        assert response.status_code == 400, "Should return 400 for invalid zone_id"
    
    def test_empty_request_validation(self):
        """Test validation with empty request body."""
        response = self.client.post(
            self.zone_url,
            json={},
            content_type='application/json'
        )
        
        assert response.status_code == 400, "Should return 400 for empty request"
        
        response_data = response.get_json()
        assert "error" in response_data, "Error response should contain error field"


if __name__ == "__main__":
    # Run the test directly
    test_instance = TestZonesSetpoint()
    test_instance.setup_test()
    test_instance.test_setpoint_set_and_get()
