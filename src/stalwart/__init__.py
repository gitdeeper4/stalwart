"""STALWART - Structural Testing and Lifecycle Warning through Advanced Real-Time Tracking

A comprehensive sensor-driven framework for predictive bridge safety monitoring.
Monitors 9 critical structural parameters with 94.7% accuracy and provides
6-18 month early warning of structural degradation.

Version 2.0.0 (AI Edition) adds:
- Anomaly detection using Isolation Forest and Autoencoders
- Failure prediction with Random Forest, XGBoost, and LSTM
- Pattern recognition in sensor data
- Automated feature engineering
- Ensemble learning for robust predictions

Research Paper:
    Baladi, S., Johnson, R., Chen, M., Schmidt, K., & Williams, S. (2026).
    STALWART: Sensor-Driven Predictive Framework for Structural Health Monitoring
    and Failure Prevention in Long-Span Bridge Infrastructure.
    Journal of Bridge Engineering and Structural Health Monitoring.

DOI: 10.5281/zenodo.18655299
"""

__version__ = "2.0.0"
__author__ = "Samir Baladi"
__email__ = "gitdeeper@gmail.com"
__license__ = "MIT"
__doi__ = "10.5281/zenodo.18655299"

# Core classes
from .core.bridge import Bridge
from .core.sensor import Sensor, SensorArray
from .core.measurement import Measurement, TimeSeries

# Analysis modules - import specific functions
from .analysis.metrics import (
    calculate_afc, calculate_alsa, calculate_cpii,
    calculate_ffd, calculate_lts, calculate_ccf,
    calculate_tvr, calculate_bd, calculate_sed,
    calculate_health_index, MetricResult
)
from .analysis.metrics import (
    AFC, ALSA, CPII, FFD, LTS, CCF, TVR, BD, SED
)

# Machine Learning (v2.0.0 AI Edition)
try:
    from .ml.models import (
        RandomForestPredictor,
        XGBoostPredictor,
        LSTMPredictor,
        EnsemblePredictor
    )
    from .ml.anomaly_detection import (
        IsolationForestDetector,
        AutoencoderDetector,
        StatisticalDetector
    )
    from .ml.prediction import FailurePredictor, RemainingLifePredictor
    from .ml.feature_engineering import FeatureExtractor, SensorFusion
    HAS_ML = True
except ImportError as e:
    HAS_ML = False
    # Define placeholders
    RandomForestPredictor = None
    XGBoostPredictor = None
    LSTMPredictor = None
    EnsemblePredictor = None
    IsolationForestDetector = None
    AutoencoderDetector = None
    StatisticalDetector = None
    FailurePredictor = None
    RemainingLifePredictor = None
    FeatureExtractor = None
    SensorFusion = None

# API and dashboard
try:
    from .api.client import APIClient
    from .dashboard.app import Dashboard
    HAS_API = True
except ImportError:
    HAS_API = False
    APIClient = None
    Dashboard = None

# Utilities
from .utils.config import load_config
from .utils.logger import setup_logger
from .utils.constants import THRESHOLDS, ALERT_LEVELS

__all__ = [
    # Version info
    '__version__', '__author__', '__email__', '__license__', '__doi__',
    
    # Core
    'Bridge', 'Sensor', 'SensorArray', 'Measurement', 'TimeSeries',
    
    # Metrics - functions
    'calculate_afc', 'calculate_alsa', 'calculate_cpii',
    'calculate_ffd', 'calculate_lts', 'calculate_ccf',
    'calculate_tvr', 'calculate_bd', 'calculate_sed',
    'calculate_health_index', 'MetricResult',
    
    # Metrics - classes
    'AFC', 'ALSA', 'CPII', 'FFD', 'LTS', 'CCF', 'TVR', 'BD', 'SED',
    
    # Machine Learning (v2.0.0)
    'RandomForestPredictor', 'XGBoostPredictor', 'LSTMPredictor', 'EnsemblePredictor',
    'IsolationForestDetector', 'AutoencoderDetector', 'StatisticalDetector',
    'FailurePredictor', 'RemainingLifePredictor',
    'FeatureExtractor', 'SensorFusion', 'HAS_ML',
    
    # API & Dashboard
    'APIClient', 'Dashboard', 'HAS_API',
    
    # Utils
    'load_config', 'setup_logger', 'THRESHOLDS', 'ALERT_LEVELS'
]
