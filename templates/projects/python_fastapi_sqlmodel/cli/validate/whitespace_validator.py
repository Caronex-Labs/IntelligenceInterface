#!/usr/bin/env python3
"""
Template Whitespace Control Validation Tool

This script validates Jinja2 templates by rendering them with sample data
and checking if the generated Python code compiles correctly.

Used to verify fixes for whitespace control issues.
"""

import ast
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
import json

class TemplateValidator:
    """Validates template rendering and Python syntax"""
    
    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=False,
            lstrip_blocks=False
        )
        
        # Sample configuration data for rendering templates
        self.sample_data = {
            'domain': 'user',
            'entity_name': 'User',
            'domain_name_plural': 'users',
            'app_name': 'test_app',
            'package_name': 'test_app',
            'description': 'Test application',
            'author': 'Test Author',
            'email': 'test@example.com',
            'database_name': 'test_db',
            'repository': {
                'crud_operations': {
                    'create': {'enabled': True, 'validation': True, 'return_created': True, 'auto_refresh': True},
                    'read': {'enabled': True},
                    'update': {'enabled': True},
                    'delete': {'enabled': True, 'soft_delete': True}
                },
                'query_methods': True,
                'caching': {'enabled': True, 'backend': 'redis'},
                'performance': {'query_logging': True},
                'database': {
                    'provider': 'postgresql',
                    'dialect': 'asyncpg',
                    'connection_pool': {'min_size': 5, 'max_size': 20}
                },
                'async_operations': {'session_management': 'dependency_injection'}
            },
            'usecase': {
                'business_rules': {'enabled': True},
                'events': {'enabled': True},
                'caching': {'enabled': True}
            },
            'api': {
                'router': {'enabled': True},
                'dependencies': {'enabled': True}
            }
        }
    
    def render_template(self, template_path: str) -> Tuple[bool, str, Optional[str]]:
        """
        Render a template with sample data
        
        Returns:
            (success, content, error_message)
        """
        try:
            template = self.env.get_template(template_path)
            content = template.render(**self.sample_data)
            return True, content, None
        except TemplateSyntaxError as e:
            return False, "", f"Template syntax error: {e}"
        except Exception as e:
            return False, "", f"Rendering error: {e}"
    
    def validate_python_syntax(self, content: str, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Python syntax of generated content
        
        Returns:
            (is_valid, error_message)
        """
        try:
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            error_msg = f"Python syntax error in {file_path} at line {e.lineno}: {e.msg}"
            if e.text:
                error_msg += f"\n  Code: {e.text.strip()}"
            return False, error_msg
        except Exception as e:
            return False, f"Unexpected error parsing {file_path}: {e}"
    
    def validate_template_file(self, template_path: str) -> Dict[str, any]:
        """
        Validate a single template file
        
        Returns validation result dictionary
        """
        result = {
            'template_path': template_path,
            'render_success': False,
            'syntax_valid': False,
            'render_error': None,
            'syntax_error': None,
            'content_length': 0
        }
        
        # Try to render the template
        render_success, content, render_error = self.render_template(template_path)
        result['render_success'] = render_success
        result['render_error'] = render_error
        
        if not render_success:
            return result
        
        result['content_length'] = len(content)
        
        # Check if it's a Python file and validate syntax
        if template_path.endswith('.py.j2'):
            syntax_valid, syntax_error = self.validate_python_syntax(content, template_path)
            result['syntax_valid'] = syntax_valid
            result['syntax_error'] = syntax_error
        else:
            # Non-Python files are considered syntactically valid if they render
            result['syntax_valid'] = True
        
        return result
    
    def validate_all_templates(self) -> List[Dict[str, any]]:
        """Validate all template files"""
        results = []
        
        # Find all template files
        template_files = list(self.template_dir.rglob("*.j2"))
        
        print(f"Validating {len(template_files)} template files...")
        
        for template_file in template_files:
            # Get relative path for template loading
            rel_path = template_file.relative_to(self.template_dir)
            
            print(f"Validating: {rel_path}")
            result = self.validate_template_file(str(rel_path))
            results.append(result)
        
        return results
    
    def generate_test_project(self, output_dir: str) -> Tuple[bool, str]:
        """
        Generate a complete test project to validate all templates together
        
        Returns:
            (success, error_message)
        """
        try:
            output_path = Path(output_dir)
            if output_path.exists():
                shutil.rmtree(output_path)
            output_path.mkdir(parents=True)
            
            # Render all templates to output directory
            template_files = list(self.template_dir.rglob("*.j2"))
            
            for template_file in template_files:
                rel_path = template_file.relative_to(self.template_dir)
                
                # Skip test directories for now
                if 'test-init-project' in str(rel_path) or 'manual-test' in str(rel_path):
                    continue
                
                # Render template
                success, content, error = self.render_template(str(rel_path))
                if not success:
                    return False, f"Failed to render {rel_path}: {error}"
                
                # Create output file (remove .j2 extension)
                output_file_path = output_path / str(rel_path).replace('.j2', '')
                output_file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write rendered content
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return True, ""
            
        except Exception as e:
            return False, f"Error generating test project: {e}"
    
    def validate_generated_project(self, project_dir: str) -> Dict[str, any]:
        """
        Validate all Python files in a generated project
        
        Returns validation summary
        """
        project_path = Path(project_dir)
        python_files = list(project_path.rglob("*.py"))
        
        results = {
            'total_files': len(python_files),
            'valid_files': 0,
            'invalid_files': 0,
            'errors': []
        }
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                is_valid, error = self.validate_python_syntax(content, str(py_file))
                
                if is_valid:
                    results['valid_files'] += 1
                else:
                    results['invalid_files'] += 1
                    results['errors'].append({
                        'file': str(py_file.relative_to(project_path)),
                        'error': error
                    })
                    
            except Exception as e:
                results['invalid_files'] += 1
                results['errors'].append({
                    'file': str(py_file.relative_to(project_path)),
                    'error': f"Could not read file: {e}"
                })
        
        return results
    
    def run_comprehensive_validation(self) -> Dict[str, any]:
        """
        Run comprehensive validation of templates and generated project
        
        Returns complete validation report
        """
        print("Starting comprehensive template validation...")
        
        # Step 1: Validate individual templates
        print("\n1. Validating individual templates...")
        template_results = self.validate_all_templates()
        
        # Step 2: Generate test project
        print("\n2. Generating test project...")
        test_project_dir = "/tmp/template_validation_test"
        project_success, project_error = self.generate_test_project(test_project_dir)
        
        # Step 3: Validate generated project
        project_results = None
        if project_success:
            print("\n3. Validating generated project...")
            project_results = self.validate_generated_project(test_project_dir)
        
        # Compile results
        report = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'template_validation': {
                'total_templates': len(template_results),
                'render_failures': len([r for r in template_results if not r['render_success']]),
                'syntax_failures': len([r for r in template_results if not r['syntax_valid']]),
                'details': template_results
            },
            'project_generation': {
                'success': project_success,
                'error': project_error,
                'output_dir': test_project_dir if project_success else None
            },
            'project_validation': project_results
        }
        
        return report
    
    def print_summary(self, report: Dict[str, any]):
        """Print a summary of validation results"""
        print("\n" + "="*80)
        print("TEMPLATE VALIDATION SUMMARY")
        print("="*80)
        
        # Template validation summary
        tv = report['template_validation']
        print(f"Templates Analyzed: {tv['total_templates']}")
        print(f"Render Failures: {tv['render_failures']}")
        print(f"Python Syntax Failures: {tv['syntax_failures']}")
        
        if tv['render_failures'] > 0 or tv['syntax_failures'] > 0:
            print("\nFAILED TEMPLATES:")
            for result in tv['details']:
                if not result['render_success'] or not result['syntax_valid']:
                    print(f"  ❌ {result['template_path']}")
                    if result['render_error']:
                        print(f"     Render: {result['render_error']}")
                    if result['syntax_error']:
                        print(f"     Syntax: {result['syntax_error']}")
        
        # Project generation summary
        pg = report['project_generation']
        print(f"\nProject Generation: {'✅ SUCCESS' if pg['success'] else '❌ FAILED'}")
        if not pg['success']:
            print(f"  Error: {pg['error']}")
        
        # Project validation summary
        if report['project_validation']:
            pv = report['project_validation']
            total = pv['total_files']
            valid = pv['valid_files']
            invalid = pv['invalid_files']
            
            print("\nGenerated Project Validation:")
            print(f"  Total Python Files: {total}")
            print(f"  Valid Files: {valid}")
            print(f"  Invalid Files: {invalid}")
            print(f"  Success Rate: {(valid/total*100):.1f}%" if total > 0 else "  Success Rate: N/A")
            
            if invalid > 0:
                print("\nFIRST 5 SYNTAX ERRORS:")
                for error in pv['errors'][:5]:
                    print(f"  ❌ {error['file']}")
                    print(f"     {error['error']}")

def main():
    """Main function"""
    script_dir = Path(__file__).parent
    
    validator = TemplateValidator(str(script_dir))
    report = validator.run_comprehensive_validation()
    
    # Save detailed report
    report_file = script_dir / "validation_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    validator.print_summary(report)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Return exit code based on results
    has_failures = (
        report['template_validation']['render_failures'] > 0 or
        report['template_validation']['syntax_failures'] > 0 or
        not report['project_generation']['success'] or
        (report['project_validation'] and report['project_validation']['invalid_files'] > 0)
    )
    
    return 1 if has_failures else 0

if __name__ == "__main__":
    exit(main())