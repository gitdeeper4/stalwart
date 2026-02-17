"""Constants and thresholds for STALWART."""

from typing import Dict, Any

# Parameter names
PARAMETERS = [
    'AFC',   # Aeroelastic Flutter Coefficient
    'ALSA',  # Axle Load Strain Accumulation
    'CPII',  # Cable/Pier Integrity Index
    'FFD',   # Fundamental Frequency Drift (%)
    'LTS',   # Locked-in Thermal Stress (% of yield)
    'CCF',   # Chloride/Carbonation Flux (%)
    'TVR',   # Transient Vibration Response
    'BD',    # Bearing Displacement (mm)
    'SED'    # Strain Energy Density (%)
]

# Safe thresholds for each parameter (from research paper)
THRESHOLDS: Dict[str, Dict[str, float]] = {
    'AFC': {
        'warning': 0.60,
        'caution': 0.75,
        'critical': 0.85,
        'min': 0.0,
        'max': 1.0
    },
    'ALSA': {
        'warning': 0.60,
        'caution': 0.75,
        'critical': 0.90,
        'min': 0.0,
        'max': 2.0
    },
    'CPII': {
        'warning': 0.90,
        'caution': 0.75,
        'critical': 0.60,
        'min': 0.0,
        'max': 1.0,
        'inverted': True  # Lower is worse
    },
    'FFD': {
        'warning': 3.0,
        'caution': 5.0,
        'critical': 8.0,
        'min': -1.0,
        'max': 15.0,
        'unit': '%'
    },
    'LTS': {
        'warning': 15.0,
        'caution': 30.0,
        'critical': 50.0,
        'min': 0.0,
        'max': 100.0,
        'unit': '% of yield'
    },
    'CCF': {
        'warning': 40.0,
        'caution': 70.0,
        'critical': 100.0,
        'min': 0.0,
        'max': 200.0,
        'unit': '%'
    },
    'TVR': {
        'warning': 0.85,
        'caution': 0.70,
        'critical': 0.55,
        'min': 0.0,
        'max': 1.0,
        'inverted': True
    },
    'BD': {
        'warning': 10.0,
        'caution': 15.0,
        'critical': 20.0,
        'min': -25.0,
        'max': 25.0,
        'unit': 'mm'
    },
    'SED': {
        'warning': 50.0,
        'caution': 70.0,
        'critical': 85.0,
        'min': 0.0,
        'max': 100.0,
        'unit': '%'
    }
}

# Alert levels
ALERT_LEVELS = {
    'INFO': 0,
    'WARNING': 1,
    'CAUTION': 2,
    'CRITICAL': 3,
    'EMERGENCY': 4
}

# Bridge types
BRIDGE_TYPES = [
    'suspension',
    'cable_stayed',
    'truss',
    'arch',
    'girder',
    'box_girder',
    'cantilever',
    'movable'
]

# Sensor types
SENSOR_TYPES = [
    'accelerometer',
    'strain_gauge',
    'temperature',
    'corrosion',
    'lvdt',
    'anemometer',
    'load_cell',
    'tilt'
]

# Default sampling rates (Hz)
SAMPLING_RATES = {
    'accelerometer': 100,
    'strain_gauge': 10,
    'temperature': 0.1,
    'corrosion': 0.01,
    'lvdt': 1,
    'anemometer': 4,
    'load_cell': 1,
    'tilt': 10
}

# Material properties
MATERIAL_PROPERTIES = {
    'steel': {
        'elastic_modulus': 200e9,  # Pa
        'density': 7850,  # kg/m³
        'yield_strength': 350e6,  # Pa
        'thermal_expansion': 12e-6,  # /°C
        'poisson_ratio': 0.3
    },
    'concrete': {
        'elastic_modulus': 30e9,  # Pa
        'density': 2400,  # kg/m³
        'compressive_strength': 35e6,  # Pa
        'thermal_expansion': 10e-6,  # /°C
        'poisson_ratio': 0.2
    },
    'composite': {
        'elastic_modulus': 150e9,  # Pa
        'density': 5000,  # kg/m³
        'yield_strength': 400e6,  # Pa
        'thermal_expansion': 11e-6,  # /°C
        'poisson_ratio': 0.25
    }
}

# Economic parameters (from research paper)
ECONOMIC = {
    'avg_savings_per_bridge': 3.4e6,  # $3.4M
    'installation_cost': 109675,  # $109,675
    'annual_operation_cost': 8500,  # $8,500/year
    'roi_3year': 0.435,  # 43.5% ROI over 3 years
    'payback_years': 2.1,
    'false_alarm_rate': 0.023,  # 2.3%
    'prediction_accuracy': 0.947,  # 94.7%
    'true_detection_rate': 0.981  # 98.1%
}

# Research validation (from paper)
VALIDATION = {
    'bridges_tested': 47,
    'study_months': 36,
    'sensor_readings': 4.7e9,
    'data_volume_tb': 18.4,
    'early_warning_min': 6,  # months
    'early_warning_max': 18,  # months
    'lead_time_mean': 6.8,  # months
    'lead_time_median': 6.2  # months
}

# API configuration
API_CONFIG = {
    'rate_limits': {
        'free': {'minute': 60, 'day': 1000},
        'basic': {'minute': 600, 'day': 50000},
        'pro': {'minute': 6000, 'day': 1000000}
    },
    'default_page_size': 100,
    'max_page_size': 1000,
    'timeout_seconds': 30
}

# Dashboard configuration
DASHBOARD_CONFIG = {
    'refresh_rate': 30,  # seconds
    'default_time_range': '7d',
    'chart_height': 400,
    'max_alerts_display': 100
}
