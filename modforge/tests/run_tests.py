

#!/usr/bin/env python3
"""Test runner for ModForge Game Mod Manager."""

import unittest
import sys
import os

def run_tests():
    """Run all tests and report results."""
    # Add the project root to the path
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')

    # Run tests with verbose output
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # Return success/failure
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

