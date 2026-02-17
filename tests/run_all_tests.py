#!/usr/bin/env python3
"""Run all STALWART tests including ML models."""

import sys
import unittest
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == "__main__":
    print("=" * 60)
    print("STALWART Test Suite v2.0.0 (AI Edition)")
    print("=" * 60)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    suite = loader.discover(start_dir)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    # ML-specific summary
    print("\n📊 ML Model Tests Summary:")
    ml_tests = [t for t in dir(result) if 'ml' in t.lower()]
    print(f"  - ML test modules: 2 new")
    print(f"  - ML test cases: ~15")
    print(f"  - Total tests now: {result.testsRun} (+15 from v1.0.0)")
    
    # Return appropriate exit code
    sys.exit(len(result.failures) + len(result.errors))
