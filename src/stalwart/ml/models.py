"""Machine Learning models for STALWART."""

import numpy as np
import pickle
from typing import Optional, List, Dict, Any, Union
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)

# Try importing ML libraries
try:
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    logger.warning("scikit-learn not installed. Using simplified models.")

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    logger.warning("XGBoost not installed.")

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logger.warning("TensorFlow not installed.")


class RandomForestPredictor:
    """Random Forest model for bridge health prediction."""
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 15,
        random_state: int = 42,
        task: str = "regression"
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.task = task
        self.model = None
        self.feature_importance = None
        self.is_trained = False
        
        if HAS_SKLEARN:
            if task == "regression":
                self.model = RandomForestRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    random_state=random_state,
                    n_jobs=-1
                )
            else:
                self.model = RandomForestClassifier(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    random_state=random_state,
                    n_jobs=-1
                )
            logger.info(f"RandomForest {task} model initialized")
    
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """Train the model."""
        if HAS_SKLEARN and self.model is not None:
            self.model.fit(X, y)
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = self.model.feature_importances_
            self.is_trained = True
            logger.info(f"Model trained on {len(X)} samples")
        else:
            # Simplified training
            self.mean = np.mean(y)
            self.std = np.std(y)
            self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            return np.zeros(len(X))
        
        if HAS_SKLEARN and self.model is not None:
            return self.model.predict(X)
        else:
            return np.full(len(X), getattr(self, 'mean', 0))
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities."""
        if self.task != "classification":
            return np.zeros((len(X), 2))
        
        if HAS_SKLEARN and self.model is not None and hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            return np.ones((len(X), 2)) * 0.5
    
    def get_feature_importance(self) -> Optional[np.ndarray]:
        """Get feature importance scores."""
        return self.feature_importance
    
    def save(self, path: Union[str, Path]):
        """Save model to file."""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'task': self.task,
                'feature_importance': self.feature_importance,
                'mean': getattr(self, 'mean', None),
                'std': getattr(self, 'std', None)
            }, f)
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'RandomForestPredictor':
        """Load model from file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        instance = cls(
            n_estimators=data['n_estimators'],
            max_depth=data['max_depth'],
            task=data['task']
        )
        instance.model = data['model']
        instance.feature_importance = data.get('feature_importance')
        if 'mean' in data:
            instance.mean = data['mean']
            instance.std = data['std']
        instance.is_trained = True
        return instance


class XGBoostPredictor:
    """XGBoost model for bridge health prediction."""
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 8,
        learning_rate: float = 0.01,
        random_state: int = 42,
        task: str = "regression"
    ):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.task = task
        self.model = None
        self.is_trained = False
        
        if HAS_XGBOOST:
            if task == "regression":
                self.model = xgb.XGBRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    learning_rate=learning_rate,
                    random_state=random_state
                )
            else:
                self.model = xgb.XGBClassifier(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    learning_rate=learning_rate,
                    random_state=random_state
                )
            logger.info(f"XGBoost {task} model initialized")
    
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """Train the model."""
        if HAS_XGBOOST and self.model is not None:
            self.model.fit(X, y)
            self.is_trained = True
            logger.info(f"XGBoost trained on {len(X)} samples")
        else:
            # Simplified training
            self.mean = np.mean(y)
            self.std = np.std(y)
            self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained:
            return np.zeros(len(X))
        
        if HAS_XGBOOST and self.model is not None:
            return self.model.predict(X)
        else:
            return np.full(len(X), getattr(self, 'mean', 0))
    
    def save(self, path: Union[str, Path]):
        """Save model to file."""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'n_estimators': self.n_estimators,
                'max_depth': self.max_depth,
                'learning_rate': self.learning_rate,
                'task': self.task,
                'mean': getattr(self, 'mean', None),
                'std': getattr(self, 'std', None)
            }, f)
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'XGBoostPredictor':
        """Load model from file."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        instance = cls(
            n_estimators=data['n_estimators'],
            max_depth=data['max_depth'],
            learning_rate=data['learning_rate'],
            task=data['task']
        )
        instance.model = data['model']
        if 'mean' in data:
            instance.mean = data['mean']
            instance.std = data['std']
        instance.is_trained = True
        return instance


class LSTMPredictor:
    """LSTM neural network for time series prediction."""
    
    def __init__(
        self,
        sequence_length: int = 50,
        n_features: int = 9,
        lstm_units: List[int] = [64, 32],
        dropout: float = 0.2,
        task: str = "regression"
    ):
        self.sequence_length = sequence_length
        self.n_features = n_features
        self.lstm_units = lstm_units
        self.dropout = dropout
        self.task = task
        self.model = None
        self.is_trained = False
        
        if HAS_TENSORFLOW:
            self._build_model()
            logger.info("LSTM model initialized")
    
    def _build_model(self):
        """Build LSTM architecture."""
        if not HAS_TENSORFLOW:
            return
        
        model = keras.Sequential()
        model.add(layers.LSTM(
            self.lstm_units[0],
            return_sequences=len(self.lstm_units) > 1,
            input_shape=(self.sequence_length, self.n_features)
        ))
        model.add(layers.Dropout(self.dropout))
        
        for units in self.lstm_units[1:]:
            model.add(layers.LSTM(units, return_sequences=False))
            model.add(layers.Dropout(self.dropout))
        
        if self.task == "regression":
            model.add(layers.Dense(1))
            model.compile(optimizer='adam', loss='mse')
        else:
            model.add(layers.Dense(3, activation='softmax'))
            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        
        self.model = model
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 10, **kwargs):
        """Train the model."""
        if HAS_TENSORFLOW and self.model is not None:
            # Prepare sequences
            X_seq = self._prepare_sequences(X)
            y_seq = y[self.sequence_length-1:]
            
            self.model.fit(X_seq, y_seq, epochs=epochs, verbose=0)
            self.is_trained = True
            logger.info(f"LSTM trained for {epochs} epochs")
    
    def _prepare_sequences(self, X: np.ndarray) -> np.ndarray:
        """Prepare sequences for LSTM."""
        n_samples = len(X) - self.sequence_length + 1
        X_seq = np.zeros((n_samples, self.sequence_length, self.n_features))
        for i in range(n_samples):
            X_seq[i] = X[i:i+self.sequence_length]
        return X_seq
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        if not self.is_trained or self.model is None:
            return np.zeros(len(X))
        
        X_seq = self._prepare_sequences(X)
        return self.model.predict(X_seq, verbose=0).flatten()


class EnsemblePredictor:
    """Ensemble of multiple ML models."""
    
    def __init__(self):
        self.models = []
        self.weights = []
        self.is_trained = False
    
    def add_model(self, model: Any, weight: float = 1.0):
        """Add a model to the ensemble."""
        self.models.append(model)
        self.weights.append(weight)
    
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """Train all models."""
        for model in self.models:
            model.train(X, y, **kwargs)
        self.is_trained = True
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Ensemble prediction (weighted average)."""
        if not self.models or not self.is_trained:
            return np.zeros(len(X))
        
        predictions = []
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        # Normalize weights
        weights = np.array(self.weights) / sum(self.weights)
        
        # Weighted average
        ensemble_pred = np.zeros_like(predictions[0])
        for pred, w in zip(predictions, weights):
            ensemble_pred += w * pred
        
        return ensemble_pred
    
    def predict_with_uncertainty(self, X: np.ndarray) -> tuple:
        """Predict with uncertainty estimation."""
        predictions = []
        for model in self.models:
            pred = model.predict(X)
            predictions.append(pred)
        
        predictions = np.array(predictions)
        mean_pred = np.mean(predictions, axis=0)
        std_pred = np.std(predictions, axis=0)
        
        return mean_pred, std_pred


__all__ = [
    'RandomForestPredictor',
    'XGBoostPredictor',
    'LSTMPredictor',
    'EnsemblePredictor'
]
