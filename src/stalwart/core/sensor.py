"""Sensor data structures and interfaces."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SensorSpecs:
    """Sensor specifications."""
    sensor_type: str  # accelerometer, strain_gauge, temperature, corrosion, lvdt, anemometer, load_cell, tilt
    model: str
    manufacturer: str
    range_min: float
    range_max: float
    accuracy: float
    resolution: float
    sampling_rate: float  # Hz
    output_type: str  # analog, digital, i2c, spi, rs485
    power_consumption: float  # mW
    ip_rating: str  # IP67, etc.
    calibration_date: Optional[datetime] = None
    calibration_due: Optional[datetime] = None


class Sensor:
    """Base sensor class."""
    
    def __init__(self, sensor_id: str, specs: SensorSpecs, location: str = ""):
        self.sensor_id = sensor_id
        self.specs = specs
        self.location = location
        self.bridge_id = None
        self.last_reading = None
        self.last_reading_time = None
        self.readings = []
        self.status = "active"  # active, inactive, error, calibrating
        self.error_count = 0
        
        logger.info(f"Sensor {sensor_id} initialized: {specs.sensor_type}")
    
    def read(self) -> Optional[float]:
        """Read current sensor value."""
        # This would interface with actual hardware
        # Placeholder implementation
        import random
        value = random.uniform(self.specs.range_min, self.specs.range_max)
        
        self.last_reading = value
        self.last_reading_time = datetime.now()
        self.readings.append((self.last_reading_time, value))
        
        # Keep only last 1000 readings in memory
        if len(self.readings) > 1000:
            self.readings = self.readings[-1000:]
        
        return value
    
    def read_batch(self, duration: float, sampling_rate: Optional[float] = None) -> List[float]:
        """Read batch of sensor data for specified duration."""
        rate = sampling_rate or self.specs.sampling_rate
        n_samples = int(duration * rate)
        
        values = []
        for _ in range(n_samples):
            values.append(self.read())
        
        return values
    
    def calibrate(self, reference_value: float):
        """Calibrate sensor against reference."""
        current_value = self.read()
        offset = reference_value - current_value
        
        # Update calibration
        self.specs.calibration_date = datetime.now()
        
        logger.info(f"Sensor {self.sensor_id} calibrated: offset = {offset:.6f}")
        return offset
    
    def check_health(self) -> Dict[str, Any]:
        """Check sensor health status."""
        health = {
            'sensor_id': self.sensor_id,
            'status': self.status,
            'error_count': self.error_count,
            'last_reading': self.last_reading,
            'last_reading_time': self.last_reading_time,
            'calibration_due': self.specs.calibration_due,
            'readings_count': len(self.readings)
        }
        
        # Check if calibration is overdue
        if self.specs.calibration_due and datetime.now() > self.specs.calibration_due:
            health['warning'] = "Calibration overdue"
            self.status = "warning"
        
        return health
    
    def reset(self):
        """Reset sensor to initial state."""
        self.readings = []
        self.error_count = 0
        self.status = "active"
        logger.info(f"Sensor {self.sensor_id} reset")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'sensor_id': self.sensor_id,
            'sensor_type': self.specs.sensor_type,
            'model': self.specs.model,
            'manufacturer': self.specs.manufacturer,
            'location': self.location,
            'bridge_id': self.bridge_id,
            'status': self.status,
            'last_reading': self.last_reading,
            'last_reading_time': self.last_reading_time.isoformat() if self.last_reading_time else None
        }


class Accelerometer(Sensor):
    """Accelerometer sensor for vibration monitoring."""
    
    def __init__(self, sensor_id: str, location: str = "", **kwargs):
        specs = SensorSpecs(
            sensor_type="accelerometer",
            model=kwargs.get('model', "MEMS-100"),
            manufacturer=kwargs.get('manufacturer', "Microstrain"),
            range_min=kwargs.get('range_min', -2.0),
            range_max=kwargs.get('range_max', 2.0),
            accuracy=kwargs.get('accuracy', 0.001),
            resolution=kwargs.get('resolution', 0.0001),
            sampling_rate=kwargs.get('sampling_rate', 100.0),
            output_type=kwargs.get('output_type', "i2c"),
            power_consumption=kwargs.get('power', 50.0),
            ip_rating=kwargs.get('ip_rating', "IP67")
        )
        super().__init__(sensor_id, specs, location)
    
    def get_fft(self, duration: float = 10.0) -> tuple:
        """Get FFT of accelerometer data."""
        data = self.read_batch(duration, 100)
        from scipy import fft
        
        n = len(data)
        freqs = fft.fftfreq(n, 1/100)
        fft_vals = np.abs(fft.fft(data))
        
        # Return positive frequencies only
        positive = freqs > 0
        return freqs[positive], fft_vals[positive]


class StrainGauge(Sensor):
    """Fiber Bragg Grating strain gauge."""
    
    def __init__(self, sensor_id: str, location: str = "", **kwargs):
        specs = SensorSpecs(
            sensor_type="strain_gauge",
            model=kwargs.get('model', "FBG-2000"),
            manufacturer=kwargs.get('manufacturer', "Micron Optics"),
            range_min=kwargs.get('range_min', -5000.0),
            range_max=kwargs.get('range_max', 5000.0),
            accuracy=kwargs.get('accuracy', 1.0),
            resolution=kwargs.get('resolution', 0.1),
            sampling_rate=kwargs.get('sampling_rate', 10.0),
            output_type=kwargs.get('output_type', "optical"),
            power_consumption=kwargs.get('power', 20.0),
            ip_rating=kwargs.get('ip_rating', "IP68")
        )
        super().__init__(sensor_id, specs, location)


class TemperatureSensor(Sensor):
    """RTD temperature sensor."""
    
    def __init__(self, sensor_id: str, location: str = "", **kwargs):
        specs = SensorSpecs(
            sensor_type="temperature",
            model=kwargs.get('model', "PT100"),
            manufacturer=kwargs.get('manufacturer', "Omega"),
            range_min=kwargs.get('range_min', -50.0),
            range_max=kwargs.get('range_max', 150.0),
            accuracy=kwargs.get('accuracy', 0.1),
            resolution=kwargs.get('resolution', 0.01),
            sampling_rate=kwargs.get('sampling_rate', 1.0),
            output_type=kwargs.get('output_type', "rtd"),
            power_consumption=kwargs.get('power', 5.0),
            ip_rating=kwargs.get('ip_rating', "IP67")
        )
        super().__init__(sensor_id, specs, location)


class CorrosionProbe(Sensor):
    """Electrochemical corrosion probe."""
    
    def __init__(self, sensor_id: str, location: str = "", **kwargs):
        specs = SensorSpecs(
            sensor_type="corrosion",
            model=kwargs.get('model', "iCOR-100"),
            manufacturer=kwargs.get('manufacturer', "Giatec"),
            range_min=kwargs.get('range_min', 0.1),
            range_max=kwargs.get('range_max', 1000.0),
            accuracy=kwargs.get('accuracy', 10.0),
            resolution=kwargs.get('resolution', 0.1),
            sampling_rate=kwargs.get('sampling_rate', 0.01),  # 1 per 100 seconds
            output_type=kwargs.get('output_type', "i2c"),
            power_consumption=kwargs.get('power', 100.0),
            ip_rating=kwargs.get('ip_rating', "IP68")
        )
        super().__init__(sensor_id, specs, location)


class LVDT(Sensor):
    """Linear Variable Differential Transformer for displacement."""
    
    def __init__(self, sensor_id: str, location: str = "", **kwargs):
        specs = SensorSpecs(
            sensor_type="lvdt",
            model=kwargs.get('model', "LD620-25"),
            manufacturer=kwargs.get('manufacturer', "Omega"),
            range_min=kwargs.get('range_min', -25.0),
            range_max=kwargs.get('range_max', 25.0),
            accuracy=kwargs.get('accuracy', 0.01),
            resolution=kwargs.get('resolution', 0.001),
            sampling_rate=kwargs.get('sampling_rate', 1.0),
            output_type=kwargs.get('output_type', "analog"),
            power_consumption=kwargs.get('power', 25.0),
            ip_rating=kwargs.get('ip_rating', "IP67")
        )
        super().__init__(sensor_id, specs, location)


class Anemometer(Sensor):
    """Ultrasonic anemometer for wind measurement."""
    
    def __init__(self, sensor_id: str, location: str = "", **kwargs):
        specs = SensorSpecs(
            sensor_type="anemometer",
            model=kwargs.get('model', "WindSonic"),
            manufacturer=kwargs.get('manufacturer', "Gill"),
            range_min=kwargs.get('range_min', 0.0),
            range_max=kwargs.get('range_max', 60.0),
            accuracy=kwargs.get('accuracy', 0.1),
            resolution=kwargs.get('resolution', 0.01),
            sampling_rate=kwargs.get('sampling_rate', 4.0),
            output_type=kwargs.get('output_type', "rs232"),
            power_consumption=kwargs.get('power', 40.0),
            ip_rating=kwargs.get('ip_rating', "IP66")
        )
        super().__init__(sensor_id, specs, location)


class SensorArray:
    """Array of sensors for coordinated monitoring."""
    
    def __init__(self, array_id: str, sensors: List[Sensor] = None):
        self.array_id = array_id
        self.sensors = sensors or []
        self.bridge_id = None
    
    def add_sensor(self, sensor: Sensor):
        """Add sensor to array."""
        self.sensors.append(sensor)
    
    def read_all(self) -> Dict[str, float]:
        """Read all sensors in array."""
        readings = {}
        for sensor in self.sensors:
            try:
                readings[sensor.sensor_id] = sensor.read()
            except Exception as e:
                logger.error(f"Error reading sensor {sensor.sensor_id}: {e}")
                readings[sensor.sensor_id] = None
        return readings
    
    def get_sensors_by_type(self, sensor_type: str) -> List[Sensor]:
        """Get all sensors of a specific type."""
        return [s for s in self.sensors if s.specs.sensor_type == sensor_type]
    
    def check_health(self) -> Dict[str, Any]:
        """Check health of all sensors in array."""
        health = {}
        for sensor in self.sensors:
            health[sensor.sensor_id] = sensor.check_health()
        return health
