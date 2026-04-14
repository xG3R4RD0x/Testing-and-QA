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


def create_dispatch_callback():
    """Create a dispatch callback that generates implementation and test scenarios"""
    
    def dispatch_requirement(payload: dict) -> dict:
        """
        Dispatch callback that generates implementation and test scenarios
        based on the requirement and codebase patterns
        """
        try:
            req_id = payload.get("requirement", {}).get("id")
            subtasks = payload.get("subtasks", [])
            codebase = payload.get("codebase_analysis", {})
            framework = codebase.get("detected_stack", {}).get("framework", "")
            language = codebase.get("detected_stack", {}).get("language", "")
            
            # Generate implementation and test scenarios for each subtask
            enriched_subtasks = []
            for subtask in subtasks:
                task_id = subtask.get("id")
                title = subtask.get("title", "")
                description = subtask.get("description", "")
                
                # Generate implementation steps based on framework and task
                implementation = _generate_implementation(
                    task_id, title, description, framework, language, payload
                )
                
                # Generate BDD test scenarios
                test = _generate_test_scenarios(
                    task_id, title, description, framework, language
                )
                
                enriched_subtasks.append({
                    "id": task_id,
                    "implementation": implementation,
                    "test": test,
                })
            
            return {
                "success": True,
                "requirement_id": req_id,
                "subtasks": enriched_subtasks,
            }
        
        except Exception as e:
            logger.error(f"Dispatch callback error: {e}")
            return {
                "success": False,
                "requirement_id": payload.get("requirement", {}).get("id"),
                "error": str(e),
            }
    
    return dispatch_requirement


def _generate_implementation(task_id, title, description, framework, language, payload):
    """Generate implementation steps for a task"""
    implementation_parts = [
        f"## Overview",
        f"{description}\n",
        f"## Implementation Steps",
    ]
    
    # Add framework-specific steps
    if "Phoenix" in framework:
        implementation_parts.extend(_get_phoenix_steps(task_id, title, description))
    elif "Django" in framework:
        implementation_parts.extend(_get_django_steps(task_id, title, description))
    elif "Rails" in framework:
        implementation_parts.extend(_get_rails_steps(task_id, title, description))
    else:
        # Generic steps
        implementation_parts.extend([
            "1. Analyze requirements and create necessary schema/models",
            "2. Implement core business logic",
            "3. Add input validation and error handling",
            "4. Create API endpoints/handlers",
            "5. Add logging and monitoring",
            "6. Test edge cases and error scenarios",
        ])
    
    return "\n".join(implementation_parts)


def _generate_test_scenarios(task_id, title, description, framework, language):
    """Generate BDD test scenarios for a task"""
    test_parts = [
        f"Feature: {title}",
        f"  Background:",
        f"    Given the system is initialized",
        f"",
        f"  Scenario: Basic functionality works",
        f"    When the user performs the action",
        f"    Then the system should respond correctly",
        f"",
        f"  Scenario: Handle invalid inputs",
        f"    When the user provides invalid input",
        f"    Then the system should reject it gracefully",
        f"",
        f"  Scenario: Verify success state",
        f"    When the action completes successfully",
        f"    Then all data should be persisted correctly",
    ]
    
    return "\n".join(test_parts)


def _get_phoenix_steps(task_id, title, description):
    """Get Phoenix/Elixir-specific implementation steps"""
    return [
        "1. Create database migration if needed:",
        "   - Run `mix ecto.gen.migration` to generate migration file",
        "   - Define schema changes in migration",
        "   - Run `mix ecto.migrate` to apply changes",
        "2. Create/update Ecto schema in `lib/app_name/schemas/`:",
        "   - Define fields with appropriate types",
        "   - Add validations in changeset function",
        "   - Include associations if needed",
        "3. Create/update context module in `lib/app_name/`:",
        "   - Add query functions to fetch data",
        "   - Add mutation functions (create, update, delete)",
        "   - Handle error cases with {:ok, result} or {:error, changeset}",
        "4. Create LiveView or Controller if UI needed:",
        "   - Create live view module in `lib/app_name_web/live/`",
        "   - Use streams for large collections: `stream(socket, :items, items)`",
        "   - Implement `handle_event` for user interactions",
        "5. Add tests in `test/app_name/`:",
        "   - Test context functions with ExUnit",
        "   - Test validations and error cases",
        "6. Update templates if needed:",
        "   - Use `<.input>` component from core_components",
        "   - Add proper form handling with `Phoenix.Component.to_form`",
    ]


def _get_django_steps(task_id, title, description):
    """Get Django-specific implementation steps"""
    return [
        "1. Create database migration if needed:",
        "   - Run `python manage.py makemigrations` to detect model changes",
        "   - Review migration file",
        "   - Run `python manage.py migrate` to apply changes",
        "2. Create/update Django model in `models.py`:",
        "   - Define fields with appropriate types",
        "   - Add validation methods",
        "   - Define string representation with `__str__`",
        "3. Create/update views:",
        "   - Create class-based views inheriting from generic views",
        "   - Implement GET/POST handlers",
        "   - Handle form validation and errors",
        "4. Create/update forms:",
        "   - Create ModelForm subclass",
        "   - Add field validation and cleaning",
        "5. Register in admin if applicable",
        "6. Create URL patterns in `urls.py`",
        "7. Create templates in `templates/` directory",
    ]


def _get_rails_steps(task_id, title, description):
    """Get Rails-specific implementation steps"""
    return [
        "1. Generate migration:",
        "   - Run `rails generate migration MigrationName`",
        "   - Define schema changes",
        "   - Run `rails db:migrate`",
        "2. Create/update Active Record model in `app/models/`",
        "3. Create/update controller in `app/controllers/`",
        "4. Create/update views in `app/views/`",
        "5. Add routes in `config/routes.rb`",
        "6. Create tests in `spec/`",
    ]


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Missing required argument: path to requirements.json",
            "usage": "complete-tasks <path-to-requirements.json>",
        }), file=sys.stderr)
        sys.exit(1)
    
    requirements_file = sys.argv[1]
    
    # Create dispatch callback that generates implementation and test scenarios
    dispatch_callback = create_dispatch_callback()
    
    # Run orchestrator with the dispatch callback
    orchestrator = CompleteTasksOrchestrator()
    result = orchestrator.run(requirements_file, dispatch_callback=dispatch_callback)
    
    # Output result as JSON
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
