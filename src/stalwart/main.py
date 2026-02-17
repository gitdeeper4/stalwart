"""STALWART main entry point."""

import argparse
import sys
from pathlib import Path

from .utils.logger import setup_logger, get_logger
from .utils.config import load_config
from .core.bridge import Bridge, BridgeSpecs
from .core.sensor import (
    Accelerometer, StrainGauge, TemperatureSensor,
    CorrosionProbe, LVDT, Anemometer
)
from .analysis.processor import AnalysisProcessor
from .api.app import start_api
from .dashboard.app import start_dashboard

logger = get_logger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="STALWART Bridge Monitoring System")
    parser.add_argument('--config', '-c', type=str, default='./config/config.yml',
                       help='Configuration file path')
    parser.add_argument('--mode', '-m', choices=['monitor', 'analyze', 'api', 'dashboard'],
                       default='monitor', help='Operation mode')
    parser.add_argument('--bridge', '-b', type=str, help='Bridge ID to monitor')
    parser.add_argument('--duration', '-d', type=int, default=60,
                       help='Monitoring duration in seconds')
    parser.add_argument('--port', '-p', type=int, help='API/Dashboard port')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='API/Dashboard host')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = 'DEBUG' if args.debug else 'INFO'
    setup_logger(level=log_level, log_file='./logs/stalwart.log')
    
    logger.info("STALWART v1.0.0 starting...")
    logger.info(f"Mode: {args.mode}")
    
    # Load configuration
    config = load_config(args.config)
    
    if args.mode == 'api':
        # Start API server
        port = args.port or config.api.port
        start_api(host=args.host, port=port, debug=args.debug)
    
    elif args.mode == 'dashboard':
        # Start dashboard
        port = args.port or config.dashboard.port
        start_dashboard(host=args.host, port=port, debug=args.debug)
    
    elif args.mode in ['monitor', 'analyze']:
        # Create test bridge if none specified
        if not args.bridge:
            logger.info("No bridge specified, creating test bridge")
            bridge = create_test_bridge()
        else:
            # Load bridge from database/file
            bridge = load_bridge(args.bridge)
        
        if args.mode == 'monitor':
            # Continuous monitoring
            monitor_bridge(bridge, args.duration)
        else:
            # One-time analysis
            analyze_bridge(bridge)
    
    return 0


def create_test_bridge() -> Bridge:
    """Create a test bridge with sample sensors."""
    
    specs = BridgeSpecs(
        name="Test Bridge",
        bridge_id="TEST-001",
        bridge_type="suspension",
        span_length=500.0,
        year_built=2000,
        critical_flutter_speed=70.0,
        location="Test Location",
        daily_traffic=50000,
        truck_percentage=10.0
    )
    
    bridge = Bridge(specs)
    
    # Add sensors
    for i in range(6):
        bridge.add_sensor(Accelerometer(f"ACC-00{i}", f"mid-span-{i}"))
    
    for i in range(4):
        bridge.add_sensor(StrainGauge(f"STR-00{i}", f"girder-{i}"))
    
    for i in range(3):
        bridge.add_sensor(TemperatureSensor(f"TEMP-00{i}", f"deck-{i}"))
    
    bridge.add_sensor(CorrosionProbe("CORR-001", "pier-1"))
    bridge.add_sensor(LVDT("LVDT-001", "joint-1"))
    bridge.add_sensor(Anemometer("WIND-001", "mid-span"))
    
    logger.info(f"Test bridge created with {len(bridge.sensors)} sensors")
    return bridge


def load_bridge(bridge_id: str) -> Bridge:
    """Load bridge from database or file."""
    # Placeholder - would load from database
    logger.info(f"Loading bridge {bridge_id}...")
    return create_test_bridge()


def monitor_bridge(bridge: Bridge, duration: int):
    """Continuous bridge monitoring."""
    import time
    
    logger.info(f"Starting continuous monitoring for {duration} seconds")
    logger.info("Press Ctrl+C to stop")
    
    processor = AnalysisProcessor(bridge)
    
    try:
        start_time = time.time()
        while time.time() - start_time < duration:
            # Read sensors
            measurements = []
            for sensor in bridge.sensors:
                try:
                    value = sensor.read()
                    from .core.measurement import Measurement
                    m = Measurement(
                        sensor_id=sensor.sensor_id,
                        bridge_id=bridge.specs.bridge_id,
                        timestamp=datetime.now(),
                        value=value,
                        unit="unknown"
                    )
                    measurements.append(m)
                except Exception as e:
                    logger.error(f"Error reading sensor {sensor.sensor_id}: {e}")
            
            # Analyze
            status = processor.analyze(measurements)
            
            # Check alerts
            alerts = bridge.check_alerts()
            
            # Display status
            print(f"\n[{status.timestamp.strftime('%H:%M:%S')}] "
                  f"Health: {status.overall_health:.1f}% "
                  f"Risk: {status.risk_level}")
            
            time.sleep(10)  # Monitor every 10 seconds
    
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    
    logger.info("Monitoring complete")


def analyze_bridge(bridge: Bridge):
    """One-time bridge analysis."""
    logger.info("Performing one-time analysis...")
    
    # Read all sensors once
    measurements = []
    for sensor in bridge.sensors:
        try:
            value = sensor.read()
            from .core.measurement import Measurement
            from datetime import datetime
            m = Measurement(
                sensor_id=sensor.sensor_id,
                bridge_id=bridge.specs.bridge_id,
                timestamp=datetime.now(),
                value=value,
                unit="unknown"
            )
            measurements.append(m)
        except Exception as e:
            logger.error(f"Error reading sensor {sensor.sensor_id}: {e}")
    
    # Analyze
    processor = AnalysisProcessor(bridge)
    status = processor.analyze(measurements)
    
    # Display results
    print("\n" + "="*60)
    print(f"BRIDGE ANALYSIS: {bridge.specs.name} ({bridge.specs.bridge_id})")
    print("="*60)
    print(f"Timestamp: {status.timestamp}")
    print(f"Overall Health: {status.overall_health:.1f}%")
    print(f"Risk Level: {status.risk_level}")
    print("-"*60)
    print("Parameters:")
    for param, value in status.parameters.items():
        print(f"  {param}: {value:.3f}")
    print("="*60)


if __name__ == "__main__":
    sys.exit(main())
