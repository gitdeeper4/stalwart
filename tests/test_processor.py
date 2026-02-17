#!/usr/bin/env python3
"""Tests for STALWART analysis processor."""

import sys
import unittest
from pathlib import Path
from datetime import datetime
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stalwart.core.bridge import Bridge, BridgeSpecs
from src.stalwart.core.sensor import Accelerometer, StrainGauge
from src.stalwart.core.measurement import Measurement
from src.stalwart.analysis.processor import AnalysisProcessor
from src.stalwart.analysis.metrics import MetricResult


class TestAnalysisProcessor(unittest.TestCase):
    """Test AnalysisProcessor class."""
    
    def setUp(self):
        specs = BridgeSpecs(
            name="Test Bridge",
            bridge_id="TEST-001",
            bridge_type="suspension",
            span_length=500.0,
            year_built=2000,
            critical_flutter_speed=70.0
        )
        self.bridge = Bridge(specs)
        
        self.bridge.add_sensor(Accelerometer("ACC-001", "mid-span"))
        self.bridge.add_sensor(Accelerometer("ACC-002", "quarter"))
        self.bridge.add_sensor(StrainGauge("STR-001", "girder-1"))
        
        self.processor = AnalysisProcessor(self.bridge)
    
    def test_processor_initialization(self):
        self.assertEqual(self.processor.bridge, self.bridge)
        self.assertIn('AFC', self.processor.metrics_history)
    
    def test_organize_measurements(self):
        measurements = [
            Measurement("ACC-001", "TEST-001", datetime.now(), 0.123, "m/s²"),
            Measurement("ACC-002", "TEST-001", datetime.now(), 0.456, "m/s²"),
            Measurement("STR-001", "TEST-001", datetime.now(), 150.0, "με"),
        ]
        
        organized = self.processor._organize_measurements(measurements)
        
        self.assertIn('accelerometer', organized)
        self.assertIn('strain_gauge', organized)
        self.assertEqual(len(organized['accelerometer']), 2)
        self.assertEqual(len(organized['strain_gauge']), 1)
    
    def test_estimate_frequency_simple(self):
        fs = 100
        t = np.arange(0, 10, 1/fs)
        signal = np.sin(2 * np.pi * 1.2 * t)
        
        freq = self.processor._estimate_frequency_simple(signal.tolist(), fs)
        self.assertAlmostEqual(freq, 1.2, delta=0.1)
    
    def test_estimate_damping_simple(self):
        fs = 100
        t = np.arange(0, 10, 1/fs)
        signal = np.exp(-0.02 * t) * np.sin(2 * np.pi * 1.2 * t)
        
        damping = self.processor._estimate_damping_simple(signal.tolist())
        self.assertGreater(damping, 0)
        self.assertLess(damping, 0.05)  # يجب أن تكون أقل من 0.05
    
    def test_determine_risk_level(self):
        # Test SAFE condition
        metrics_safe = {
            'AFC': MetricResult(0.3, "SAFE", 0.9, {}),
            'ALSA': MetricResult(0.4, "SAFE", 0.9, {}),
        }
        level = self.processor._determine_risk_level(metrics_safe, 85.0)
        self.assertEqual(level, "SAFE")
        
        # Test MONITOR condition (warning_count == 1)
        metrics_monitor = {
            'AFC': MetricResult(0.5, "SAFE", 0.9, {}),
            'ALSA': MetricResult(0.65, "WARNING", 0.9, {}),
        }
        level = self.processor._determine_risk_level(metrics_monitor, 75.0)
        self.assertEqual(level, "MONITOR")
        
        # Test WARNING condition (caution_count >= 1)
        metrics_warning1 = {
            'AFC': MetricResult(0.65, "WARNING", 0.9, {}),
            'ALSA': MetricResult(0.4, "SAFE", 0.9, {}),
            'CCF': MetricResult(35.0, "CAUTION", 0.9, {}),
        }
        level = self.processor._determine_risk_level(metrics_warning1, 75.0)
        self.assertEqual(level, "WARNING")
        
        # Test WARNING condition (warning_count >= 2)
        metrics_warning2 = {
            'AFC': MetricResult(0.65, "WARNING", 0.9, {}),
            'ALSA': MetricResult(0.4, "WARNING", 0.9, {}),
        }
        level = self.processor._determine_risk_level(metrics_warning2, 75.0)
        self.assertEqual(level, "WARNING")
        
        # Test CAUTION condition
        metrics_caution = {
            'AFC': MetricResult(0.8, "CAUTION", 0.9, {}),
            'ALSA': MetricResult(0.4, "SAFE", 0.9, {}),
            'FFD': MetricResult(4.0, "CAUTION", 0.9, {}),
        }
        level = self.processor._determine_risk_level(metrics_caution, 65.0)
        self.assertEqual(level, "WARNING")  # caution_count >= 1 -> WARNING
        
        # Test CRITICAL condition
        metrics_critical = {
            'AFC': MetricResult(0.86, "CRITICAL", 0.9, {}),
            'ALSA': MetricResult(0.4, "SAFE", 0.9, {}),
        }
        level = self.processor._determine_risk_level(metrics_critical, 50.0)
        self.assertEqual(level, "CRITICAL")


if __name__ == "__main__":
    unittest.main()
