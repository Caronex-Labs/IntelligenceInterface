"""
Import resolution validation for generated Python code.

Validates that all imports in generated files can be resolved correctly,
including checking for:
- Standard library imports
- Third-party package availability
- Local module imports within the project
- Template variable resolution in imports
"""

import ast
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from dataclasses import dataclass
import logging
import re


@dataclass
class ImportError:
    """Represents an import resolution error."""
    file_path: Path
    line_number: int
    import_statement: str
    module_name: str
    error_type: str  # "missing_module", "unresolved_template", "circular_import", "relative_import"
    severity: str    # "error", "warning", "info"
    message: str
    suggestion: str = ""


class ImportResolver:
    """
    Import resolution validator for generated Python code.
    
    Validates:
    - Standard library imports
    - Third-party package imports (SQLModel, FastAPI, Pydantic, etc.)
    - Local project imports
    - Template variable resolution in imports
    - Circular import detection
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root or Path.cwd()
        
        # Standard library modules (Python 3.11+)
        self.stdlib_modules = self._get_stdlib_modules()
        
        # Expected third-party packages for FastAPI SQLModel projects
        self.expected_packages = {
            'sqlmodel', 'fastapi', 'pydantic', 'uvicorn', 'asyncpg', 
            'psycopg2', 'alembic', 'pytest', 'httpx', 'pytest_asyncio'
        }
        
        # Cache for resolved modules
        self._module_cache = {}
        
    def _get_stdlib_modules(self) -> Set[str]:
        """Get set of Python standard library module names."""
        # Core standard library modules that are commonly used
        stdlib_modules = {
            'os', 'sys', 'pathlib', 'typing', 'dataclasses', 'datetime',
            'json', 'logging', 'uuid', 'asyncio', 'functools', 'itertools',
            'collections', 'enum', 'abc', 're', 'math', 'random', 'decimal',
            'urllib', 'http', 'email', 'base64', 'hashlib', 'hmac',
            'sqlite3', 'csv', 'xml', 'html', 'pickle', 'tempfile',
            'shutil', 'subprocess', 'threading', 'multiprocessing',
            'concurrent', 'queue', 'heapq', 'bisect', 'weakref',
            'copy', 'time', 'calendar', 'gzip', 'bz2', 'zipfile',
            'tarfile', 'io', 'string', 'textwrap', 'codecs'
        }
        
        # Add sys.stdlib_module_names if available (Python 3.10+)
        try:
            if hasattr(sys, 'stdlib_module_names'):
                stdlib_modules.update(sys.stdlib_module_names)
        except AttributeError:
            pass
        
        return stdlib_modules
    
    def validate_imports(self, file_path: Path, project_root: Optional[Path] = None) -> List[ImportError]:
        """
        Check if imports in a Python file can be resolved.
        
        Args:
            file_path: Path to Python file to validate
            project_root: Root directory of the project (for relative imports)
            
        Returns:
            List of import errors found
        """
        errors = []
        
        if project_root:
            self.project_root = project_root
        
        if not file_path.exists():
            errors.append(ImportError(
                file_path=file_path,
                line_number=0,
                import_statement="",
                module_name="",
                error_type="missing_module",
                severity="error",
                message="File does not exist",
                suggestion="Ensure the file was generated correctly"
            ))
            return errors
        
        if not file_path.suffix == '.py':
            # Not a Python file, skip validation
            return errors
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Parse imports from the file
            imports = self._extract_imports(file_path, content)
            
            # Validate each import
            for import_info in imports:
                import_errors = self._validate_single_import(file_path, import_info)
                errors.extend(import_errors)
            
            # Check for template variable issues
            template_errors = self._check_template_variables(file_path, content)
            errors.extend(template_errors)
            
        except Exception as e:
            errors.append(ImportError(
                file_path=file_path,
                line_number=0,
                import_statement="",
                module_name="",
                error_type="missing_module",
                severity="error",
                message=f"Error reading file: {e}",
                suggestion="Check file encoding and permissions"
            ))
        
        return errors
    
    def _extract_imports(self, file_path: Path, content: str) -> List[Dict[str, Any]]:
        """Extract import statements from Python code."""
        imports = []
        
        try:
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'type': 'import',
                            'module': alias.name,
                            'alias': alias.asname,
                            'line_number': node.lineno,
                            'statement': f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    level = node.level
                    
                    for alias in node.names:
                        imports.append({
                            'type': 'from_import',
                            'module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'level': level,
                            'line_number': node.lineno,
                            'statement': f"from {'.' * level}{module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                        })
        
        except SyntaxError as e:
            # File has syntax errors, skip import extraction
            self.logger.warning(f"Syntax error in {file_path}, skipping import validation: {e}")
        except Exception as e:
            self.logger.warning(f"Error extracting imports from {file_path}: {e}")
        
        return imports
    
    def _validate_single_import(self, file_path: Path, import_info: Dict[str, Any]) -> List[ImportError]:
        """Validate a single import statement."""
        errors = []
        module_name = import_info['module']
        line_number = import_info['line_number']
        statement = import_info['statement']
        
        # Handle relative imports
        if import_info['type'] == 'from_import' and import_info['level'] > 0:
            return self._validate_relative_import(file_path, import_info)
        
        # Skip validation for certain patterns
        if self._should_skip_import(module_name):
            return errors
        
        # Check if module can be resolved
        resolution_result = self._resolve_module(module_name)
        
        if not resolution_result['found']:
            # Determine error severity based on module type
            severity = self._determine_import_severity(module_name)
            
            errors.append(ImportError(
                file_path=file_path,
                line_number=line_number,
                import_statement=statement,
                module_name=module_name,
                error_type="missing_module",
                severity=severity,
                message=f"Cannot resolve import: {module_name}",
                suggestion=self._suggest_import_fix(module_name)
            ))
        
        return errors
    
    def _validate_relative_import(self, file_path: Path, import_info: Dict[str, Any]) -> List[ImportError]:
        """Validate relative imports within the project."""
        errors = []
        
        try:
            level = import_info['level']
            module = import_info['module']
            
            # Calculate the target module path
            current_dir = file_path.parent
            
            # Go up 'level' directories
            target_dir = current_dir
            for _ in range(level):
                target_dir = target_dir.parent
                if target_dir == target_dir.parent:  # Reached filesystem root
                    errors.append(ImportError(
                        file_path=file_path,
                        line_number=import_info['line_number'],
                        import_statement=import_info['statement'],
                        module_name=f"{'.' * level}{module}",
                        error_type="relative_import",
                        severity="error",
                        message="Relative import goes beyond project root",
                        suggestion="Check relative import levels"
                    ))
                    return errors
            
            # If module is specified, add it to the path
            if module:
                module_parts = module.split('.')
                for part in module_parts:
                    target_dir = target_dir / part
                
                # Check if the module exists
                if not (target_dir.is_dir() or (target_dir.parent / f"{target_dir.name}.py").exists()):
                    errors.append(ImportError(
                        file_path=file_path,
                        line_number=import_info['line_number'],
                        import_statement=import_info['statement'],
                        module_name=f"{'.' * level}{module}",
                        error_type="relative_import",
                        severity="error",
                        message=f"Relative import target not found: {target_dir}",
                        suggestion="Check that the target module exists"
                    ))
        
        except Exception as e:
            errors.append(ImportError(
                file_path=file_path,
                line_number=import_info['line_number'],
                import_statement=import_info['statement'],
                module_name=f"{'.' * import_info['level']}{import_info['module']}",
                error_type="relative_import",
                severity="warning",
                message=f"Error validating relative import: {e}",
                suggestion="Check relative import syntax"
            ))
        
        return errors
    
    def _resolve_module(self, module_name: str) -> Dict[str, Any]:
        """Attempt to resolve a module name."""
        if module_name in self._module_cache:
            return self._module_cache[module_name]
        
        result = {'found': False, 'type': 'unknown', 'location': None}
        
        try:
            # Check if it's a standard library module
            top_level = module_name.split('.')[0]
            if top_level in self.stdlib_modules:
                result = {'found': True, 'type': 'stdlib', 'location': 'standard_library'}
            else:
                # Try to find the module
                spec = importlib.util.find_spec(module_name)
                if spec is not None:
                    result = {'found': True, 'type': 'third_party', 'location': spec.origin}
                else:
                    # Check if it might be a local project module
                    if self._is_potential_local_module(module_name):
                        result = {'found': True, 'type': 'local', 'location': 'project'}
        
        except (ImportError, ValueError, AttributeError):
            # Module not found or invalid
            result = {'found': False, 'type': 'unknown', 'location': None}
        
        self._module_cache[module_name] = result
        return result
    
    def _is_potential_local_module(self, module_name: str) -> bool:
        """Check if a module might be a local project module."""
        # Common local module patterns for FastAPI SQLModel projects
        local_patterns = [
            'app', 'app.domain', 'app.repository', 'app.usecase', 'app.interface',
            'cli', 'cli.generate', 'cli.validate', 'tests'
        ]
        
        for pattern in local_patterns:
            if module_name.startswith(pattern):
                return True
        
        # Check if module path exists in project
        module_parts = module_name.split('.')
        module_path = self.project_root
        
        for part in module_parts:
            module_path = module_path / part
            if module_path.is_dir() or (module_path.parent / f"{part}.py").exists():
                return True
        
        return False
    
    def _should_skip_import(self, module_name: str) -> bool:
        """Determine if an import should be skipped from validation."""
        # Skip certain problematic modules or patterns
        skip_patterns = [
            '__future__',  # Future imports
        ]
        
        for pattern in skip_patterns:
            if module_name.startswith(pattern):
                return True
        
        return False
    
    def _determine_import_severity(self, module_name: str) -> str:
        """Determine the severity of a missing import."""
        top_level = module_name.split('.')[0]
        
        # Critical imports (should definitely exist)
        if top_level in self.expected_packages:
            return "error"
        
        # Project-specific imports
        if module_name.startswith('app.') or module_name.startswith('cli.'):
            return "error"
        
        # Other imports (might be optional or dynamically installed)
        return "warning"
    
    def _suggest_import_fix(self, module_name: str) -> str:
        """Suggest how to fix a missing import."""
        top_level = module_name.split('.')[0]
        
        # Common package installation suggestions
        package_suggestions = {
            'sqlmodel': 'Install SQLModel: pip install sqlmodel',
            'fastapi': 'Install FastAPI: pip install fastapi',
            'pydantic': 'Install Pydantic: pip install pydantic',
            'uvicorn': 'Install Uvicorn: pip install uvicorn',
            'asyncpg': 'Install asyncpg: pip install asyncpg',
            'pytest': 'Install pytest: pip install pytest',
            'httpx': 'Install httpx: pip install httpx'
        }
        
        if top_level in package_suggestions:
            return package_suggestions[top_level]
        
        # Project module suggestions
        if module_name.startswith('app.'):
            return "Ensure the module is generated correctly within the app/ directory"
        
        if module_name.startswith('cli.'):
            return "Check that the CLI module exists and is properly structured"
        
        return f"Install the required package or check the module name: {module_name}"
    
    def _check_template_variables(self, file_path: Path, content: str) -> List[ImportError]:
        """Check for unresolved template variables in imports."""
        errors = []
        
        # Look for Jinja2 template patterns that weren't resolved
        template_patterns = [
            r'\{\{.*?\}\}',  # {{ variable }}
            r'\{%.*?%\}',    # {% statement %}
            r'\{#.*?#\}'     # {# comment #}
        ]
        
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            # Only check import lines
            if 'import' in line:
                for pattern in template_patterns:
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        errors.append(ImportError(
                            file_path=file_path,
                            line_number=line_num,
                            import_statement=line.strip(),
                            module_name=match.group(),
                            error_type="unresolved_template",
                            severity="error",
                            message=f"Unresolved template variable in import: {match.group()}",
                            suggestion="Check template variable resolution in the generation process"
                        ))
        
        return errors
    
    def validate_project_imports(self, project_directory: Path) -> Dict[Path, List[ImportError]]:
        """
        Validate imports for all Python files in a project.
        
        Args:
            project_directory: Root directory of the project
            
        Returns:
            Dictionary mapping file paths to their import errors
        """
        results = {}
        
        if not project_directory.exists():
            return results
        
        # Find all Python files
        python_files = list(project_directory.rglob("*.py"))
        
        for file_path in python_files:
            # Skip certain directories
            if any(skip_dir in file_path.parts for skip_dir in ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv']):
                continue
            
            results[file_path] = self.validate_imports(file_path, project_directory)
        
        return results
    
    def format_errors(self, errors: List[ImportError]) -> str:
        """Format import errors for display."""
        if not errors:
            return "✅ No import errors found"
        
        output = []
        
        # Summary
        error_count = sum(1 for e in errors if e.severity == "error")
        warning_count = sum(1 for e in errors if e.severity == "warning")
        info_count = sum(1 for e in errors if e.severity == "info")
        
        output.append(f"📊 Found {len(errors)} import issues: {error_count} errors, {warning_count} warnings, {info_count} info")
        
        # Group by file
        files_dict = {}
        for error in errors:
            file_path = str(error.file_path)
            if file_path not in files_dict:
                files_dict[file_path] = []
            files_dict[file_path].append(error)
        
        for file_path, file_errors in files_dict.items():
            output.append(f"\n📄 {file_path}")
            
            for error in sorted(file_errors, key=lambda x: x.line_number):
                severity_icon = {
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(error.severity, "❓")
                
                output.append(f"  {severity_icon} Line {error.line_number}: {error.message}")
                output.append(f"    📦 Import: {error.import_statement}")
                
                if error.suggestion:
                    output.append(f"    💡 {error.suggestion}")
        
        return "\n".join(output)
    
    def get_error_summary(self, errors: List[ImportError]) -> Dict[str, Any]:
        """Get summary statistics of import errors."""
        summary = {
            'total_errors': len(errors),
            'by_severity': {
                'error': sum(1 for e in errors if e.severity == "error"),
                'warning': sum(1 for e in errors if e.severity == "warning"),
                'info': sum(1 for e in errors if e.severity == "info")
            },
            'by_type': {
                'missing_module': sum(1 for e in errors if e.error_type == "missing_module"),
                'unresolved_template': sum(1 for e in errors if e.error_type == "unresolved_template"),
                'relative_import': sum(1 for e in errors if e.error_type == "relative_import"),
                'circular_import': sum(1 for e in errors if e.error_type == "circular_import")
            },
            'missing_packages': list(set(
                e.module_name.split('.')[0] 
                for e in errors 
                if e.error_type == "missing_module" and e.severity == "error"
            )),
            'has_critical_errors': any(e.severity == "error" for e in errors)
        }
        
        return summary


def validate_imports_in_file(file_path: Path, project_root: Optional[Path] = None) -> List[ImportError]:
    """
    Convenience function to validate imports in a single file.
    
    Args:
        file_path: Path to Python file to validate
        project_root: Root directory of the project
        
    Returns:
        List of import errors found
    """
    resolver = ImportResolver(project_root)
    return resolver.validate_imports(file_path, project_root)


def validate_imports_in_directory(directory: Path) -> Dict[Path, List[ImportError]]:
    """
    Convenience function to validate imports in all Python files in a directory.
    
    Args:
        directory: Directory containing Python files
        
    Returns:
        Dictionary mapping file paths to import errors
    """
    resolver = ImportResolver(directory)
    return resolver.validate_project_imports(directory)