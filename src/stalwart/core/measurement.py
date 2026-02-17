"""Measurement data structures."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import numpy as np
import json


@dataclass
class Measurement:
    """Single measurement from a sensor."""
    sensor_id: str
    bridge_id: str
    timestamp: datetime
    value: float
    unit: str
    quality: float = 1.0  # 0-1, 1 = excellent quality
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sensor_id': self.sensor_id,
            'bridge_id': self.bridge_id,
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'unit': self.unit,
            'quality': self.quality
        }


@dataclass
class TimeSeries:
    """Time series of measurements."""
    sensor_id: str
    bridge_id: str
    measurements: List[Measurement]
    parameter: Optional[str] = None  # AFC, ALSA, etc. if computed
    
    def __post_init__(self):
        if self.measurements:
            self.measurements.sort(key=lambda x: x.timestamp)
    
    @property
    def values(self) -> np.ndarray:
        return np.array([m.value for m in self.measurements])
    
    @property
    def timestamps(self) -> List[datetime]:
        return [m.timestamp for m in self.measurements]
    
    @property
    def start_time(self) -> Optional[datetime]:
        return self.timestamps[0] if self.measurements else None
    
    @property
    def end_time(self) -> Optional[datetime]:
        return self.timestamps[-1] if self.measurements else None
    
    @property
    def duration(self) -> Optional[float]:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def resample(self, frequency: str = '1min') -> 'TimeSeries':
        """Resample time series to specified frequency."""
        # Placeholder - would need actual resampling logic
        return self
    
    def filter(self, min_quality: float = 0.5) -> 'TimeSeries':
        """Filter measurements by quality."""
        filtered = [m for m in self.measurements if m.quality >= min_quality]
        return TimeSeries(self.sensor_id, self.bridge_id, filtered, self.parameter)
    
    def to_dataframe(self):
        """Convert to pandas DataFrame."""
        import pandas as pd
        df = pd.DataFrame([
            {'timestamp': m.timestamp, 'value': m.value, 'quality': m.quality}
            for m in self.measurements
        ])
        df.set_index('timestamp', inplace=True)
        return df
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sensor_id': self.sensor_id,
            'bridge_id': self.bridge_id,
            'parameter': self.parameter,
            'measurements': [m.to_dict() for m in self.measurements],
            'count': len(self.measurements),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }
    
    def save_to_file(self, filename: str):
        """Save time series to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filename: str):
        """Load time series from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        measurements = []
        for m_data in data['measurements']:
            m = Measurement(
                sensor_id=m_data['sensor_id'],
                bridge_id=m_data['bridge_id'],
                timestamp=datetime.fromisoformat(m_data['timestamp']),
                value=m_data['value'],
                unit=m_data['unit'],
                quality=m_data.get('quality', 1.0)
            )
            measurements.append(m)
        
        return cls(
            sensor_id=data['sensor_id'],
            bridge_id=data['bridge_id'],
            measurements=measurements,
            parameter=data.get('parameter')
        )
