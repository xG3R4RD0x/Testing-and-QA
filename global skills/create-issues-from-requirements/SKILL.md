---
name: create-issues-from-requirements
description: Use when you have a requirements.json file and need to automatically create GitHub issues from structured requirements with hierarchical sub-tasks, deduplication, and project board integration
---

# Create Issues from Requirements

Create GitHub issues automatically from a `requirements.json` file with proper hierarchical structure, linking, and project board integration.

## Purpose

This skill automates the creation of GitHub issues from a structured requirements file, ensuring:
- Main requirements and subtasks get their own issues
- Subtasks are linked as sub-issues to parent requirements
- Requirement issues include checklists referencing all subtasks
- Deduplication prevents duplicate issues
- Optional project board integration

## When to Use

- You have a `requirements.json` file in `/Users/admin/dev/Reports/{project-name}/`
- You want to create GitHub issues from the requirements structure
- You need to organize requirements and subtasks in GitHub
- You want to integrate issues with a GitHub project board

## Requirements

- GitHub CLI (`gh`) must be installed and authenticated
- Access to the target GitHub repository
- A valid `requirements.json` file with main requirements and sub-tasks

## File Structure

The skill expects a `requirements.json` file with this structure:

```json
{
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Requirement Title",
      "description": "Detailed description",
      "sub_tasks": [
        {
          "id": "TASK-001-01",
          "title": "Task Title",
          "description": "Task description",
          "implementation": "Implementation steps",
          "test": "Test cases"
        }
      ]
    }
  ]
}
```

## Command Syntax

```bash
/create-issues-from-requirements <project-name> [--repo owner/repo] [--board board-name] [--dry-run] [--update]
```

### Parameters

- `<project-name>` (required): Name of the project (must match directory in `/Users/admin/dev/Reports/`)
- `--repo owner/repo` (required): GitHub repository in format `owner/repo`
- `--board board-name` (optional): GitHub project board name to add issues to
- `--dry-run` (optional): Preview changes without creating issues
- `--update` (optional): Update existing issues instead of skipping them

### Examples

```bash
# Create issues with dry-run to preview
/create-issues-from-requirements goetz-kundenportal-phoenix --repo repo-test --board "Hamm-therapy-test" --dry-run

# Create issues in repository
/create-issues-from-requirements goetz-kundenportal-phoenix --repo repo-test --board "Hamm-therapy-test"

# Update existing issues
/create-issues-from-requirements my-project --repo my-org/my-repo --update
```

## Workflow

### 1. Validation
- Checks if `requirements.json` exists in `/Users/admin/dev/Reports/{project-name}/`
- Verifies GitHub repository exists and is accessible
- Validates project board if provided

### 2. Parsing
- Reads and parses the `requirements.json` file
- Validates structure and required fields

### 3. Deduplication
- Searches for existing issues by requirement/task ID
- Decides whether to skip or update based on flags

### 4. Issue Creation
- Creates sub-task issues first (to get issue numbers)
- Creates requirement issues with checklist links
- Links sub-tasks as sub-issues to parent requirements

### 5. Project Board Integration
- Adds created issues to project board (if provided)

### 6. Summary Report
- Displays creation/update summary
- Shows any skipped or failed issues
- Lists all created issue numbers

## Issue Format

### Main Requirement Issues

**Title Format:** `[REQ-{id}] {title}`

**Body:**
```
## Description
{description}

## Subtasks
- [ ] [TASK-{id}](https://github.com/owner/repo/issues/{number}) - {subtask_title}
- [ ] [TASK-{id}](https://github.com/owner/repo/issues/{number}) - {subtask_title}

## Related
Parent requirement for sub-issues
```

**Labels:** `requirement`, `status:pending`

### Sub-Task Issues

**Title Format:** `[TASK-{id}] {title}`

**Body:**
```
## Description
{description}

## Implementation Steps
{implementation}

## Test Cases
{test}

## Parent Requirement
Linked as sub-issue to requirement
```

**Labels:** `subtask`, `status:pending`

## Error Handling

- If creating a sub-task fails, the skill will retry once
- If retry fails, the issue is skipped and logged
- Parent requirement issues can still be created if some sub-tasks fail
- All errors are reported in the final summary

## Output

### Dry-Run Output

```
=== REQUIREMENTS ISSUE CREATION - DRY RUN ===

Project: goetz-kundenportal-phoenix
Repository: repo-test
Project Board: Hamm-therapy-test

REQUIREMENTS TO CREATE:
1. [REQ-001] Migrate Forms from Configuration to Database
   - 6 sub-tasks

2. [REQ-002] Implement Form Versioning System
   - 5 sub-tasks

...

SUMMARY:
- Total Requirements: 7
- Total Sub-tasks: 32
- Would create: 39 issues

Run without --dry-run to create these issues.
```

### Creation Output

```
=== CREATING REQUIREMENTS ISSUES ===

[✓] Created REQ-001: Migrate Forms from Configuration to Database (#123)
    [✓] TASK-001-01: Create appropriate data structure (#124)
    [✓] TASK-001-02: Seed existing forms into database (#125)
    ...

[✓] Created REQ-002: Implement Form Versioning System (#126)
    [✓] TASK-002-01: Create form version schema (#127)
    ...

=== SUMMARY ===
✓ Created: 39 issues
- Skipped: 0 issues
- Failed: 0 issues
✓ Added to project board: "Hamm-therapy-test"
```

## Notes

- Effort hours and cost information are intentionally excluded from issues
- Requirements and sub-tasks are created as separate GitHub issues
- Sub-tasks are linked as sub-issues to maintain hierarchy
- Requirement issues automatically create a checklist of subtasks
- The skill preserves the original requirement and task IDs for tracking
