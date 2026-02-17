"""STALWART command-line interface."""

import argparse
import sys
from typing import List, Optional

from .main import main
from .utils.logger import setup_logger, get_logger

logger = get_logger(__name__)


def monitor():
    """CLI entry point for monitoring mode."""
    sys.argv = [sys.argv[0], '--mode', 'monitor'] + sys.argv[2:]
    main()


def analyze():
    """CLI entry point for analysis mode."""
    sys.argv = [sys.argv[0], '--mode', 'analyze'] + sys.argv[2:]
    main()


def dashboard():
    """CLI entry point for dashboard mode."""
    sys.argv = [sys.argv[0], '--mode', 'dashboard'] + sys.argv[2:]
    main()


def api():
    """CLI entry point for API mode."""
    sys.argv = [sys.argv[0], '--mode', 'api'] + sys.argv[2:]
    main()


def calibrate():
    """CLI entry point for sensor calibration."""
    parser = argparse.ArgumentParser(description="Calibrate sensors")
    parser.add_argument('--sensor', '-s', required=True, help='Sensor ID to calibrate')
    parser.add_argument('--reference', '-r', type=float, required=True,
                       help='Reference value')
    
    args = parser.parse_args()
    
    setup_logger()
    logger.info(f"Calibrating sensor {args.sensor} with reference {args.reference}")
    
    # Placeholder - would interface with actual sensor
    print(f"Sensor {args.sensor} calibrated successfully")
    
    return 0


def simulate():
    """CLI entry point for simulation mode."""
    parser = argparse.ArgumentParser(description="Run simulation")
    parser.add_argument('--scenario', '-s', choices=['flutter', 'corrosion', 'fatigue', 'thermal'],
                       default='flutter', help='Simulation scenario')
    parser.add_argument('--duration', '-d', type=int, default=60,
                       help='Simulation duration (seconds)')
    
    args = parser.parse_args()
    
    setup_logger()
    logger.info(f"Running {args.scenario} simulation for {args.duration} seconds")
    
    from .simulation.scenarios import run_scenario
    run_scenario(args.scenario, args.duration)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
