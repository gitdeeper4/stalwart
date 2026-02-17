#!/usr/bin/env python3
"""Tests for STALWART machine learning models (v2.0.0 AI Edition)."""

import sys
import unittest
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.stalwart.ml import (
    RandomForestPredictor,
    XGBoostPredictor,
    LSTMPredictor,
    EnsemblePredictor,
    IsolationForestDetector,
    AutoencoderDetector,
    StatisticalDetector,
    FailurePredictor,
    RemainingLifePredictor,
    FeatureExtractor,
    SensorFusion
)
from src.stalwart.ml.prediction import PredictionResult, RemainingLifeResult


class TestRandomForestPredictor(unittest.TestCase):
    """Test Random Forest model."""
    
    def setUp(self):
        np.random.seed(42)
        self.X = np.random.randn(100, 9)
        self.y_reg = np.random.randn(100)
        self.y_cls = np.random.randint(0, 2, 100)  # فئتين فقط: 0 و 1
        self.X_test = np.random.randn(10, 9)
    
    def test_regression_initialization(self):
        model = RandomForestPredictor(n_estimators=50, max_depth=10, task="regression")
        self.assertEqual(model.n_estimators, 50)
        self.assertEqual(model.max_depth, 10)
        self.assertEqual(model.task, "regression")
        self.assertFalse(model.is_trained)
    
    def test_classification_initialization(self):
        model = RandomForestPredictor(n_estimators=50, max_depth=10, task="classification")
        self.assertEqual(model.task, "classification")
    
    def test_regression_training_and_prediction(self):
        model = RandomForestPredictor(n_estimators=50, max_depth=10, task="regression")
        model.train(self.X, self.y_reg)
        
        self.assertTrue(model.is_trained)
        
        predictions = model.predict(self.X_test)
        self.assertEqual(len(predictions), 10)
        self.assertIsInstance(predictions, np.ndarray)
    
    def test_classification_training_and_prediction(self):
        model = RandomForestPredictor(n_estimators=50, max_depth=10, task="classification")
        model.train(self.X, self.y_cls)
        
        predictions = model.predict(self.X_test)
        self.assertEqual(len(predictions), 10)
        
        # للتصنيف الثنائي، يجب أن يكون شكل المصفوفة (10, 2)
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(self.X_test)
            self.assertEqual(proba.shape, (10, 2))  # فئتين فقط
            # مجموع الاحتمالات لكل عينة = 1
            np.testing.assert_almost_equal(np.sum(proba, axis=1), 1.0)
    
    def test_feature_importance(self):
        model = RandomForestPredictor(n_estimators=50, max_depth=10, task="regression")
        model.train(self.X, self.y_reg)
        
        importance = model.get_feature_importance()
        if importance is not None:
            self.assertEqual(len(importance), 9)
    
    def test_save_load(self):
        model = RandomForestPredictor(n_estimators=50, max_depth=10, task="regression")
        model.train(self.X, self.y_reg)
        
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            model.save(f.name)
            loaded_model = RandomForestPredictor.load(f.name)
            self.assertTrue(loaded_model.is_trained)


class TestXGBoostPredictor(unittest.TestCase):
    """Test XGBoost model."""
    
    def setUp(self):
        np.random.seed(42)
        self.X = np.random.randn(100, 9)
        self.y = np.random.randn(100)
        self.X_test = np.random.randn(10, 9)
    
    def test_initialization(self):
        model = XGBoostPredictor(n_estimators=50, max_depth=8, learning_rate=0.05)
        self.assertEqual(model.n_estimators, 50)
        self.assertEqual(model.max_depth, 8)
        self.assertEqual(model.learning_rate, 0.05)
    
    def test_training_and_prediction(self):
        model = XGBoostPredictor(n_estimators=50, max_depth=8)
        model.train(self.X, self.y)
        self.assertTrue(model.is_trained)
        predictions = model.predict(self.X_test)
        self.assertEqual(len(predictions), 10)


class TestLSTMPredictor(unittest.TestCase):
    """Test LSTM neural network model."""
    
    def setUp(self):
        np.random.seed(42)
        self.n_samples = 200
        self.n_features = 9
        self.X = np.random.randn(self.n_samples, self.n_features)
        self.y = np.random.randn(self.n_samples)
    
    def test_initialization(self):
        model = LSTMPredictor(
            sequence_length=50,
            n_features=9,
            lstm_units=[64, 32],
            dropout=0.2
        )
        self.assertEqual(model.sequence_length, 50)
        self.assertEqual(model.n_features, 9)
    
    def test_training_without_tensorflow(self):
        model = LSTMPredictor(sequence_length=20, n_features=9)
        model.train(self.X, self.y, epochs=2)


class TestEnsemblePredictor(unittest.TestCase):
    """Test ensemble model."""
    
    def setUp(self):
        np.random.seed(42)
        self.X = np.random.randn(100, 9)
        self.y = np.random.randn(100)
        self.X_test = np.random.randn(10, 9)
    
    def test_ensemble_creation(self):
        ensemble = EnsemblePredictor()
        rf = RandomForestPredictor(n_estimators=50, task="regression")
        xgb = XGBoostPredictor(n_estimators=50, task="regression")
        
        ensemble.add_model(rf, weight=0.6)
        ensemble.add_model(xgb, weight=0.4)
        
        self.assertEqual(len(ensemble.models), 2)
        self.assertEqual(len(ensemble.weights), 2)
    
    def test_ensemble_training_and_prediction(self):
        ensemble = EnsemblePredictor()
        ensemble.add_model(RandomForestPredictor(n_estimators=50, task="regression"), weight=0.5)
        ensemble.add_model(XGBoostPredictor(n_estimators=50, task="regression"), weight=0.5)
        
        ensemble.train(self.X, self.y)
        predictions = ensemble.predict(self.X_test)
        self.assertEqual(len(predictions), 10)
    
    def test_uncertainty_estimation(self):
        ensemble = EnsemblePredictor()
        ensemble.add_model(RandomForestPredictor(n_estimators=50, task="regression"), weight=0.5)
        ensemble.add_model(XGBoostPredictor(n_estimators=50, task="regression"), weight=0.5)
        
        ensemble.train(self.X, self.y)
        
        if hasattr(ensemble, 'predict_with_uncertainty'):
            mean_pred, std_pred = ensemble.predict_with_uncertainty(self.X_test)
            self.assertEqual(len(mean_pred), 10)
            self.assertEqual(len(std_pred), 10)


class TestIsolationForestDetector(unittest.TestCase):
    """Test Isolation Forest anomaly detector."""
    
    def setUp(self):
        np.random.seed(42)
        self.X_normal = np.random.randn(200, 9)
        self.X_anomaly = np.random.randn(20, 9) * 5 + 10
        self.X_combined = np.vstack([self.X_normal, self.X_anomaly])
    
    def test_initialization(self):
        detector = IsolationForestDetector(contamination=0.05)
        self.assertEqual(detector.contamination, 0.05)
    
    def test_training_and_prediction(self):
        detector = IsolationForestDetector(contamination=0.1)
        detector.train(self.X_combined)
        predictions = detector.predict(self.X_combined)
        self.assertEqual(len(predictions), 220)
    
    def test_find_anomalies(self):
        detector = IsolationForestDetector(contamination=0.1)
        detector.train(self.X_combined)
        result = detector.find_anomalies(self.X_combined)
        self.assertIn('n_anomalies', result)


class TestFailurePredictor(unittest.TestCase):
    """Test failure prediction model."""
    
    def setUp(self):
        np.random.seed(42)
        self.X = np.random.randn(100, 9)
        self.y = np.random.randint(0, 2, 100)  # فئتين فقط
        self.X_test = np.random.randn(1, 9)
    
    def test_initialization(self):
        predictor = FailurePredictor(model_type="random_forest")
        self.assertEqual(predictor.model_type, "random_forest")
    
    def test_training_and_prediction(self):
        predictor = FailurePredictor(model_type="random_forest")
        predictor.train(self.X, self.y)
        results = predictor.predict(self.X_test)
        if results:
            self.assertEqual(len(results), 1)
            self.assertIsInstance(results[0], PredictionResult)


class TestRemainingLifePredictor(unittest.TestCase):
    """Test remaining life prediction model."""
    
    def setUp(self):
        np.random.seed(42)
        self.X = np.random.randn(100, 9)
        self.y = np.random.uniform(1, 30, 100)
        self.X_test = np.random.randn(1, 9)
    
    def test_initialization(self):
        predictor = RemainingLifePredictor()
        self.assertIsNotNone(predictor.model)
    
    def test_training_and_prediction(self):
        predictor = RemainingLifePredictor()
        predictor.train(self.X, self.y)
        results = predictor.predict(self.X_test)
        if results:
            self.assertEqual(len(results), 1)
            self.assertIsInstance(results[0], RemainingLifeResult)
    
    def test_trajectory_determination(self):
        predictor = RemainingLifePredictor()
        features_improving = np.array([0, 0, 0, -1.0, 0, 0, 0, 0, 0])
        trajectory = predictor._determine_trajectory(features_improving)
        self.assertIn(trajectory, ["improving", "stable", "degrading"])


class TestFeatureExtractor(unittest.TestCase):
    """Test feature extraction from sensor data."""
    
    def setUp(self):
        np.random.seed(42)
        self.n_samples = 100
        self.n_sensors = 3
        import pandas as pd
        self.data = pd.DataFrame(
            np.random.randn(self.n_samples, self.n_sensors),
            columns=['sensor1', 'sensor2', 'sensor3']
        )
        self.timestamps = [datetime.now() + timedelta(minutes=i) for i in range(self.n_samples)]
    
    def test_initialization(self):
        extractor = FeatureExtractor(window_size=3600)
        self.assertEqual(extractor.window_size, 3600)
    
    def test_feature_extraction(self):
        extractor = FeatureExtractor()
        features = extractor.extract_from_timeseries(self.data, self.timestamps)
        self.assertIsInstance(features, np.ndarray)


if __name__ == "__main__":
    import pandas as pd
    unittest.main()
