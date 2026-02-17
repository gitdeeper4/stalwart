"""Bridge data structures and management."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import numpy as np

from ..utils.constants import THRESHOLDS
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BridgeSpecs:
    """Bridge specifications from design."""
    name: str
    bridge_id: str
    bridge_type: str  # suspension, cable-stayed, truss, arch, girder
    span_length: float  # meters
    year_built: int
    design_life: int = 75  # years
    critical_flutter_speed: Optional[float] = None  # m/s
    design_load: Optional[float] = None  # kN
    material_type: str = "steel"  # steel, concrete, composite
    location: str = ""
    climate_zone: str = "temperate"
    daily_traffic: int = 0
    truck_percentage: float = 0.0


@dataclass
class BridgeStatus:
    """Current bridge health status."""
    bridge_id: str
    timestamp: datetime
    overall_health: float  # 0-100%
    risk_level: str  # SAFE, MONITOR, CAUTION, CRITICAL
    parameters: Dict[str, float]
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    remaining_life: Optional[float] = None  # months
    last_inspection: Optional[datetime] = None
    next_inspection: Optional[datetime] = None


class Bridge:
    """Main bridge class representing a monitored structure."""
    
    def __init__(self, specs: BridgeSpecs):
        self.specs = specs
        self.sensors = []
        self.status = None
        self.measurements = []
        self.alerts = []
        
        logger.info(f"Bridge {specs.bridge_id} initialized: {specs.name}")
    
    def add_sensor(self, sensor):
        """Add a sensor to the bridge."""
        self.sensors.append(sensor)
        logger.debug(f"Sensor {sensor.sensor_id} added to bridge {self.specs.bridge_id}")
    
    def get_sensors_by_type(self, sensor_type: str):
        """Get all sensors of a specific type."""
        return [s for s in self.sensors if s.specs.sensor_type == sensor_type]
    
    def get_parameter(self, parameter: str) -> Optional[float]:
        """Get current value of a specific parameter."""
        if self.status and self.status.parameters:
            return self.status.parameters.get(parameter)
        return None
    
    def update_status(self, measurements: List[Any]) -> BridgeStatus:
        """Update bridge health status based on new measurements."""
        from ..analysis.processor import AnalysisProcessor
        
        processor = AnalysisProcessor(self)
        self.status = processor.analyze(measurements)
        return self.status
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check for any alert conditions."""
        if not self.status:
            return []
        
        alerts = []
        for param_name, param_value in self.status.parameters.items():
            thresholds = THRESHOLDS.get(param_name, {})
            
            if thresholds:
                if param_value >= thresholds.get('critical', float('inf')):
                    level = 'CRITICAL'
                elif param_value >= thresholds.get('caution', float('inf')):
                    level = 'CAUTION'
                elif param_value >= thresholds.get('warning', float('inf')):
                    level = 'WARNING'
                else:
                    continue
                
                alert = {
                    'bridge_id': self.specs.bridge_id,
                    'timestamp': datetime.now(),
                    'parameter': param_name,
                    'value': param_value,
                    'level': level,
                    'message': f"{param_name} = {param_value:.3f} ({level})"
                }
                alerts.append(alert)
                self.alerts.append(alert)
                
                logger.warning(f"Alert: {alert['message']}")
        
        return alerts
    
    def get_remaining_life(self) -> Optional[float]:
        """Estimate remaining service life in months."""
        if not self.status:
            return None
        
        features = self._extract_features()
        # Placeholder - would use actual ML model
        return 120.0  # 10 years
    
    def _extract_features(self) -> np.ndarray:
        """Extract feature vector for ML models."""
        features = []
        
        # Add bridge specifications
        features.append(self.specs.span_length / 1000)  # normalize
        features.append(self.specs.year_built / 2000)  # normalize
        features.append(self.specs.daily_traffic / 100000)  # normalize
        
        # Add current parameters
        if self.status:
            for param in ['AFC', 'ALSA', 'CPII', 'FFD', 'LTS', 'CCF', 'TVR', 'BD', 'SED']:
                features.append(self.status.parameters.get(param, 0.0))
        
        return np.array(features).reshape(1, -1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'specs': {
                'bridge_id': self.specs.bridge_id,
                'name': self.specs.name,
                'bridge_type': self.specs.bridge_type,
                'span_length': self.specs.span_length,
                'year_built': self.specs.year_built
            },
            'sensors': [s.to_dict() for s in self.sensors],
            'status': {
                'timestamp': self.status.timestamp.isoformat() if self.status else None,
                'overall_health': self.status.overall_health if self.status else None,
                'risk_level': self.status.risk_level if self.status else None,
                'parameters': self.status.parameters if self.status else {}
            } if self.status else None,
            'alerts': self.alerts[-10:]  # last 10 alerts
        }
    
    def save_to_file(self, filename: str):
        """Save bridge data to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Bridge data saved to {filename}")
    
    @classmethod
    def load_from_file(cls, filename: str):
        """Load bridge data from JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        specs = BridgeSpecs(**data['specs'])
        bridge = cls(specs)
        return bridge
