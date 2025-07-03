#!/usr/bin/env python3
"""
Test runner script for the bittensor subnet template.
This script runs all test files in the tests directory, excluding README and __pycache__.
"""

import unittest
import sys
import os
from pathlib import Path

def run_tests():
    """Discover and run all tests in the tests directory."""
    # Get the tests directory
    tests_dir = Path(__file__).parent / "tests"
    
    # Find all test files (files starting with test_)
    test_files = []
    for test_file in tests_dir.glob("test_*.py"):
        if test_file.is_file():
            test_files.append(str(test_file))
    
    print(f"Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  - {test_file}")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load tests from each file
    for test_file in test_files:
        try:
            # Import the test module
            module_name = os.path.relpath(test_file, os.getcwd()).replace('/', '.').replace('.py', '')
            module = __import__(module_name, fromlist=['*'])
            
            # Load tests from the module
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
            print(f"Loaded tests from {test_file}")
        except Exception as e:
            print(f"Error loading tests from {test_file}: {e}")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 