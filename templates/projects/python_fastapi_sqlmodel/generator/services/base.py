
"""
Base structure generator for project initialization.

This service handles the creation of the initial project directory structure
and basic files that don't belong to any specific architectural layer.
"""

from pathlib import Path
from typing import Dict, Any, List
import logging
import shutil
import pkg_resources

from ..utils.logging_utils import get_logger
from ..utils.type_aliases import PathLike
from ..types.models.internal_models import GenerationResult, TemplateContext

logger = get_logger(__name__)


class BaseStructureGenerator:
    """Creates the initial directory structure and base files for FastAPI SQLModel projects."""

    def __init__(self, output_dir: PathLike) -> None:
        """
        Initialize the base structure generator.
        
        Args:
            output_dir: Root directory where the project structure will be created
        """
        self.output_dir = Path(output_dir)
        self.logger = get_logger(__name__)
        # Detect source template directory
        self.template_dir = self._get_template_source_dir()
        
        self.logger.debug("BaseStructureGenerator initialized", extra={
            "output_dir": str(self.output_dir),
            "template_dir": str(self.template_dir),
            "operation": "init"
        })

    def _get_template_source_dir(self) -> Path:
        """
        Get the source template directory from the installed package.
        
        Returns:
            Path to the template source directory
        """
        self.logger.debug("Detecting template source directory", extra={"operation": "detect_template_dir"})
        
        # For development, use current directory structure
        current_file = Path(__file__)
        template_dir = current_file.parent.parent.parent
        
        if template_dir.exists():
            self.logger.debug("Using development template directory", extra={
                "template_dir": str(template_dir),
                "source": "development",
                "operation": "detect_template_dir"
            })
            return template_dir
        
        # Fallback for installed package
        try:
            package_path = pkg_resources.resource_filename('python_fastapi_sqlmodel', '')
            template_dir = Path(package_path)
            self.logger.debug("Using installed package template directory", extra={
                "template_dir": str(template_dir),
                "source": "package",
                "operation": "detect_template_dir"
            })
            return template_dir
        except Exception as e:
            self.logger.error("Could not locate template source directory", exc_info=True, extra={
                "operation": "detect_template_dir",
                "error_type": type(e).__name__
            })
            raise RuntimeError("Could not locate template source directory")

    def create_directory_structure(self) -> GenerationResult:
        """
        Create the basic directory structure for FastAPI project.
        
        Creates:
        - app/ (main application directory)
        - app/domain/ (domain entities)
        - app/repository/ (data access layer)
        - app/usecase/ (business logic layer) 
        - app/interface/ (API interface layer)
        - app/service/ (domain-agnostic services)
        - tests/ (test directories)
        - tests/fixtures/ (test fixtures)
        - tests/integration/ (integration tests)
        - tests/unit/ (unit tests)
        - docs/ (documentation)
        
        Returns:
            GenerationResult with details about created directories
        """
        directories = [
            "app",
            "app/domain",
            "app/repository", 
            "app/usecase",
            "app/interface",
            "app/service",
            "tests",
            "tests/fixtures",
            "tests/integration", 
            "tests/unit",
            "docs"
        ]
        
        result = GenerationResult(
            success=True,
            operation_type="create_directory_structure"
        )
        
        with self.logger.timed_operation("create_directory_structure", extra={
            "total_directories": len(directories),
            "output_dir": str(self.output_dir)
        }):
            created_count = 0
            for directory in directories:
                dir_path = self.output_dir / directory
                existed_before = dir_path.exists()
                
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    
                    if not existed_before:
                        created_count += 1
                        result.add_generated_file(str(dir_path))
                    else:
                        result.add_skipped_file(str(dir_path))
                    
                    self.logger.debug("Directory processed", extra={
                        "directory": directory,
                        "full_path": str(dir_path),
                        "existed_before": existed_before,
                        "operation": "create_directory"
                    })
                except Exception as e:
                    error_msg = f"Failed to create directory {directory}: {str(e)}"
                    result.add_error(error_msg)
                    self.logger.error(error_msg, exc_info=True, extra={
                        "directory": directory,
                        "operation": "create_directory"
                    })
            
            result.metadata.update({
                "total_directories": len(directories),
                "newly_created": created_count,
                "output_dir": str(self.output_dir)
            })
            
            self.logger.info("Directory structure creation completed", extra={
                "total_directories": len(directories),
                "newly_created": created_count,
                "output_dir": str(self.output_dir),
                "operation": "create_directory_structure"
            })
        
        return result

    def copy_static_files(self) -> GenerationResult:
        """
        Copy static files that don't require template processing.
        
        Static files copied:
        - app/__init__.py
        - app/core/__init__.py
        - app/core/README.md
        - app/core/layer_config.yaml (CRITICAL for domain generation)
        - app/repository/__init__.py
        - app/repository/README.md
        - app/repository/layer_config.yaml (CRITICAL for domain generation)
        - app/usecase/__init__.py
        - app/usecase/README.md
        - app/usecase/layer_config.yaml (CRITICAL for domain generation)
        - app/interface/__init__.py
        - app/interface/README.md
        - app/interface/layer_config.yaml (CRITICAL for domain generation)
        - app/service/__init__.py
        - app/service/README.md
        - app/service/layer_config.yaml (CRITICAL for domain generation)
        - tests/__init__.py
        - tests/fixtures/__init__.py
        - pyproject.toml
        - justfile
        
        Returns:
            GenerationResult with details about copied files
        """
        static_files = [
            "app/__init__.py",
            "app/core/__init__.py",
            "app/core/README.md",
            "app/core/layer_config.yaml",
            "app/repository/__init__.py", 
            "app/repository/README.md",
            "app/repository/layer_config.yaml",
            "app/usecase/__init__.py",
            "app/usecase/README.md",
            "app/usecase/layer_config.yaml",
            "app/interface/__init__.py",
            "app/interface/README.md",
            "app/interface/layer_config.yaml",
            "app/service/__init__.py",
            "app/service/README.md",
            "app/service/layer_config.yaml",
            "tests/__init__.py",
            "tests/fixtures/__init__.py",
            "pyproject.toml",
            "justfile"
        ]
        
        result = GenerationResult(
            success=True,
            operation_type="copy_static_files"
        )
        
        with self.logger.timed_operation("copy_static_files", extra={
            "total_files": len(static_files),
            "template_dir": str(self.template_dir),
            "output_dir": str(self.output_dir)
        }):
            for file_path in static_files:
                source_file = self.template_dir / file_path
                dest_file = self.output_dir / file_path
                
                self.logger.debug("Processing static file", extra={
                    "file_path": file_path,
                    "source_file": str(source_file),
                    "dest_file": str(dest_file),
                    "source_exists": source_file.exists(),
                    "operation": "copy_static_file"
                })
                
                if source_file.exists():
                    try:
                        # Create parent directory if needed
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, dest_file)
                        result.add_generated_file(str(dest_file))
                        
                        self.logger.debug("Static file copied successfully", extra={
                            "file_path": file_path,
                            "source_size": source_file.stat().st_size,
                            "operation": "copy_static_file"
                        })
                    except Exception as e:
                        error_msg = f"Failed to copy static file {file_path}: {str(e)}"
                        result.add_error(error_msg)
                        self.logger.error(error_msg, exc_info=True, extra={
                            "file_path": file_path,
                            "operation": "copy_static_file"
                        })
                else:
                    warning_msg = f"Static file not found: {file_path}"
                    result.add_warning(warning_msg)
                    self.logger.warning("Static file not found", extra={
                        "file_path": file_path,
                        "source_file": str(source_file),
                        "template_dir": str(self.template_dir),
                        "operation": "copy_static_file"
                    })
            
            result.metadata.update({
                "total_files": len(static_files),
                "template_dir": str(self.template_dir),
                "output_dir": str(self.output_dir)
            })
            
            self.logger.info("Static files copy operation completed", extra={
                "total_files": len(static_files),
                "copied_count": len(result.files_generated),
                "missing_count": len(result.warnings),
                "operation": "copy_static_files"
            })
        
        return result

    def copy_template_files(self) -> GenerationResult:
        """
        Copy all template files (.j2) and their associated YAML configs to exact same locations.
        
        Template files and configs copied (preserving exact structure):
        - README.md.j2
        - docker-compose.yml.j2
        - app/__init__.py.j2
        - app/config.py.j2
        - app/database.py.j2
        - app/main.py.j2
        - app/interface/exceptions.py.j2
        - app/domain/{{domain}}/ (entire folder with all .j2 files and YAML configs)
        - app/repository/{{domain}}/ (entire folder with all .j2 files and YAML configs)
        - app/usecase/{{domain}}/ (entire folder with all .j2 files and YAML configs)
        - app/interface/{{domain}}/ (entire folder with all .j2 files and YAML configs)
        - app/service/{{service_name}}/ (entire folder with all .j2 files and YAML configs)
        
        Returns:
            GenerationResult with details about copied template files
        """
        # Individual template files
        template_files = [
            "README.md.j2",
            "docker-compose.yml.j2", 
            "app/__init__.py.j2",
            "app/config.py.j2",
            "app/database.py.j2",
            "app/main.py.j2",
            "app/interface/exceptions.py.j2"
        ]
        
        # Template directories (with all contents)
        template_dirs = [
            "app/domain/{{domain}}",
            "app/repository/{{domain}}",
            "app/usecase/{{domain}}",
            "app/interface/{{domain}}",
            "app/service/{{service_name}}"
        ]
        
        result = GenerationResult(
            success=True,
            operation_type="copy_template_files"
        )
        
        with self.logger.timed_operation("copy_template_files", extra={
            "individual_files": len(template_files),
            "template_dirs": len(template_dirs),
            "template_dir": str(self.template_dir),
            "output_dir": str(self.output_dir)
        }):
            # Process individual template files
            self.logger.debug("Processing individual template files", extra={
                "file_count": len(template_files),
                "operation": "copy_individual_templates"
            })
            
            for file_path in template_files:
                source_file = self.template_dir / file_path
                dest_file = self.output_dir / file_path
                
                self.logger.debug("Processing template file", extra={
                    "file_path": file_path,
                    "source_file": str(source_file),
                    "dest_file": str(dest_file),
                    "source_exists": source_file.exists(),
                    "operation": "copy_template_file"
                })
                
                if source_file.exists():
                    try:
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source_file, dest_file)
                        result.add_generated_file(str(dest_file))
                        
                        self.logger.debug("Template file copied successfully", extra={
                            "file_path": file_path,
                            "source_size": source_file.stat().st_size,
                            "operation": "copy_template_file"
                        })
                    except Exception as e:
                        error_msg = f"Failed to copy template file {file_path}: {str(e)}"
                        result.add_error(error_msg)
                        self.logger.error(error_msg, exc_info=True, extra={
                            "file_path": file_path,
                            "operation": "copy_template_file"
                        })
                else:
                    warning_msg = f"Template file not found: {file_path}"
                    result.add_warning(warning_msg)
                    self.logger.warning("Template file not found", extra={
                        "file_path": file_path,
                        "source_file": str(source_file),
                        "operation": "copy_template_file"
                    })
            
            # Process template directories
            self.logger.debug("Processing template directories", extra={
                "dir_count": len(template_dirs),
                "operation": "copy_template_directories"
            })
            
            for dir_path in template_dirs:
                source_dir = self.template_dir / dir_path
                dest_dir = self.output_dir / dir_path
                
                self.logger.debug("Processing template directory", extra={
                    "dir_path": dir_path,
                    "source_dir": str(source_dir),
                    "dest_dir": str(dest_dir),
                    "source_exists": source_dir.exists(),
                    "operation": "copy_template_directory"
                })
                
                if source_dir.exists():
                    try:
                        # Count files before copying
                        source_files = list(source_dir.rglob("*"))
                        source_file_count = len([f for f in source_files if f.is_file()])
                        
                        if dest_dir.exists():
                            self.logger.debug("Removing existing destination directory", extra={
                                "dest_dir": str(dest_dir),
                                "operation": "copy_template_directory"
                            })
                            shutil.rmtree(dest_dir)
                        
                        shutil.copytree(source_dir, dest_dir)
                        
                        # Add all copied files to the result
                        for copied_file in dest_dir.rglob("*"):
                            if copied_file.is_file():
                                result.add_generated_file(str(copied_file))
                        
                        self.logger.debug("Template directory copied successfully", extra={
                            "dir_path": dir_path,
                            "source_file_count": source_file_count,
                            "copied_file_count": len([f for f in dest_dir.rglob("*") if f.is_file()]),
                            "operation": "copy_template_directory"
                        })
                    except Exception as e:
                        error_msg = f"Failed to copy template directory {dir_path}: {str(e)}"
                        result.add_error(error_msg)
                        self.logger.error(error_msg, exc_info=True, extra={
                            "dir_path": dir_path,
                            "operation": "copy_template_directory"
                        })
                else:
                    warning_msg = f"Template directory not found: {dir_path}"
                    result.add_warning(warning_msg)
                    self.logger.warning("Template directory not found", extra={
                        "dir_path": dir_path,
                        "source_dir": str(source_dir),
                        "operation": "copy_template_directory"
                    })
            
            result.metadata.update({
                "total_individual_files": len(template_files),
                "total_template_dirs": len(template_dirs),
                "template_dir": str(self.template_dir),
                "output_dir": str(self.output_dir)
            })
            
            self.logger.info("Template files copy operation completed", extra={
                "total_individual_files": len(template_files),
                "total_template_dirs": len(template_dirs),
                "total_copied_files": len(result.files_generated),
                "warnings_count": len(result.warnings),
                "errors_count": len(result.errors),
                "operation": "copy_template_files"
            })
        
        return result

    def copy_main_files(self, context: TemplateContext) -> GenerationResult:
        """
        Copy core application files that will be processed later by generator service.
        
        Files identified for future template processing:
        - app/__init__.py.j2
        - app/config.py.j2
        - app/database.py.j2
        - app/main.py.j2
        - app/interface/exceptions.py.j2
        
        Args:
            context: Template context with project configuration (for future use)
            
        Returns:
            GenerationResult with details about template files that need processing
        """
        main_template_files = [
            "app/__init__.py.j2",
            "app/config.py.j2", 
            "app/database.py.j2",
            "app/main.py.j2",
            "app/interface/exceptions.py.j2"
        ]
        
        result = GenerationResult(
            success=True,
            operation_type="copy_main_files"
        )
        
        self.logger.debug("Identifying main files for template processing", extra={
            "candidate_files": main_template_files,
            "context_domain": context.domain if context else None,
            "output_dir": str(self.output_dir),
            "operation": "identify_main_files"
        })
        
        # Check paths of files that exist and need processing
        for file_path in main_template_files:
            dest_file = self.output_dir / file_path
            
            self.logger.debug("Checking main template file", extra={
                "file_path": file_path,
                "dest_file": str(dest_file),
                "exists": dest_file.exists(),
                "operation": "check_main_file"
            })
            
            if dest_file.exists():
                result.add_generated_file(str(dest_file))
            else:
                warning_msg = f"Main template file not found: {file_path}"
                result.add_warning(warning_msg)
        
        result.metadata.update({
            "total_candidates": len(main_template_files),
            "context_domain": context.domain if context else None,
            "output_dir": str(self.output_dir)
        })
        
        self.logger.info("Main files identification completed", extra={
            "total_candidates": len(main_template_files),
            "found_files": len(result.files_generated),
            "missing_files": len(result.warnings),
            "operation": "copy_main_files"
        })
        
        return result

    def copy_project_files(self, context: TemplateContext) -> GenerationResult:
        """
        Copy project-level files for future template processing.
        
        Files identified for future template processing:
        - README.md.j2
        - docker-compose.yml.j2
        
        Args:
            context: Template context with project configuration (for future use)
            
        Returns:
            GenerationResult with details about template files that need processing
        """
        project_template_files = [
            "README.md.j2",
            "docker-compose.yml.j2"
        ]
        
        result = GenerationResult(
            success=True,
            operation_type="copy_project_files"
        )
        
        self.logger.debug("Identifying project files for template processing", extra={
            "candidate_files": project_template_files,
            "context_domain": context.domain if context else None,
            "output_dir": str(self.output_dir),
            "operation": "identify_project_files"
        })
        
        # Check paths of files that exist and need processing
        for file_path in project_template_files:
            dest_file = self.output_dir / file_path
            
            self.logger.debug("Checking project template file", extra={
                "file_path": file_path,
                "dest_file": str(dest_file),
                "exists": dest_file.exists(),
                "operation": "check_project_file"
            })
            
            if dest_file.exists():
                result.add_generated_file(str(dest_file))
            else:
                warning_msg = f"Project template file not found: {file_path}"
                result.add_warning(warning_msg)
        
        result.metadata.update({
            "total_candidates": len(project_template_files),
            "context_domain": context.domain if context else None,
            "output_dir": str(self.output_dir)
        })
        
        self.logger.info("Project files identification completed", extra={
            "total_candidates": len(project_template_files),
            "found_files": len(result.files_generated),
            "missing_files": len(result.warnings),
            "operation": "copy_project_files"
        })
        
        return result
