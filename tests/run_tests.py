#!/usr/bin/env python
"""
Test runner script for CtrlAI.

This script runs all the unit tests for the CtrlAI application.
"""

import unittest
import sys
import os
import logging


def run_tests():
    """Run all unit tests and return the result."""
    # Disable logging during tests
    logging.disable(logging.CRITICAL)
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(os.path.dirname(__file__), pattern="test_*.py")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Re-enable logging
    logging.disable(logging.NOTSET)
    
    return result


if __name__ == "__main__":
    # Run the tests
    result = run_tests()
    
    # Print summary
    print("\nTest Summary:")
    print(f"  Ran {result.testsRun} tests")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Skipped: {len(result.skipped)}")
    
    # Exit with appropriate code
    if not result.wasSuccessful():
        sys.exit(1)
    sys.exit(0)