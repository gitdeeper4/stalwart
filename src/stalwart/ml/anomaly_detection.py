"""Anomaly detection for bridge sensor data."""

import numpy as np
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from pathlib import Path
import pickle

from ..utils.logger import get_logger

logger = get_logger(__name__)

try:
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler
    from sklearn.covariance import EllipticEnvelope
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TF = True
except ImportError:
    HAS_TF = False


class IsolationForestDetector:
    """Isolation Forest for anomaly detection in sensor data."""
    
    def __init__(
        self,
        contamination: float = 0.01,
        n_estimators: int = 100,
        random_state: int = 42
    ):
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.is_trained = False
        
        if HAS_SKLEARN:
            self.model = IsolationForest(
                n_estimators=n_estimators,
                contamination=contamination,
                random_state=random_state,
                n_jobs=-1
            )
            logger.info(f"Isolation Forest initialized (contamination={contamination})")
        else:
            logger.warning("scikit-learn not available, using statistical detection")
    
    def train(self, X: np.ndarray):
        """Train the isolation forest model."""
        if HAS_SKLEARN and self.model is not None:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_trained = True
            logger.info(f"Isolation Forest trained on {len(X)} samples")
        else:
            # Statistical baseline
            self.mean = np.mean(X, axis=0)
            self.std = np.std(X, axis=0)
            self.threshold = 3.0  # 3 sigma
            self.is_trained = True
            logger.info("Statistical anomaly detector trained")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomalies (-1 for anomaly, 1 for normal)."""
        if not self.is_trained:
            logger.error("Model not trained")
            return np.ones(len(X))
        
        if HAS_SKLEARN and self.model is not None and self.scaler is not None:
            X_scaled = self.scaler.transform(X)
            return self.model.predict(X_scaled)
        else:
            # Statistical detection
            z_scores = np.abs((X - self.mean) / (self.std + 1e-8))
            is_anomaly = np.any(z_scores > self.threshold, axis=1)
            return np.where(is_anomaly, -1, 1)
    
    def score_samples(self, X: np.ndarray) -> np.ndarray:
        """Get anomaly scores (higher = more normal)."""
        if HAS_SKLEARN and self.model is not None and self.scaler is not None:
            X_scaled = self.scaler.transform(X)
            return self.model.score_samples(X_scaled)
        else:
            # Statistical scoring
            z_scores = np.abs((X - self.mean) / (self.std + 1e-8))
            return -np.max(z_scores, axis=1)
    
    def find_anomalies(
        self,
        X: np.ndarray,
        timestamps: Optional[List[datetime]] = None
    ) -> Dict[str, Any]:
        """Find and return anomalies with details."""
        predictions = self.predict(X)
        anomaly_indices = np.where(predictions == -1)[0]
        
        result = {
            'n_anomalies': len(anomaly_indices),
            'anomaly_rate': len(anomaly_indices) / len(X),
            'indices': anomaly_indices.tolist(),
            'scores': self.score_samples(X)[anomaly_indices].tolist()
        }
        
        if timestamps is not None:
            result['timestamps'] = [timestamps[i] for i in anomaly_indices]
        
        return result
    
    def save(self, path: str):
        """Save model to disk."""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'contamination': self.contamination,
                'n_estimators': self.n_estimators,
                'mean': getattr(self, 'mean', None),
                'std': getattr(self, 'std', None),
                'threshold': getattr(self, 'threshold', None)
            }, f)
        logger.info(f"Model saved to {path}")
    
    @classmethod
    def load(cls, path: str) -> 'IsolationForestDetector':
        """Load model from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
        
        detector = cls(
            contamination=data['contamination'],
            n_estimators=data['n_estimators']
        )
        detector.model = data['model']
        detector.scaler = data['scaler']
        
        if 'mean' in data:
            detector.mean = data['mean']
            detector.std = data['std']
            detector.threshold = data['threshold']
        
        detector.is_trained = True
        return detector


class AutoencoderDetector:
    """Deep learning autoencoder for anomaly detection."""
    
    def __init__(
        self,
        input_dim: int,
        encoding_dim: int = 32,
        hidden_layers: List[int] = [64, 32],
        learning_rate: float = 0.001,
        contamination: float = 0.01
    ):
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.hidden_layers = hidden_layers
        self.learning_rate = learning_rate
        self.contamination = contamination
        self.model = None
        self.threshold = None
        self.is_trained = False
        
        if HAS_TF:
            self._build_model()
            logger.info(f"Autoencoder initialized (input_dim={input_dim})")
        else:
            logger.warning("TensorFlow not available, autoencoder disabled")
    
    def _build_model(self):
        """Build autoencoder architecture."""
        if not HAS_TF:
            return
        
        # Encoder
        encoder_input = layers.Input(shape=(self.input_dim,))
        x = encoder_input
        
        for units in self.hidden_layers:
            x = layers.Dense(units, activation='relu')(x)
            x = layers.Dropout(0.2)(x)
        
        encoded = layers.Dense(self.encoding_dim, activation='relu')(x)
        
        # Decoder
        x = encoded
        for units in reversed(self.hidden_layers):
            x = layers.Dense(units, activation='relu')(x)
            x = layers.Dropout(0.2)(x)
        
        decoded = layers.Dense(self.input_dim, activation='linear')(x)
        
        # Autoencoder model
        self.autoencoder = keras.Model(encoder_input, decoded)
        
        # Encoder model (for feature extraction)
        self.encoder = keras.Model(encoder_input, encoded)
        
        # Compile
        optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
        self.autoencoder.compile(optimizer=optimizer, loss='mse')
        
        logger.info("Autoencoder architecture built")
    
    def train(
        self,
        X: np.ndarray,
        validation_split: float = 0.2,
        epochs: int = 100,
        batch_size: int = 32
    ):
        """Train the autoencoder."""
        if not HAS_TF or self.autoencoder is None:
            logger.error("Autoencoder not available")
            return
        
        # Train autoencoder
        history = self.autoencoder.fit(
            X, X,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            verbose=0
        )
        
        self.is_trained = True
        logger.info(f"Autoencoder trained for {epochs} epochs")
        
        # Calculate reconstruction error threshold
        X_pred = self.autoencoder.predict(X, verbose=0)
        reconstruction_errors = np.mean((X - X_pred) ** 2, axis=1)
        
        # Set threshold at specified percentile
        self.threshold = np.percentile(
            reconstruction_errors,
            100 * (1 - self.contamination)
        )
        
        logger.info(f"Anomaly threshold set to {self.threshold:.4f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomalies (-1 for anomaly, 1 for normal)."""
        if not self.is_trained or self.autoencoder is None:
            logger.error("Autoencoder not trained")
            return np.ones(len(X))
        
        # Calculate reconstruction error
        X_pred = self.autoencoder.predict(X, verbose=0)
        errors = np.mean((X - X_pred) ** 2, axis=1)
        
        # Classify based on threshold
        is_anomaly = errors > self.threshold
        return np.where(is_anomaly, -1, 1)
    
    def get_features(self, X: np.ndarray) -> np.ndarray:
        """Extract encoded features."""
        if self.encoder is None:
            return X
        return self.encoder.predict(X, verbose=0)
    
    def save(self, path: str):
        """Save autoencoder model."""
        if self.autoencoder is not None:
            self.autoencoder.save(path)
            logger.info(f"Autoencoder saved to {path}")
    
    @classmethod
    def load(cls, path: str, input_dim: int) -> 'AutoencoderDetector':
        """Load autoencoder model."""
        detector = cls(input_dim=input_dim)
        detector.autoencoder = keras.models.load_model(path)
        detector.encoder = keras.Model(
            detector.autoencoder.input,
            detector.autoencoder.layers[4].output  # Adjust index as needed
        )
        detector.is_trained = True
        return detector


class StatisticalDetector:
    """Statistical methods for anomaly detection."""
    
    def __init__(self, method: str = "zscore", threshold: float = 3.0):
        """
        Args:
            method: "zscore", "iqr", "mad"
            threshold: Threshold for anomaly detection
        """
        self.method = method
        self.threshold = threshold
        self.stats = {}
        self.is_trained = False
    
    def train(self, X: np.ndarray):
        """Compute statistical baselines."""
        if self.method == "zscore":
            self.stats['mean'] = np.mean(X, axis=0)
            self.stats['std'] = np.std(X, axis=0)
        elif self.method == "iqr":
            self.stats['q1'] = np.percentile(X, 25, axis=0)
            self.stats['q3'] = np.percentile(X, 75, axis=0)
            self.stats['iqr'] = self.stats['q3'] - self.stats['q1']
        elif self.method == "mad":
            self.stats['median'] = np.median(X, axis=0)
            self.stats['mad'] = np.median(np.abs(X - self.stats['median']), axis=0)
        
        self.is_trained = True
        logger.info(f"Statistical detector trained (method={self.method})")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict anomalies."""
        if not self.is_trained:
            return np.ones(len(X))
        
        if self.method == "zscore":
            z_scores = np.abs((X - self.stats['mean']) / (self.stats['std'] + 1e-8))
            is_anomaly = np.any(z_scores > self.threshold, axis=1)
        elif self.method == "iqr":
            lower = self.stats['q1'] - self.threshold * self.stats['iqr']
            upper = self.stats['q3'] + self.threshold * self.stats['iqr']
            is_anomaly = np.any((X < lower) | (X > upper), axis=1)
        elif self.method == "mad":
            mad_scores = np.abs(X - self.stats['median']) / (self.stats['mad'] + 1e-8)
            is_anomaly = np.any(mad_scores > self.threshold, axis=1)
        else:
            is_anomaly = np.zeros(len(X), dtype=bool)
        
        return np.where(is_anomaly, -1, 1)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistical baselines."""
        return self.stats
