#!/usr/bin/env python3
"""
Script to update the embedded documentation in docs.py from LLM_USAGE.md.

Run this script whenever LLM_USAGE.md is updated to keep the embedded 
documentation in sync.
"""

import sys
from pathlib import Path


def update_embedded_docs():
    """Update the embedded documentation from LLM_USAGE.md."""
    # Find the LLM_USAGE.md file
    project_root = Path(__file__).parent.parent.parent
    source_file = project_root / "LLM_USAGE.md"
    target_file = Path(__file__).parent / "docs.py"
    
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        return False
    
    if not target_file.exists():
        print(f"❌ Target file not found: {target_file}")
        return False
    
    try:
        # Read the source content
        source_content = source_file.read_text(encoding='utf-8')
        
        # Escape any triple quotes in the content
        escaped_content = source_content.replace('"""', '\\"\\"\\"')
        
        # Read the current docs.py file
        current_content = target_file.read_text(encoding='utf-8')
        
        # Find the start and end of the LLM_USAGE_CONTENT variable
        start_marker = 'LLM_USAGE_CONTENT = """'
        end_marker = '"""'
        
        start_idx = current_content.find(start_marker)
        if start_idx == -1:
            print("❌ Could not find LLM_USAGE_CONTENT variable")
            return False
        
        # Find the end of the content (after the start marker)
        content_start = start_idx + len(start_marker)
        end_idx = current_content.find(end_marker, content_start)
        if end_idx == -1:
            print("❌ Could not find end of LLM_USAGE_CONTENT variable")
            return False
        
        # Replace the content
        new_content = (
            current_content[:content_start] + 
            escaped_content + 
            current_content[end_idx:]
        )
        
        # Write the updated file
        target_file.write_text(new_content, encoding='utf-8')
        
        print("✅ Successfully updated embedded documentation")
        print(f"📄 Source: {source_file}")
        print(f"📄 Target: {target_file}")
        print(f"📊 Content length: {len(source_content)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating documentation: {e}")
        return False


if __name__ == "__main__":
    success = update_embedded_docs()
    sys.exit(0 if success else 1)