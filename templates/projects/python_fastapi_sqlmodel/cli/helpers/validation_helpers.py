"""
Validation Helper Classes

Provides validation utilities for generated code and templates,
ensuring quality and correctness of the template generation system.
"""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of code validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class CodeValidator:
    """Validates generated Python code for syntax and quality."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_python_syntax(self, content: str, filename: str = "<generated>") -> ValidationResult:
        """
        Validate Python code syntax using AST parsing.
        
        Args:
            content: Python code content
            filename: Filename for error reporting
            
        Returns:
            ValidationResult with syntax validation results
        """
        result = ValidationResult(valid=True)
        
        try:
            # Parse AST
            tree = ast.parse(content, filename=filename)
            
            # Basic code metrics
            result.metrics.update({
                'lines_of_code': len(content.splitlines()),
                'ast_nodes': len(list(ast.walk(tree))),
                'classes': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
                'functions': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
                'imports': len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
            })
            
        except SyntaxError as e:
            result.valid = False
            result.errors.append(f"Syntax error in {filename}: {e}")
            
        except Exception as e:
            result.valid = False
            result.errors.append(f"AST parsing error in {filename}: {e}")
        
        return result
    
    def validate_sqlmodel_patterns(self, content: str) -> ValidationResult:
        """
        Validate SQLModel-specific patterns in generated code.
        
        Args:
            content: Python code content
            
        Returns:
            ValidationResult with SQLModel pattern validation
        """
        result = ValidationResult(valid=True)
        
        # Check for required SQLModel imports
        required_imports = [
            'from sqlmodel import',
            'SQLModel',
            'Field'
        ]
        
        for import_pattern in required_imports:
            if import_pattern not in content:
                result.warnings.append(f"Missing expected SQLModel import: {import_pattern}")
        
        # Check for table configuration
        if 'table=True' not in content and 'class ' in content:
            result.warnings.append("SQLModel class may be missing table=True configuration")
        
        # Check for proper field definitions
        if 'Field(' in content:
            result.metrics['field_definitions'] = content.count('Field(')
        else:
            result.warnings.append("No Field() definitions found in SQLModel entity")
        
        return result
    
    def validate_async_patterns(self, content: str) -> ValidationResult:
        """
        Validate async/await patterns in generated code.
        
        Args:
            content: Python code content
            
        Returns:
            ValidationResult with async pattern validation
        """
        result = ValidationResult(valid=True)
        
        # Count async functions
        async_def_count = content.count('async def ')
        await_count = content.count('await ')
        
        result.metrics.update({
            'async_functions': async_def_count,
            'await_calls': await_count
        })
        
        # Validate async/await balance
        if async_def_count > 0 and await_count == 0:
            result.warnings.append("Async functions defined but no await calls found")
        
        if await_count > 0 and async_def_count == 0:
            result.errors.append("Await calls found but no async functions defined")
            result.valid = False
        
        # Check for async session usage
        if 'AsyncSession' in content:
            if 'await session.' not in content:
                result.warnings.append("AsyncSession imported but no async session operations found")
        
        return result
    
    def validate_preservation_markers(self, content: str) -> ValidationResult:
        """
        Validate @pyhex preservation markers in generated code.
        
        Args:
            content: Python code content
            
        Returns:
            ValidationResult with preservation marker validation
        """
        result = ValidationResult(valid=True)
        
        # Find all preservation markers
        begin_markers = []
        end_markers = []
        
        for line_num, line in enumerate(content.splitlines(), 1):
            if '@pyhex:begin:' in line:
                marker_name = line.split('@pyhex:begin:')[1].strip()
                begin_markers.append((line_num, marker_name))
            elif '@pyhex:end:' in line:
                marker_name = line.split('@pyhex:end:')[1].strip()
                end_markers.append((line_num, marker_name))
        
        result.metrics.update({
            'preservation_blocks': len(begin_markers),
            'begin_markers': len(begin_markers),
            'end_markers': len(end_markers)
        })
        
        # Validate marker pairing
        if len(begin_markers) != len(end_markers):
            result.errors.append(f"Mismatched preservation markers: {len(begin_markers)} begin, {len(end_markers)} end")
            result.valid = False
        
        # Validate marker names match
        begin_names = [name for _, name in begin_markers]
        end_names = [name for _, name in end_markers]
        
        for begin_name in begin_names:
            if begin_name not in end_names:
                result.errors.append(f"Unmatched begin marker: @pyhex:begin:{begin_name}")
                result.valid = False
        
        for end_name in end_names:
            if end_name not in begin_names:
                result.errors.append(f"Unmatched end marker: @pyhex:end:{end_name}")
                result.valid = False
        
        return result
    
    def validate_complete_file(self, file_path: Path) -> ValidationResult:
        """
        Perform complete validation on a generated file.
        
        Args:
            file_path: Path to generated file
            
        Returns:
            ValidationResult with complete validation results
        """
        if not file_path.exists():
            return ValidationResult(
                valid=False,
                errors=[f"File does not exist: {file_path}"]
            )
        
        try:
            content = file_path.read_text()
            
            # Combine all validation results
            results = [
                self.validate_python_syntax(content, str(file_path)),
                self.validate_sqlmodel_patterns(content),
                self.validate_async_patterns(content),
                self.validate_preservation_markers(content)
            ]
            
            # Aggregate results
            combined_result = ValidationResult(valid=True)
            
            for result in results:
                if not result.valid:
                    combined_result.valid = False
                combined_result.errors.extend(result.errors)
                combined_result.warnings.extend(result.warnings)
                combined_result.metrics.update(result.metrics)
            
            return combined_result
            
        except Exception as e:
            return ValidationResult(
                valid=False,
                errors=[f"Error reading file {file_path}: {e}"]
            )


class TemplateValidator:
    """Validates Jinja2 templates for syntax and best practices."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_template_syntax(self, template_path: Path) -> ValidationResult:
        """
        Validate Jinja2 template syntax.
        
        Args:
            template_path: Path to template file
            
        Returns:
            ValidationResult with template validation results
        """
        result = ValidationResult(valid=True)
        
        if not template_path.exists():
            return ValidationResult(
                valid=False,
                errors=[f"Template file does not exist: {template_path}"]
            )
        
        try:
            import jinja2
            
            # Read template content
            content = template_path.read_text()
            
            # Create environment and parse template
            env = jinja2.Environment()
            env.parse(content)
            
            # Template metrics
            result.metrics.update({
                'template_size': len(content),
                'variable_count': content.count('{{'),
                'block_count': content.count('{%'),
                'comment_count': content.count('{#')
            })
            
        except jinja2.TemplateSyntaxError as e:
            result.valid = False
            result.errors.append(f"Template syntax error in {template_path}: {e}")
            
        except Exception as e:
            result.valid = False
            result.errors.append(f"Error validating template {template_path}: {e}")
        
        return result
    
    def validate_template_variables(self, template_path: Path, expected_vars: List[str]) -> ValidationResult:
        """
        Validate that template uses expected variables.
        
        Args:
            template_path: Path to template file
            expected_vars: List of expected variable names
            
        Returns:
            ValidationResult with variable validation results
        """
        result = ValidationResult(valid=True)
        
        try:
            content = template_path.read_text()
            
            missing_vars = []
            for var in expected_vars:
                if f"{{{{{var}" not in content and f"{{{{{var}}}}}" not in content:
                    missing_vars.append(var)
            
            if missing_vars:
                result.warnings.extend([f"Expected variable not found: {var}" for var in missing_vars])
            
            result.metrics['missing_variables'] = len(missing_vars)
            
        except Exception as e:
            result.valid = False
            result.errors.append(f"Error checking template variables: {e}")
        
        return result