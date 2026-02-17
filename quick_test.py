#!/usr/bin/env python3
"""Quick test for STALWART core functionality."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from src.stalwart.core.bridge import Bridge, BridgeSpecs
from src.stalwart.core.sensor import Accelerometer, StrainGauge
from src.stalwart.analysis.metrics import calculate_afc, calculate_ffd
from src.stalwart.utils.logger import setup_logger

def main():
    """Simple test function."""
    setup_logger()
    
    print("=" * 60)
    print("STALWART Quick Test")
    print("=" * 60)
    
    # Create test bridge
    specs = BridgeSpecs(
        name="Test Bridge",
        bridge_id="TEST-001",
        bridge_type="suspension",
        span_length=500.0,
        year_built=2000
    )
    bridge = Bridge(specs)
    
    # Add sensors
    bridge.add_sensor(Accelerometer("ACC-001", "mid-span"))
    bridge.add_sensor(StrainGauge("STR-001", "girder-1"))
    
    print(f"\n✅ Bridge created: {bridge.specs.name}")
    print(f"✅ Sensors: {len(bridge.sensors)}")
    
    # Test metric calculation
    print("\n📊 Testing AFC calculation...")
    afc = calculate_afc(
        wind_speed=15.0,
        vertical_amplitude=0.05,
        damping_ratio=0.02,
        frequency=1.2,
        critical_flutter_speed=70.0,
        design_amplitude=0.1,
        design_damping=0.024,
        design_frequency=1.2
    )
    print(f"   AFC = {afc.value:.3f} ({afc.status})")
    
    print("\n✅ Quick test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
