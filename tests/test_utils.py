#!/usr/bin/env python3
"""Tests for STALWART utility modules."""

import sys
import unittest
import tempfile
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stalwart.utils.constants import THRESHOLDS, PARAMETERS, SENSOR_TYPES
from src.stalwart.utils.logger import setup_logger, get_logger
from src.stalwart.utils.config import load_config, STALWARTConfig


class TestConstants(unittest.TestCase):
    """Test constants module."""
    
    def test_parameters(self):
        """Test parameters list."""
        self.assertEqual(len(PARAMETERS), 9)
        self.assertIn('AFC', PARAMETERS)
        self.assertIn('FFD', PARAMETERS)
        self.assertIn('SED', PARAMETERS)
    
    def test_sensor_types(self):
        """Test sensor types list."""
        self.assertIn('accelerometer', SENSOR_TYPES)
        self.assertIn('strain_gauge', SENSOR_TYPES)
        self.assertIn('temperature', SENSOR_TYPES)
    
    def test_thresholds_structure(self):
        """Test thresholds structure."""
        self.assertIn('AFC', THRESHOLDS)
        self.assertIn('warning', THRESHOLDS['AFC'])
        self.assertIn('caution', THRESHOLDS['AFC'])
        self.assertIn('critical', THRESHOLDS['AFC'])


class TestLogger(unittest.TestCase):
    """Test logger module."""
    
    def test_setup_logger(self):
        """Test logger setup."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            logger = setup_logger("test", "DEBUG", log_file)
            
            self.assertEqual(logger.name, "test")
            self.assertEqual(logger.level, 10)  # DEBUG
            
            # Test logging
            logger.info("Test message")
            
            # Check log file
            self.assertTrue(os.path.exists(log_file))
    
    def test_get_logger(self):
        """Test getting logger."""
        logger1 = get_logger("test1")
        logger2 = get_logger("test2")
        
        self.assertIsNotNone(logger1)
        self.assertIsNotNone(logger2)
        self.assertNotEqual(logger1.name, logger2.name)


class TestConfig(unittest.TestCase):
    """Test config module."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = STALWARTConfig()
        
        self.assertEqual(config.env, "development")
        self.assertEqual(config.database.host, "localhost")
        self.assertEqual(config.api.port, 8000)
        self.assertEqual(config.data_dir, "./data")
    
    def test_config_from_dict(self):
        """Test config from dictionary."""
        data = {
            'env': 'production',
            'database': {
                'host': 'testhost',
                'port': 5433,
                'name': 'testdb'
            },
            'api': {
                'port': 9000
            }
        }
        
        config = STALWARTConfig._from_dict(data)
        
        self.assertEqual(config.env, "production")
        self.assertEqual(config.database.host, "testhost")
        self.assertEqual(config.database.port, 5433)
        self.assertEqual(config.database.name, "testdb")
        self.assertEqual(config.api.port, 9000)
    
    def test_load_config(self):
        """Test loading config from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""
env: testing
database:
  host: localhost
  port: 5432
api:
  port: 8000
            """)
            f.flush()
            
            config = load_config(f.name)
            
            self.assertEqual(config.env, "testing")
            self.assertEqual(config.database.host, "localhost")
            
            os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
