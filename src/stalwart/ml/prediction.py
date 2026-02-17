"""Failure prediction and remaining life estimation."""

import numpy as np
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..utils.logger import get_logger
from .models import RandomForestPredictor, XGBoostPredictor, LSTMPredictor, EnsemblePredictor

logger = get_logger(__name__)


@dataclass
class PredictionResult:
    """Result of a failure prediction."""
    time_to_failure: float  # months
    confidence: float  # 0-1
    failure_mode: str  # e.g., "fatigue", "corrosion", "flutter"
    probability: float  # 0-1
    details: Dict[str, Any]


@dataclass
class RemainingLifeResult:
    """Result of remaining life estimation."""
    years_remaining: float
    confidence_interval: Tuple[float, float]  # (lower, upper)
    health_trajectory: str  # "improving", "stable", "degrading"
    recommended_action: str
    details: Dict[str, Any]


class FailurePredictor:
    """Predict bridge failure modes and timing."""
    
    def __init__(self, model_type: str = "ensemble"):
        self.model_type = model_type
        self.model = None
        self.feature_names = [
            'AFC', 'ALSA', 'CPII', 'FFD', 'LTS', 'CCF', 'TVR', 'BD', 'SED',
            'age', 'traffic', 'span', 'temperature'
        ]
        self.failure_modes = [
            'fatigue_crack',
            'corrosion_failure',
            'aeroelastic_flutter',
            'bearing_failure',
            'thermal_stress',
            'cable_rupture'
        ]
        self.is_trained = False
    
    def _create_model(self):
        """Create prediction model based on type."""
        if self.model_type == "random_forest":
            self.model = RandomForestPredictor(
                n_estimators=100,
                max_depth=15,
                task="classification"
            )
        elif self.model_type == "xgboost":
            self.model = XGBoostPredictor(
                n_estimators=100,
                max_depth=8,
                task="classification"
            )
        elif self.model_type == "ensemble":
            ensemble = EnsemblePredictor()
            ensemble.add_model(
                RandomForestPredictor(n_estimators=100, max_depth=15, task="classification"),
                weight=0.4
            )
            ensemble.add_model(
                XGBoostPredictor(n_estimators=100, max_depth=8, task="classification"),
                weight=0.6
            )
            self.model = ensemble
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        failure_times: Optional[np.ndarray] = None
    ):
        """Train failure prediction model."""
        self._create_model()
        
        if self.model is None:
            logger.error("Failed to create model")
            return
        
        logger.info(f"Training failure predictor on {len(X)} samples")
        self.model.train(X, y)
        self.is_trained = True
        
        # Train time-to-failure model if data available
        if failure_times is not None:
            self.time_model = RandomForestPredictor(task="regression")
            self.time_model.train(X, failure_times)
    
    def predict(self, X: np.ndarray) -> List[PredictionResult]:
        """Predict failure for current state."""
        if not self.is_trained or self.model is None:
            logger.error("Model not trained")
            return []
        
        # Predict failure mode
        mode_probs = self.model.predict_proba(X)
        failure_mode_idx = np.argmax(mode_probs, axis=1)
        failure_mode = self.failure_modes[failure_mode_idx[0]]
        
        # Predict time to failure if time model exists
        if hasattr(self, 'time_model'):
            ttf = self.time_model.predict(X)[0]
        else:
            # Estimate from current metrics
            ttf = self._estimate_time_to_failure(X[0])
        
        # Calculate confidence
        confidence = np.max(mode_probs)
        
        result = PredictionResult(
            time_to_failure=ttf,
            confidence=confidence,
            failure_mode=failure_mode,
            probability=confidence,
            details={
                'all_probabilities': {
                    mode: prob for mode, prob in zip(self.failure_modes, mode_probs[0])
                }
            }
        )
        
        return [result]
    
    def _estimate_time_to_failure(self, features: np.ndarray) -> float:
        """Estimate time to failure from current metrics."""
        # Simplified estimation based on research paper
        # In production, use trained model
        
        # Extract parameters
        alsa = features[1]  # ALSA
        ffd = features[3]   # FFD
        ccf = features[5]   # CCF
        
        # Research-based estimation
        if alsa > 0.9 or ffd > 8.0 or ccf > 100:
            return 1.5  # 1.5 months
        elif alsa > 0.75 or ffd > 5.0 or ccf > 70:
            return 4.0  # 4 months
        elif alsa > 0.6 or ffd > 3.0 or ccf > 40:
            return 9.0  # 9 months
        else:
            return 24.0  # 2 years


class RemainingLifePredictor:
    """Predict remaining service life of bridges."""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
        
        # Create ensemble of regressors
        self.model = EnsemblePredictor()
        self.model.add_model(
            RandomForestPredictor(n_estimators=100, max_depth=15, task="regression"),
            weight=0.5
        )
        self.model.add_model(
            XGBoostPredictor(n_estimators=100, max_depth=8, task="regression"),
            weight=0.5
        )
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,  # remaining life in years
        validation_split: float = 0.2
    ):
        """Train remaining life prediction model."""
        logger.info(f"Training remaining life predictor on {len(X)} samples")
        self.model.train(X, y, validation_split=validation_split)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> List[RemainingLifeResult]:
        """Predict remaining life for current state."""
        if not self.is_trained or self.model is None:
            logger.error("Model not trained")
            return []
        
        # Point prediction
        years_pred = self.model.predict(X)[0]
        
        # Uncertainty estimation
        if hasattr(self.model, 'predict_with_uncertainty'):
            _, uncertainty = self.model.predict_with_uncertainty(X)
            ci_lower = years_pred - 1.96 * uncertainty[0]
            ci_upper = years_pred + 1.96 * uncertainty[0]
        else:
            # Approximate confidence interval
            ci_lower = years_pred * 0.8
            ci_upper = years_pred * 1.2
        
        # Determine health trajectory from recent trends
        trajectory = self._determine_trajectory(X[0])
        
        # Recommended action based on remaining life
        if years_pred < 2:
            action = "IMMEDIATE INTERVENTION REQUIRED"
        elif years_pred < 5:
            action = "Plan major rehabilitation within 2 years"
        elif years_pred < 10:
            action = "Increase monitoring frequency"
        else:
            action = "Continue routine monitoring"
        
        result = RemainingLifeResult(
            years_remaining=years_pred,
            confidence_interval=(ci_lower, ci_upper),
            health_trajectory=trajectory,
            recommended_action=action,
            details={
                'prediction_uncertainty': uncertainty[0] if 'uncertainty' in locals() else years_pred * 0.2,
                'confidence_level': 0.95
            }
        )
        
        return [result]
    
    def _determine_trajectory(self, features: np.ndarray) -> str:
        """Determine health trajectory from features."""
        # Simplified - in production, use trend analysis
        ffd = features[3]  # FFD
        alsa = features[1]  # ALSA
        
        if ffd < -0.5 or alsa < -0.1:
            return "improving"
        elif ffd > 1.0 or alsa > 0.1:
            return "degrading"
        else:
            return "stable"
    
    def batch_predict(self, X_list: List[np.ndarray]) -> List[RemainingLifeResult]:
        """Predict for multiple bridges."""
        results = []
        for X in X_list:
            results.extend(self.predict(X.reshape(1, -1)))
        return results
