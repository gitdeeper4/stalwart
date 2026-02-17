"""STALWART Machine Learning Module - AI-Powered Bridge Intelligence

This module provides advanced AI capabilities for bridge health monitoring.
Version: 2.0.0 (AI Edition)
"""

# Import directly from files
from .models import (
    RandomForestPredictor,
    XGBoostPredictor,
    LSTMPredictor,
    EnsemblePredictor
)

from .anomaly_detection import (
    IsolationForestDetector,
    AutoencoderDetector,
    StatisticalDetector
)

from .prediction import (
    FailurePredictor,
    RemainingLifePredictor,
    PredictionResult,
    RemainingLifeResult
)

from .feature_engineering import (
    FeatureExtractor,
    SensorFusion
)

__all__ = [
    # Models
    'RandomForestPredictor',
    'XGBoostPredictor',
    'LSTMPredictor',
    'EnsemblePredictor',
    
    # Anomaly Detection
    'IsolationForestDetector',
    'AutoencoderDetector',
    'StatisticalDetector',
    
    # Prediction
    'FailurePredictor',
    'RemainingLifePredictor',
    'PredictionResult',
    'RemainingLifeResult',
    
    # Features
    'FeatureExtractor',
    'SensorFusion'
]

__version__ = "2.0.0"
