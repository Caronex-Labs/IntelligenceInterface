"""Configuration validator for YAML domain configurations"""
import yaml
import jsonschema
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import click

from cli.generate.config.models import DomainConfig
from pydantic import ValidationError


@dataclass
class ConfigValidationIssue:
    """Represents a configuration validation issue"""
    file_path: Path
    severity: str  # "error", "warning", "info"
    message: str
    location: str = ""
    suggestion: str = ""


class ConfigValidator:
    """YAML configuration validator"""
    
    def __init__(self):
        self.schema = self._generate_schema()
    
    def _generate_schema(self) -> Dict[str, Any]:
        """Generate JSON schema from Pydantic models"""
        try:
            return DomainConfig.model_json_schema()
        except Exception:
            # Fallback basic schema if Pydantic schema generation fails
            return {
                "type": "object",
                "required": ["domain", "entities"],
                "properties": {
                    "domain": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "plural": {"type": "string"},
                            "entities": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "entities": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "object",
                            "required": ["name", "fields"],
                            "properties": {
                                "name": {"type": "string", "minLength": 1},
                                "fields": {
                                    "type": "array",
                                    "minItems": 1,
                                    "items": {
                                        "type": "object",
                                        "required": ["name", "type"],
                                        "properties": {
                                            "name": {"type": "string", "minLength": 1},
                                            "type": {"type": "string", "minLength": 1},
                                            "required": {"type": "boolean"},
                                            "index": {"type": "boolean"},
                                            "unique": {"type": "boolean"},
                                            "default": {"type": "string"},
                                            "foreign_key": {"type": "string"}
                                        }
                                    }
                                },
                                "relationships": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["entity", "type"],
                                        "properties": {
                                            "entity": {"type": "string"},
                                            "type": {"type": "string", "enum": ["one_to_one", "one_to_many", "many_to_one", "many_to_many"]},
                                            "back_populates": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "endpoints": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["method", "path", "operation"],
                            "properties": {
                                "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]},
                                "path": {"type": "string"},
                                "operation": {"type": "string"}
                            }
                        }
                    }
                }
            }
    
    def validate_file(self, config_path: Path) -> List[ConfigValidationIssue]:
        """Validate a single configuration file"""
        issues = []
        
        if not config_path.exists():
            return [ConfigValidationIssue(
                file_path=config_path,
                severity="error",
                message="Configuration file does not exist",
                suggestion="Create the configuration file"
            )]
        
        try:
            # Load YAML content
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if config_data is None:
                return [ConfigValidationIssue(
                    file_path=config_path,
                    severity="error",
                    message="Configuration file is empty or invalid YAML",
                    suggestion="Add valid YAML content to the file"
                )]
            
            # JSON Schema validation
            try:
                jsonschema.validate(config_data, self.schema)
            except jsonschema.ValidationError as e:
                issues.append(ConfigValidationIssue(
                    file_path=config_path,
                    severity="error",
                    message=f"Schema validation failed: {e.message}",
                    location=f"Path: {'.'.join(str(p) for p in e.absolute_path)}",
                    suggestion="Fix the configuration structure according to the schema"
                ))
            
            # Pydantic model validation (more detailed)
            try:
                DomainConfig(**config_data)
            except ValidationError as e:
                for error in e.errors():
                    location = " -> ".join(str(loc) for loc in error['loc'])
                    issues.append(ConfigValidationIssue(
                        file_path=config_path,
                        severity="error",
                        message=f"Validation error: {error['msg']}",
                        location=f"Field: {location}",
                        suggestion="Check field types and required values"
                    ))
            
            # Additional business logic validation
            if not issues:  # Only if basic validation passed
                issues.extend(self._validate_business_rules(config_path, config_data))
            
        except yaml.YAMLError as e:
            issues.append(ConfigValidationIssue(
                file_path=config_path,
                severity="error",
                message=f"YAML syntax error: {e}",
                suggestion="Fix YAML syntax errors"
            ))
        except Exception as e:
            issues.append(ConfigValidationIssue(
                file_path=config_path,
                severity="error",
                message=f"Unexpected error: {e}",
                suggestion="Check file format and content"
            ))
        
        return issues
    
    def _validate_business_rules(self, config_path: Path, config_data: Dict[str, Any]) -> List[ConfigValidationIssue]:
        """Validate business logic rules"""
        issues = []
        
        # Check entity naming consistency
        domain_name = config_data.get('domain', {}).get('name', '')
        entities = config_data.get('entities', [])
        
        for entity in entities:
            entity_name = entity.get('name', '')
            
            # Entity name should be related to domain or be explicitly different
            if domain_name and entity_name and domain_name.lower() not in entity_name.lower():
                issues.append(ConfigValidationIssue(
                    file_path=config_path,
                    severity="warning",
                    message=f"Entity '{entity_name}' name doesn't relate to domain '{domain_name}'",
                    location=f"Entity: {entity_name}",
                    suggestion="Consider naming entities consistently with the domain"
                ))
            
            # Check for required ID field pattern
            fields = entity.get('fields', [])
            has_id_field = any(field.get('name') == 'id' for field in fields)
            
            if not has_id_field:
                issues.append(ConfigValidationIssue(
                    file_path=config_path,
                    severity="info",
                    message=f"Entity '{entity_name}' doesn't have an explicit 'id' field",
                    location=f"Entity: {entity_name}",
                    suggestion="SQLModel will auto-generate ID if not specified"
                ))
            
            # Check for timestamp fields
            timestamp_fields = ['created_at', 'updated_at']
            existing_timestamps = [field.get('name') for field in fields if field.get('name') in timestamp_fields]
            
            if not existing_timestamps:
                issues.append(ConfigValidationIssue(
                    file_path=config_path,
                    severity="info",
                    message=f"Entity '{entity_name}' doesn't have timestamp fields",
                    location=f"Entity: {entity_name}",
                    suggestion="Consider adding created_at and updated_at fields for auditing"
                ))
        
        # Check relationship consistency
        issues.extend(self._validate_relationships(config_path, config_data))
        
        # Check endpoint configuration
        issues.extend(self._validate_endpoints(config_path, config_data))
        
        return issues
    
    def _validate_relationships(self, config_path: Path, config_data: Dict[str, Any]) -> List[ConfigValidationIssue]:
        """Validate entity relationships"""
        issues = []
        entities = config_data.get('entities', [])
        entity_names = {entity.get('name') for entity in entities}
        
        for entity in entities:
            entity_name = entity.get('name', '')
            relationships = entity.get('relationships', [])
            
            for rel in relationships:
                target_entity = rel.get('entity', '')
                rel_type = rel.get('type', '')
                
                # Check if target entity exists
                if target_entity not in entity_names:
                    issues.append(ConfigValidationIssue(
                        file_path=config_path,
                        severity="error",
                        message=f"Relationship target '{target_entity}' not found in entities",
                        location=f"Entity: {entity_name} -> {target_entity}",
                        suggestion="Add the target entity or fix the relationship reference"
                    ))
                
                # Check relationship type validity
                valid_types = ['one_to_one', 'one_to_many', 'many_to_one', 'many_to_many']
                if rel_type not in valid_types:
                    issues.append(ConfigValidationIssue(
                        file_path=config_path,
                        severity="error",
                        message=f"Invalid relationship type '{rel_type}'",
                        location=f"Entity: {entity_name} -> {target_entity}",
                        suggestion=f"Use one of: {', '.join(valid_types)}"
                    ))
                
                # Check for foreign key fields in many_to_one relationships
                if rel_type == 'many_to_one':
                    fields = entity.get('fields', [])
                    fk_field_name = f"{target_entity.lower()}_id"
                    has_fk = any(field.get('name') == fk_field_name for field in fields)
                    
                    if not has_fk:
                        issues.append(ConfigValidationIssue(
                            file_path=config_path,
                            severity="warning",
                            message=f"Many-to-one relationship might need foreign key field '{fk_field_name}'",
                            location=f"Entity: {entity_name} -> {target_entity}",
                            suggestion=f"Add '{fk_field_name}' field with foreign_key: '{target_entity.lower()}.id'"
                        ))
        
        return issues
    
    def _validate_endpoints(self, config_path: Path, config_data: Dict[str, Any]) -> List[ConfigValidationIssue]:
        """Validate API endpoint configuration"""
        issues = []
        endpoints = config_data.get('endpoints', [])
        
        if not endpoints:
            issues.append(ConfigValidationIssue(
                file_path=config_path,
                severity="info",
                message="No API endpoints defined",
                suggestion="Add endpoints configuration for REST API generation"
            ))
            return issues
        
        # Check for standard CRUD operations
        operations = {ep.get('operation') for ep in endpoints}
        crud_operations = {'create', 'get_by_id', 'list', 'update', 'delete'}
        missing_crud = crud_operations - operations
        
        if missing_crud:
            issues.append(ConfigValidationIssue(
                file_path=config_path,
                severity="info",
                message=f"Missing standard CRUD operations: {', '.join(missing_crud)}",
                suggestion="Consider adding standard CRUD endpoints for complete API"
            ))
        
        # Check endpoint path patterns
        for endpoint in endpoints:
            path = endpoint.get('path', '')
            method = endpoint.get('method', '')
            operation = endpoint.get('operation', '')
            
            # Validate path format
            if not path.startswith('/'):
                issues.append(ConfigValidationIssue(
                    file_path=config_path,
                    severity="warning",
                    message=f"Endpoint path '{path}' should start with '/'",
                    location=f"Endpoint: {method} {path}",
                    suggestion="Use absolute paths starting with '/'"
                ))
            
            # Check method-operation consistency
            method_operation_map = {
                'POST': ['create', 'action'],
                'GET': ['get_by_id', 'list', 'search'],
                'PUT': ['update', 'replace'],
                'PATCH': ['update', 'partial_update'],
                'DELETE': ['delete', 'remove']
            }
            
            expected_ops = method_operation_map.get(method, [])
            if operation and expected_ops and operation not in expected_ops:
                issues.append(ConfigValidationIssue(
                    file_path=config_path,
                    severity="warning",
                    message=f"Operation '{operation}' unusual for {method} method",
                    location=f"Endpoint: {method} {path}",
                    suggestion=f"Consider operations: {', '.join(expected_ops)}"
                ))
        
        return issues
    
    def validate_directory(self, directory: Path, pattern: str = "**/*.yaml") -> List[ConfigValidationIssue]:
        """Validate all configuration files in directory"""
        issues = []
        
        for config_file in directory.rglob(pattern):
            file_issues = self.validate_file(config_file)
            issues.extend(file_issues)
        
        # Also check .yml files
        if pattern.endswith('.yaml'):
            yml_pattern = pattern.replace('.yaml', '.yml')
            for config_file in directory.rglob(yml_pattern):
                file_issues = self.validate_file(config_file)
                issues.extend(file_issues)
        
        return issues
    
    def format_issues(self, issues: List[ConfigValidationIssue]) -> str:
        """Format issues for display"""
        if not issues:
            return "✅ No configuration issues found"
        
        output = []
        issues_by_file = {}
        
        for issue in issues:
            file_path = str(issue.file_path)
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        for file_path, file_issues in issues_by_file.items():
            output.append(f"\n📄 {file_path}")
            
            for issue in file_issues:
                severity_icon = {
                    "error": "❌",
                    "warning": "⚠️",
                    "info": "ℹ️"
                }.get(issue.severity, "❓")
                
                output.append(f"  {severity_icon} {issue.message}")
                if issue.location:
                    output.append(f"    📍 {issue.location}")
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
              default=Path('.'), help='Path to validate')
@click.option('--pattern', default='**/*.yaml', 
              help='File pattern to validate (default: **/*.yaml)')
@click.option('--format', type=click.Choice(['text', 'json']), default='text',
              help='Output format')
@click.option('--fail-on-error', is_flag=True,
              help='Exit with error code if errors found')
def main(path: Path, pattern: str, format: str, fail_on_error: bool):
    """Configuration validator for YAML domain configurations"""
    validator = ConfigValidator()
    
    if path.is_file():
        issues = validator.validate_file(path)
    else:
        issues = validator.validate_directory(path, pattern)
    
    if format == 'json':
        import json
        issues_data = [
            {
                'file': str(issue.file_path),
                'severity': issue.severity,
                'message': issue.message,
                'location': issue.location,
                'suggestion': issue.suggestion
            }
            for issue in issues
        ]
        click.echo(json.dumps(issues_data, indent=2))
    else:
        click.echo(validator.format_issues(issues))
    
    if fail_on_error and any(issue.severity == "error" for issue in issues):
        raise click.ClickException("Configuration validation failed with errors")


if __name__ == '__main__':
    main()