"""
Test Runner Module

This module coordinates all validation components to provide comprehensive
testing and verification of generated code. It runs test generation,
SQLAlchemy validation, and bug verification in a coordinated manner.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess
import sys

from cli.validate.test_generator import TestGenerator
from cli.validate.runtime_validator import SQLAlchemyRuntimeValidator
from cli.validate.bug_verifier import BugVerifier
from cli.generate.config.models import DomainConfig
from cli.generate.config.loader import ConfigLoader


class ValidationTestRunner:
    """Coordinates all validation tests for generated code."""
    
    def __init__(self, project_path: Path, output_dir: Optional[Path] = None):
        self.project_path = Path(project_path)
        self.output_dir = Path(output_dir) if output_dir else self.project_path / "validation_output"
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "project_path": str(self.project_path),
            "test_generation": {},
            "sqlalchemy_validation": {},
            "bug_verification": {},
            "overall_summary": {}
        }
        
    def run_comprehensive_validation(self, domain_configs: Optional[List[DomainConfig]] = None) -> Dict[str, Any]:
        """
        Run comprehensive validation including test generation, runtime validation,
        and bug verification.
        
        Args:
            domain_configs: Optional list of domain configurations to test
            
        Returns:
            Comprehensive validation results
        """
        print("🚀 Starting Comprehensive Validation")
        print(f"📁 Project Path: {self.project_path}")
        print(f"📄 Output Directory: {self.output_dir}")
        
        start_time = time.time()
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 1: Generate validation tests
            print("\n📝 Step 1: Generating Validation Tests")
            self.results["test_generation"] = self._run_test_generation(domain_configs)
            
            # Step 2: Run SQLAlchemy runtime validation
            print("\n🔍 Step 2: Running SQLAlchemy Runtime Validation")
            self.results["sqlalchemy_validation"] = self._run_sqlalchemy_validation()
            
            # Step 3: Verify critical bugs are fixed
            print("\n🐛 Step 3: Verifying Critical Bug Fixes")
            self.results["bug_verification"] = self._run_bug_verification()
            
            # Step 4: Run generated tests (if possible)
            print("\n🧪 Step 4: Running Generated Tests")
            self.results["generated_test_execution"] = self._run_generated_tests()
            
            # Step 5: Generate summary report
            print("\n📊 Step 5: Generating Summary Report")
            self.results["overall_summary"] = self._generate_summary()
            
        except Exception as e:
            print(f"❌ Critical error during validation: {e}")
            self.results["critical_error"] = str(e)
        
        finally:
            elapsed_time = time.time() - start_time
            self.results["execution_time_seconds"] = elapsed_time
            
            # Save results to file
            results_file = self.output_dir / "validation_results.json"
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"\n💾 Results saved to: {results_file}")
            print(f"⏱️  Total execution time: {elapsed_time:.2f} seconds")
        
        return self.results
    
    def _run_test_generation(self, domain_configs: Optional[List[DomainConfig]]) -> Dict[str, Any]:
        """Generate validation tests for domain configurations."""
        results = {
            "status": "running",
            "domains_processed": [],
            "tests_generated": {},
            "errors": []
        }
        
        try:
            # If no domain configs provided, try to load from project
            if not domain_configs:
                domain_configs = self._discover_domain_configs()
            
            if not domain_configs:
                results["status"] = "skipped"
                results["reason"] = "No domain configurations found"
                return results
            
            test_output_dir = self.output_dir / "generated_tests"
            test_output_dir.mkdir(parents=True, exist_ok=True)
            
            for domain_config in domain_configs:
                domain_name = domain_config.domain.name
                print(f"  📋 Generating tests for domain: {domain_name}")
                
                try:
                    # Generate tests
                    generator = TestGenerator(domain_config, test_output_dir)
                    test_files = generator.generate_all_validation_tests()
                    
                    # Write test files to disk
                    domain_test_dir = test_output_dir / f"test_{domain_name.lower()}"
                    domain_test_dir.mkdir(parents=True, exist_ok=True)
                    
                    written_files = []
                    for test_type, test_content in test_files.items():
                        test_file = domain_test_dir / f"{test_type}.py"
                        test_file.write_text(test_content)
                        written_files.append(str(test_file))
                    
                    results["domains_processed"].append(domain_name)
                    results["tests_generated"][domain_name] = {
                        "test_files": written_files,
                        "test_types": list(test_files.keys())
                    }
                    
                    print(f"    ✅ Generated {len(test_files)} test types for {domain_name}")
                    
                except Exception as e:
                    error_msg = f"Failed to generate tests for {domain_name}: {str(e)}"
                    results["errors"].append(error_msg)
                    print(f"    ❌ {error_msg}")
            
            if results["domains_processed"]:
                results["status"] = "completed"
            else:
                results["status"] = "failed"
                
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"❌ Test generation failed: {e}")
        
        return results
    
    def _run_sqlalchemy_validation(self) -> Dict[str, Any]:
        """Run SQLAlchemy runtime validation."""
        results = {
            "status": "running",
            "validation_results": {},
            "errors": []
        }
        
        try:
            # Look for generated app directory
            app_dir = self.project_path / "app"
            if not app_dir.exists():
                results["status"] = "skipped"
                results["reason"] = "No app directory found"
                return results
            
            print("  🔧 Running SQLAlchemy integration tests")
            
            # Run validation
            validator = SQLAlchemyRuntimeValidator(app_dir)
            validation_results = validator.validate_sqlalchemy_integration()
            
            results["validation_results"] = validation_results
            
            # Count passed/failed tests
            passed_tests = sum(1 for result in validation_results.values() if result is True)
            total_tests = len([r for r in validation_results.values() if isinstance(r, bool)])
            
            results["summary"] = {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            }
            
            if "critical_error" in validation_results:
                results["status"] = "error"
                results["error"] = validation_results["critical_error"]
            elif passed_tests == total_tests:
                results["status"] = "passed"
            else:
                results["status"] = "failed"
            
            print(f"    📊 SQLAlchemy validation: {passed_tests}/{total_tests} tests passed")
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"❌ SQLAlchemy validation failed: {e}")
        
        return results
    
    def _run_bug_verification(self) -> Dict[str, Any]:
        """Run verification of 15 critical bugs."""
        results = {
            "status": "running",
            "bug_results": {},
            "errors": []
        }
        
        try:
            print("  🐛 Verifying 15 critical bugs are fixed")
            
            # Run bug verification
            verifier = BugVerifier(self.project_path)
            bug_results = verifier.verify_15_critical_bugs()
            
            results["bug_results"] = bug_results
            
            # Count fixed/broken bugs
            fixed_bugs = sum(1 for fixed in bug_results.values() if fixed)
            total_bugs = len(bug_results)
            
            results["summary"] = {
                "total_bugs": total_bugs,
                "fixed_bugs": fixed_bugs,
                "broken_bugs": total_bugs - fixed_bugs,
                "fix_rate": (fixed_bugs / total_bugs * 100) if total_bugs > 0 else 0
            }
            
            if fixed_bugs == total_bugs:
                results["status"] = "all_fixed"
            elif fixed_bugs > 0:
                results["status"] = "partially_fixed"
            else:
                results["status"] = "none_fixed"
            
            print(f"    🔧 Bug verification: {fixed_bugs}/{total_bugs} bugs fixed")
            
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"❌ Bug verification failed: {e}")
        
        return results
    
    def _run_generated_tests(self) -> Dict[str, Any]:
        """Run the generated test files using pytest."""
        results = {
            "status": "running",
            "test_results": {},
            "errors": []
        }
        
        try:
            test_dir = self.output_dir / "generated_tests"
            if not test_dir.exists():
                results["status"] = "skipped"
                results["reason"] = "No generated tests directory found"
                return results
            
            print("  🧪 Running generated pytest tests")
            
            # Change to project directory for imports to work
            original_cwd = Path.cwd()
            
            try:
                # Add project path to sys.path for imports
                sys.path.insert(0, str(self.project_path))
                
                # Find pytest executable
                pytest_cmd = self._find_pytest_executable()
                
                if not pytest_cmd:
                    results["status"] = "skipped"
                    results["reason"] = "pytest not found"
                    return results
                
                # Run pytest with JSON output
                pytest_args = [
                    pytest_cmd,
                    str(test_dir),
                    "--json-report",
                    f"--json-report-file={self.output_dir}/pytest_report.json",
                    "-v",
                    "--tb=short"
                ]
                
                result = subprocess.run(
                    pytest_args,
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                results["return_code"] = result.returncode
                results["stdout"] = result.stdout
                results["stderr"] = result.stderr
                
                # Try to read pytest JSON report
                json_report_file = self.output_dir / "pytest_report.json"
                if json_report_file.exists():
                    with open(json_report_file) as f:
                        pytest_json = json.load(f)
                        results["test_results"] = pytest_json
                
                if result.returncode == 0:
                    results["status"] = "passed"
                    print("    ✅ All generated tests passed")
                else:
                    results["status"] = "failed"
                    print(f"    ❌ Generated tests failed (exit code: {result.returncode})")
                
            finally:
                # Clean up sys.path
                if str(self.project_path) in sys.path:
                    sys.path.remove(str(self.project_path))
                
        except subprocess.TimeoutExpired:
            results["status"] = "timeout"
            results["error"] = "Test execution timed out after 5 minutes"
            print("    ⏰ Test execution timed out")
        except Exception as e:
            results["status"] = "error"
            results["error"] = str(e)
            print(f"❌ Generated test execution failed: {e}")
        
        return results
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate overall summary of validation results."""
        summary = {
            "overall_status": "unknown",
            "total_score": 0,
            "max_score": 0,
            "component_scores": {},
            "recommendations": []
        }
        
        try:
            # Score test generation
            if self.results["test_generation"]["status"] == "completed":
                summary["component_scores"]["test_generation"] = 100
            elif self.results["test_generation"]["status"] == "skipped":
                summary["component_scores"]["test_generation"] = 0
            else:
                summary["component_scores"]["test_generation"] = 0
            summary["max_score"] += 100
            
            # Score SQLAlchemy validation
            if "summary" in self.results["sqlalchemy_validation"]:
                sql_summary = self.results["sqlalchemy_validation"]["summary"]
                summary["component_scores"]["sqlalchemy_validation"] = sql_summary["success_rate"]
            else:
                summary["component_scores"]["sqlalchemy_validation"] = 0
            summary["max_score"] += 100
            
            # Score bug verification
            if "summary" in self.results["bug_verification"]:
                bug_summary = self.results["bug_verification"]["summary"]
                summary["component_scores"]["bug_verification"] = bug_summary["fix_rate"]
            else:
                summary["component_scores"]["bug_verification"] = 0
            summary["max_score"] += 100
            
            # Score generated test execution
            if self.results["generated_test_execution"]["status"] == "passed":
                summary["component_scores"]["generated_tests"] = 100
            elif self.results["generated_test_execution"]["status"] == "skipped":
                summary["component_scores"]["generated_tests"] = 50  # Partial credit
            else:
                summary["component_scores"]["generated_tests"] = 0
            summary["max_score"] += 100
            
            # Calculate total score
            summary["total_score"] = sum(summary["component_scores"].values())
            summary["percentage"] = (summary["total_score"] / summary["max_score"] * 100) if summary["max_score"] > 0 else 0
            
            # Determine overall status
            if summary["percentage"] >= 90:
                summary["overall_status"] = "excellent"
            elif summary["percentage"] >= 70:
                summary["overall_status"] = "good"
            elif summary["percentage"] >= 50:
                summary["overall_status"] = "fair"
            else:
                summary["overall_status"] = "poor"
            
            # Generate recommendations
            summary["recommendations"] = self._generate_recommendations()
            
        except Exception as e:
            summary["error"] = str(e)
            print(f"❌ Summary generation failed: {e}")
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # SQLAlchemy recommendations
        if "summary" in self.results["sqlalchemy_validation"]:
            sql_summary = self.results["sqlalchemy_validation"]["summary"]
            if sql_summary["success_rate"] < 80:
                recommendations.append(
                    "🔧 SQLAlchemy integration has issues - review entity field configurations"
                )
        
        # Bug verification recommendations
        if "summary" in self.results["bug_verification"]:
            bug_summary = self.results["bug_verification"]["summary"]
            if bug_summary["fix_rate"] < 100:
                recommendations.append(
                    f"🐛 {bug_summary['broken_bugs']} critical bugs still need fixing"
                )
        
        # Test execution recommendations
        if self.results["generated_test_execution"]["status"] == "failed":
            recommendations.append(
                "🧪 Generated tests are failing - review entity and repository implementations"
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ All validations passed - code quality is excellent!")
        else:
            recommendations.append("📚 Review OBSERVATIONS.md for detailed bug descriptions and fixes")
        
        return recommendations
    
    def _discover_domain_configs(self) -> List[DomainConfig]:
        """Discover domain configurations in the project."""
        configs = []
        
        try:
            # Look for config files in various locations
            config_locations = [
                self.project_path / "configs",
                self.project_path / "app" / "domain"
            ]
            
            loader = ConfigLoader()
            
            for location in config_locations:
                if location.exists():
                    # Look for domain config files
                    config_files = list(location.rglob("*domain*.yaml")) + list(location.rglob("domain.yaml"))
                    
                    for config_file in config_files:
                        try:
                            config = loader.load_config(config_file)
                            if isinstance(config, DomainConfig):
                                configs.append(config)
                        except Exception as e:
                            print(f"Warning: Could not load config {config_file}: {e}")
        
        except Exception as e:
            print(f"Warning: Config discovery failed: {e}")
        
        return configs
    
    def _find_pytest_executable(self) -> Optional[str]:
        """Find pytest executable in common locations."""
        possible_commands = ["pytest", "python -m pytest", "uv run pytest"]
        
        for cmd in possible_commands:
            try:
                result = subprocess.run(
                    cmd.split() + ["--version"],
                    capture_output=True,
                    timeout=10
                )
                if result.returncode == 0:
                    return cmd.split()[0]  # Return just the executable
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return None
    
    def print_summary_report(self):
        """Print a formatted summary report to console."""
        print("\n" + "="*60)
        print("🎯 VALIDATION SUMMARY REPORT")
        print("="*60)
        
        if "overall_summary" in self.results:
            summary = self.results["overall_summary"]
            
            print(f"📊 Overall Score: {summary.get('percentage', 0):.1f}% ({summary.get('total_score', 0):.0f}/{summary.get('max_score', 400)})")
            print(f"🏆 Status: {summary.get('overall_status', 'unknown').upper()}")
            
            print("\n📋 Component Scores:")
            for component, score in summary.get("component_scores", {}).items():
                print(f"  • {component.replace('_', ' ').title()}: {score:.1f}%")
            
            print("\n💡 Recommendations:")
            for rec in summary.get("recommendations", []):
                print(f"  {rec}")
        
        print("\n🔍 Detailed Results:")
        
        # Test Generation
        if "test_generation" in self.results:
            tg = self.results["test_generation"]
            status_icon = "✅" if tg["status"] == "completed" else "❌"
            print(f"  {status_icon} Test Generation: {tg['status']} ({len(tg.get('domains_processed', []))} domains)")
        
        # SQLAlchemy Validation
        if "sqlalchemy_validation" in self.results:
            sv = self.results["sqlalchemy_validation"]
            if "summary" in sv:
                status_icon = "✅" if sv["status"] == "passed" else "❌"
                print(f"  {status_icon} SQLAlchemy: {sv['summary']['passed_tests']}/{sv['summary']['total_tests']} tests passed")
        
        # Bug Verification
        if "bug_verification" in self.results:
            bv = self.results["bug_verification"]
            if "summary" in bv:
                status_icon = "✅" if bv["status"] == "all_fixed" else "❌"
                print(f"  {status_icon} Bug Fixes: {bv['summary']['fixed_bugs']}/{bv['summary']['total_bugs']} bugs fixed")
        
        # Generated Tests
        if "generated_test_execution" in self.results:
            gte = self.results["generated_test_execution"]
            status_icon = "✅" if gte["status"] == "passed" else "❌"
            print(f"  {status_icon} Generated Tests: {gte['status']}")
        
        print("="*60)


def run_comprehensive_validation(project_path: Path, domain_configs: Optional[List[DomainConfig]] = None) -> Dict[str, Any]:
    """
    Run comprehensive validation for a project.
    
    Args:
        project_path: Path to the project to validate
        domain_configs: Optional domain configurations to test
        
    Returns:
        Comprehensive validation results
    """
    runner = ValidationTestRunner(project_path)
    results = runner.run_comprehensive_validation(domain_configs)
    runner.print_summary_report()
    return results


# CLI entry point
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python test_runner.py <project_path> [output_dir]")
        sys.exit(1)
    
    project_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    if not project_path.exists():
        print(f"Project path does not exist: {project_path}")
        sys.exit(1)
    
    print(f"🚀 Running comprehensive validation for: {project_path}")
    
    runner = ValidationTestRunner(project_path, output_dir)
    results = runner.run_comprehensive_validation()
    
    runner.print_summary_report()
    
    # Exit with appropriate code
    if "overall_summary" in results:
        percentage = results["overall_summary"].get("percentage", 0)
        if percentage >= 70:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
    else:
        sys.exit(1)  # Error