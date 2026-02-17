#!/usr/bin/env python3
"""Tests for STALWART core modules."""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stalwart.core.bridge import Bridge, BridgeSpecs
from src.stalwart.core.sensor import (
    Accelerometer, StrainGauge, TemperatureSensor,
    CorrosionProbe, LVDT, Anemometer, SensorArray
)
from src.stalwart.core.measurement import Measurement, TimeSeries
from datetime import datetime


class TestBridge(unittest.TestCase):
    """Test Bridge class."""
    
    def setUp(self):
        self.specs = BridgeSpecs(
            name="Test Bridge",
            bridge_id="TEST-001",
            bridge_type="suspension",
            span_length=500.0,
            year_built=2000,
            critical_flutter_speed=70.0
        )
        self.bridge = Bridge(self.specs)
    
    def test_bridge_creation(self):
        """Test bridge initialization."""
        self.assertEqual(self.bridge.specs.name, "Test Bridge")
        self.assertEqual(self.bridge.specs.bridge_id, "TEST-001")
        self.assertEqual(len(self.bridge.sensors), 0)
    
    def test_add_sensor(self):
        """Test adding sensors to bridge."""
        sensor = Accelerometer("ACC-001", "mid-span")
        self.bridge.add_sensor(sensor)
        self.assertEqual(len(self.bridge.sensors), 1)
        self.assertEqual(self.bridge.sensors[0].sensor_id, "ACC-001")
    
    def test_get_sensors_by_type(self):
        """Test getting sensors by type."""
        self.bridge.add_sensor(Accelerometer("ACC-001", "mid-span"))
        self.bridge.add_sensor(Accelerometer("ACC-002", "quarter"))
        self.bridge.add_sensor(StrainGauge("STR-001", "girder"))
        
        accels = self.bridge.get_sensors_by_type("accelerometer")
        strains = self.bridge.get_sensors_by_type("strain_gauge")
        
        self.assertEqual(len(accels), 2)
        self.assertEqual(len(strains), 1)


class TestSensors(unittest.TestCase):
    """Test Sensor classes."""
    
    def test_accelerometer(self):
        """Test accelerometer sensor."""
        sensor = Accelerometer("ACC-001", "mid-span")
        self.assertEqual(sensor.sensor_id, "ACC-001")
        self.assertEqual(sensor.specs.sensor_type, "accelerometer")
        self.assertEqual(sensor.specs.sampling_rate, 100.0)
        
        # Test reading
        value = sensor.read()
        self.assertIsNotNone(value)
        self.assertGreaterEqual(value, sensor.specs.range_min)
        self.assertLessEqual(value, sensor.specs.range_max)
    
    def test_strain_gauge(self):
        """Test strain gauge sensor."""
        sensor = StrainGauge("STR-001", "girder-1")
        self.assertEqual(sensor.sensor_id, "STR-001")
        self.assertEqual(sensor.specs.sensor_type, "strain_gauge")
        
        value = sensor.read()
        self.assertIsNotNone(value)
    
    def test_temperature_sensor(self):
        """Test temperature sensor."""
        sensor = TemperatureSensor("TEMP-001", "deck")
        self.assertEqual(sensor.sensor_id, "TEMP-001")
        
        value = sensor.read()
        self.assertIsNotNone(value)
    
    def test_corrosion_probe(self):
        """Test corrosion probe."""
        sensor = CorrosionProbe("CORR-001", "pier-1")
        self.assertEqual(sensor.sensor_id, "CORR-001")
        
        value = sensor.read()
        self.assertIsNotNone(value)
    
    def test_lvdt(self):
        """Test LVDT displacement sensor."""
        sensor = LVDT("LVDT-001", "joint-1")
        self.assertEqual(sensor.sensor_id, "LVDT-001")
        
        value = sensor.read()
        self.assertIsNotNone(value)
    
    def test_anemometer(self):
        """Test anemometer."""
        sensor = Anemometer("WIND-001", "mid-span")
        self.assertEqual(sensor.sensor_id, "WIND-001")
        
        value = sensor.read()
        self.assertIsNotNone(value)
    
    def test_sensor_array(self):
        """Test sensor array."""
        array = SensorArray("ARRAY-001")
        array.add_sensor(Accelerometer("ACC-001", "mid-span"))
        array.add_sensor(Accelerometer("ACC-002", "quarter"))
        
        readings = array.read_all()
        self.assertEqual(len(readings), 2)
        self.assertIn("ACC-001", readings)


class TestMeasurement(unittest.TestCase):
    """Test Measurement and TimeSeries classes."""
    
    def test_measurement_creation(self):
        """Test measurement creation."""
        m = Measurement(
            sensor_id="ACC-001",
            bridge_id="TEST-001",
            timestamp=datetime.now(),
            value=0.123,
            unit="m/s²"
        )
        self.assertEqual(m.sensor_id, "ACC-001")
        self.assertEqual(m.value, 0.123)
        self.assertEqual(m.unit, "m/s²")
    
    def test_timeseries(self):
        """Test time series."""
        measurements = []
        for i in range(10):
            m = Measurement(
                sensor_id="ACC-001",
                bridge_id="TEST-001",
                timestamp=datetime.now(),
                value=float(i),
                unit="m/s²"
            )
            measurements.append(m)
        
        ts = TimeSeries("ACC-001", "TEST-001", measurements)
        self.assertEqual(len(ts.measurements), 10)
        self.assertEqual(len(ts.values), 10)


if __name__ == "__main__":
    unittest.main()
