"""Unit tests for database module"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from database import DatabaseManager, InMemoryFallback, DatabaseError


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
        assert fallback.get(999) is None
    
    def test_get_all(self):
        """Test getting all values"""
        fallback = InMemoryFallback()
        fallback.set(1, 10)
        fallback.set(2, 20)
        fallback.set(3, 30)
        
        all_values = fallback.get_all()
        assert all_values == {1: 10, 2: 20, 3: 30}
    
    def test_clear(self):
        """Test clearing all data"""
        fallback = InMemoryFallback()
        fallback.set(1, 10)
        fallback.set(2, 20)
        
        fallback.clear()
        assert fallback.get_all() == {}


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
        assert db.fallback is not None
        assert db.is_healthy() is True
    
    def test_set_and_get(self):
        """Test basic database operations"""
        db = DatabaseManager(self.db_path)
        
        # Set value
        db.set(1000, 123)
        
        # Get value
        value = db.get(1000)
        assert value == 123
    
    def test_fallback_on_error(self):
        """Test fallback mechanism when database fails"""
        db = DatabaseManager(self.db_path, enable_fallback=True)
        
        # Set value in database
        db.set(500, 999)
        
        # Simulate database failure
        with patch.object(db, 'db', side_effect=Exception("Database error")):
            # Should fall back to in-memory storage
            value = db.get(500)
            assert value == 999  # Should get from fallback
            
            # Should be able to set in fallback
            db.set(501, 888)
            assert db.fallback.get(501) == 888
    
    def test_get_status(self):
        """Test status reporting"""
        db = DatabaseManager(self.db_path)
        status = db.get_status()
        
        assert 'healthy' in status
        assert 'using_fallback' in status
        assert 'entries' in status
        assert status['healthy'] is True
        assert status['using_fallback'] is False
    
    def test_retry_mechanism(self):
        """Test retry mechanism for transient failures"""
        db = DatabaseManager(self.db_path)
        
        # Mock db.set to fail twice then succeed
        call_count = 0
        original_set = db.db.set
        
        def mock_set(key, value):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Transient error")
            return original_set(key, value)
        
        with patch.object(db.db, 'set', side_effect=mock_set):
            db.set(123, 456)
            assert call_count == 3  # Should retry and succeed on third attempt


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 