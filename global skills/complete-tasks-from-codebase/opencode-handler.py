#!/usr/bin/env python3
"""
OpenCode Skill: Complete Tasks from Codebase

This skill enriches requirements.json files with:
- test: Gherkin test scenarios for requirements and subtasks
- implementation: Step-by-step implementation guidance for subtasks

USAGE:
  /complete-tasks <path-to-requirements.json>
  
EXAMPLE:
  /complete-tasks /Users/admin/dev/Reports/hamm-therapy/requirements.json

This skill is designed to work directly within OpenCode's chat interface.
It uses the built-in LLM to analyze your codebase and generate tests + implementation guidance.
"""

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any


class OpenCodeSkillHandler:
    """
    Handler for the OpenCode skill command.
    Integrates with OpenCode's chat system to enrich requirements.
    """
    
    def __init__(self):
        self.skill_dir = Path(__file__).parent
        self.executor_script = self.skill_dir / 'complete-tasks.py'
    
    def parse_command(self, args: list) -> Dict[str, Any]:
        """Parse the /complete-tasks command arguments."""
        if not args:
            return {
                'success': False,
                'error': 'Missing requirements path',
                'usage': '/complete-tasks <path-to-requirements.json>'
            }
        
        requirements_path = args[0]
        
        return {
            'success': True,
            'requirements_path': requirements_path
        }
    
    def validate_path(self, path: str) -> tuple[bool, Optional[str]]:
        """Validate that the requirements file exists and is readable."""
        p = Path(path)
        
        if not p.exists():
            return False, f"File not found: {path}"
        
        if not p.is_file():
            return False, f"Not a file: {path}"
        
        if not p.suffix == '.json':
            return False, f"Not a JSON file: {path}"
        
        # Try to parse it
        try:
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'main_requirements' not in data:
                return False, "Invalid requirements.json: missing 'main_requirements' key"
            
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
        except Exception as e:
            return False, f"Error reading file: {str(e)}"
        
        return True, None
    
    def execute(self, requirements_path: str) -> Dict[str, Any]:
        """Execute the complete-tasks skill."""
        # Validate the path
        is_valid, error = self.validate_path(requirements_path)
        if not is_valid:
            return {
                'success': False,
                'error': error
            }
        
        # Run the executor script
        try:
            result = subprocess.run(
                ['python3', str(self.executor_script), requirements_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f"Execution failed: {result.stderr}"
                }
            
            # Parse the JSON output from the script
            output = json.loads(result.stdout)
            return output
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Skill execution timed out (>5 minutes)'
            }
        except json.JSONDecodeError:
            return {
                'success': False,
                'error': f"Invalid output format: {result.stdout}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Execution error: {str(e)}"
            }


def handle_command(args: list) -> None:
    """
    Main entry point for the OpenCode skill command.
    
    Called by OpenCode when user runs: /complete-tasks <path>
    """
    handler = OpenCodeSkillHandler()
    
    # Parse arguments
    parsed = handler.parse_command(args)
    if not parsed['success']:
        print(f"Error: {parsed['error']}")
        if 'usage' in parsed:
            print(f"Usage: {parsed['usage']}")
        return
    
    requirements_path = parsed['requirements_path']
    
    # Execute the skill
    print(f"\n🚀 Starting Complete Tasks from Codebase skill...")
    print(f"📄 Processing: {requirements_path}\n")
    
    result = handler.execute(requirements_path)
    
    if result['success']:
        print(f"✅ SKILL EXECUTION COMPLETE!\n")
        print(f"📊 Summary:")
        print(f"  - Requirements enriched: {result['requirements_enriched']}")
        print(f"  - Total subtasks processed: {result['total_subtasks']}")
        print(f"  - File updated: {result['requirements_path']}\n")
        print(f"🔍 Codebase Analysis:")
        analysis = result['codebase_analysis']
        print(f"  - Language: {analysis['language']}")
        print(f"  - Frameworks: {', '.join(analysis['frameworks'])}")
        print(f"  - Test framework: {analysis['test_framework']}\n")
        print(f"✨ All requirements have been enriched with:")
        print(f"  ✓ Gherkin test scenarios (test field)")
        print(f"  ✓ Implementation guidance (implementation field)")
    else:
        print(f"❌ ERROR: {result['error']}")


if __name__ == "__main__":
    # When called as a script from the command line
    if len(sys.argv) > 1:
        handle_command(sys.argv[1:])
    else:
        print("Usage: python opencode-handler.py <path-to-requirements.json>")
