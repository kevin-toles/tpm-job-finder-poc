#!/usr/bin/env python3
"""
Comprehensive test runner for the TPM Job Finder POC.

Runs unit, integration, regression, and end-to-end tests with proper reporting.
Supports different test categories and provides detailed coverage reporting.
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path
import json
import time
from datetime import datetime


class TestRunner:
    """Main test runner for the job finder system."""
    
    def __init__(self, project_root=None):
        if project_root is None:
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
            
        self.tests_dir = self.project_root / "tests"
        
    def run_unit_tests(self, verbose=False):
        """Run all unit tests."""
        print("\n🧪 Running Unit Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest", 
            str(self.tests_dir / "unit"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10"
        ]
        
        return subprocess.run(cmd, capture_output=True, text=True)
        
    def run_integration_tests(self, verbose=False):
        """Run all integration tests."""
        print("\n🔗 Running Integration Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "integration"), 
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10"
        ]
        
        return subprocess.run(cmd, capture_output=True, text=True)
        
    def run_regression_tests(self, verbose=False):
        """Run all regression tests."""
        print("\n🔄 Running Regression Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "regression"),
            "-v" if verbose else "-q", 
            "--tb=short",
            "--durations=10"
        ]
        
        return subprocess.run(cmd, capture_output=True, text=True)
        
    def run_e2e_tests(self, verbose=False):
        """Run all end-to-end tests."""
        print("\n🎯 Running End-to-End Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            str(self.tests_dir / "e2e"),
            "-v" if verbose else "-q",
            "--tb=short", 
            "--durations=10"
        ]
        
        return subprocess.run(cmd, capture_output=True, text=True)
        
    def run_performance_tests(self, verbose=False):
        """Run performance tests."""
        print("\n⚡ Running Performance Tests...")
        print("=" * 50)
        
        cmd = [
            "python", "-m", "pytest",
            "-m", "performance",
            str(self.tests_dir),
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10"
        ]
        
        return subprocess.run(cmd, capture_output=True, text=True)
        
    def run_coverage_report(self):
        """Generate test coverage report."""
        print("\n📊 Generating Coverage Report...")
        print("=" * 50)
        
        # Run tests with coverage
        cmd = [
            "python", "-m", "pytest",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            str(self.tests_dir)
        ]
        
        return subprocess.run(cmd, capture_output=True, text=True)
        
    def run_specific_component(self, component, verbose=False):
        """Run tests for a specific component."""
        print(f"\n🎯 Running Tests for {component}...")
        print("=" * 50)
        
        component_paths = [
            self.tests_dir / "unit" / component,
            self.tests_dir / "integration" / component,
            self.tests_dir / "regression" / component,
        ]
        
        existing_paths = [p for p in component_paths if p.exists()]
        
        if not existing_paths:
            print(f"❌ No tests found for component: {component}")
            return None
            
        cmd = [
            "python", "-m", "pytest",
            "-v" if verbose else "-q",
            "--tb=short"
        ]
        cmd.extend([str(p) for p in existing_paths])
        
        return subprocess.run(cmd, capture_output=True, text=True)
        
    def run_all_tests(self, verbose=False, include_e2e=True, include_performance=False):
        """Run all test suites."""
        start_time = time.time()
        results = {}
        
        print("🚀 Running Complete Test Suite")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run each test suite
        test_suites = [
            ("unit", self.run_unit_tests),
            ("integration", self.run_integration_tests),
            ("regression", self.run_regression_tests)
        ]
        
        if include_e2e:
            test_suites.append(("e2e", self.run_e2e_tests))
            
        if include_performance:
            test_suites.append(("performance", self.run_performance_tests))
            
        for suite_name, suite_func in test_suites:
            result = suite_func(verbose)
            results[suite_name] = result
            
            if result.returncode == 0:
                print(f"✅ {suite_name.upper()} tests passed")
            else:
                print(f"❌ {suite_name.upper()} tests failed")
                if verbose:
                    print(result.stdout)
                    print(result.stderr)
                    
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\n📋 Test Summary")
        print("=" * 60)
        
        total_suites = len(results)
        passed_suites = sum(1 for r in results.values() if r.returncode == 0)
        
        print(f"Total test suites: {total_suites}")
        print(f"Passed: {passed_suites}")
        print(f"Failed: {total_suites - passed_suites}")
        print(f"Duration: {duration:.2f} seconds")
        
        # Show detailed results
        for suite_name, result in results.items():
            status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
            print(f"  {suite_name.upper()}: {status}")
            
        return all(r.returncode == 0 for r in results.values())
        
    def validate_test_structure(self):
        """Validate that all required test files exist."""
        print("\n🔍 Validating Test Structure...")
        print("=" * 50)
        
        required_test_dirs = [
            "tests/unit/scraping_service_v2",
            "tests/unit/job_aggregator", 
            "tests/unit/cli",
            "tests/integration/scraping_service_v2",
            "tests/integration/job_aggregator",
            "tests/regression/scraping_service_v2",
            "tests/e2e"
        ]
        
        missing_dirs = []
        existing_dirs = []
        
        for test_dir in required_test_dirs:
            full_path = self.project_root / test_dir
            if full_path.exists():
                existing_dirs.append(test_dir)
            else:
                missing_dirs.append(test_dir)
                
        print(f"✅ Found {len(existing_dirs)} test directories:")
        for dir_path in existing_dirs:
            test_files = list((self.project_root / dir_path).glob("test_*.py"))
            print(f"  {dir_path} ({len(test_files)} test files)")
            
        if missing_dirs:
            print(f"\n❌ Missing {len(missing_dirs)} test directories:")
            for dir_path in missing_dirs:
                print(f"  {dir_path}")
                
        return len(missing_dirs) == 0
        
    def setup_test_environment(self):
        """Setup the test environment with required dependencies."""
        print("\n⚙️ Setting up Test Environment...")
        print("=" * 50)
        
        # Check if pytest is installed
        try:
            import pytest
            print("✅ pytest is available")
        except ImportError:
            print("❌ pytest not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pytest"])
            
        # Check for other test dependencies
        test_deps = [
            "pytest-asyncio",
            "pytest-cov", 
            "pytest-mock"
        ]
        
        for dep in test_deps:
            try:
                __import__(dep.replace("-", "_"))
                print(f"✅ {dep} is available")
            except ImportError:
                print(f"⚠️ {dep} not found (optional)")
                
        return True


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="TPM Job Finder Test Runner")
    
    parser.add_argument(
        "suite",
        nargs="?",
        choices=["unit", "integration", "regression", "e2e", "performance", "all", "validate"],
        default="all",
        help="Test suite to run (default: all)"
    )
    
    parser.add_argument(
        "--component",
        help="Run tests for specific component (e.g., scraping_service_v2, job_aggregator)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--no-e2e",
        action="store_true", 
        help="Skip end-to-end tests (faster execution)"
    )
    
    parser.add_argument(
        "--include-performance",
        action="store_true",
        help="Include performance tests"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Setup test environment"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner()
    
    # Setup environment if requested
    if args.setup:
        runner.setup_test_environment()
        return
        
    # Validate test structure
    if args.suite == "validate":
        success = runner.validate_test_structure()
        sys.exit(0 if success else 1)
        
    # Run specific component tests
    if args.component:
        result = runner.run_specific_component(args.component, args.verbose)
        if result is None:
            sys.exit(1)
        sys.exit(0 if result.returncode == 0 else 1)
        
    # Generate coverage report
    if args.coverage:
        result = runner.run_coverage_report()
        print("\n📊 Coverage report generated in htmlcov/")
        sys.exit(0 if result.returncode == 0 else 1)
        
    # Run specific test suite
    if args.suite == "unit":
        result = runner.run_unit_tests(args.verbose)
    elif args.suite == "integration":
        result = runner.run_integration_tests(args.verbose)
    elif args.suite == "regression":
        result = runner.run_regression_tests(args.verbose)
    elif args.suite == "e2e":
        result = runner.run_e2e_tests(args.verbose)
    elif args.suite == "performance":
        result = runner.run_performance_tests(args.verbose)
    elif args.suite == "all":
        success = runner.run_all_tests(
            verbose=args.verbose,
            include_e2e=not args.no_e2e,
            include_performance=args.include_performance
        )
        sys.exit(0 if success else 1)
        
    # Print output for single suite runs
    if hasattr(result, 'returncode'):
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)


if __name__ == "__main__":
    main()
