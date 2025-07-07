#!/usr/bin/env python3
"""
Test script to verify that auth/user domain generation is fixed.

This script creates a temporary project and tests the authentication
domain generation functionality.
"""

import tempfile
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_auth_domain_generation():
    """Test that auth domain generation works properly."""
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_dir = temp_path / "test_project"
        
        print(f"Testing auth domain generation in: {project_dir}")
        
        try:
            # Import the project initializer
            from cli.generate.project_initializer import ProjectInitializer
            
            # Create initializer
            initializer = ProjectInitializer()
            
            # Initialize project with authentication enabled
            project_config = {
                'auth_type': 'email_password'
            }
            
            print("Initializing project with authentication...")
            results = initializer.initialize_project(
                project_name="test_auth_project",
                target_dir=project_dir,
                project_config=project_config,
                clean_existing=True
            )
            
            # Check results
            success_count = len([r for r in results if r.success])
            error_count = len([r for r in results if not r.success])
            
            print(f"Generation completed: {success_count} successful, {error_count} errors")
            
            # Check if auth domain files were created
            auth_files_to_check = [
                project_dir / 'app' / 'domain' / 'Auth' / 'entities.py',
                project_dir / 'app' / 'domain' / 'User' / 'entities.py',
                project_dir / 'app' / 'repository' / 'Auth' / 'protocols.py',
                project_dir / 'app' / 'repository' / 'User' / 'protocols.py',
            ]
            
            missing_files = []
            for file_path in auth_files_to_check:
                if not file_path.exists():
                    missing_files.append(str(file_path.relative_to(project_dir)))
                else:
                    print(f"✅ Created: {file_path.relative_to(project_dir)}")
            
            if missing_files:
                print(f"❌ Missing auth files: {missing_files}")
                return False
            
            # Check if templates were copied
            template_files_to_check = [
                project_dir / 'app' / 'domain' / '{{domain}}' / 'entities.py.j2',
                project_dir / 'app' / 'repository' / '{{domain}}' / 'protocols.py.j2',
            ]
            
            missing_templates = []
            for template_path in template_files_to_check:
                if not template_path.exists():
                    missing_templates.append(str(template_path.relative_to(project_dir)))
                else:
                    print(f"✅ Copied template: {template_path.relative_to(project_dir)}")
            
            if missing_templates:
                print(f"⚠️ Missing templates: {missing_templates}")
            
            print("✅ Auth domain generation test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_auth_domain_generation()
    exit(0 if success else 1)