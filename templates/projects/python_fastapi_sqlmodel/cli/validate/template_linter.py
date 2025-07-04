"""Template linter for Jinja2 templates and pattern validation"""
import re
from pathlib import Path
from typing import List
from dataclasses import dataclass
from jinja2 import Environment, TemplateSyntaxError
import click


@dataclass
class ValidationIssue:
    """Represents a validation issue found in templates"""
    file_path: Path
    line_number: int
    column: int
    severity: str  # "error", "warning", "info"
    rule_id: str
    message: str
    suggestion: str = ""


class ValidationRule:
    """Base class for template validation rules"""
    
    def __init__(self, rule_id: str, description: str):
        self.rule_id = rule_id
        self.description = description
    
    def validate(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate template content and return issues"""
        raise NotImplementedError


class Jinja2SyntaxRule(ValidationRule):
    """Validates Jinja2 template syntax"""
    
    def __init__(self):
        super().__init__("J001", "Jinja2 template syntax validation")
    
    def validate(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Check Jinja2 syntax validity"""
        issues = []
        env = Environment()
        
        try:
            env.parse(content)
        except TemplateSyntaxError as e:
            issues.append(ValidationIssue(
                file_path=file_path,
                line_number=e.lineno or 0,
                column=0,
                severity="error",
                rule_id=self.rule_id,
                message=f"Jinja2 syntax error: {e.message}",
                suggestion="Check template syntax and fix the error"
            ))
        
        return issues


class HexagonalArchitectureRule(ValidationRule):
    """Validates hexagonal architecture compliance"""
    
    def __init__(self):
        super().__init__("H001", "Hexagonal architecture compliance")
    
    def validate(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Check hexagonal architecture patterns"""
        issues = []
        parts = file_path.parts
        
        if "domain" in parts:
            issues.extend(self._validate_domain_layer(file_path, content))
        elif "application" in parts:
            issues.extend(self._validate_application_layer(file_path, content))
        elif "infrastructure" in parts:
            issues.extend(self._validate_infrastructure_layer(file_path, content))
        elif "interface" in parts:
            issues.extend(self._validate_interface_layer(file_path, content))
        
        return issues
    
    def _validate_domain_layer(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate domain layer dependencies"""
        issues = []
        
        # Domain layer should not import from other layers
        forbidden_imports = ["infrastructure", "interface", "application"]
        for forbidden in forbidden_imports:
            if f"from {forbidden}" in content or f"import {forbidden}" in content:
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=self._find_import_line(content, forbidden),
                    column=0,
                    severity="error",
                    rule_id=self.rule_id,
                    message=f"Domain layer should not import from {forbidden} layer",
                    suggestion="Remove dependency or move logic to appropriate layer"
                ))
        
        return issues
    
    def _validate_application_layer(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate application layer dependencies"""
        issues = []
        
        # Application layer should not import from infrastructure or interface
        forbidden_imports = ["infrastructure", "interface"]
        for forbidden in forbidden_imports:
            if f"from {forbidden}" in content or f"import {forbidden}" in content:
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=self._find_import_line(content, forbidden),
                    column=0,
                    severity="error",
                    rule_id=self.rule_id,
                    message=f"Application layer should not import from {forbidden} layer",
                    suggestion="Use dependency injection or interfaces instead"
                ))
        
        return issues
    
    def _validate_infrastructure_layer(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate infrastructure layer patterns"""
        # Infrastructure layer has more flexibility
        return []
    
    def _validate_interface_layer(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Validate interface layer patterns"""
        # Interface layer should primarily use application layer
        return []
    
    def _find_import_line(self, content: str, module: str) -> int:
        """Find line number of import statement"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if f"from {module}" in line or f"import {module}" in line:
                return i
        return 0


class NamingConventionRule(ValidationRule):
    """Validates naming conventions"""
    
    def __init__(self):
        super().__init__("N001", "Naming convention compliance")
    
    def validate(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Check naming conventions"""
        issues = []
        
        # Check class naming (PascalCase)
        class_pattern = r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            if not self._is_pascal_case(class_name):
                line_num = content[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(),
                    severity="warning",
                    rule_id=self.rule_id,
                    message=f"Class name '{class_name}' should use PascalCase",
                    suggestion="Use PascalCase for class names (e.g., UserEntity)"
                ))
        
        # Check function naming (snake_case)
        function_pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        for match in re.finditer(function_pattern, content):
            function_name = match.group(1)
            if not self._is_snake_case(function_name):
                line_num = content[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=match.start(),
                    severity="warning",
                    rule_id=self.rule_id,
                    message=f"Function name '{function_name}' should use snake_case",
                    suggestion="Use snake_case for function names (e.g., get_user_by_id)"
                ))
        
        return issues
    
    def _is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase convention"""
        return bool(re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention"""
        return bool(re.match(r'^[a-z_][a-z0-9_]*$', name))


class CodePreservationRule(ValidationRule):
    """Validates code preservation markers"""
    
    def __init__(self):
        super().__init__("P001", "Code preservation marker validation")
    
    def validate(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Check code preservation markers"""
        issues = []
        
        # Find all preservation markers
        begin_pattern = r'#\s*@pyhex:begin:(\w+)'
        end_pattern = r'#\s*@pyhex:end:(\w+)'
        
        begin_markers = {}
        end_markers = {}
        
        # Collect begin markers
        for match in re.finditer(begin_pattern, content):
            marker_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            begin_markers[marker_name] = line_num
        
        # Collect end markers
        for match in re.finditer(end_pattern, content):
            marker_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            end_markers[marker_name] = line_num
        
        # Check for unmatched markers
        for marker_name, line_num in begin_markers.items():
            if marker_name not in end_markers:
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=0,
                    severity="error",
                    rule_id=self.rule_id,
                    message=f"Unmatched @pyhex:begin:{marker_name} marker",
                    suggestion=f"Add corresponding @pyhex:end:{marker_name} marker"
                ))
        
        for marker_name, line_num in end_markers.items():
            if marker_name not in begin_markers:
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=0,
                    severity="error",
                    rule_id=self.rule_id,
                    message=f"Unmatched @pyhex:end:{marker_name} marker",
                    suggestion=f"Add corresponding @pyhex:begin:{marker_name} marker"
                ))
        
        return issues


class SQLModelPatternRule(ValidationRule):
    """Validates SQLModel usage patterns"""
    
    def __init__(self):
        super().__init__("S001", "SQLModel pattern validation")
    
    def validate(self, file_path: Path, content: str) -> List[ValidationIssue]:
        """Check SQLModel patterns"""
        issues = []
        
        # Check for SQLModel imports in entity files
        if "entities" in str(file_path) and "sqlmodel" not in content.lower():
            issues.append(ValidationIssue(
                file_path=file_path,
                line_number=1,
                column=0,
                severity="warning",
                rule_id=self.rule_id,
                message="Entity file should import SQLModel",
                suggestion="Add 'from sqlmodel import SQLModel, Field'"
            ))
        
        # Check for table=True in model definitions
        model_pattern = r'class\s+\w+.*SQLModel.*\):'
        for match in re.finditer(model_pattern, content):
            model_def = match.group(0)
            if "table=True" not in content[match.start():match.end() + 100]:
                line_num = content[:match.start()].count('\n') + 1
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=line_num,
                    column=0,
                    severity="info",
                    rule_id=self.rule_id,
                    message="SQLModel class might need table=True parameter",
                    suggestion="Add table=True for database table models"
                ))
        
        return issues


class TemplateLinter:
    """Main template linter class"""
    
    def __init__(self):
        self.rules = [
            Jinja2SyntaxRule(),
            HexagonalArchitectureRule(),
            NamingConventionRule(),
            CodePreservationRule(),
            SQLModelPatternRule()
        ]
        self.ignored_patterns = [
            r'__pycache__',
            r'\.git',
            r'\.pytest_cache',
            r'htmlcov',
            r'\.coverage'
        ]
    
    def lint_file(self, file_path: Path) -> List[ValidationIssue]:
        """Lint a single template file"""
        if not file_path.exists() or not file_path.is_file():
            return []
        
        # Skip ignored files
        for pattern in self.ignored_patterns:
            if re.search(pattern, str(file_path)):
                return []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except (UnicodeDecodeError, PermissionError):
            return []
        
        issues = []
        for rule in self.rules:
            try:
                rule_issues = rule.validate(file_path, content)
                issues.extend(rule_issues)
            except Exception as e:
                # Don't let rule failures break the entire linting process
                issues.append(ValidationIssue(
                    file_path=file_path,
                    line_number=0,
                    column=0,
                    severity="error",
                    rule_id="LINT001",
                    message=f"Linting rule {rule.rule_id} failed: {e}",
                    suggestion="Check rule implementation"
                ))
        
        return issues
    
    def lint_directory(self, directory: Path, pattern: str = "**/*.j2") -> List[ValidationIssue]:
        """Lint all template files in directory"""
        issues = []
        
        for file_path in directory.rglob(pattern):
            file_issues = self.lint_file(file_path)
            issues.extend(file_issues)
        
        # Also lint Python files for architecture compliance
        for file_path in directory.rglob("**/*.py"):
            file_issues = self.lint_file(file_path)
            issues.extend(file_issues)
        
        return issues
    
    def format_issues(self, issues: List[ValidationIssue]) -> str:
        """Format issues for display"""
        if not issues:
            return "✅ No issues found"
        
        output = []
        issues_by_file = {}
        
        for issue in issues:
            file_path = str(issue.file_path)
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        for file_path, file_issues in issues_by_file.items():
            output.append(f"\n📄 {file_path}")
            
            for issue in sorted(file_issues, key=lambda x: x.line_number):
                severity_icon = {
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(issue.severity, "❓")
                
                output.append(f"  {severity_icon} Line {issue.line_number}: [{issue.rule_id}] {issue.message}")
                if issue.suggestion:
                    output.append(f"    💡 {issue.suggestion}")
        
        # Summary
        error_count = sum(1 for issue in issues if issue.severity == "error")
        warning_count = sum(1 for issue in issues if issue.severity == "warning")
        info_count = sum(1 for issue in issues if issue.severity == "info")
        
        output.insert(0, f"📊 Found {len(issues)} issues: {error_count} errors, {warning_count} warnings, {info_count} info")
        
        return "\n".join(output)


@click.command()
@click.option('--path', type=click.Path(exists=True, path_type=Path), 
              default=Path('.'), help='Path to lint')
@click.option('--pattern', default='**/*.j2', 
              help='File pattern to lint (default: **/*.j2)')
@click.option('--check-syntax', is_flag=True, 
              help='Only check Jinja2 syntax')
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.option('--fail-on-error', is_flag=True,
              help='Exit with error code if issues found')
def main(path: Path, pattern: str, check_syntax: bool, format: str, fail_on_error: bool):
    """Template linter for Jinja2 templates and architecture validation"""
    linter = TemplateLinter()
    
    if check_syntax:
        # Only run syntax validation
        linter.rules = [rule for rule in linter.rules if isinstance(rule, Jinja2SyntaxRule)]
    
    if path.is_file():
        issues = linter.lint_file(path)
    else:
        issues = linter.lint_directory(path, pattern)
    
    if format == 'json':
        import json
        issues_data = [
            {
                'file': str(issue.file_path),
                'line': issue.line_number,
                'column': issue.column,
                'severity': issue.severity,
                'rule': issue.rule_id,
                'message': issue.message,
                'suggestion': issue.suggestion
            }
            for issue in issues
        ]
        click.echo(json.dumps(issues_data, indent=2))
    else:
        click.echo(linter.format_issues(issues))
    
    if fail_on_error and any(issue.severity == "error" for issue in issues):
        raise click.ClickException("Linting failed with errors")


if __name__ == '__main__':
    main()