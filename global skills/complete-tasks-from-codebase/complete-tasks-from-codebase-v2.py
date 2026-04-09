#!/usr/bin/env python3
"""
OpenCode Skill Entrypoint: Complete Tasks from Codebase v2.0.0

This is the main entry point that OpenCode (or any agent) will call.
It orchestrates the complete workflow:
1. KB detection & caching
2. Codebase analysis
3. Subagent dispatch (with retry)
4. JSON enrichment
5. Cleanup
"""

import sys
import json
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Import components from lib
from lib.complete_tasks_orchestrator import CompleteTasksOrchestrator


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing required argument: path to requirements.json",
            "usage": "complete-tasks <path-to-requirements.json>",
        }), file=sys.stderr)
        sys.exit(1)
    
    requirements_file = sys.argv[1]
    
    # Run orchestrator
    orchestrator = CompleteTasksOrchestrator()
    result = orchestrator.run(requirements_file, dispatch_callback=None)
    
    # Output result as JSON
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
