"""STALWART nine-parameter metrics calculations.

Based on research paper:
Baladi, S. et al. (2026). STALWART: Sensor-Driven Predictive Framework
for Structural Health Monitoring and Failure Prevention.
"""

import numpy as np
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass

from ..utils.constants import THRESHOLDS
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricResult:
    """Result of a metric calculation."""
    value: float
    status: str  # SAFE, WARNING, CAUTION, CRITICAL
    confidence: float  # 0-1
    details: Dict[str, Any]


# ============================================================================
# Parameter 1: Aeroelastic Flutter Coefficient (AFC)
# ============================================================================

class AFC:
    """Aeroelastic Flutter Coefficient indicator."""
    name = "AFC"
    full_name = "Aeroelastic Flutter Coefficient"
    unit = ""
    threshold = THRESHOLDS['AFC']


def calculate_afc(
    wind_speed: float,
    vertical_amplitude: float,
    damping_ratio: float,
    frequency: float,
    critical_flutter_speed: float,
    design_amplitude: float,
    design_damping: float,
    design_frequency: float
) -> MetricResult:
    """Calculate Aeroelastic Flutter Coefficient."""
    VR = wind_speed / critical_flutter_speed
    AR = np.sqrt(vertical_amplitude / design_amplitude) if design_amplitude > 0 else 0
    DR = 1 - (damping_ratio / design_damping) if design_damping > 0 else 0
    FR = abs(frequency - design_frequency) / design_frequency if design_frequency > 0 else 0
    
    AFC = VR * AR * (1 + DR) * (1 + FR)
    AFC_safe = AFC * 1.1
    
    thresholds = THRESHOLDS['AFC']
    if AFC_safe < thresholds['warning']:
        status = "SAFE"
    elif AFC_safe < thresholds['caution']:
        status = "WARNING"
    elif AFC_safe < thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(AFC_safe, status, 0.9, {
        'velocity_ratio': VR,
        'amplitude_ratio': AR,
        'damping_reduction': DR,
        'frequency_shift': FR
    })


# ============================================================================
# Parameter 2: Axle Load Strain Accumulation (ALSA)
# ============================================================================

class ALSA:
    """Axle Load Strain Accumulation indicator."""
    name = "ALSA"
    full_name = "Axle Load Strain Accumulation"
    unit = ""
    threshold = THRESHOLDS['ALSA']


def calculate_alsa(
    strain_measurements: np.ndarray,
    yield_strain: float,
    design_cycles: int = 100_000_000
) -> MetricResult:
    """Calculate Axle Load Strain Accumulation."""
    try:
        from rainflow import count_cycles
        HAS_RAINFLOW = True
    except ImportError:
        HAS_RAINFLOW = False
        ALSA = np.mean(strain_measurements) / yield_strain
        return MetricResult(ALSA, "WARNING", 0.5, {"note": "simplified calculation"})
    
    E = 200e9
    stress = strain_measurements * 1e-6 * E / 1e6
    
    cycles = count_cycles(stress)
    
    D_total = 0.0
    for cycle in cycles:
        if len(cycle) == 3:
            stress_range, _, n_cycles = cycle
        elif len(cycle) == 2:
            stress_range, n_cycles = cycle
        else:
            continue
        
        if stress_range > 0:
            N_f = 2e12 / (stress_range ** 3)
            D_total += n_cycles / N_f
    
    if len(strain_measurements) > 0:
        ALSA = D_total * design_cycles / len(strain_measurements)
    else:
        ALSA = 0.0
    
    thresholds = THRESHOLDS['ALSA']
    if ALSA < thresholds['warning']:
        status = "SAFE"
    elif ALSA < thresholds['caution']:
        status = "WARNING"
    elif ALSA < thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(ALSA, status, 0.9, {
        'damage_total': D_total,
        'cycles_counted': len(cycles)
    })


# ============================================================================
# Parameter 3: Cable/Pier Integrity Index (CPII)
# ============================================================================

class CPII:
    """Cable/Pier Integrity Index indicator."""
    name = "CPII"
    full_name = "Cable/Pier Integrity Index"
    unit = ""
    threshold = THRESHOLDS['CPII']


def calculate_cpii(
    wire_breaks: Optional[int] = None,
    total_wires: Optional[int] = None,
    bridge_type: str = "cable_stayed",
    **kwargs
) -> MetricResult:
    """Calculate Cable/Pier Integrity Index."""
    if bridge_type in ['cable_stayed', 'suspension'] and wire_breaks and total_wires:
        N_critical = int(0.02 * total_wires)
        CPII = 1 - (wire_breaks / N_critical)
    else:
        CPII = 1.0
    
    thresholds = THRESHOLDS['CPII']
    if CPII > thresholds['warning']:
        status = "SAFE"
    elif CPII > thresholds['caution']:
        status = "WARNING"
    elif CPII > thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(CPII, status, 0.85, {})


# ============================================================================
# Parameter 4: Fundamental Frequency Drift (FFD)
# ============================================================================

class FFD:
    """Fundamental Frequency Drift indicator."""
    name = "FFD"
    full_name = "Fundamental Frequency Drift"
    unit = "%"
    threshold = THRESHOLDS['FFD']


def calculate_ffd(
    current_frequency: float,
    baseline_frequency: float,
    temperature: Optional[float] = None,
    reference_temperature: Optional[float] = None,
    **kwargs
) -> MetricResult:
    """Calculate Fundamental Frequency Drift."""
    if temperature and reference_temperature:
        delta_T = temperature - reference_temperature
        frequency_corrected = current_frequency * (1 + 0.0002 * delta_T)
    else:
        frequency_corrected = current_frequency
    
    FFD = (frequency_corrected - baseline_frequency) / baseline_frequency * 100
    
    thresholds = THRESHOLDS['FFD']
    abs_ffd = abs(FFD)
    
    if abs_ffd < thresholds['warning']:
        status = "SAFE"
    elif abs_ffd < thresholds['caution']:
        status = "WARNING"
    elif abs_ffd < thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(FFD, status, 0.95, {})


# ============================================================================
# Parameter 5: Locked-in Thermal Stress (LTS)
# ============================================================================

class LTS:
    """Locked-in Thermal Stress indicator."""
    name = "LTS"
    full_name = "Locked-in Thermal Stress"
    unit = "% of yield"
    threshold = THRESHOLDS['LTS']


def calculate_lts(
    temperature_delta: float,
    measured_expansion: float,
    expected_expansion: float,
    **kwargs
) -> MetricResult:
    """Calculate Locked-in Thermal Stress."""
    joint_efficiency = measured_expansion / expected_expansion if expected_expansion > 0 else 1
    thermal_stress = 200e9 * 12e-6 * temperature_delta * (1 - joint_efficiency)
    LTS = thermal_stress / 350e6 * 100
    
    thresholds = THRESHOLDS['LTS']
    if LTS < thresholds['warning']:
        status = "SAFE"
    elif LTS < thresholds['caution']:
        status = "WARNING"
    elif LTS < thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(LTS, status, 0.9, {})


# ============================================================================
# Parameter 6: Chloride/Carbonation Flux (CCF)
# ============================================================================

class CCF:
    """Chloride/Carbonation Flux indicator."""
    name = "CCF"
    full_name = "Chloride/Carbonation Flux"
    unit = "%"
    threshold = THRESHOLDS['CCF']


def calculate_ccf(
    chloride_concentration: Optional[float] = None,
    carbonation_depth: Optional[float] = None,
    concrete_cover: Optional[float] = None,
    **kwargs
) -> MetricResult:
    """Calculate Chloride/Carbonation Flux."""
    ccf_values = []
    if chloride_concentration:
        ccf_values.append(chloride_concentration / 0.4 * 100)
    if carbonation_depth and concrete_cover:
        ccf_values.append(carbonation_depth / concrete_cover * 100)
    
    CCF = max(ccf_values) if ccf_values else 0.0
    
    thresholds = THRESHOLDS['CCF']
    if CCF < thresholds['warning']:
        status = "SAFE"
    elif CCF < thresholds['caution']:
        status = "WARNING"
    elif CCF < thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(CCF, status, 0.85, {})


# ============================================================================
# Parameter 7: Transient Vibration Response (TVR)
# ============================================================================

class TVR:
    """Transient Vibration Response indicator."""
    name = "TVR"
    full_name = "Transient Vibration Response"
    unit = ""
    threshold = THRESHOLDS['TVR']


def calculate_tvr(
    current_damping: float,
    baseline_damping: float,
    current_decay_time: float,
    baseline_decay_time: float
) -> MetricResult:
    """Calculate Transient Vibration Response."""
    damping_ratio = current_damping / baseline_damping
    decay_ratio = baseline_decay_time / current_decay_time
    
    TVR = damping_ratio * decay_ratio
    TVR = max(0.1, min(1.0, TVR))
    
    thresholds = THRESHOLDS['TVR']
    if TVR > thresholds['warning']:
        status = "SAFE"
    elif TVR > thresholds['caution']:
        status = "WARNING"
    elif TVR > thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(TVR, status, 0.9, {})


# ============================================================================
# Parameter 8: Bearing Displacement (BD)
# ============================================================================

class BD:
    """Bearing Displacement indicator."""
    name = "BD"
    full_name = "Bearing Displacement"
    unit = "mm"
    threshold = THRESHOLDS['BD']


def calculate_bd(
    displacement: float,
    displacement_capacity: float,
    **kwargs
) -> MetricResult:
    """Calculate Bearing Displacement."""
    BD = abs(displacement) / displacement_capacity * 100 if displacement_capacity > 0 else 0
    
    thresholds = THRESHOLDS['BD']
    if BD < thresholds['warning']:
        status = "SAFE"
    elif BD < thresholds['caution']:
        status = "WARNING"
    elif BD < thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(BD, status, 0.95, {})


# ============================================================================
# Parameter 9: Strain Energy Density (SED)
# ============================================================================

class SED:
    """Strain Energy Density indicator."""
    name = "SED"
    full_name = "Strain Energy Density"
    unit = "%"
    threshold = THRESHOLDS['SED']


def calculate_sed(
    local_strain: float,
    global_strain: float,
    **kwargs
) -> MetricResult:
    """Calculate Strain Energy Density."""
    U_ratio = (local_strain / global_strain) ** 2 if global_strain > 0 else 1
    SED = U_ratio * 50  # Simplified
    
    thresholds = THRESHOLDS['SED']
    if SED < thresholds['warning']:
        status = "SAFE"
    elif SED < thresholds['caution']:
        status = "WARNING"
    elif SED < thresholds['critical']:
        status = "CAUTION"
    else:
        status = "CRITICAL"
    
    return MetricResult(SED, status, 0.85, {})


# ============================================================================
# Health Index Calculation
# ============================================================================

def calculate_health_index(metrics: Dict[str, MetricResult]) -> float:
    """Calculate overall health index."""
    weights = {
        'AFC': 0.10, 'ALSA': 0.15, 'CPII': 0.15,
        'FFD': 0.15, 'LTS': 0.10, 'CCF': 0.10,
        'TVR': 0.10, 'BD': 0.05, 'SED': 0.10
    }
    
    health = 0.0
    total_weight = 0.0
    
    for param, metric in metrics.items():
        if param in weights:
            thresholds = THRESHOLDS.get(param, {})
            inverted = thresholds.get('inverted', False)
            
            if inverted:
                param_health = metric.value * 100
            else:
                max_val = thresholds.get('max', 1.0)
                param_health = max(0, 100 - (metric.value / max_val * 100))
            
            health += weights[param] * param_health
            total_weight += weights[param]
    
    return health / total_weight if total_weight > 0 else 50.0


# List of all metric classes for easy import
METRIC_CLASSES = [AFC, ALSA, CPII, FFD, LTS, CCF, TVR, BD, SED]
METRIC_NAMES = [cls.name for cls in METRIC_CLASSES]

# Export all classes and functions
__all__ = [
    'AFC', 'ALSA', 'CPII', 'FFD', 'LTS', 'CCF', 'TVR', 'BD', 'SED',
    'MetricResult',
    'calculate_afc', 'calculate_alsa', 'calculate_cpii',
    'calculate_ffd', 'calculate_lts', 'calculate_ccf',
    'calculate_tvr', 'calculate_bd', 'calculate_sed',
    'calculate_health_index',
    'METRIC_CLASSES', 'METRIC_NAMES'
]
