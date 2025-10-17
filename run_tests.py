#!/usr/bin/env python3
"""
Test runner script for the Mergington High School Activities API
"""
import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run all tests with coverage"""
    project_root = Path(__file__).parent
    
    print("🧪 Running FastAPI tests...")
    print("=" * 50)
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-v"
    ]
    
    try:
        result = subprocess.run(cmd, cwd=project_root, check=True)
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)