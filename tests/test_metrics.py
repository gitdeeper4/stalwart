#!/usr/bin/env python3
"""Tests for STALWART nine metrics."""

import sys
import unittest
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stalwart.analysis.metrics import (
    calculate_afc, calculate_alsa, calculate_cpii,
    calculate_ffd, calculate_lts, calculate_ccf,
    calculate_tvr, calculate_bd, calculate_sed,
    calculate_health_index, MetricResult
)
from src.stalwart.utils.constants import THRESHOLDS


class TestMetrics(unittest.TestCase):
    """Test all nine STALWART metrics."""
    
    def test_afc(self):
        result = calculate_afc(
            wind_speed=15.0,
            vertical_amplitude=0.05,
            damping_ratio=0.02,
            frequency=1.2,
            critical_flutter_speed=70.0,
            design_amplitude=0.1,
            design_damping=0.024,
            design_frequency=1.2
        )
        self.assertIsInstance(result, MetricResult)
        self.assertGreater(result.value, 0)
        self.assertLess(result.value, 1)
    
    def test_alsa(self):
        strain_data = np.random.normal(200, 50, 1000)
        result = calculate_alsa(strain_measurements=strain_data, yield_strain=2000)
        self.assertIsInstance(result, MetricResult)
    
    def test_cpii_cable(self):
        result = calculate_cpii(wire_breaks=15, total_wires=15000, bridge_type="suspension")
        self.assertIsInstance(result, MetricResult)
    
    def test_cpii_pier(self):
        result = calculate_cpii(bridge_type="girder")
        self.assertIsInstance(result, MetricResult)
    
    def test_ffd(self):
        result = calculate_ffd(current_frequency=1.18, baseline_frequency=1.20)
        self.assertIsInstance(result, MetricResult)
    
    def test_ffd_with_temperature(self):
        result = calculate_ffd(
            current_frequency=1.18,
            baseline_frequency=1.20,
            temperature=25.0,
            reference_temperature=20.0
        )
        self.assertIsInstance(result, MetricResult)
    
    def test_lts(self):
        result = calculate_lts(
            temperature_delta=25.0,
            measured_expansion=150.0,
            expected_expansion=200.0
        )
        self.assertIsInstance(result, MetricResult)
    
    def test_ccf_chloride(self):
        result = calculate_ccf(chloride_concentration=0.25)
        self.assertIsInstance(result, MetricResult)
    
    def test_ccf_carbonation(self):
        result = calculate_ccf(carbonation_depth=30, concrete_cover=50)
        self.assertIsInstance(result, MetricResult)
    
    def test_tvr(self):
        result = calculate_tvr(
            current_damping=0.021,
            baseline_damping=0.024,
            current_decay_time=4.2,
            baseline_decay_time=5.0
        )
        self.assertIsInstance(result, MetricResult)
        self.assertLessEqual(result.value, 1.0)
        self.assertGreaterEqual(result.value, 0.1)
    
    def test_bd(self):
        result = calculate_bd(displacement=8.5, displacement_capacity=25.0)
        self.assertIsInstance(result, MetricResult)
    
    def test_sed(self):
        result = calculate_sed(local_strain=350, global_strain=200)
        self.assertIsInstance(result, MetricResult)
    
    def test_health_index(self):
        metrics = {
            'AFC': MetricResult(0.42, "SAFE", 0.9, {}),
            'ALSA': MetricResult(0.58, "WARNING", 0.9, {}),
            'CPII': MetricResult(0.91, "SAFE", 0.9, {}),
            'FFD': MetricResult(2.3, "SAFE", 0.9, {}),
            'LTS': MetricResult(18.5, "SAFE", 0.9, {}),
            'CCF': MetricResult(34.2, "SAFE", 0.9, {}),
            'TVR': MetricResult(0.88, "SAFE", 0.9, {}),
            'BD': MetricResult(34.0, "WARNING", 0.9, {}),
            'SED': MetricResult(42.3, "SAFE", 0.9, {})
        }
        health = calculate_health_index(metrics)
        self.assertGreater(health, 0)
        self.assertLessEqual(health, 100)


class TestThresholds(unittest.TestCase):
    """Test threshold values from research paper."""
    
    def test_thresholds_from_paper(self):
        self.assertEqual(THRESHOLDS['AFC']['warning'], 0.60)
        self.assertEqual(THRESHOLDS['AFC']['caution'], 0.75)
        self.assertEqual(THRESHOLDS['AFC']['critical'], 0.85)
        self.assertEqual(THRESHOLDS['ALSA']['warning'], 0.60)
        self.assertEqual(THRESHOLDS['ALSA']['caution'], 0.75)
        self.assertEqual(THRESHOLDS['ALSA']['critical'], 0.90)
        self.assertEqual(THRESHOLDS['FFD']['warning'], 3.0)
        self.assertEqual(THRESHOLDS['FFD']['caution'], 5.0)
        self.assertEqual(THRESHOLDS['FFD']['critical'], 8.0)


if __name__ == "__main__":
    unittest.main()
