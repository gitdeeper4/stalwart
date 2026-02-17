"""Main analysis processor for STALWART."""

from typing import Dict, List, Optional, Any
from datetime import datetime
import numpy as np

from ..core.bridge import Bridge, BridgeStatus
from ..core.measurement import Measurement
from .metrics import (
    calculate_afc, calculate_alsa, calculate_cpii,
    calculate_ffd, calculate_lts, calculate_ccf,
    calculate_tvr, calculate_bd, calculate_sed,
    calculate_health_index, MetricResult
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnalysisProcessor:
    """Main processor for bridge health analysis."""
    
    def __init__(self, bridge: Bridge):
        self.bridge = bridge
        self.metrics_history: Dict[str, List[Dict[str, Any]]] = {
            'AFC': [], 'ALSA': [], 'CPII': [], 'FFD': [],
            'LTS': [], 'CCF': [], 'TVR': [], 'BD': [], 'SED': []
        }
    
    def analyze(self, measurements: List[Measurement]) -> BridgeStatus:
        """Analyze bridge health based on measurements."""
        logger.info(f"Analyzing bridge {self.bridge.specs.bridge_id}")
        
        sensor_data = self._organize_measurements(measurements)
        metrics = {}
        
        # Calculate metrics
        if 'accelerometer' in sensor_data:
            accel_values = [m.value for m in sensor_data['accelerometer']]
            
            # FFD
            frequency = self._estimate_frequency_simple(accel_values)
            ffd_result = calculate_ffd(
                current_frequency=frequency,
                baseline_frequency=frequency
            )
            metrics['FFD'] = ffd_result
            
            # TVR
            current_damping = self._estimate_damping_simple(accel_values)
            current_decay = self._estimate_decay_time_simple(accel_values)
            tvr_result = calculate_tvr(
                current_damping=current_damping,
                baseline_damping=0.024,
                current_decay_time=current_decay,
                baseline_decay_time=5.0
            )
            metrics['TVR'] = tvr_result
        
        if 'strain_gauge' in sensor_data:
            strain_values = [m.value for m in sensor_data['strain_gauge']]
            alsa_result = calculate_alsa(
                strain_measurements=np.array(strain_values),
                yield_strain=2000
            )
            metrics['ALSA'] = alsa_result
            
            sed_result = calculate_sed(
                local_strain=max(strain_values) if strain_values else 0,
                global_strain=np.mean(strain_values) if strain_values else 0
            )
            metrics['SED'] = sed_result
        
        # Add default metrics
        metrics['CPII'] = calculate_cpii(bridge_type=self.bridge.specs.bridge_type)
        metrics['AFC'] = calculate_afc(15.0, 0.05, 0.02, 1.2, 70.0, 0.1, 0.024, 1.2)
        metrics['LTS'] = calculate_lts(25.0, 150.0, 200.0)
        metrics['CCF'] = calculate_ccf(chloride_concentration=0.25)
        metrics['BD'] = calculate_bd(8.5, 25.0)
        
        # Calculate health index
        health_index = calculate_health_index(metrics)
        
        # Determine risk level
        risk_level = self._determine_risk_level(metrics, health_index)
        
        # Create status
        status = BridgeStatus(
            bridge_id=self.bridge.specs.bridge_id,
            timestamp=datetime.now(),
            overall_health=health_index,
            risk_level=risk_level,
            parameters={k: v.value for k, v in metrics.items()}
        )
        
        logger.info(f"Analysis complete: Health={health_index:.1f}%, Risk={risk_level}")
        
        return status
    
    def _organize_measurements(self, measurements: List[Measurement]) -> Dict[str, List[Measurement]]:
        """Organize measurements by sensor type."""
        organized = {}
        for m in measurements:
            if m.sensor_id.startswith('ACC'):
                sensor_type = 'accelerometer'
            elif m.sensor_id.startswith('STR'):
                sensor_type = 'strain_gauge'
            elif m.sensor_id.startswith('TEMP'):
                sensor_type = 'temperature'
            elif m.sensor_id.startswith('CORR'):
                sensor_type = 'corrosion'
            elif m.sensor_id.startswith('LVDT'):
                sensor_type = 'lvdt'
            elif m.sensor_id.startswith('WIND'):
                sensor_type = 'anemometer'
            else:
                sensor_type = 'unknown'
            
            if sensor_type not in organized:
                organized[sensor_type] = []
            organized[sensor_type].append(m)
        
        return organized
    
    def _estimate_damping_simple(self, values: List[float]) -> float:
        """Simple damping estimation."""
        if len(values) < 20:
            return 0.024
        
        max_val = max(abs(v) for v in values)
        min_val = min(abs(v) for v in values)
        
        if max_val + min_val > 0:
            damping = 0.5 * (max_val - min_val) / (max_val + min_val)
            # التأكد من أن القيمة أقل من 0.05 (وليس أقل من أو يساوي)
            return min(0.049, max(0.001, damping))
        
        return 0.024
    
    def _estimate_frequency_simple(self, values: List[float], fs: float = 100) -> float:
        """Simple frequency estimation."""
        if len(values) < 100:
            return 1.2
        
        values = np.array(values) - np.mean(values)
        
        zero_crossings = 0
        for i in range(1, len(values)):
            if values[i-1] * values[i] < 0:
                zero_crossings += 1
        
        if zero_crossings > 0:
            duration = len(values) / fs
            freq = (zero_crossings / 2) / duration
            return round(freq * 10) / 10
        
        return 1.2
    
    def _estimate_decay_time_simple(self, values: List[float]) -> float:
        """Simple decay time estimation."""
        if len(values) < 50:
            return 5.0
        
        max_idx = np.argmax(np.abs(values))
        max_val = abs(values[max_idx])
        
        if max_val == 0:
            return 5.0
        
        half_val = max_val * 0.5
        for i in range(max_idx, min(max_idx + 100, len(values))):
            if abs(values[i]) < half_val:
                return (i - max_idx) / 100
        
        return 5.0
    
    def _determine_risk_level(self, metrics: Dict[str, MetricResult], health_index: float) -> str:
        """
        Determine overall risk level from metrics.
        
        Risk levels (from most to least severe):
        - EMERGENCY: Critical failure imminent
        - CRITICAL: Immediate action required
        - CAUTION: Serious concerns, plan intervention
        - WARNING: Potential issues, increase monitoring
        - MONITOR: Normal variation, keep watching
        - SAFE: No concerns
        """
        
        critical_count = sum(1 for m in metrics.values() if m.status == "CRITICAL")
        caution_count = sum(1 for m in metrics.values() if m.status == "CAUTION")
        warning_count = sum(1 for m in metrics.values() if m.status == "WARNING")
        
        # Priority-based decision
        if critical_count >= 2:
            return "EMERGENCY"
        elif critical_count == 1:
            return "CRITICAL"
        elif caution_count >= 3:
            return "CAUTION"
        elif caution_count >= 1:
            return "WARNING"
        elif warning_count >= 2:
            return "WARNING"
        elif warning_count == 1:
            return "MONITOR"
        elif health_index < 60:
            return "WARNING"
        elif health_index < 75:
            return "MONITOR"
        else:
            return "SAFE"
