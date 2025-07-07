from pathlib import Path
import shutil
from typing import Optional
from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import GenerationResult, TemplateContext

class ProjectInitializer:

    def __init__(self, target_dir: PathLike, clean_existing: bool = False) -> None:
        self.target_dir = Path(target_dir)
        self.clean_existing = clean_existing
        self.logger = get_logger(__name__)

    def initialize(self, auth: bool) -> GenerationResult:
        result = GenerationResult(
            success=True,
            operation_type="project_initialization",
            metadata={"auth_enabled": auth, "target_dir": str(self.target_dir)}
        )
        
        self.logger.debug("Starting project initialization", extra={
            "target_dir": str(self.target_dir),
            "auth_enabled": auth,
            "clean_existing": self.clean_existing,
            "operation": "initialize",
            "phase": "start"
        })
        
        try:
            with self.logger.timed_operation("project_initialization", extra={"target_dir": str(self.target_dir)}):
                # 1. Check/clean/create target dir
                self.logger.debug("Starting target directory setup", extra={"operation": "setup_target_dir", "phase": "start"})
                self._check_clean_create_target_dir()
                
                # 2. Copy all template project files from installed tool dir to target dir
                #!BUG: This is not copying over the base config files
                self.logger.debug("Starting template file copying", extra={"operation": "copy_templates", "phase": "start"})
                template_result = self._copy_template_files()
                result.files_generated.extend(template_result.files_generated)
                result.warnings.extend(template_result.warnings)

                #!BUG: We need to add a step where we generate all the base project files and layer files from their templates. 
                
                # 3. Generate the default health domain. Copy the source project's health configs and run the generate method on the target directory
                #!BUG: This is not working. There is no health domain generated in the target project.
                self.logger.debug("Starting health domain generation", extra={"operation": "generate_health_domain", "phase": "start"})
                health_result = self._generate_default_health_domain()
                result.files_generated.extend(health_result.files_generated)
                result.warnings.extend(health_result.warnings)

                # 4. If auth is enabled, use the generate domain function to create the required user and auth domains.
                #!BUG: This is not working. There is no auth domain generated in the target project.
                if auth:
                    self.logger.debug("Starting auth domains generation", extra={"operation": "generate_auth_domains", "phase": "start"})
                    auth_result = self._generate_auth_domains()
                    result.files_generated.extend(auth_result.files_generated)
                    result.warnings.extend(auth_result.warnings)
                else:
                    self.logger.debug("Skipping auth domains generation", extra={"auth_enabled": False, "operation": "generate_auth_domains", "phase": "skipped"})

                # 5. Run uv sync
                self.logger.debug("Starting uv sync", extra={"operation": "uv_sync", "phase": "start"})
                sync_result = self._run_uv_sync()
                result.warnings.extend(sync_result.warnings)
                
                # 6. Run tests and linters
                self.logger.debug("Starting tests and linters", extra={"operation": "tests_linters", "phase": "start"})
                test_result = self._run_tests_and_linters()
                result.warnings.extend(test_result.warnings)
            
            self.logger.info("Project initialization completed successfully", extra={
                "target_dir": str(self.target_dir),
                "auth_enabled": auth,
                "operation": "initialize",
                "phase": "complete"
            })
            
        except Exception as e:
            result.add_error(f"Project initialization failed: {str(e)}")
            self.logger.error("Project initialization failed", exc_info=True, extra={
                "target_dir": str(self.target_dir),
                "auth_enabled": auth,
                "operation": "initialize",
                "phase": "failed"
            })
        
        return result

    def _check_clean_create_target_dir(self) -> None:
        self.logger.debug("Checking target directory", extra={
            "target_dir": str(self.target_dir),
            "exists": self.target_dir.exists(),
            "clean_existing": self.clean_existing,
            "operation": "check_target_dir"
        })
        
        # Check and optionally clean existing directory
        if self.target_dir.exists() and self.clean_existing:
            self.logger.info("Cleaning existing target directory", extra={
                "target_dir": str(self.target_dir),
                "operation": "clean_target_dir"
            })
            shutil.rmtree(self.target_dir)
        elif self.target_dir.exists():
            self.logger.debug("Target directory exists, keeping existing content", extra={
                "target_dir": str(self.target_dir),
                "operation": "keep_existing_dir"
            })
        
        # Create target directory
        self.logger.debug("Creating target directory", extra={
            "target_dir": str(self.target_dir),
            "operation": "create_target_dir"
        })
        self.target_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("Target directory setup completed", extra={
            "target_dir": str(self.target_dir),
            "operation": "setup_target_dir",
            "phase": "complete"
        })

    def _copy_template_files(self) -> GenerationResult:
        """
        Copy template project files using BaseStructureGenerator services.
        
        This method orchestrates the copying of all essential project files:
        1. Create complete directory structure (app/, tests/, configs/, docs/)
        2. Copy static files (__init__.py files for each architectural layer)
        3. Copy .j2 template files to target/app/layer/{{domain}}/ for domain generation
        4. Copy configuration files (.yaml files for domain configs)
        5. Copy and process main application files (main.py.j2, config.py.j2, database.py.j2)
        6. Generate essential project files (pyproject.toml, justfile, .gitignore, .env.sample)
        
        Uses BaseStructureGenerator to:
        - create_directory_structure(): Creates the hexagonal architecture directory layout
        - copy_static_files(): Copies non-template files that don't require processing
        - copy_template_files(): Copies all .j2 template files and domain directories
        - copy_main_files(): Copies and processes core application template files
        - copy_project_files(): Generates project configuration and build files
        
        All operations include proper error handling and logging for debugging.
        """
        result = GenerationResult(
            success=True,
            operation_type="copy_template_files"
        )
        
        # Initialize BaseStructureGenerator with target directory
        from ..services.base import BaseStructureGenerator
        structure_generator = BaseStructureGenerator(str(self.target_dir))
        
        # Create project context for template processing
        context = TemplateContext(
            domain="project",  # Required field for TemplateContext
            package_name=self.target_dir.name.lower(),
            description=f"FastAPI SQLModel project: {self.target_dir.name}",
            metadata={
                'project_name': self.target_dir.name,
                'project_slug': self.target_dir.name.lower(),
                'app_name': self.target_dir.name.lower()
            }
        )
        
        try:
            # 1. Create complete directory structure
            self.logger.debug("Creating directory structure", extra={
                "target_dir": str(self.target_dir),
                "operation": "create_directory_structure"
            })
            dir_result = structure_generator.create_directory_structure()
            result.files_generated.extend(dir_result.files_generated)
            result.warnings.extend(dir_result.warnings)
            result.errors.extend(dir_result.errors)
            if not dir_result.success:
                result.success = False
            self.logger.debug("Directory structure created", extra={
                "file_count": len(dir_result.files_generated),
                "operation": "create_directory_structure",
                "phase": "complete"
            })
            
            # 2. Copy static files (non-templates)
            self.logger.debug("Copying static files", extra={
                "target_dir": str(self.target_dir),
                "operation": "copy_static_files"
            })
            static_result = structure_generator.copy_static_files()
            result.files_generated.extend(static_result.files_generated)
            result.warnings.extend(static_result.warnings)
            result.errors.extend(static_result.errors)
            if not static_result.success:
                result.success = False
            self.logger.debug("Static files copied", extra={
                "file_count": len(static_result.files_generated),
                "operation": "copy_static_files",
                "phase": "complete"
            })
            
            # 3. Copy .j2 template files and domain directories
            self.logger.debug("Copying template files and domain directories", extra={
                "target_dir": str(self.target_dir),
                "operation": "copy_template_files"
            })
            template_result = structure_generator.copy_template_files()
            result.files_generated.extend(template_result.files_generated)
            result.warnings.extend(template_result.warnings)
            result.errors.extend(template_result.errors)
            if not template_result.success:
                result.success = False
            self.logger.debug("Template files copied", extra={
                "file_count": len(template_result.files_generated),
                "operation": "copy_template_files",
                "phase": "complete"
            })
            
            # 4. Copy and process main application files
            self.logger.debug("Copying main application files", extra={
                "target_dir": str(self.target_dir),
                "context": context.model_dump(),
                "operation": "copy_main_files"
            })
            main_result = structure_generator.copy_main_files(context)
            result.files_generated.extend(main_result.files_generated)
            result.warnings.extend(main_result.warnings)
            result.errors.extend(main_result.errors)
            if not main_result.success:
                result.success = False
            self.logger.debug("Main files copied", extra={
                "file_count": len(main_result.files_generated),
                "operation": "copy_main_files",
                "phase": "complete"
            })
            
            # 5. Generate project configuration files
            self.logger.debug("Generating project configuration files", extra={
                "target_dir": str(self.target_dir),
                "context": context.model_dump(),
                "operation": "copy_project_files"
            })
            project_result = structure_generator.copy_project_files(context)
            result.files_generated.extend(project_result.files_generated)
            result.warnings.extend(project_result.warnings)
            result.errors.extend(project_result.errors)
            if not project_result.success:
                result.success = False
            self.logger.debug("Project files generated", extra={
                "file_count": len(project_result.files_generated),
                "operation": "copy_project_files",
                "phase": "complete"
            })
            
            # Log successful operations with detailed breakdown
            total_files = (len(dir_result.files_generated) + len(static_result.files_generated) + 
                          len(template_result.files_generated) + len(main_result.files_generated) + 
                          len(project_result.files_generated))
            self.logger.info("Template files copied successfully", extra={
                "file_count": total_files,
                "directory_files": len(dir_result.files_generated),
                "static_files": len(static_result.files_generated),
                "template_files": len(template_result.files_generated),
                "main_files": len(main_result.files_generated),
                "project_files": len(project_result.files_generated),
                "operation": "copy_templates",
                "phase": "complete"
            })
            
        except Exception as e:
            # Handle errors with descriptive messages
            result.add_error(f"Template file copying failed: {str(e)}")
            self.logger.error("Template file copying failed", exc_info=True, extra={
                "target_dir": str(self.target_dir),
                "operation": "copy_templates",
                "phase": "failed"
            })
        
        return result

    def _generate_auth_domains(self) -> GenerationResult:
        result = GenerationResult(
            success=True,
            operation_type="generate_auth_domains"
        )
        
        self.logger.debug("Starting auth domains generation", extra={
            "target_dir": str(self.target_dir),
            "operation": "generate_auth_domains",
            "phase": "start"
        })
        
        try:
            from ..services.core import CoreLayerGenerator
            
            # Generate Auth domain (AccessToken, RefreshToken entities)
            self.logger.debug("Generating Auth domain", extra={
                "domain": "Auth",
                "target_dir": str(self.target_dir),
                "operation": "generate_auth_domain"
            })
            
            domain_generator = CoreLayerGenerator(str(self.target_dir))
            
            with self.logger.timed_operation("auth_domain_generation", extra={"domain": "Auth"}):
                auth_success = domain_generator.generate_domain("Auth")
            
            if auth_success:
                result.add_generated_file("app/domain/Auth/")
                self.logger.info("Auth domain generated successfully", extra={
                    "domain": "Auth",
                    "target_dir": str(self.target_dir),
                    "operation": "generate_domain",
                    "phase": "complete"
                })
            else:
                result.add_error("Auth domain generation failed")
                self.logger.error("Auth domain generation failed", extra={
                    "domain": "Auth",
                    "target_dir": str(self.target_dir),
                    "operation": "generate_domain",
                    "phase": "failed"
                })
            
            # Generate User domain (User entity with auth fields)
            self.logger.debug("Generating User domain", extra={
                "domain": "User",
                "target_dir": str(self.target_dir),
                "operation": "generate_user_domain"
            })
            
            with self.logger.timed_operation("user_domain_generation", extra={"domain": "User"}):
                user_success = domain_generator.generate_domain("User")
            
            if user_success:
                result.add_generated_file("app/domain/User/")
                self.logger.info("User domain generated successfully", extra={
                    "domain": "User",
                    "target_dir": str(self.target_dir),
                    "operation": "generate_domain",
                    "phase": "complete"
                })
            else:
                result.add_error("User domain generation failed")
                self.logger.error("User domain generation failed", extra={
                    "domain": "User",
                    "target_dir": str(self.target_dir),
                    "operation": "generate_domain",
                    "phase": "failed"
                })
            
            # Overall success depends on both domains
            if not (auth_success and user_success):
                result.success = False
                
        except Exception as e:
            result.add_error(f"Auth domains generation failed with exception: {str(e)}")
            self.logger.error("Auth domains generation failed with exception", exc_info=True, extra={
                "target_dir": str(self.target_dir),
                "operation": "generate_auth_domains",
                "phase": "failed"
            })
        
        return result

    def _run_uv_sync(self) -> GenerationResult:
        result = GenerationResult(
            success=True,
            operation_type="uv_sync"
        )
        
        self.logger.debug("Starting uv sync", extra={
            "target_dir": str(self.target_dir),
            "operation": "uv_sync",
            "phase": "start"
        })
        
        try:
            import subprocess
            from pathlib import Path
            
            # Check if target directory exists
            target_path = Path(self.target_dir)
            if not target_path.exists():
                result.add_error(f"Target directory does not exist: {self.target_dir}")
                return result
            
            # Check if pyproject.toml exists
            pyproject_path = target_path / "pyproject.toml"
            if not pyproject_path.exists():
                result.add_warning(f"pyproject.toml not found in {self.target_dir}, skipping uv sync")
                return result
            
            self.logger.debug("Running uv sync command", extra={
                "target_dir": str(self.target_dir),
                "operation": "subprocess_uv_sync",
                "phase": "execute"
            })
            
            # Run uv sync with timeout
            with self.logger.timed_operation("uv_sync_subprocess", extra={"target_dir": str(self.target_dir)}):
                completed_process = subprocess.run(
                    ["uv", "sync"],
                    cwd=str(target_path),
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
            
            if completed_process.returncode == 0:
                result.add_modified_file("uv.lock")
                self.logger.info("UV sync completed successfully", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "uv_sync",
                    "phase": "complete",
                    "return_code": completed_process.returncode
                })
                
                # Log any output for debugging
                if completed_process.stdout.strip():
                    self.logger.debug("UV sync stdout", extra={
                        "stdout": completed_process.stdout.strip(),
                        "operation": "uv_sync"
                    })
            else:
                result.add_error(f"UV sync failed with return code {completed_process.returncode}")
                self.logger.error("UV sync failed", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "uv_sync",
                    "phase": "failed",
                    "return_code": completed_process.returncode,
                    "stderr": completed_process.stderr.strip()
                })
                
        except FileNotFoundError:
            result.add_error("UV command not found. Please install UV: https://docs.astral.sh/uv/getting-started/installation/")
            self.logger.error("UV command not found", extra={
                "target_dir": str(self.target_dir),
                "operation": "uv_sync",
                "phase": "failed",
                "error_type": "FileNotFoundError"
            })
            
        except subprocess.TimeoutExpired:
            result.add_error("UV sync timed out after 5 minutes")
            self.logger.error("UV sync timed out", extra={
                "target_dir": str(self.target_dir),
                "operation": "uv_sync",
                "phase": "failed",
                "error_type": "TimeoutExpired",
                "timeout_seconds": 300
            })
            
        except subprocess.CalledProcessError as e:
            result.add_error(f"UV sync failed: {e}")
            self.logger.error("UV sync subprocess error", extra={
                "target_dir": str(self.target_dir),
                "operation": "uv_sync",
                "phase": "failed",
                "error_type": "CalledProcessError",
                "return_code": e.returncode
            })
            
        except Exception as e:
            result.add_error(f"UV sync failed with unexpected error: {str(e)}")
            self.logger.error("UV sync unexpected error", exc_info=True, extra={
                "target_dir": str(self.target_dir),
                "operation": "uv_sync",
                "phase": "failed",
                "error_type": type(e).__name__
            })
        
        return result

    def _generate_default_health_domain(self) -> GenerationResult:
        """Generate the default Health domain using conventions."""
        result = GenerationResult(
            success=True,
            operation_type="generate_health_domain",
            metadata={"domain": "Health"}
        )
        
        self.logger.debug("Starting health domain generation", extra={
            "domain": "Health",
            "target_dir": str(self.target_dir),
            "operation": "generate_health_domain",
            "phase": "start"
        })
        
        try:
            from ..services.core import CoreLayerGenerator
            
            # Simple: just pass domain name, everything else is convention-based
            self.logger.debug("Initializing core layer generator", extra={
                "domain": "Health",
                "target_dir": str(self.target_dir),
                "operation": "initialize_generator"
            })
            domain_generator = CoreLayerGenerator(str(self.target_dir))
            
            with self.logger.timed_operation("health_domain_generation", extra={"domain": "Health"}):
                success = domain_generator.generate_domain("Health")
            
            if success:
                self.logger.info("Health domain generated successfully", extra={
                    "domain": "Health",
                    "target_dir": str(self.target_dir),
                    "operation": "generate_domain",
                    "phase": "complete"
                })
            else:
                result.add_error("Health domain generation failed")
                self.logger.error("Health domain generation failed", extra={
                    "domain": "Health",
                    "target_dir": str(self.target_dir),
                    "operation": "generate_domain",
                    "phase": "failed"
                })
                
        except Exception as e:
            result.add_error(f"Health domain generation failed with exception: {str(e)}")
            self.logger.error("Health domain generation failed with exception", exc_info=True, extra={
                "domain": "Health",
                "target_dir": str(self.target_dir),
                "operation": "generate_domain",
                "phase": "failed"
            })
        
        return result

    def _run_tests_and_linters(self) -> GenerationResult:
        result = GenerationResult(
            success=True,
            operation_type="tests_and_linters"
        )
        
        self.logger.debug("Starting tests and linters", extra={
            "target_dir": str(self.target_dir),
            "operation": "tests_linters",
            "phase": "start"
        })
        
        try:
            import subprocess
            from pathlib import Path
            
            target_path = Path(self.target_dir)
            
            # Check if target directory exists
            if not target_path.exists():
                result.add_error(f"Target directory does not exist: {self.target_dir}")
                return result
            
            # Check if virtual environment exists (indicates uv sync was successful)
            venv_path = target_path / ".venv"
            if not venv_path.exists():
                result.add_warning("Virtual environment not found, skipping tests and linters")
                self.logger.warning("Virtual environment not found", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "tests_linters",
                    "phase": "skip_no_venv"
                })
                return result
            
            # Run pytest if test directory exists
            test_dir = target_path / "test"
            if test_dir.exists() and any(test_dir.glob("**/*.py")):
                self.logger.debug("Running pytest", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "pytest",
                    "phase": "execute"
                })
                
                try:
                    with self.logger.timed_operation("pytest_execution", extra={"target_dir": str(self.target_dir)}):
                        pytest_result = subprocess.run(
                            ["uv", "run", "pytest", "-v", "--tb=short"],
                            cwd=str(target_path),
                            capture_output=True,
                            text=True,
                            timeout=180  # 3 minute timeout for tests
                        )
                    
                    if pytest_result.returncode == 0:
                        result.add_modified_file("test results")
                        self.logger.info("Tests passed successfully", extra={
                            "target_dir": str(self.target_dir),
                            "operation": "pytest",
                            "phase": "complete",
                            "return_code": pytest_result.returncode
                        })
                    else:
                        result.add_warning(f"Some tests failed (return code: {pytest_result.returncode})")
                        self.logger.warning("Tests failed", extra={
                            "target_dir": str(self.target_dir),
                            "operation": "pytest",
                            "phase": "tests_failed",
                            "return_code": pytest_result.returncode,
                            "stderr": pytest_result.stderr.strip()
                        })
                        
                except subprocess.TimeoutExpired:
                    result.add_warning("Tests timed out after 3 minutes")
                    self.logger.warning("Tests timed out", extra={
                        "target_dir": str(self.target_dir),
                        "operation": "pytest",
                        "phase": "timeout"
                    })
                    
            else:
                self.logger.debug("No test directory found, skipping tests", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "pytest",
                    "phase": "skip_no_tests"
                })
            
            # Run ruff linting if available
            try:
                self.logger.debug("Running ruff linting", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "ruff_lint",
                    "phase": "execute"
                })
                
                ruff_result = subprocess.run(
                    ["uv", "run", "ruff", "check", "."],
                    cwd=str(target_path),
                    capture_output=True,
                    text=True,
                    timeout=60  # 1 minute timeout for linting
                )
                
                if ruff_result.returncode == 0:
                    self.logger.info("Ruff linting passed", extra={
                        "target_dir": str(self.target_dir),
                        "operation": "ruff_lint",
                        "phase": "complete"
                    })
                else:
                    result.add_warning(f"Ruff linting found issues (return code: {ruff_result.returncode})")
                    self.logger.warning("Ruff linting issues found", extra={
                        "target_dir": str(self.target_dir),
                        "operation": "ruff_lint",
                        "phase": "issues_found",
                        "return_code": ruff_result.returncode,
                        "stdout": ruff_result.stdout.strip()
                    })
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                result.add_warning("Ruff linting unavailable or timed out")
                self.logger.debug("Ruff linting unavailable", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "ruff_lint",
                    "phase": "unavailable"
                })
            
            # Run black formatting check if available
            try:
                self.logger.debug("Running black format check", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "black_check",
                    "phase": "execute"
                })
                
                black_result = subprocess.run(
                    ["uv", "run", "black", "--check", "."],
                    cwd=str(target_path),
                    capture_output=True,
                    text=True,
                    timeout=60  # 1 minute timeout for formatting check
                )
                
                if black_result.returncode == 0:
                    self.logger.info("Black formatting check passed", extra={
                        "target_dir": str(self.target_dir),
                        "operation": "black_check",
                        "phase": "complete"
                    })
                else:
                    result.add_warning(f"Black formatting issues found (return code: {black_result.returncode})")
                    self.logger.warning("Black formatting issues found", extra={
                        "target_dir": str(self.target_dir),
                        "operation": "black_check",
                        "phase": "issues_found",
                        "return_code": black_result.returncode,
                        "stdout": black_result.stdout.strip()
                    })
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                result.add_warning("Black formatting check unavailable or timed out")
                self.logger.debug("Black formatting check unavailable", extra={
                    "target_dir": str(self.target_dir),
                    "operation": "black_check",
                    "phase": "unavailable"
                })
                
        except Exception as e:
            result.add_error(f"Tests and linters failed with unexpected error: {str(e)}")
            self.logger.error("Tests and linters unexpected error", exc_info=True, extra={
                "target_dir": str(self.target_dir),
                "operation": "tests_linters",
                "phase": "failed",
                "error_type": type(e).__name__
            })
        
        return result
