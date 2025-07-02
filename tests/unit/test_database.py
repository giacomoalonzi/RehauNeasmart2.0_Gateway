"""Unit tests for database module"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from database import DatabaseManager, InMemoryFallback, DatabaseException, DatabaseOperationError


class TestInMemoryFallback:
    """Test InMemoryFallback functionality"""
    
    def test_set_and_get(self):
        """Test basic set and get operations"""
        fallback = InMemoryFallback()
        fallback.set(100, 42)
        assert fallback.get(100) == 42
    
    def test_get_nonexistent(self):
        """Test getting non-existent key"""
        fallback = InMemoryFallback()
        assert fallback.get(999) == 0
    
    def test_get_all(self):
        """Test getting all values"""
        fallback = InMemoryFallback()
        fallback.set(1, 10)
        fallback.set(2, 20)
        fallback.set(3, 30)
        
        all_values = fallback.get_all_data()
        assert all_values == {1: 10, 2: 20, 3: 30}
    
    def test_clear(self):
        """Test clearing all data"""
        fallback = InMemoryFallback()
        fallback.set(1, 10)
        fallback.set(2, 20)
        
        fallback.clear()
        assert fallback.get_all_data() == {}


class TestDatabaseManager:
    """Test DatabaseManager functionality"""
    
    def setup_method(self):
        """Setup test database"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db_path = self.temp_file.name
        self.temp_file.close()
    
    def teardown_method(self):
        """Cleanup test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_initialization(self):
        """Test database manager initialization"""
        db = DatabaseManager(self.db_path)
        assert db.db_path == self.db_path
        assert db._fallback is not None
        assert db._connection_healthy is True
    
    def test_set_and_get(self):
        """Test basic database operations"""
        db = DatabaseManager(self.db_path)
        
        # Set value
        db.set_register(1000, 123)
        
        # Get value
        value = db.get_register(1000)
        assert value == 123
    
    def test_fallback_on_error(self):
        """Test fallback mechanism when database fails"""
        db = DatabaseManager(self.db_path, enable_fallback=True)
        
        # Set value in database first
        db.set_register(500, 999)
        
        # Clear the fallback to ensure it's empty
        db._fallback._data.clear()
        
        # Simulate database failure by patching _execute_with_retry to always return None
        def mock_execute_with_retry(operation, *args, **kwargs):
            return None
        
        with patch.object(db, '_execute_with_retry', side_effect=mock_execute_with_retry):
            # Should fall back to in-memory storage (which is empty)
            value = db.get_register(500)
            assert value == 0  # Should get default from empty fallback
            
            # Set a value while db is down - should go to fallback
            db.set_register(501, 888)
            assert db._fallback.get(501) == 888
    
    def test_get_status(self):
        """Test status reporting"""
        db = DatabaseManager(self.db_path)
        status = db.get_status()
        
        assert 'healthy' in status
        assert 'using_fallback' in status
        assert 'db_entries' in status
        assert 'fallback_entries' in status
        assert status['healthy'] is True
        assert status['using_fallback'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 