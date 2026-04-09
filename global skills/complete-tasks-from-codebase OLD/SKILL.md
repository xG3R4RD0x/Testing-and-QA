---
name: complete-tasks-from-codebase
description: Analyze your codebase and automatically enrich requirements.json with Gherkin test scenarios and step-by-step implementation guidance
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: requirements-management
tags:
  - requirements
  - testing
  - gherkin
  - bdd
  - implementation
  - code-analysis
  - automation
---

# Complete Tasks from Codebase

This skill analyzes your project repository and automatically enriches `requirements.json` files by generating:
- **Gherkin BDD test scenarios** for each requirement and subtask
- **Implementation guidance** with step-by-step instructions for each subtask

## When to Use This Skill

Use this skill when you:
- Have a `requirements.json` file that needs enrichment
- Want to automatically generate test scenarios
- Need step-by-step implementation guidance for your subtasks
- Want your codebase analyzed to provide framework-aware guidance
- Need to create BDD test specs for your requirements

## How to Use This Skill

### Basic Command

```
/complete-tasks <path-to-requirements.json>
```

### Example

```
/complete-tasks /Users/admin/dev/Reports/hamm-therapy/requirements.json
```

## What This Skill Does

### Stage 1: Codebase Analysis
The skill analyzes your repository and automatically detects:
- Programming language (Elixir, Python, JavaScript, TypeScript, Java, Go, Ruby)
- Frameworks (Phoenix, Django, Express, React, Rails, Spring, etc.)
- Key modules and architecture patterns
- Dependencies and versions
- Test frameworks used

### Stage 2: Requirements Enrichment

**For each requirement:**
- Generates 3 Gherkin test scenarios
  - Happy path (success case)
  - Error handling (validation failures)
  - Edge cases (boundary conditions)

**For each subtask:**
- Generates detailed implementation guidance including:
  - Overview (what needs to be built)
  - Key files (relative paths to modify/create)
  - Implementation steps (5-8 numbered actions)
  - Key considerations (patterns, dependencies, gotchas)
  - Cross-references to related subtasks

### Stage 3: Safe File Update
- Creates timestamped backup of original file
- Updates the requirements.json with enriched content
- Preserves original structure and existing data

## Output Format

Your `requirements.json` gets enriched with:

```json
{
  "id": "REQ-001",
  "title": "User Authentication",
  "test": "Feature: User Authentication\n  Scenario: ...",
  "subtasks": [
    {
      "id": "TASK-001-001",
      "title": "Create user model",
      "implementation": "## Overview\n...",
      "test": "Feature: Create user model\n  Scenario: ..."
    }
  ]
}
```

## Supported Technologies

### Languages
- Elixir
- Python
- JavaScript
- TypeScript
- Java
- Go
- Ruby

### Frameworks
- Phoenix (Elixir)
- Django, Flask (Python)
- Express, Fastify (Node.js)
- React, Next.js (JavaScript/TypeScript)
- Rails (Ruby)
- Spring, Quarkus (Java)
- Gin, Echo (Go)

### Test Frameworks
- ExUnit (Elixir)
- pytest (Python)
- Jest (JavaScript/TypeScript)
- RSpec (Ruby)
- JUnit (Java)
- testing (Go)

## Features

✨ **Fully Automated** - No configuration needed, just point to your requirements.json

✨ **Smart Codebase Analysis** - Automatically detects your tech stack

✨ **Production-Quality Tests** - Generates realistic, complete Gherkin scenarios

✨ **Framework-Aware Guidance** - Implementation hints tailored to your framework

✨ **Safe Operations** - Creates timestamped backups before modifying files

✨ **Flexible Input** - Supports different JSON key naming conventions

✨ **Token Efficient** - Designed for LLM integration with minimal token usage

## Requirements

Your `requirements.json` file should have this structure:

```json
{
  "repository_name": "my-project",
  "requirements": [
    {
      "id": "REQ-001",
      "title": "Feature Title",
      "description": "Feature description",
      "subtasks": [
        {
          "id": "TASK-001-001",
          "title": "Subtask Title",
          "description": "Subtask description"
        }
      ]
    }
  ]
}
```

Alternative key names are also supported:
- `main_requirements` instead of `requirements`
- `sub_tasks` instead of `subtasks`

## Examples

### Elixir/Phoenix Project

Input:
```json
{
  "id": "REQ-003",
  "title": "Patient Overview",
  "subtasks": [
    {
      "id": "TASK-003-001",
      "title": "Filter patients without therapy plan",
      "description": "Implement a filter..."
    }
  ]
}
```

Output (Gherkin test):
```gherkin
Feature: Filter patients without therapy plan
  
  Scenario: Successfully filter patients without therapy plan
    Given a database with patients
    When the user applies the "no therapy plan" filter
    Then only patients without therapy plans are displayed
    And the count is accurate
```

Output (Implementation):
```markdown
## Overview
Filter patients without therapy plan implementation...

## Key Files
- lib/hamm_therapy_web/live/patient_overview_live.ex
- lib/hamm_therapy/accounts/patient_queries.ex

## Implementation Steps
1. Create database query function...
2. Add filter parameter to LiveView...
3. Implement filter toggle in UI...
[... more steps ...]
```

## Performance

- **Speed**: 3-5 seconds for typical project (14+ requirements)
- **Token Usage**: ~18,350 tokens for 14 requirements + 44 subtasks
- **Backup**: Automatic timestamped backup before modifications

## Troubleshooting

### Skill not recognized in autocomplete

1. Verify this directory exists:
   ```
   /Users/admin/.agents/skills/complete-tasks-from-codebase/
   ```

2. Check that SKILL.md has the correct frontmatter:
   ```yaml
   ---
   name: complete-tasks-from-codebase
   description: ...
   ---
   ```

3. Reload OpenCode or restart your session

### File not found error

Ensure you provide the **absolute path** to your requirements.json:
```
/complete-tasks /Users/admin/dev/Reports/my-project/requirements.json
```

### Invalid JSON error

Verify your requirements.json has:
- Valid JSON syntax
- Either `main_requirements` or `requirements` key
- List of requirement objects with id, title, description

### Tests/Implementation not generated

The skill will skip generation if:
- Fields already contain valid Gherkin/Markdown
- Fields are not empty

Delete the field content to regenerate.

## Advanced Features

### Cross-References

The skill automatically adds references between related subtasks:

```markdown
## Key Considerations
- Dependencies: Coordinate with TASK-003-002
- See TASK-003-003 for similar patterns
```

### Existing Content Preservation

If some tests or implementations are already present (and valid), the skill will:
- Skip generating new ones for those fields
- Fill in only missing fields
- Preserve your manual edits

### Flexible Input/Output

The skill supports multiple JSON structures:
- Both `main_requirements` and `requirements` keys
- Both `sub_tasks` and `subtasks` naming
- Preserves all other fields and metadata

## Next Steps

After running the skill:

1. **Review Generated Content** - Check the test scenarios and implementation guidance
2. **Customize If Needed** - Adjust wording or add specific details
3. **Share with Team** - Use enriched requirements for planning and development
4. **Generate Code** - Use implementation guidance to start coding
5. **Write Tests** - Use Gherkin scenarios as test specifications

## Support

For issues or questions:
- Check the README.md for detailed documentation
- Review PROMPTS-REFERENCE.md for technical details
- See OPENCODE-INTEGRATION.md for integration specifics

---

**Version:** 1.0.0  
**Status:** Production Ready ✅  
**Last Updated:** 2026-03-24
