"""
AST-based Python syntax validation for generated code.

Provides comprehensive syntax checking using Python's AST module to ensure
generated Python files are syntactically correct and follow basic coding standards.
"""

import ast
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import logging


@dataclass
class SyntaxError:
    """Represents a syntax error found in Python code."""
    file_path: Path
    line_number: int
    column: int
    message: str
    error_type: str  # "syntax", "semantic", "style"
    severity: str    # "error", "warning", "info"
    suggestion: str = ""


class PythonSyntaxValidator:
    """
    AST-based Python syntax validator for generated code.
    
    Validates:
    - Basic Python syntax using AST parsing
    - Import statement correctness
    - Function and class definitions
    - Common coding issues
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_generated_python(self, file_path: Path) -> List[SyntaxError]:
        """
        Validate Python file syntax using AST parsing.
        
        Args:
            file_path: Path to Python file to validate
            
        Returns:
            List of syntax errors found (empty if valid)
        """
        errors = []
        
        if not file_path.exists():
            errors.append(SyntaxError(
                file_path=file_path,
                line_number=0,
                column=0,
                message="File does not exist",
                error_type="syntax",
                severity="error",
                suggestion="Ensure the file was generated correctly"
            ))
            return errors
        
        if not file_path.suffix == '.py':
            # Not a Python file, skip validation
            return errors
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Validate using AST
            errors.extend(self._validate_ast_syntax(file_path, content))
            
            # Additional semantic checks
            if not errors:  # Only if syntax is valid
                errors.extend(self._validate_semantic_issues(file_path, content))
                errors.extend(self._validate_code_style(file_path, content))
            
        except UnicodeDecodeError as e:
            errors.append(SyntaxError(
                file_path=file_path,
                line_number=0,
                column=0,
                message=f"File encoding error: {e}",
                error_type="syntax",
                severity="error",
                suggestion="Ensure file is saved with UTF-8 encoding"
            ))
        except Exception as e:
            errors.append(SyntaxError(
                file_path=file_path,
                line_number=0,
                column=0,
                message=f"Unexpected validation error: {e}",
                error_type="syntax",
                severity="error",
                suggestion="Check file for corruption or unusual content"
            ))
        
        return errors
    
    def _validate_ast_syntax(self, file_path: Path, content: str) -> List[SyntaxError]:
        """Validate basic Python syntax using AST parsing."""
        errors = []
        
        try:
            # Parse the AST
            tree = ast.parse(content, filename=str(file_path))
            
            # Additional AST-based validations
            errors.extend(self._check_ast_structure(file_path, tree))
            
        except SyntaxError as e:
            errors.append(SyntaxError(
                file_path=file_path,
                line_number=e.lineno or 0,
                column=e.offset or 0,
                message=f"Python syntax error: {e.msg}",
                error_type="syntax",
                severity="error",
                suggestion="Fix the syntax error according to Python grammar rules"
            ))
        except Exception as e:
            errors.append(SyntaxError(
                file_path=file_path,
                line_number=0,
                column=0,
                message=f"AST parsing error: {e}",
                error_type="syntax",
                severity="error",
                suggestion="Check for unusual syntax or encoding issues"
            ))
        
        return errors
    
    def _check_ast_structure(self, file_path: Path, tree: ast.AST) -> List[SyntaxError]:
        """Check AST structure for common issues."""
        errors = []
        
        try:
            # Check for empty modules (except test files)
            if isinstance(tree, ast.Module) and not tree.body:
                if not file_path.name.startswith('test_') and file_path.name != '__init__.py':
                    errors.append(SyntaxError(
                        file_path=file_path,
                        line_number=1,
                        column=0,
                        message="Empty Python module",
                        error_type="semantic",
                        severity="warning",
                        suggestion="Add module content or docstring"
                    ))
            
            # Check for undefined names (basic check)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    # This is a very basic check - full name resolution would require
                    # more sophisticated analysis
                    if node.id in ['undefined', 'None', 'True', 'False']:
                        continue  # Skip built-ins
                    
                # Check for potentially problematic patterns
                if isinstance(node, ast.FunctionDef):
                    if not node.body:
                        errors.append(SyntaxError(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            message=f"Empty function definition: {node.name}",
                            error_type="semantic",
                            severity="warning",
                            suggestion="Add function body or use 'pass' statement"
                        ))
                
                if isinstance(node, ast.ClassDef):
                    if not node.body:
                        errors.append(SyntaxError(
                            file_path=file_path,
                            line_number=node.lineno,
                            column=node.col_offset,
                            message=f"Empty class definition: {node.name}",
                            error_type="semantic",
                            severity="warning",
                            suggestion="Add class body or use 'pass' statement"
                        ))
        
        except Exception as e:
            self.logger.warning(f"Error checking AST structure for {file_path}: {e}")
        
        return errors
    
    def _validate_semantic_issues(self, file_path: Path, content: str) -> List[SyntaxError]:
        """Check for semantic issues in the code."""
        errors = []
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Check for common issues
            if line.startswith('import ') or line.startswith('from '):
                # Check for problematic imports
                if 'import *' in line:
                    errors.append(SyntaxError(
                        file_path=file_path,
                        line_number=line_num,
                        column=0,
                        message="Star import detected (import *)",
                        error_type="semantic",
                        severity="warning",
                        suggestion="Use specific imports instead of star imports"
                    ))
            
            # Check for TODO/FIXME comments
            if 'TODO' in line or 'FIXME' in line:
                errors.append(SyntaxError(
                    file_path=file_path,
                    line_number=line_num,
                    column=line.find('TODO') if 'TODO' in line else line.find('FIXME'),
                    message="TODO/FIXME comment found",
                    error_type="style",
                    severity="info",
                    suggestion="Complete the TODO or remove the comment"
                ))
            
            # Check for potential SQLModel issues
            if 'SQLModel' in line and 'table=' not in line and 'class ' in line:
                if not any(keyword in line for keyword in ['Protocol', 'Base', 'Mixin']):
                    errors.append(SyntaxError(
                        file_path=file_path,
                        line_number=line_num,
                        column=0,
                        message="SQLModel class may need table=True parameter",
                        error_type="semantic",
                        severity="info",
                        suggestion="Add table=True for database table models"
                    ))
        
        return errors
    
    def _validate_code_style(self, file_path: Path, content: str) -> List[SyntaxError]:
        """Check for code style issues."""
        errors = []
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            # Check line length (basic check)
            if len(line) > 120:
                errors.append(SyntaxError(
                    file_path=file_path,
                    line_number=line_num,
                    column=120,
                    message=f"Line too long ({len(line)} > 120 characters)",
                    error_type="style",
                    severity="info",
                    suggestion="Break long lines for better readability"
                ))
            
            # Check for trailing whitespace
            if line.endswith(' ') or line.endswith('\t'):
                errors.append(SyntaxError(
                    file_path=file_path,
                    line_number=line_num,
                    column=len(line.rstrip()),
                    message="Trailing whitespace",
                    error_type="style",
                    severity="info",
                    suggestion="Remove trailing whitespace"
                ))
        
        return errors
    
    def validate_multiple_files(self, file_paths: List[Path]) -> Dict[Path, List[SyntaxError]]:
        """
        Validate multiple Python files.
        
        Args:
            file_paths: List of Python file paths to validate
            
        Returns:
            Dictionary mapping file paths to their validation errors
        """
        results = {}
        
        for file_path in file_paths:
            results[file_path] = self.validate_generated_python(file_path)
        
        return results
    
    def validate_directory(self, directory: Path, pattern: str = "**/*.py") -> Dict[Path, List[SyntaxError]]:
        """
        Validate all Python files in a directory.
        
        Args:
            directory: Directory to search for Python files
            pattern: Glob pattern for finding files (default: **/*.py)
            
        Returns:
            Dictionary mapping file paths to their validation errors
        """
        if not directory.exists():
            return {}
        
        python_files = list(directory.glob(pattern))
        return self.validate_multiple_files(python_files)
    
    def format_errors(self, errors: List[SyntaxError]) -> str:
        """Format syntax errors for display."""
        if not errors:
            return "✅ No syntax errors found"
        
        output = []
        
        # Group by severity
        error_count = sum(1 for e in errors if e.severity == "error")
        warning_count = sum(1 for e in errors if e.severity == "warning") 
        info_count = sum(1 for e in errors if e.severity == "info")
        
        output.append(f"📊 Found {len(errors)} issues: {error_count} errors, {warning_count} warnings, {info_count} info")
        
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
                
                location = f"Line {error.line_number}"
                if error.column > 0:
                    location += f", Column {error.column}"
                
                output.append(f"  {severity_icon} {location}: {error.message}")
                
                if error.suggestion:
                    output.append(f"    💡 {error.suggestion}")
        
        return "\n".join(output)
    
    def get_error_summary(self, errors: List[SyntaxError]) -> Dict[str, Any]:
        """Get summary statistics of validation errors."""
        summary = {
            'total_errors': len(errors),
            'by_severity': {
                'error': sum(1 for e in errors if e.severity == "error"),
                'warning': sum(1 for e in errors if e.severity == "warning"),
                'info': sum(1 for e in errors if e.severity == "info")
            },
            'by_type': {
                'syntax': sum(1 for e in errors if e.error_type == "syntax"),
                'semantic': sum(1 for e in errors if e.error_type == "semantic"),
                'style': sum(1 for e in errors if e.error_type == "style")
            },
            'has_critical_errors': any(e.severity == "error" for e in errors)
        }
        
        return summary


def validate_generated_python_file(file_path: Path) -> List[SyntaxError]:
    """
    Convenience function to validate a single Python file.
    
    Args:
        file_path: Path to Python file to validate
        
    Returns:
        List of syntax errors found
    """
    validator = PythonSyntaxValidator()
    return validator.validate_generated_python(file_path)


def validate_generated_python_directory(directory: Path) -> Dict[Path, List[SyntaxError]]:
    """
    Convenience function to validate all Python files in a directory.
    
    Args:
        directory: Directory containing Python files
        
    Returns:
        Dictionary mapping file paths to validation errors
    """
    validator = PythonSyntaxValidator()
    return validator.validate_directory(directory)