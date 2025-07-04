#!/usr/bin/env python3
"""
Template Whitespace Control Analysis Tool

This script analyzes Jinja2 templates to identify problematic whitespace control patterns
that cause Python indentation errors in generated code.

Key Issues to Find:
1. {%- ... -%} patterns that strip essential indentation
2. try: blocks followed by conditional content  
3. @abstractmethod decorators with misaligned methods
4. @pytest.mark decorators with indentation issues
"""

import re
from pathlib import Path
from typing import List
from dataclasses import dataclass

@dataclass
class WhitespaceIssue:
    """Represents a whitespace control issue in a template"""
    file_path: str
    line_number: int
    line_content: str
    issue_type: str
    description: str
    suggested_fix: str

class TemplateWhitespaceAnalyzer:
    """Analyzes Jinja2 templates for whitespace control issues"""
    
    def __init__(self, template_dir: str):
        self.template_dir = Path(template_dir)
        self.issues = []
        
        # Problematic patterns to detect
        self.problematic_patterns = [
            # Pattern 1: Conditional blocks with trailing dash that affect indentation
            {
                'name': 'conditional_with_trailing_dash',
                'pattern': r'(\s+){% if.*-%}\s*\n(\s*)(.*)',
                'description': 'Conditional block with -%} that may strip indentation',
                'type': 'indentation_issue'
            },
            # Pattern 2: Try blocks followed by conditional content
            {
                'name': 'try_block_with_conditional',
                'pattern': r'(\s+)try:\s*\n(\s*){% if.*-%}',
                'description': 'Try block followed by conditional with -%} that strips indentation',
                'type': 'try_block_issue'
            },
            # Pattern 3: Method definitions with conditional decorators
            {
                'name': 'method_with_conditional_decorator',
                'pattern': r'(\s*){% if.*-%}\s*\n(\s*)@\w+',
                'description': 'Decorator in conditional block that may lose indentation',
                'type': 'decorator_issue'
            },
            # Pattern 4: Async/def methods in conditional blocks
            {
                'name': 'method_definition_in_conditional',
                'pattern': r'(\s*){% if.*-%}\s*\n(\s*)(async\s+)?def\s+',
                'description': 'Method definition in conditional block losing indentation',
                'type': 'method_definition_issue'
            }
        ]
    
    def analyze_file(self, file_path: Path) -> List[WhitespaceIssue]:
        """Analyze a single template file for whitespace issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Check each pattern
            for pattern_info in self.problematic_patterns:
                pattern = pattern_info['pattern']
                matches = re.finditer(pattern, content, re.MULTILINE)
                
                for match in matches:
                    # Find line number
                    line_num = content[:match.start()].count('\n') + 1
                    line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                    
                    # Create issue
                    issue = WhitespaceIssue(
                        file_path=str(file_path),
                        line_number=line_num,
                        line_content=line_content.strip(),
                        issue_type=pattern_info['type'],
                        description=pattern_info['description'],
                        suggested_fix=self._suggest_fix(pattern_info['name'], match, line_content)
                    )
                    issues.append(issue)
            
            # Additional specific checks
            issues.extend(self._check_specific_patterns(file_path, lines))
                    
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return issues
    
    def _suggest_fix(self, pattern_name: str, match: re.Match, line_content: str) -> str:
        """Suggest a fix for the identified pattern"""
        fixes = {
            'conditional_with_trailing_dash': 'Remove -%} and use %} instead',
            'try_block_with_conditional': 'Remove -%} to preserve indentation after try:',
            'method_with_conditional_decorator': 'Remove -%} to maintain decorator indentation',
            'method_definition_in_conditional': 'Remove -%} to preserve method indentation'
        }
        return fixes.get(pattern_name, 'Review whitespace control usage')
    
    def _check_specific_patterns(self, file_path: Path, lines: List[str]) -> List[WhitespaceIssue]:
        """Check for specific problematic patterns in context"""
        issues = []
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Look for try: followed by conditional blocks
            if 'try:' in line and i + 1 < len(lines):
                next_line = lines[i + 1]
                if '{% if' in next_line and '-%}' in next_line:
                    issues.append(WhitespaceIssue(
                        file_path=str(file_path),
                        line_number=line_num + 1,
                        line_content=next_line.strip(),
                        issue_type='try_conditional_indentation',
                        description='Conditional block after try: using -%} will break indentation',
                        suggested_fix='Remove -%} to preserve proper indentation inside try block'
                    ))
            
            # Look for @abstractmethod patterns
            if '@abstractmethod' in line and i + 1 < len(lines):
                next_line = lines[i + 1]
                if 'async def' in next_line or 'def ' in next_line:
                    # Check if there's inconsistent indentation
                    current_indent = len(line) - len(line.lstrip())
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_indent <= current_indent:
                        issues.append(WhitespaceIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            line_content=line.strip(),
                            issue_type='abstractmethod_indentation',
                            description='@abstractmethod decorator may have indentation issue with following method',
                            suggested_fix='Ensure method definition is properly indented relative to decorator'
                        ))
        
        return issues
    
    def analyze_all_templates(self) -> List[WhitespaceIssue]:
        """Analyze all template files in the directory"""
        all_issues = []
        
        # Find all .j2 files
        template_files = list(self.template_dir.rglob("*.j2"))
        
        print(f"Analyzing {len(template_files)} template files...")
        
        for template_file in template_files:
            print(f"Analyzing: {template_file.relative_to(self.template_dir)}")
            file_issues = self.analyze_file(template_file)
            all_issues.extend(file_issues)
        
        return all_issues
    
    def generate_report(self, issues: List[WhitespaceIssue]) -> str:
        """Generate a detailed analysis report"""
        report = []
        report.append("=" * 80)
        report.append("TEMPLATE WHITESPACE CONTROL ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"Total Issues Found: {len(issues)}")
        report.append("")
        
        # Group by issue type
        by_type = {}
        for issue in issues:
            if issue.issue_type not in by_type:
                by_type[issue.issue_type] = []
            by_type[issue.issue_type].append(issue)
        
        # Report by type
        for issue_type, type_issues in by_type.items():
            report.append(f"Issue Type: {issue_type.upper()}")
            report.append(f"Count: {len(type_issues)}")
            report.append("-" * 40)
            
            for issue in type_issues:
                report.append(f"  File: {Path(issue.file_path).name}")
                report.append(f"  Line {issue.line_number}: {issue.line_content}")
                report.append(f"  Issue: {issue.description}")
                report.append(f"  Fix: {issue.suggested_fix}")
                report.append("")
        
        # Summary of files with issues
        files_with_issues = set(issue.file_path for issue in issues)
        report.append("FILES WITH ISSUES:")
        report.append("-" * 20)
        for file_path in sorted(files_with_issues):
            file_issues = [i for i in issues if i.file_path == file_path]
            report.append(f"  {Path(file_path).name}: {len(file_issues)} issues")
        
        return "\n".join(report)

def main():
    """Main function to run the analysis"""
    # Get the template directory
    script_dir = Path(__file__).parent
    template_dir = script_dir
    
    print("Jinja2 Template Whitespace Control Analysis")
    print("=" * 50)
    print(f"Analyzing templates in: {template_dir}")
    print()
    
    # Create analyzer and run analysis
    analyzer = TemplateWhitespaceAnalyzer(template_dir)
    issues = analyzer.analyze_all_templates()
    
    # Generate and save report
    report = analyzer.generate_report(issues)
    
    # Save report to file
    report_file = script_dir / "whitespace_analysis_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Print summary
    print("\nAnalysis Complete!")
    print(f"Found {len(issues)} whitespace control issues")
    print(f"Report saved to: {report_file}")
    print("\nTop Issues Found:")
    
    # Show sample issues
    by_type = {}
    for issue in issues:
        if issue.issue_type not in by_type:
            by_type[issue.issue_type] = []
        by_type[issue.issue_type].append(issue)
    
    for issue_type, type_issues in list(by_type.items())[:3]:
        print(f"  {issue_type}: {len(type_issues)} occurrences")
    
    return len(issues) > 0

if __name__ == "__main__":
    main()