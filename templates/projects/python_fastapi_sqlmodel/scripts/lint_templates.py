#!/usr/bin/env python3
"""
Jinja2 Template Linting and Formatting Script

This script provides comprehensive linting and auto-fixing for Jinja2 templates
using djLint (for formatting and auto-fix) and j2lint (for advanced validation).

Usage:
    python scripts/lint_templates.py [options] [path]

Examples:
    # Lint all templates in current directory
    python scripts/lint_templates.py

    # Auto-fix all templates
    python scripts/lint_templates.py --fix

    # Lint specific directory
    python scripts/lint_templates.py app/interface/

    # Lint specific file
    python scripts/lint_templates.py app/__init__.py.j2

    # Verbose output with both tools
    python scripts/lint_templates.py --verbose --both-tools
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_jinja2_templates(path: Path) -> List[Path]:
    """Find all Jinja2 template files in the given path."""
    if path.is_file() and path.suffix == '.j2':
        return [path]
    
    if path.is_dir():
        return list(path.rglob('*.j2'))
    
    return []


def run_djlint(templates: List[Path], fix: bool = False, verbose: bool = False) -> bool:
    """Run djLint on the templates."""
    if not templates:
        logger.info("No Jinja2 templates found for djLint")
        return True
    
    cmd = ["uv", "run", "djlint", "--profile=jinja"]
    
    if fix:
        cmd.append("--reformat")
        logger.info(f"Running djLint auto-fix on {len(templates)} templates...")
    else:
        logger.info(f"Running djLint lint on {len(templates)} templates...")
    
    # djLint doesn't have --verbose flag, just use verbose for logging
    
    # Add template paths
    cmd.extend([str(t) for t in templates])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error(f"djLint failed: {e}")
        return False


def run_j2lint(templates: List[Path], verbose: bool = False) -> bool:
    """Run j2lint on the templates."""
    if not templates:
        logger.info("No Jinja2 templates found for j2lint")
        return True
    
    logger.info(f"Running j2lint validation on {len(templates)} templates...")
    
    success = True
    for template in templates:
        cmd = ["uv", "run", "j2lint", str(template)]
        
        # Add ignore flags for problematic rules
        cmd.extend([
            "-i", "single-statement-per-line", "jinja-statements-indentation", 
            "jinja-statements-delimiter", "single-space-decorator",
            "operator-enclosed-by-spaces"  # S2 - filter spacing (djLint handles this)
        ])
        
        # j2lint doesn't have --verbose flag, just use verbose for logging
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                success = False
                logger.error(f"j2lint failed for {template}")
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
            elif verbose:
                logger.info(f"j2lint passed for {template}")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"j2lint failed for {template}: {e}")
            success = False
    
    return success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Lint and format Jinja2 templates using djLint and j2lint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to template file or directory (default: current directory)"
    )
    
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix templates using djLint formatter"
    )
    
    parser.add_argument(
        "--djlint-only",
        action="store_true",
        help="Run only djLint (skip j2lint validation)"
    )
    
    parser.add_argument(
        "--j2lint-only",
        action="store_true",
        help="Run only j2lint (skip djLint)"
    )
    
    parser.add_argument(
        "--both-tools",
        action="store_true",
        help="Run both djLint and j2lint (default behavior)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Resolve path
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        logger.error(f"Path does not exist: {target_path}")
        sys.exit(1)
    
    # Find templates
    templates = find_jinja2_templates(target_path)
    if not templates:
        logger.warning(f"No Jinja2 templates found in {target_path}")
        sys.exit(0)
    
    logger.info(f"Found {len(templates)} Jinja2 template(s)")
    
    success = True
    
    # Determine which tools to run
    run_djlint_tool = not args.j2lint_only
    run_j2lint_tool = not args.djlint_only
    
    # Run djLint
    if run_djlint_tool:
        djlint_success = run_djlint(templates, fix=args.fix, verbose=args.verbose)
        if not djlint_success:
            success = False
            logger.error("djLint found issues")
    
    # Run j2lint (only if not fixing, as it might find issues after djLint formatting)
    if run_j2lint_tool:
        j2lint_success = run_j2lint(templates, verbose=args.verbose)
        if not j2lint_success:
            success = False
            logger.error("j2lint found issues")
    
    if success:
        logger.info("All templates passed validation!")
        if args.fix:
            logger.info("Templates have been auto-fixed by djLint")
    else:
        logger.error("Some templates have issues that need attention")
        if not args.fix:
            logger.info("Run with --fix to automatically fix formatting issues")
        sys.exit(1)


if __name__ == "__main__":
    main()