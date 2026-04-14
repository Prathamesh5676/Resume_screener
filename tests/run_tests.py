#!/usr/bin/env python3
"""
Integration Test Runner for Resume Screener

This script runs the full pipeline integration test.
Make sure the application and services are running before executing.
"""

import os
import sys
import subprocess

def check_services():
    """Check if required services are running"""
    print("Checking if services are running...")

    # Check if FastAPI is running on port 8000
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            print("FastAPI server is running")
        else:
            print("FastAPI server not responding correctly")
            return False
    except:
        print("FastAPI server not running on http://127.0.0.1:8000")
        print("   Start with: uvicorn app.main:app --reload")
        return False

    # Check if Redis is running
    try:
        result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True, timeout=5)
        if "PONG" in result.stdout:
            print("Redis is running")
        else:
            print("Redis not responding")
            return False
    except:
        print("Redis not running")
        print("   Start with: redis-server")
        return False

    return True

def check_test_file():
    """Check if sample resume file exists"""
    test_file = "tests/sample_resume.pdf"
    if os.path.exists(test_file):
        print(f"Test file found: {test_file}")
        return True
    else:
        print(f"Test file missing: {test_file}")
        print("   Please place a sample PDF resume in the tests/ directory")
        return False

def run_test():
    """Run the integration test"""
    print("\nRunning integration test...")
    print("=" * 50)

    try:
        # Import and run the test
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from test_pipeline import test_full_pipeline

        test_full_pipeline()
        print("\nAll tests passed!")

    except Exception as e:
        print(f"\nTest failed: {e}")
        return False

    return True

def main():
    print("Resume Screener Integration Test Runner")
    print("=" * 50)

    # Pre-flight checks
    if not check_services():
        print("\nService checks failed. Please start required services.")
        sys.exit(1)

    if not check_test_file():
        print("\nTest file check failed. Please add sample resume.")
        sys.exit(1)

    # Run the test
    if run_test():
        print("\nIntegration test completed successfully!")
        sys.exit(0)
    else:
        print("\nIntegration test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()