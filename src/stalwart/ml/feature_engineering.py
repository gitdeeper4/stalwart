"""Feature engineering for bridge sensor data."""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger(__name__)

# محاولة استيراد SciPy
try:
    from scipy import signal, stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("SciPy not installed. Using simplified feature extraction.")


class FeatureExtractor:
    """Extract features from raw sensor data for ML models."""
    
    def __init__(self, window_size: int = 3600):  # 1 hour in seconds
        self.window_size = window_size
        self.feature_names = []
    
    def extract_from_timeseries(
        self,
        data: 'pd.DataFrame',
        timestamps: List[datetime]
    ) -> np.ndarray:
        """
        Extract features from time series data.
        
        Args:
            data: DataFrame with sensor readings
            timestamps: List of timestamps
        
        Returns:
            Feature matrix
        """
        features = []
        
        # Statistical features per sensor
        for col in data.columns:
            col_features = self._extract_statistical_features(data[col].values)
            features.extend(col_features)
            self.feature_names.extend([
                f'{col}_mean', f'{col}_std', f'{col}_min', f'{col}_max',
                f'{col}_range', f'{col}_q25', f'{col}_q75'
            ])
        
        # Rate of change features
        for col in data.columns:
            diff = np.diff(data[col].values)
            if len(diff) > 0:
                features.append(np.mean(diff))
                features.append(np.std(diff))
                self.feature_names.extend([f'{col}_roc_mean', f'{col}_roc_std'])
            else:
                features.extend([0, 0])
        
        return np.array(features).reshape(1, -1)
    
    def _extract_statistical_features(self, values: np.ndarray) -> List[float]:
        """Extract statistical features from a single sensor."""
        if len(values) == 0:
            return [0.0] * 7
        
        features = [
            float(np.mean(values)),
            float(np.std(values)),
            float(np.min(values)),
            float(np.max(values)),
            float(np.max(values) - np.min(values)),  # range
            float(np.percentile(values, 25)),
            float(np.percentile(values, 75))
        ]
        
        return features
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names."""
        return self.feature_names


class SensorFusion:
    """Fuse data from multiple sensors for comprehensive analysis."""
    
    def __init__(self):
        self.sensor_types = [
            'accelerometer', 'strain_gauge', 'temperature',
            'corrosion', 'lvdt', 'anemometer'
        ]
    
    def fuse_sensor_data(
        self,
        sensor_data: Dict[str, np.ndarray]
    ) -> np.ndarray:
        """
        Fuse data from multiple sensors into a single feature vector.
        
        Args:
            sensor_data: Dictionary mapping sensor type to data array
        
        Returns:
            Fused feature vector
        """
        fused_features = []
        
        for sensor_type in self.sensor_types:
            if sensor_type in sensor_data:
                data = sensor_data[sensor_type]
                features = self._extract_sensor_features(data, sensor_type)
                fused_features.extend(features)
            else:
                # Add zeros for missing sensors
                fused_features.extend([0.0] * 6)
        
        return np.array(fused_features)
    
    def _extract_sensor_features(self, data: np.ndarray, sensor_type: str) -> List[float]:
        """Extract features specific to sensor type."""
        features = []
        
        # Common features for all sensors
        features.append(float(np.mean(data)))
        features.append(float(np.std(data)))
        features.append(float(np.min(data)))
        features.append(float(np.max(data)))
        
        # Simple additional features
        features.append(float(np.percentile(data, 75)))
        features.append(float(np.percentile(data, 25)))
        
        return features
    
    def create_synchronized_matrix(
        self,
        sensor_data: Dict[str, np.ndarray],
        timestamps: Dict[str, List[datetime]]
    ) -> Tuple[np.ndarray, List[datetime]]:
        """
        Create synchronized data matrix from multiple sensors.
        
        Args:
            sensor_data: Dictionary mapping sensor type to data array
            timestamps: Dictionary mapping sensor type to timestamps
        
        Returns:
            Tuple of (synchronized_data_matrix, common_timestamps)
        """
        # Find common time range
        all_times = []
        for sensor, times in timestamps.items():
            all_times.extend(times)
        
        if not all_times:
            return np.array([]), []
        
        # Convert timestamps to numeric
        numeric_times = {}
        for sensor, times in timestamps.items():
            numeric_times[sensor] = np.array([t.timestamp() for t in times])
        
        # Use minimum length as common
        min_len = min(len(data) for data in sensor_data.values())
        
        # Truncate all to same length
        synchronized_data = []
        for sensor, data in sensor_data.items():
            synchronized_data.append(data[:min_len])
        
        common_times = list(timestamps[list(timestamps.keys())[0]])[:min_len]
        
        return np.array(synchronized_data).T, common_times
