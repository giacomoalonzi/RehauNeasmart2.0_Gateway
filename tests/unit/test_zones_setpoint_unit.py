#!/usr/bin/env python3

import pytest
from unittest.mock import Mock, patch
from app_factory import create_app
from models.zone_models import ZoneRequest, ZoneData


class TestZonesSetpointUnit:
    """Unit tests for zones setpoint functionality with mocked dependencies."""
    
    @pytest.fixture(autouse=True)
    def setup_test(self):
        """Setup test environment with mocked Modbus context."""
        # Create test app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Test endpoint URL
        self.zone_url = "/api/zones/1/2"
        
        # Mock Modbus context
        self.mock_context = Mock()
        self.mock_context.__getitem__.return_value = Mock()
        
        # Mock the app's Modbus context
        with patch.object(self.app, 'config') as mock_config:
            mock_config.__getitem__.side_effect = lambda key: {
                'MODBUS_CONTEXT': self.mock_context,
                'SLAVE_ID': 1
            }.get(key)
    
    def test_setpoint_request_validation(self):
        """Test ZoneRequest validation for setpoint."""
        # Valid setpoint
        valid_request = ZoneRequest(setpoint=20)
        is_valid, error_msg = valid_request.validate()
        assert is_valid, f"Valid setpoint should pass validation: {error_msg}"
        
        # Invalid setpoint type
        invalid_request = ZoneRequest(setpoint="invalid")
        is_valid, error_msg = invalid_request.validate()
        assert not is_valid, "Invalid setpoint should fail validation"
        assert "invalid setpoint" in error_msg.lower()
        
        # Empty request
        empty_request = ZoneRequest()
        is_valid, error_msg = empty_request.validate()
        assert not is_valid, "Empty request should fail validation"
        assert "one of state or setpoint need to be specified" in error_msg
    
    def test_zone_data_model(self):
        """Test ZoneData model serialization."""
        zone_data = ZoneData(
            state=1,
            setpoint=20.0,
            temperature=22.5,
            relative_humidity=45
        )
        
        data_dict = zone_data.to_dict()
        
        assert data_dict["state"] == 1
        assert data_dict["setpoint"] == 20.0
        assert data_dict["temperature"] == 22.5
        assert data_dict["relativeHumidity"] == 45  # camelCase for frontend
    
    @patch('services.zone_service.ZoneService')
    def test_setpoint_endpoint_mock(self, mock_zone_service):
        """Test setpoint endpoint with mocked service."""
        # Setup mock
        mock_service_instance = Mock()
        mock_zone_service.return_value = mock_service_instance
        
        # Mock successful validation
        mock_service_instance.validate_zone_params.return_value = (True, "")
        
        # Mock successful update
        mock_service_instance.update_zone_data.return_value = (
            True, 
            "Zone updated successfully", 
            [12345]  # Mock DPT 9001 setpoint
        )
        
        # Test POST request
        setpoint_data = {"setpoint": 20}
        response = self.client.post(
            self.zone_url,
            json=setpoint_data,
            content_type='application/json'
        )
        
        assert response.status_code == 202
        response_data = response.get_json()
        assert response_data["message"] == "Zone updated successfully"
        assert "dpt_9001_setpoint" in response_data
    
    @patch('services.zone_service.ZoneService')
    def test_get_zone_data_mock(self, mock_zone_service):
        """Test GET zone data with mocked service."""
        # Setup mock
        mock_service_instance = Mock()
        mock_zone_service.return_value = mock_service_instance
        
        # Mock successful validation
        mock_service_instance.validate_zone_params.return_value = (True, "")
        
        # Mock zone data
        mock_zone_data = ZoneData(
            state=1,
            setpoint=20.0,
            temperature=22.5,
            relative_humidity=45
        )
        mock_service_instance.get_zone_data.return_value = mock_zone_data
        
        # Test GET request
        response = self.client.get(self.zone_url)
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        assert response_data["state"] == 1
        assert response_data["setpoint"] == 20.0
        assert response_data["temperature"] == 22.5
        assert response_data["relativeHumidity"] == 45


if __name__ == "__main__":
    # Run the test directly
    test_instance = TestZonesSetpointUnit()
    test_instance.setup_test()
    test_instance.test_setpoint_request_validation()
    test_instance.test_zone_data_model()
    print("✅ Unit tests completed successfully!")
