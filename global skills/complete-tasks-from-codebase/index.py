#!/usr/bin/env python3
"""
OpenCode Skill Entrypoint: Complete Tasks from Codebase
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point for the OpenCode skill"""
    skill_dir = Path(__file__).parent
    executor = skill_dir / "complete-tasks.py"
    
    # Get arguments
    args = sys.argv[1:]
    
    # Run the executor
    try:
        result = subprocess.run(
            ["python3", str(executor)] + args,
            capture_output=True,
            text=True
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        sys.exit(result.returncode)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
