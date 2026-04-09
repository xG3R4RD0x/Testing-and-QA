# Complete Tasks from Codebase - OpenCode Skill

## Overview

This OpenCode skill automatically enriches `requirements.json` files with:
- **Tests**: Gherkin BDD test scenarios for each requirement and subtask
- **Implementation Guidance**: Step-by-step implementation instructions for each subtask

The skill analyzes your codebase to understand:
- Programming language and frameworks
- Project architecture and patterns
- Key modules and dependencies
- Testing approaches

All analysis is done locally within OpenCode chat—no external API calls required.

## Features

✨ **Automatic Language Detection**
- Detects Elixir, Python, JavaScript, TypeScript, Java, Go, Ruby projects
- Identifies frameworks: Phoenix, Django, Express, React, etc.
- Understands test frameworks: ExUnit, pytest, Jest, etc.

✨ **Smart Test Generation**
- Creates realistic Gherkin BDD scenarios
- Happy path (success case)
- Error handling (validation/exceptions)
- Edge cases (boundary conditions)

✨ **Implementation Guidance**
- Step-by-step actionable steps
- Key files with relative paths
- Architectural considerations
- Cross-references between related subtasks

✨ **Safe File Operations**
- Creates timestamped backups before updating
- Preserves original structure
- Handles both `main_requirements` and `requirements` keys
- Supports `sub_tasks` and `subtasks` naming

## Installation

The skill is already installed in OpenCode. To use it:

```
/complete-tasks <path-to-requirements.json>
```

## Usage

### Basic Usage

```bash
/complete-tasks /Users/admin/dev/Reports/hamm-therapy/requirements.json
```

### Expected Input

Your `requirements.json` should have this structure:

```json
{
  "repository_name": "my-project",
  "requirements": [
    {
      "id": "REQ-001",
      "title": "User Authentication",
      "description": "Implement user login and session management",
      "subtasks": [
        {
          "id": "TASK-001-001",
          "title": "Create user model",
          "description": "Define the user data structure"
        }
      ]
    }
  ]
}
```

### Output

The skill enriches your file with:

```json
{
  "id": "REQ-001",
  "title": "User Authentication",
  "test": "Feature: User Authentication\n  Scenario: ...",
  "subtasks": [
    {
      "id": "TASK-001-001",
      "title": "Create user model",
      "description": "...",
      "implementation": "## Overview\n...",
      "test": "Feature: Create user model\n  Scenario: ..."
    }
  ]
}
```

## How It Works

The skill operates in 3 stages:

### Stage 1: Codebase Analysis
- Scans your repository structure
- Detects programming language
- Identifies frameworks and key modules
- Extracts dependencies
- Analyzes architecture patterns
- Creates a compact analysis (~450 tokens max)

### Stage 2: Requirements Enrichment
**For each requirement:**
- Generates 3 Gherkin test scenarios (happy path, error, edge case)

**For each subtask:**
- Generates detailed implementation guidance with:
  - Overview (2-3 sentences)
  - Key files (with relative paths)
  - Implementation steps (5-8 numbered steps)
  - Key considerations (patterns, gotchas)
  - Cross-references to related subtasks
- Generates 3 Gherkin test scenarios

### Stage 3: File Update
- Creates timestamped backup (e.g., `requirements-backup-20260324-132902.json`)
- Updates original file with enriched content
- Prints summary of changes

## Examples

### Example 1: Elixir/Phoenix Project

**Input:**
```json
{
  "id": "REQ-003",
  "title": "Patient Overview Management",
  "subtasks": [
    {
      "id": "TASK-003-001",
      "title": "Filter patients without therapy plan",
      "description": "Implement a filter for patients without therapy plan"
    }
  ]
}
```

**Output Test:**
```gherkin
Feature: Filter patients without therapy plan
  
  Scenario: Successfully filter patients without therapy plan
    Given a database with patients
    When the user applies the "no therapy plan" filter
    Then only patients without therapy plans are displayed
    And the count is accurate
  
  Scenario: Filter fails with invalid filter data
    Given invalid filter parameters
    When the filter is applied
    Then an error message is shown
    And the original list is preserved
  
  Scenario: Edge case with system having no patients
    Given an empty patient database
    When the filter is applied
    Then an empty result set is returned
    And no errors occur
```

**Output Implementation:**
```markdown
## Overview
Filter patients without therapy plan is a core component of Patient Overview Management. 
Implement a filter for patients without therapy plan

## Key Files
- lib/hamm_therapy_web/live/patient_overview_live.ex: Filter logic implementation
- lib/hamm_therapy/accounts/patient_queries.ex: Database query functions

## Implementation Steps
1. Create database query function to find patients without therapy plans
2. Add filter parameter to the LiveView component
3. Implement the filter toggle in the UI
4. Test with various patient data scenarios
5. Add filtering logic to the Phoenix component
6. Update the patient list display to show filtered results
7. Add user feedback for empty filter results

## Key Considerations
- Use Ecto queries for efficient database filtering
- Consider performance with large patient datasets
- Implement proper error handling for database failures
- Use LiveView for real-time filter updates
- Dependencies: Coordinate with other patient filters
```

## Troubleshooting

### Issue: "File not found"
**Solution:** Ensure the path to requirements.json is correct and the file exists.

### Issue: "Invalid requirements.json"
**Solution:** Verify your JSON is valid and contains either `main_requirements` or `requirements` key.

### Issue: "Unknown language" in codebase analysis
**Possible causes:**
- Repository not found (check directory structure)
- Very few source files in the repository
- Using an unsupported language

**Solution:** The skill will still work, but implementation guidance will be generic.

### Issue: Tests/Implementation not generated
**Possible causes:**
- Fields already contain error messages (from previous failed attempts)
- Fields are not empty

**Solution:** Delete existing `test` and `implementation` fields to regenerate them.

## Supported Languages & Frameworks

| Language | Frameworks | Test Framework |
|----------|-----------|----------------|
| Elixir | Phoenix, LiveView, Ecto, Oban | ExUnit |
| Python | Django, Flask | pytest |
| JavaScript | Express, React | Jest |
| TypeScript | Next.js, Express | Jest |
| Java | Spring, Quarkus | JUnit |
| Go | Gin, Echo | testing |
| Ruby | Rails, Sinatra | RSpec |

## File Backups

Before updating your requirements file, the skill creates a timestamped backup:

```
requirements-backup-20260324-132902.json
requirements-backup-20260324-132915.json
```

These are stored in the same directory as your requirements.json file. Keep them for version control or recovery.

## Token Efficiency

The skill is designed to be extremely token-efficient:

- **Stage 1**: ~500 tokens (codebase analysis, reused across all requirements)
- **Stage 2A**: ~175 tokens per requirement (14 requirements = 2,450 tokens)
- **Stage 2B**: ~175 tokens per subtask (44 subtasks = 7,700 tokens)
- **Stage 2C**: ~175 tokens per subtask (44 subtasks = 7,700 tokens)
- **Total**: ~18,350 tokens for a full project with 14 requirements + 44 subtasks

## Advanced Usage

### Working with Existing Tests/Implementation

If some tests or implementations are already present (and not error messages), the skill will:
- Skip generating new ones
- Preserve existing content
- Only fill in missing fields

### Cross-References

The skill automatically adds cross-references between related subtasks:

```markdown
## Key Considerations
- Dependencies: Coordinate with TASK-003-002 for related filtering
- See TASK-003-003 for edge case handling patterns
```

### Customizing Generated Content

For specific project needs, you can:
1. Manually edit generated tests and implementation
2. Re-run the skill on individual subtasks
3. Preserve your edits by clearing error fields only

## Development & Contributing

The skill consists of:
- `complete-tasks.py` - Main execution logic (Stage 1-3)
- `opencode-handler.py` - OpenCode command integration
- `manifest.json` - Skill metadata and configuration

### Key Classes

**CompleteTasksSkill** - Main class handling all enrichment logic
- `stage_1_analyze_codebase()` - Analyze project structure
- `stage_2_enrich_requirements()` - Generate tests and implementation
- `stage_3_update_json_file()` - Write results to file

## Support

For issues or feedback:
- Report issues at: https://github.com/anomalyco/opencode
- Check OpenCode documentation: https://opencode.ai/docs

## License

This skill is part of OpenCode and follows the same licensing terms.

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-24  
**Status:** Production Ready ✅
