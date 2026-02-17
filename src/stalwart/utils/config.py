"""Configuration management for STALWART."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    name: str = "stalwart"
    user: str = "stalwart_user"
    password: str = ""
    ssl_mode: str = "prefer"
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class InfluxDBConfig:
    """InfluxDB configuration."""
    url: str = "http://localhost:8086"
    token: str = ""
    org: str = "stalwart"
    bucket: str = "sensor_data"


@dataclass
class RedisConfig:
    """Redis configuration."""
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0
    
    @property
    def url(self) -> str:
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass
class APIConfig:
    """API configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    workers: int = 4
    rate_limit: str = "100/minute"
    api_key: Optional[str] = None


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    host: str = "0.0.0.0"
    port: int = 8501
    theme: str = "dark"
    refresh_rate: int = 30  # seconds


@dataclass
class SensorConfig:
    """Sensor configuration."""
    sampling_rates: Dict[str, float] = field(default_factory=dict)
    calibration_interval: int = 365  # days
    health_check_interval: int = 3600  # seconds


@dataclass
class STALWARTConfig:
    """Main configuration class."""
    
    # Environment
    env: str = "development"  # development, testing, production
    
    # Database
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    influxdb: InfluxDBConfig = field(default_factory=InfluxDBConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    
    # Services
    api: APIConfig = field(default_factory=APIConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    
    # Sensors
    sensors: SensorConfig = field(default_factory=SensorConfig)
    
    # Paths (relative to project root)
    data_dir: str = "./data"
    logs_dir: str = "./logs"
    models_dir: str = "./data/models"
    config_dir: str = "./config"
    
    # Thresholds file
    thresholds_file: str = "./config/thresholds.yml"
    
    @classmethod
    def from_file(cls, config_path: str) -> 'STALWARTConfig':
        """Load configuration from YAML file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file {config_path} not found, using defaults")
            return cls()
        
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls._from_dict(data)
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> 'STALWARTConfig':
        """Create config from dictionary."""
        config = cls()
        
        # Environment
        if 'env' in data:
            config.env = data['env']
        
        # Database
        if 'database' in data:
            db = data['database']
            config.database = DatabaseConfig(
                host=db.get('host', 'localhost'),
                port=db.get('port', 5432),
                name=db.get('name', 'stalwart'),
                user=db.get('user', 'stalwart_user'),
                password=db.get('password', ''),
                ssl_mode=db.get('ssl_mode', 'prefer')
            )
        
        # InfluxDB
        if 'influxdb' in data:
            inf = data['influxdb']
            config.influxdb = InfluxDBConfig(
                url=inf.get('url', 'http://localhost:8086'),
                token=inf.get('token', ''),
                org=inf.get('org', 'stalwart'),
                bucket=inf.get('bucket', 'sensor_data')
            )
        
        # Redis
        if 'redis' in data:
            rd = data['redis']
            config.redis = RedisConfig(
                host=rd.get('host', 'localhost'),
                port=rd.get('port', 6379),
                password=rd.get('password', ''),
                db=rd.get('db', 0)
            )
        
        # API
        if 'api' in data:
            api = data['api']
            config.api = APIConfig(
                host=api.get('host', '0.0.0.0'),
                port=api.get('port', 8000),
                debug=api.get('debug', False),
                workers=api.get('workers', 4),
                rate_limit=api.get('rate_limit', '100/minute'),
                api_key=api.get('api_key')
            )
        
        # Paths
        if 'paths' in data:
            paths = data['paths']
            config.data_dir = paths.get('data', './data')
            config.logs_dir = paths.get('logs', './logs')
            config.models_dir = paths.get('models', './data/models')
            config.config_dir = paths.get('config', './config')
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'env': self.env,
            'database': {
                'host': self.database.host,
                'port': self.database.port,
                'name': self.database.name,
                'user': self.database.user,
                'ssl_mode': self.database.ssl_mode
            },
            'influxdb': {
                'url': self.influxdb.url,
                'org': self.influxdb.org,
                'bucket': self.influxdb.bucket
            },
            'redis': {
                'host': self.redis.host,
                'port': self.redis.port,
                'db': self.redis.db
            },
            'api': {
                'host': self.api.host,
                'port': self.api.port,
                'debug': self.api.debug,
                'workers': self.api.workers,
                'rate_limit': self.api.rate_limit
            },
            'paths': {
                'data': self.data_dir,
                'logs': self.logs_dir,
                'models': self.models_dir,
                'config': self.config_dir
            }
        }


# Global config instance
_config = None


def load_config(config_file: Optional[str] = None) -> STALWARTConfig:
    """Load configuration."""
    global _config
    
    if _config is None:
        if config_file is None:
            config_file = "./config/config.yml"
        
        _config = STALWARTConfig.from_file(config_file)
        
        # Override with environment variables
        _override_from_env()
        
        logger.info(f"Configuration loaded from {config_file}")
    
    return _config


def _override_from_env():
    """Override configuration with environment variables."""
    global _config
    
    # Database
    if os.getenv('STALWART_DB_HOST'):
        _config.database.host = os.getenv('STALWART_DB_HOST')
    if os.getenv('STALWART_DB_PORT'):
        _config.database.port = int(os.getenv('STALWART_DB_PORT'))
    if os.getenv('STALWART_DB_NAME'):
        _config.database.name = os.getenv('STALWART_DB_NAME')
    if os.getenv('STALWART_DB_USER'):
        _config.database.user = os.getenv('STALWART_DB_USER')
    if os.getenv('STALWART_DB_PASSWORD'):
        _config.database.password = os.getenv('STALWART_DB_PASSWORD')
    
    # API
    if os.getenv('STALWART_API_KEY'):
        _config.api.api_key = os.getenv('STALWART_API_KEY')
    if os.getenv('STALWART_API_PORT'):
        _config.api.port = int(os.getenv('STALWART_API_PORT'))
    
    # Environment
    if os.getenv('STALWART_ENV'):
        _config.env = os.getenv('STALWART_ENV')
