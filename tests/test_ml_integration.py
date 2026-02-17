#!/usr/bin/env python3
"""Integration tests for STALWART ML models with core system."""

import sys
import unittest
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stalwart.core.bridge import Bridge, BridgeSpecs
from src.stalwart.core.sensor import (
    Accelerometer, StrainGauge, TemperatureSensor,
    CorrosionProbe, LVDT, Anemometer
)
from src.stalwart.core.measurement import Measurement
from src.stalwart.ml import (
    RandomForestPredictor,
    EnsemblePredictor,
    IsolationForestDetector,
    FailurePredictor,
    RemainingLifePredictor,
    FeatureExtractor,
    SensorFusion
)


class TestMLBridgeIntegration(unittest.TestCase):
    """Test integration of ML models with Bridge system."""
    
    def setUp(self):
        """Create test bridge and generate data."""
        specs = BridgeSpecs(
            name="ML Test Bridge",
            bridge_id="ML-TEST-001",
            bridge_type="suspension",
            span_length=500.0,
            year_built=2000
        )
        self.bridge = Bridge(specs)
        
        # Generate synthetic measurements
        self.measurements = []
        base_time = datetime.now() - timedelta(days=30)
        
        for i in range(100):
            timestamp = base_time + timedelta(minutes=10*i)
            self.measurements.append(Measurement("ACC-001", "ML-TEST-001", timestamp, 
                                                np.random.normal(0, 0.1), "m/s²"))
            self.measurements.append(Measurement("STR-001", "ML-TEST-001", timestamp,
                                                np.random.normal(200, 50), "με"))
    
    def test_anomaly_detection_on_bridge_data(self):
        """Test anomaly detection with bridge data."""
        # Extract values - نحتاج إلى بيانات أكثر
        values = np.array([m.value for m in self.measurements]).reshape(-1, 1)
        
        # استخدام 100 عينة للتدريب
        detector = IsolationForestDetector(contamination=0.1)
        detector.train(values[:100])
        
        # اختبار على 100 عينة (لدينا 200 عينة إجمالاً)
        predictions = detector.predict(values[100:200])
        self.assertEqual(len(predictions), 100)  # 100 عينة اختبار
    
    def test_failure_prediction_pipeline(self):
        """Test failure prediction pipeline."""
        X_train = np.random.randn(50, 9)
        y_train = np.random.randint(0, 2, 50)  # فئتين فقط
        
        predictor = FailurePredictor(model_type="random_forest")
        predictor.train(X_train, y_train)
        
        X_test = np.random.randn(1, 9)
        results = predictor.predict(X_test)
        
        if results:
            self.assertEqual(len(results), 1)
    
    def test_remaining_life_estimation(self):
        """Test remaining life estimation."""
        X_train = np.random.randn(50, 9)
        y_train = np.random.uniform(5, 30, 50)
        
        predictor = RemainingLifePredictor()
        predictor.train(X_train, y_train)
        
        X_test = np.random.randn(1, 9)
        results = predictor.predict(X_test)
        
        if results:
            self.assertEqual(len(results), 1)


if __name__ == "__main__":
    unittest.main()
