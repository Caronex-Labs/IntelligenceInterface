"""
Project Initializer for FastAPI SQLModel Projects

This module provides complete project initialization functionality, creating
the entire FastAPI project structure with all necessary files and directories.
"""

import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..helpers.generation_helpers import TemplateProcessor, FileGenerationResult

logger = logging.getLogger(__name__)


class ProjectInitializer:
    """Initializes complete FastAPI SQLModel projects with full directory structure."""
    
    # Directories and files to exclude from copy operations
    EXCLUDED_DIRECTORIES = {
        'generated', 'docs', 'milestone_test_outputs', 'archived_outputs', 
        '.git', '__pycache__', '.pytest_cache', '.mypy_cache', 'node_modules'
    }
    
    EXCLUDED_FILES = {
        '.DS_Store', 'Thumbs.db', '*.pyc', '*.pyo', '*.log'
    }
    
    def __init__(self, template_base_dir: Optional[Path] = None):
        """
        Initialize project initializer.
        
        Args:
            template_base_dir: Base directory containing template files
        """
        self.logger = logging.getLogger(__name__)
        
        # Set template base directory
        if template_base_dir is None:
            # Default to template directory relative to this file
            current_dir = Path(__file__).parent.parent.parent
            self.template_base_dir = current_dir
        else:
            self.template_base_dir = template_base_dir
            
        self.logger.info(f"ProjectInitializer template base: {self.template_base_dir}")
        
        # Initialize template processor
        self.template_processor = TemplateProcessor(self.template_base_dir)
    
    def initialize_project(
        self,
        project_name: str,
        target_dir: Path,
        project_config: Optional[Dict[str, Any]] = None,
        clean_existing: bool = False
    ) -> List[FileGenerationResult]:
        """
        Initialize complete FastAPI project structure.
        
        Args:
            project_name: Name of the project
            target_dir: Target directory for project creation
            project_config: Optional project configuration overrides
            clean_existing: Remove existing directory if it exists
            
        Returns:
            List of FileGenerationResult for each created file
        """
        self.logger.info(f"Initializing project '{project_name}' in {target_dir}")
        
        # Prepare target directory
        if target_dir.exists() and clean_existing:
            shutil.rmtree(target_dir)
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create project context
        context = self._create_project_context(project_name, project_config or {})
        
        results = []
        
        # 1. Create directory structure
        self._create_directory_structure(target_dir)
        
        # 2. Copy static files (non-templates)
        static_results = self._copy_static_files(target_dir, context)
        results.extend(static_results)
        
        # 3. Process template files
        template_results = self._process_templates(target_dir, context)
        results.extend(template_results)
        
        # 4. Create essential configuration files
        config_results = self._create_configuration_files(target_dir, context)
        results.extend(config_results)
        
        # 5. Copy template files for project-specific customization
        template_copy_results = self._copy_template_files(target_dir, context)
        results.extend(template_copy_results)
        
        # 6. Install dependencies with UV sync
        uv_result = self._install_dependencies(target_dir, context)
        if uv_result:
            results.append(uv_result)
        
        # 7. Setup co-location structure for domains
        co_location_result = self.setup_co_location_structure(target_dir)
        if co_location_result:
            results.extend(co_location_result)
        
        # 8. Run tests to validate generated project
        test_result = self._run_project_tests(target_dir, context)
        if test_result:
            results.append(test_result)
        
        self.logger.info(f"Project initialization complete: {len(results)} files created")
        return results
    
    def _create_project_context(self, project_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create template context for project initialization."""
        
        # Default project configuration
        default_config = {
            'name': project_name,
            'description': f'FastAPI SQLModel application: {project_name}',
            'version': '0.1.0',
            'author': 'Generated',
            'python_version': '>=3.12',
            'environment': 'development',
            'database_type': 'sqlite',
            'enable_cors': True,
            'enable_compression': True,
            'log_level': 'INFO'
        }
        
        # Merge with user config
        project_config = {**default_config, **config}
        
        # Create comprehensive context
        context = {
            'project_name': project_name,
            'project_slug': project_name.lower().replace(' ', '_').replace('-', '_'),
            'project_title': project_name.title(),
            'app_name': project_name.lower().replace(' ', '-').replace('_', '-'),
            'created_at': datetime.now().isoformat(),
            **project_config
        }
        
        # Add app_info for template compatibility
        context['app_info'] = {
            'name': context['app_name'],
            'title': context['project_title'],
            'description': context['description'],
            'version': context['version']
        }
        
        # Add features for template compatibility (from original config)
        context['features'] = {
            'async_support': True,
            'validation': True,
            'error_handling': True,
            'cors': context.get('enable_cors', True),
            'compression': context.get('enable_compression', True)
        }
        
        self.logger.debug(f"Created project context: {list(context.keys())}")
        return context
    
    def _create_directory_structure(self, target_dir: Path) -> None:
        """Create the complete directory structure for FastAPI project."""
        
        directories = [
            # Core application structure
            'app',
            'app/domain',
            'app/repository', 
            'app/usecase',
            'app/interface',
            
            # Testing structure
            'tests',
            'tests/fixtures',
            'tests/unit',
            'tests/integration',
            
            # Configuration and documentation
            'configs',
            'docs',
            
            # Generated content placeholder
            'generated'
        ]
        
        for dir_path in directories:
            full_path = target_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Created directory: {dir_path}")
    
    def _should_exclude_path(self, path: Path) -> bool:
        """Check if a path should be excluded from copy operations."""
        # Check if any part of the path is in excluded directories
        for part in path.parts:
            if part in self.EXCLUDED_DIRECTORIES:
                return True
        
        # Check excluded file patterns
        for pattern in self.EXCLUDED_FILES:
            if path.match(pattern):
                return True
        
        return False
    
    def _copy_static_files(self, target_dir: Path, context: Dict[str, Any]) -> List[FileGenerationResult]:
        """
        Copy static files that don't require template processing.
        
        Note: Uses explicit file list to avoid copying excluded directories like
        'generated/', 'docs/', 'milestone_test_outputs/', etc.
        """
        
        results = []
        
        # Files to copy directly (excludes build artifacts and temporary files)
        static_files = [
            'app/__init__.py',
            'app/domain/__init__.py',
            'app/repository/__init__.py',
            'app/usecase/__init__.py',
            'app/interface/__init__.py',
            'tests/__init__.py',
            'tests/fixtures/__init__.py'
        ]
        
        for file_path in static_files:
            source_file = self.template_base_dir / file_path
            target_file = target_dir / file_path
            
            # Skip excluded paths (safety check)
            if self._should_exclude_path(Path(file_path)):
                self.logger.debug(f"Skipping excluded path: {file_path}")
                continue
            
            if source_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                
                results.append(FileGenerationResult(
                    file_path=target_file,
                    template_path=str(source_file),
                    success=True,
                    content_length=target_file.stat().st_size,
                    generated_at=datetime.now()
                ))
                self.logger.debug(f"Copied static file: {file_path}")
            else:
                self.logger.warning(f"Static file not found: {source_file}")
        
        return results
    
    def _process_templates(self, target_dir: Path, context: Dict[str, Any]) -> List[FileGenerationResult]:
        """Process Jinja2 template files."""
        
        results = []
        
        # Template files to process
        template_files = [
            ('app/main.py.j2', 'app/main.py'),
            ('app/config.py.j2', 'app/config.py'),
            ('app/database.py.j2', 'app/database.py'),
            ('app/__init__.py.j2', 'app/__init__.py'),
            ('app/interface/exceptions.py.j2', 'app/interface/exceptions.py'),
            ('docker-compose.yml.j2', 'docker-compose.yml'),
            ('README.md.j2', 'README.md')
        ]
        
        for template_path, output_path in template_files:
            source_template = self.template_base_dir / template_path
            target_file = target_dir / output_path
            
            if source_template.exists():
                try:
                    # Render template
                    content = self.template_processor.render_template(template_path, context)
                    
                    # Write to target
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    target_file.write_text(content, encoding='utf-8')
                    
                    results.append(FileGenerationResult(
                        file_path=target_file,
                        template_path=template_path,
                        success=True,
                        content_length=len(content),
                        generated_at=datetime.now()
                    ))
                    self.logger.debug(f"Processed template: {template_path} -> {output_path}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to process template {template_path}: {e}")
                    results.append(FileGenerationResult(
                        file_path=target_file,
                        template_path=template_path,
                        success=False,
                        content_length=0,
                        generated_at=datetime.now(),
                        errors=[str(e)]
                    ))
            else:
                self.logger.warning(f"Template not found: {source_template}")
        
        return results
    
    def _create_configuration_files(self, target_dir: Path, context: Dict[str, Any]) -> List[FileGenerationResult]:
        """Create essential configuration files."""
        
        results = []
        
        # Create pyproject.toml
        pyproject_content = self._generate_pyproject_toml(context)
        pyproject_file = target_dir / 'pyproject.toml'
        pyproject_file.write_text(pyproject_content, encoding='utf-8')
        
        results.append(FileGenerationResult(
            file_path=pyproject_file,
            template_path='generated:pyproject.toml',
            success=True,
            content_length=len(pyproject_content),
            generated_at=datetime.now()
        ))
        
        # Create justfile for project commands
        justfile_content = self._generate_justfile(context)
        justfile_path = target_dir / 'justfile'
        justfile_path.write_text(justfile_content, encoding='utf-8')
        
        results.append(FileGenerationResult(
            file_path=justfile_path,
            template_path='generated:justfile',
            success=True,
            content_length=len(justfile_content),
            generated_at=datetime.now()
        ))
        
        # Create .gitignore
        gitignore_content = self._generate_gitignore(context)
        gitignore_path = target_dir / '.gitignore'
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        
        results.append(FileGenerationResult(
            file_path=gitignore_path,
            template_path='generated:.gitignore',
            success=True,
            content_length=len(gitignore_content),
            generated_at=datetime.now()
        ))
        
        # Create sample environment file
        env_content = self._generate_env_sample(context)
        env_path = target_dir / '.env.sample'
        env_path.write_text(env_content, encoding='utf-8')
        
        results.append(FileGenerationResult(
            file_path=env_path,
            template_path='generated:.env.sample',
            success=True,
            content_length=len(env_content),
            generated_at=datetime.now()
        ))
        
        # Note: uv.lock will be created automatically by `uv sync`
        # No need to create a placeholder - let uv handle it completely
        
        return results
    
    def _generate_pyproject_toml(self, context: Dict[str, Any]) -> str:
        """Generate pyproject.toml content."""
        return f'''[project]
name = "{context['project_slug']}"
version = "{context['version']}"
description = "{context['description']}"
requires-python = "{context['python_version']}"
dependencies = [
    "fastapi>=0.115.13",
    "sqlmodel>=0.0.24",
    "uvicorn[standard]>=0.32.1",
    "pydantic>=2.11.7",
    "pydantic-settings>=2.10.1",
    "jinja2>=3.1.6",
    "pyyaml>=6.0.2",
    "alembic>=1.14.0",
    "asyncpg>=0.30.0",  # PostgreSQL
    "aiosqlite>=0.20.0",  # SQLite
]

[dependency-groups]
dev = [
    "black>=25.1.0",
    "coverage>=7.9.1",
    "hypothesis>=6.93.1",
    "psutil>=7.0.0",
    "pytest>=8.4.1",
    "pytest-asyncio>=1.0.0",
    "pytest-bdd>=8.1.0",
    "pytest-cov>=6.2.1",
    "pytest-xdist>=3.7.0",
    "ruff>=0.12.0",
]

testing = [
    "pytest>=8.4.1",
    "pytest-asyncio>=1.0.0",
    "pytest-bdd>=8.1.0",
    "pytest-cov>=6.2.1",
    "hypothesis>=6.93.1",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["app"]

[tool.uv]
dev-dependencies = []

[tool.black]
line-length = 88
target-version = ['py312']

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow (deselect with '-m not slow')",
    "integration: marks tests as integration tests", 
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/migrations/*",
]

[tool.coverage.report]
show_missing = true
skip_covered = false
fail_under = 80
'''
    
    def _generate_justfile(self, context: Dict[str, Any]) -> str:
        """Generate justfile for project commands."""
        return f'''# {context['project_name']} - Project Commands

# Install dependencies
install:
    uv sync

# Run development server
dev:
    uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run production server
serve:
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Run tests
test:
    uv run pytest

# Run tests with coverage
test-cov:
    uv run pytest --cov=app --cov-report=html --cov-report=term

# Format code
format:
    uv run black .
    uv run ruff check --fix .

# Lint code
lint:
    uv run ruff check .
    uv run black --check .

# Type check
typecheck:
    uv run mypy app

# Generate domain from config
generate-domain config:
    fastapi-sqlmodel-generator generate --config {{{{config}}}} --output ./app

# Initialize new project
init-project name:
    fastapi-sqlmodel-generator init --project-name {{{{name}}}} --output .

# Database migrations
migrate:
    uv run alembic upgrade head

# Create new migration
migration name:
    uv run alembic revision --autogenerate -m "{{{{name}}}}"

# Clean generated files
clean:
    rm -rf __pycache__ .pytest_cache .coverage htmlcov
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {{}} +

# Run full CI pipeline
ci: format lint test

# Build Docker image
docker-build:
    docker build -t {context['project_slug']} .

# Run with Docker Compose
docker-up:
    docker-compose up -d

# Stop Docker Compose
docker-down:
    docker-compose down

# Show project info
info:
    @echo "Project: {context['project_name']}"
    @echo "Version: {context['version']}"
    @echo "Description: {context['description']}"
    @echo "Python: {context['python_version']}"
'''
    
    def _generate_gitignore(self, context: Dict[str, Any]) -> str:
        """Generate .gitignore content."""
        return '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Project specific
*.log
*.db
*.sqlite
.env.local
.env.production

# Generated files
generated/
*/generated/
'''
    
    def _generate_env_sample(self, context: Dict[str, Any]) -> str:
        """Generate .env.sample content."""
        return f'''# {context['project_name']} Environment Configuration

# Application Settings
APP_NAME={context['project_slug']}
APP_VERSION={context['version']}
APP_DESCRIPTION="{context['description']}"
ENVIRONMENT=development

# Server Settings
HOST=0.0.0.0
PORT=8000
LOG_LEVEL={context['log_level']}

# Database Settings
DATABASE_URL=sqlite:///./app.db
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Security (generate secure values for production)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
CORS_ENABLED={str(context['enable_cors']).lower()}
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Feature Flags
COMPRESSION_ENABLED={str(context['enable_compression']).lower()}
DEBUG=true

# External Services
# REDIS_URL=redis://localhost:6379
# CELERY_BROKER_URL=redis://localhost:6379
'''

    def _copy_template_files(self, target_dir: Path, context: Dict[str, Any]) -> List[FileGenerationResult]:
        """
        Copy template files (.j2) and configuration files (.yaml) to target project.
        
        This enables project-specific template customization by providing local templates
        that can be modified for special business requirements.
        """
        
        results = []
        
        # Create templates directory in target project
        templates_dir = target_dir / 'templates'
        templates_dir.mkdir(exist_ok=True)
        
        # Template files to copy (core templates for customization)
        template_files = [
            # Core application templates
            'app/main.py.j2',
            'app/config.py.j2',
            'app/database.py.j2',
            'app/__init__.py.j2',
            'app/interface/exceptions.py.j2',
            
            # Domain layer templates
            'app/domain/{{domain}}/entities.py.j2',
            'app/domain/{{domain}}/exceptions.py.j2',
            'app/domain/{{domain}}/test_entities.py.j2',
            'app/domain/{{domain}}/test_exceptions.py.j2',
            
            # Repository layer templates
            'app/repository/{{domain}}/repository.py.j2',
            'app/repository/{{domain}}/protocols.py.j2',
            'app/repository/{{domain}}/test_repository.py.j2',
            
            # Use case layer templates
            'app/usecase/{{domain}}/usecase.py.j2',
            'app/usecase/{{domain}}/schemas.py.j2',
            'app/usecase/{{domain}}/protocols.py.j2',
            'app/usecase/{{domain}}/test_usecase.py.j2',
            
            # Interface layer templates
            'app/interface/{{domain}}/router.py.j2',
            'app/interface/{{domain}}/protocols.py.j2',
            'app/interface/{{domain}}/dependencies.py.j2',
            
            # Project-level templates
            'docker-compose.yml.j2',
            'README.md.j2'
        ]
        
        # Configuration files to copy (for project-specific defaults)
        config_files = [
            'app/domain/{{domain}}/domain.yaml',
            'app/domain/{{domain}}/entities.yaml',
            'app/repository/{{domain}}/repository.yaml',
            'app/usecase/{{domain}}/usecase.yaml',
            'app/usecase/{{domain}}/business-rules.yaml',
            'app/interface/{{domain}}/interface.yaml'
        ]
        
        # Copy template files
        for template_path in template_files:
            source_file = self.template_base_dir / template_path
            target_file = templates_dir / template_path
            
            if source_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                
                results.append(FileGenerationResult(
                    file_path=target_file,
                    template_path=str(source_file),
                    success=True,
                    content_length=target_file.stat().st_size,
                    generated_at=datetime.now()
                ))
                self.logger.debug(f"Copied template file: {template_path}")
            else:
                self.logger.warning(f"Template file not found: {template_path}")
        
        # Copy configuration files
        for config_path in config_files:
            source_file = self.template_base_dir / config_path
            target_file = templates_dir / config_path
            
            if source_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                
                results.append(FileGenerationResult(
                    file_path=target_file,
                    template_path=str(source_file),
                    success=True,
                    content_length=target_file.stat().st_size,
                    generated_at=datetime.now()
                ))
                self.logger.debug(f"Copied config file: {config_path}")
            else:
                self.logger.debug(f"Config file not found (optional): {config_path}")
        
        # Create template customization guide
        guide_content = self._generate_template_customization_guide(context)
        guide_file = templates_dir / 'CUSTOMIZATION_GUIDE.md'
        guide_file.write_text(guide_content, encoding='utf-8')
        
        results.append(FileGenerationResult(
            file_path=guide_file,
            template_path='generated:template_guide',
            success=True,
            content_length=len(guide_content),
            generated_at=datetime.now()
        ))
        
        self.logger.info(f"Copied {len(results)} template and configuration files")
        return results
    
    def _install_dependencies(self, target_dir: Path, context: Dict[str, Any]) -> Optional[FileGenerationResult]:
        """
        Install dependencies using UV sync.
        
        Automatically runs 'uv sync' to install dependencies and set up the development environment
        immediately after project generation.
        """
        import subprocess
        import os
        
        self.logger.info("Installing dependencies with UV sync...")
        
        try:
            # Change to target directory for UV sync
            original_cwd = os.getcwd()
            os.chdir(target_dir)
            
            # Run uv sync
            result = subprocess.run(
                ['uv', 'sync'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                self.logger.info("Dependencies installed successfully")
                
                # Create a result record for the dependency installation
                return FileGenerationResult(
                    file_path=target_dir / '.venv',  # Virtual environment created by uv sync
                    template_path='uv:sync',
                    success=True,
                    content_length=0,  # Directory size not meaningful here
                    generated_at=datetime.now()
                )
            else:
                error_msg = f"UV sync failed with return code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                
                self.logger.error(error_msg)
                self.logger.warning("Project created successfully, but dependencies not installed")
                self.logger.warning("Please run 'uv sync' manually in the project directory")
                return None
                
        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            self.logger.error("UV sync timed out after 5 minutes")
            self.logger.warning("Please run 'uv sync' manually in the project directory")
            return None
            
        except subprocess.CalledProcessError as e:
            os.chdir(original_cwd)
            self.logger.error(f"UV sync failed: {e}")
            self.logger.warning("Please run 'uv sync' manually in the project directory")
            return None
            
        except FileNotFoundError:
            os.chdir(original_cwd)
            self.logger.error("UV not found. Please install UV: https://docs.astral.sh/uv/")
            self.logger.warning("Please install UV and run 'uv sync' manually in the project directory")
            return None
            
        except Exception as e:
            os.chdir(original_cwd)
            self.logger.error(f"Unexpected error during dependency installation: {e}")
            self.logger.warning("Please run 'uv sync' manually in the project directory")
            return None
    
    def _run_project_tests(self, target_dir: Path, context: Dict[str, Any]) -> Optional[FileGenerationResult]:
        """
        Run tests to validate generated project functionality.
        
        Automatically runs the test suite to ensure generated code works correctly
        and catches generation issues early.
        """
        import subprocess
        import os
        
        self.logger.info("Running tests to validate generated project...")
        
        # Skip tests if dependencies weren't installed
        venv_path = target_dir / '.venv'
        if not venv_path.exists():
            self.logger.warning("Virtual environment not found, skipping test execution")
            self.logger.warning("Please run 'uv sync' and then 'uv run pytest' manually")
            return None
        
        try:
            # Change to target directory for test execution
            original_cwd = os.getcwd()
            os.chdir(target_dir)
            
            # Run tests using UV
            result = subprocess.run(
                ['uv', 'run', 'pytest', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for tests
            )
            
            # Restore original directory
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                self.logger.info("All tests passed! Generated project is validated and ready for development")
                
                # Create a result record for successful test execution
                return FileGenerationResult(
                    file_path=target_dir / 'pytest.log',  # Conceptual test log
                    template_path='pytest:validation',
                    success=True,
                    content_length=len(result.stdout) if result.stdout else 0,
                    generated_at=datetime.now()
                )
            else:
                # Tests failed - this is a serious issue with generated code
                self.logger.error("Generated project tests failed!")
                if result.stdout:
                    self.logger.error(f"Test output:\n{result.stdout}")
                if result.stderr:
                    self.logger.error(f"Test errors:\n{result.stderr}")
                
                self.logger.warning("Generated project may have issues. Please review test output.")
                self.logger.warning("You can run tests manually with: uv run pytest -v")
                return None
                
        except subprocess.TimeoutExpired:
            os.chdir(original_cwd)
            self.logger.error("Test execution timed out after 2 minutes")
            self.logger.warning("Please run 'uv run pytest' manually to check test status")
            return None
            
        except subprocess.CalledProcessError as e:
            os.chdir(original_cwd)
            self.logger.error(f"Test execution failed: {e}")
            self.logger.warning("Please run 'uv run pytest' manually to check test status")
            return None
            
        except FileNotFoundError:
            os.chdir(original_cwd)
            self.logger.error("UV not found for test execution")
            self.logger.warning("Please run 'uv run pytest' manually to check test status")
            return None
            
        except Exception as e:
            os.chdir(original_cwd)
            self.logger.error(f"Unexpected error during test execution: {e}")
            self.logger.warning("Please run 'uv run pytest' manually to check test status")
            return None
    
    def _generate_template_customization_guide(self, context: Dict[str, Any]) -> str:
        """Generate guide for customizing project templates."""
        
        return f'''# Template Customization Guide

This directory contains template files (.j2) and configuration files (.yaml) that you can customize for your specific project requirements.

## Template Structure

### Core Application Templates
- `app/main.py.j2` - FastAPI application entry point
- `app/config.py.j2` - Application configuration
- `app/database.py.j2` - Database connection and setup
- `app/interface/exceptions.py.j2` - Global exception handlers

### Domain Layer Templates
- `app/domain/{{{{domain}}}}/entities.py.j2` - Entity definitions
- `app/domain/{{{{domain}}}}/exceptions.py.j2` - Domain-specific exceptions

### Repository Layer Templates
- `app/repository/{{{{domain}}}}/repository.py.j2` - Data access layer
- `app/repository/{{{{domain}}}}/protocols.py.j2` - Repository interfaces

### Use Case Layer Templates
- `app/usecase/{{{{domain}}}}/usecase.py.j2` - Business logic
- `app/usecase/{{{{domain}}}}/schemas.py.j2` - Data transfer objects

### Interface Layer Templates
- `app/interface/{{{{domain}}}}/router.py.j2` - API routes
- `app/interface/{{{{domain}}}}/dependencies.py.j2` - Dependency injection

## Configuration Files

Configuration files define default settings for each layer:
- `domain.yaml` - Domain configuration
- `entities.yaml` - Entity definitions
- `repository.yaml` - Repository settings
- `usecase.yaml` - Use case configuration
- `business-rules.yaml` - Business logic rules
- `interface.yaml` - API interface settings

## Customizing Templates

1. **Modify existing templates**: Edit .j2 files to change generated code structure
2. **Add custom variables**: Define variables in configuration files
3. **Create new templates**: Add new .j2 files for additional functionality
4. **Update configurations**: Modify .yaml files to change defaults

## Regenerating Code

After customizing templates, regenerate your domain code:

```bash
# Generate specific domain using system-installed CLI
fastapi-sqlmodel-generator generate --config your_domain.yaml --output ./app

# Or use the CLI tool if installed
{context.get('app_name', 'fastapi-app')}-cli generate --domain your_domain --template-dir templates/
```

## Best Practices

1. **Backup originals**: Keep copies of original templates before modification
2. **Test changes**: Regenerate test domains to validate template changes
3. **Document modifications**: Record changes for team collaboration
4. **Version control**: Commit template changes with clear commit messages

## Template Variables

Common variables available in templates:
- `{{{{app_name}}}}` - Application name
- `{{{{domain}}}}` - Domain name
- `{{{{domain_plural}}}}` - Plural domain name
- `{{{{package_name}}}}` - Python package name
- `{{{{database_type}}}}` - Database type (sqlite, postgresql, mysql)

Project: {context.get('app_name', 'FastAPI Application')}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
'''


    def validate_initialization(self, target_dir: Path) -> Dict[str, Any]:
        """Validate that project initialization was successful."""
        
        validation_results = {
            'success': True,
            'errors': [],
            'warnings': [],
            'files_checked': 0,
            'files_missing': [],
            'directories_checked': 0,
            'directories_missing': []
        }
        
        # Required files
        required_files = [
            'pyproject.toml',
            'README.md',
            'justfile',
            '.gitignore',
            '.env.sample',
            # Note: uv.lock is created by `uv sync`, not during initialization
            'app/main.py',
            'app/config.py',
            'app/database.py',
            'app/__init__.py'
        ]
        
        # Required directories
        required_dirs = [
            'app',
            'app/domain',
            'app/repository',
            'app/usecase',
            'app/interface',
            'tests',
            'configs'
        ]
        
        # Check files
        for file_path in required_files:
            full_path = target_dir / file_path
            validation_results['files_checked'] += 1
            if not full_path.exists():
                validation_results['files_missing'].append(file_path)
                validation_results['errors'].append(f"Required file missing: {file_path}")
        
        # Check directories
        for dir_path in required_dirs:
            full_path = target_dir / dir_path
            validation_results['directories_checked'] += 1
            if not full_path.exists():
                validation_results['directories_missing'].append(dir_path)
                validation_results['errors'].append(f"Required directory missing: {dir_path}")
        
        # Set overall success
        validation_results['success'] = len(validation_results['errors']) == 0
        
        return validation_results
    
    def setup_co_location_structure(self, project_dir: Path) -> List[FileGenerationResult]:
        """
        Setup co-location structure for domain directories.
        
        Creates proper directory structure and template directories for 
        co-located architecture where templates and configs live alongside
        generated code.
        
        Args:
            project_dir: Root directory of the project
            
        Returns:
            List of FileGenerationResult for co-location setup
        """
        self.logger.info("Setting up co-location structure for domain architecture")
        
        results = []
        
        try:
            # Create example domain structure to demonstrate co-location
            example_domains = ['Health']  # Example domain for demonstration
            
            for domain_name in example_domains:
                domain_dir = project_dir / 'app' / 'domain' / domain_name
                domain_dir.mkdir(parents=True, exist_ok=True)
                
                # Create co-location configuration templates
                config_templates = self._create_co_location_config_templates(domain_name)
                
                for filename, content in config_templates.items():
                    config_file = domain_dir / filename
                    config_file.write_text(content, encoding='utf-8')
                    
                    results.append(FileGenerationResult(
                        file_path=config_file,
                        template_path=f'generated:co_location_{filename}',
                        success=True,
                        content_length=len(content),
                        generated_at=datetime.now()
                    ))
                
                self.logger.debug(f"Setup co-location structure for domain: {domain_name}")
            
            # Create co-location documentation
            co_location_guide = self._create_co_location_guide()
            guide_file = project_dir / 'docs' / 'CO_LOCATION_GUIDE.md'
            guide_file.parent.mkdir(parents=True, exist_ok=True)
            guide_file.write_text(co_location_guide, encoding='utf-8')
            
            results.append(FileGenerationResult(
                file_path=guide_file,
                template_path='generated:co_location_guide',
                success=True,
                content_length=len(co_location_guide),
                generated_at=datetime.now()
            ))
            
            self.logger.info(f"Successfully setup co-location structure with {len(results)} files")
            
        except Exception as e:
            self.logger.error(f"Failed to setup co-location structure: {e}")
            results.append(FileGenerationResult(
                file_path=project_dir / 'co_location_setup.log',
                template_path='error:co_location_setup',
                success=False,
                content_length=0,
                generated_at=datetime.now(),
                errors=[str(e)]
            ))
        
        return results
    
    def _create_co_location_config_templates(self, domain_name: str) -> Dict[str, str]:
        """
        Create configuration templates for co-location.
        
        Args:
            domain_name: Name of the domain
            
        Returns:
            Dictionary mapping filename to content
        """
        
        # Domain configuration template
        domain_config = f'''# {domain_name} Domain Configuration
# This file configures domain-level settings for {domain_name}

name: {domain_name}
description: "{domain_name} domain configuration for co-located architecture"
package: {domain_name.lower()}

# Base fields that all entities in this domain inherit
base_fields:
  - name: id
    type: UUID
    required: true
    primary_key: true
    sqlmodel_field: "Field(primary_key=True, default_factory=uuid4)"
  - name: created_at
    type: datetime
    required: true
    sqlmodel_field: "Field(default_factory=datetime.utcnow)"
  - name: updated_at
    type: datetime
    required: true
    sqlmodel_field: "Field(default_factory=datetime.utcnow)"

# SQLModel configuration
sqlmodel_config:
  table_naming: snake_case
  field_naming: snake_case
  generate_id_fields: true
  timestamp_fields: ["created_at", "updated_at"]

# Co-location metadata
co_location:
  template_source: co_located
  config_source: co_located
  generation_mode: co_located
  template_version: "1.0.0"
'''
        
        # Entities configuration template
        entities_config = f'''# {domain_name} Entities Configuration
# This file defines entities for the {domain_name} domain

entities:
  - name: {domain_name}
    description: "Primary {domain_name} entity"
    table_name: {domain_name.lower()}s
    fields:
      - name: name
        type: str
        required: true
        description: "{domain_name} name"
        sqlmodel_field: "Field(index=True)"
      - name: description
        type: Optional[str]
        required: false
        description: "{domain_name} description"
      - name: status
        type: str
        required: true
        default: "active"
        description: "{domain_name} status"
        sqlmodel_field: "Field(default='active')"
    relationships: []

endpoints:
  - method: POST
    path: "/"
    operation: create
    description: "Create a new {domain_name.lower()}"
  - method: GET
    path: "/{{id}}"
    operation: get_by_id
    description: "Get {domain_name.lower()} by ID"
  - method: GET
    path: "/"
    operation: list
    description: "List all {domain_name.lower()}s"
  - method: PUT
    path: "/{{id}}"
    operation: update
    description: "Update {domain_name.lower()}"
  - method: DELETE
    path: "/{{id}}"
    operation: delete
    description: "Delete {domain_name.lower()}"
'''
        
        return {
            'domain.yaml': domain_config,
            'entities.yaml': entities_config
        }
    
    def _create_co_location_guide(self) -> str:
        """Create comprehensive co-location architecture guide."""
        
        return '''# Co-Location Architecture Guide

This project supports **co-location architecture** where templates and configurations live alongside generated code for easy customization and maintenance.

## What is Co-Location?

Co-location means that templates (.j2 files) and configuration files (.yaml) are stored in the same directory as the generated code, rather than in separate global directories.

### Traditional Structure:
```
configs/
  user_domain.yaml
  user_entities.yaml
templates/
  app/domain/{{domain}}/entities.py.j2
app/domain/User/
  entities.py
  exceptions.py
```

### Co-Located Structure:
```
app/domain/User/
  entities.py          # Generated code
  exceptions.py        # Generated code
  entities.py.j2       # Template (co-located)
  exceptions.py.j2     # Template (co-located)
  domain.yaml          # Config (co-located)
  entities.yaml        # Config (co-located)
```

## Benefits of Co-Location

1. **Domain Isolation**: Each domain is self-contained with its own templates and configs
2. **Easy Customization**: Modify templates for specific domains without affecting others
3. **Version Control**: Templates and configs are versioned alongside the code they generate
4. **Team Collaboration**: Different teams can work on different domains independently
5. **Template Evolution**: Templates can evolve with domain requirements

## Using Co-Location

### Generating with Co-Location

```bash
# Generate domain using co-located configs and templates (auto-detected)
fastapi-sqlmodel-generator generate --config app/domain/User/domain.yaml --output ./app
```

### Customizing Templates

1. **Modify co-located templates**: Edit `.j2` files in domain directories
2. **Update configurations**: Modify `domain.yaml` and `entities.yaml` files
3. **Regenerate**: Run generation command to apply changes

### Creating New Domains

```bash
# Create domain configs and generate (co-location auto-detected)
fastapi-sqlmodel-generator generate --config external_product.yaml --output ./app
```

## Configuration Hierarchy

Co-location supports configuration merging with this precedence:

1. **Co-located configs** (highest priority)
2. **Domain-specific overrides**
3. **Global defaults** (lowest priority)

### Example Override:
```yaml
# app/domain/User/domain.yaml
name: User
description: "Custom user domain with special requirements"

# Override global SQLModel settings
sqlmodel_config:
  table_naming: PascalCase  # Override global snake_case
  
# Domain-specific base fields
base_fields:
  - name: tenant_id
    type: UUID
    required: true
    description: "Multi-tenant isolation"
```

## Template Customization

### Basic Customization
Edit the `.j2` template files directly:

```jinja2
{# app/domain/User/entities.py.j2 #}
"""
{{ domain }} entities with custom business logic.
Generated: {{ now().strftime('%Y-%m-%d %H:%M:%S') }}
"""

from sqlmodel import SQLModel, Field
{% if custom_imports %}
{{ custom_imports }}
{% endif %}

class {{ entity.name }}(SQLModel, table=True):
    """{{ entity.description or entity.name + ' entity' }}"""
    
    {% for field in entity.fields %}
    {{ field.name }}: {{ field.python_type }} = {{ field.sqlmodel_field_params }}
    {% endfor %}
    
    {% if custom_methods %}
    # Custom business methods
    {{ custom_methods }}
    {% endif %}
```

### Advanced Customization
Create domain-specific template variables:

```yaml
# app/domain/User/domain.yaml
template_context:
  custom_imports: |
    from app.security import hash_password
    from app.notifications import send_welcome_email
  custom_methods: |
    def set_password(self, password: str) -> None:
        self.password_hash = hash_password(password)
    
    def send_welcome(self) -> None:
        send_welcome_email(self.email)
```

## Migration from Traditional to Co-Located

### Migration Process
```bash
# Modern workflow automatically handles migration
# External config → co-located breakdown → generation
fastapi-sqlmodel-generator generate --config configs/user_domain.yaml --output ./app

# This automatically creates co-located structure and generates code
```

## Best Practices

### 1. Template Versioning
Each domain tracks its template version:

```yaml
# .template_version.yaml (auto-generated)
template_version: "1.0.0"
copied_at: "2024-01-15T10:30:00"
templates:
  - entities.py.j2
  - exceptions.py.j2
source: global_templates
customization_status: modified
```

### 2. Backup Before Customization
```bash
# Backup original templates before modification
cp entities.py.j2 entities.py.j2.backup
```

### 3. Document Changes
```yaml
# domain.yaml
metadata:
  customizations:
    - "Added multi-tenant support"
    - "Custom validation for email fields"
    - "Integration with external API"
  last_modified: "2024-01-15"
  modified_by: "development-team"
```

### 4. Test Custom Templates
```bash
# Generate test domain to validate templates
fastapi-sqlmodel-generator generate --config app/domain/TestUser/domain.yaml --output ./app --validate
```

## Troubleshooting

### Template Not Found
- Ensure templates exist in domain directory
- Check template file names match expected patterns
- Verify template syntax with `--validate` flag

### Configuration Conflicts
- Use `--debug` flag to see configuration merging
- Check precedence order (co-located > domain > global)
- Validate YAML syntax in configuration files

### Generation Errors
- Check template variables are defined
- Verify template syntax with Jinja2 validator
- Use `--strict` mode for detailed error reporting

## Integration with Development Workflow

### Git Integration
```gitignore
# .gitignore
# Keep co-located templates and configs in version control
!app/domain/*/domain.yaml
!app/domain/*/entities.yaml
!app/domain/*/*.j2

# Ignore generated files
app/domain/*/entities.py
app/domain/*/exceptions.py
```

### CI/CD Pipeline
```yaml
# .github/workflows/validate-templates.yml
name: Validate Co-Located Templates
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Validate Templates
        run: |
          python -m cli.validate.template_linter app/domain/*/
```

## Future Enhancements

- **Template inheritance**: Base templates with domain overrides
- **Automated migration**: Tools for migrating existing projects
- **Template marketplace**: Sharing templates across projects
- **Real-time validation**: IDE integration for template editing

For more information, see the full documentation at `/docs/` or run:
```bash
fastapi-sqlmodel-generator --help
```
'''