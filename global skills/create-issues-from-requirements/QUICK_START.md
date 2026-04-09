# Create Issues from Requirements - Quick Start Guide

## What This Skill Does

Automatically creates GitHub issues from a structured `requirements.json` file with:
- ✅ Separate issues for each requirement and sub-task
- ✅ Requirement issues with checklists linking to sub-tasks
- ✅ Sub-task issues with implementation steps and test cases
- ✅ Automatic deduplication (no duplicate issues)
- ✅ Project board integration (optional)
- ✅ Retry logic for transient failures

## Prerequisites

Ensure you have:
- GitHub CLI (`gh`) installed and authenticated
- Access to your target GitHub repository
- A valid `requirements.json` file (see [SKILL.md](SKILL.md) for format)

## Basic Usage

### 1. Test with Dry-Run (Recommended First Step)

```bash
/create-issues-from-requirements myproject --repo myorg/myrepo --dry-run
```

This shows:
- Total requirements and sub-tasks to create
- No issues are created yet

### 2. Create Issues

```bash
/create-issues-from-requirements myproject --repo myorg/myrepo --board "My Board"
```

This:
- Creates all requirement and sub-task issues
- Links them together appropriately
- Adds them to the project board (if specified)
- Shows a summary of created/skipped/failed issues

### 3. Update Mode (If Issues Already Exist)

```bash
/create-issues-from-requirements myproject --repo myorg/myrepo --update
```

This updates existing issues instead of skipping them.

## Requirements.json Location

The skill automatically looks for:
```
/Users/admin/dev/Reports/{project-name}/requirements.json
```

Where `{project-name}` is passed as the first argument.

## Expected Output

### Dry-Run Output
```
=== REQUIREMENTS ISSUE CREATION - DRY RUN ===

Project: myproject
Repository: myorg/myrepo
Project Board: My Board

REQUIREMENTS TO CREATE:
1. [REQ-001] Requirement Title
   - 5 sub-task(s)
2. [REQ-002] Another Requirement
   - 3 sub-task(s)
...

=== SUMMARY ===
Total Requirements: 2
Total Sub-tasks: 8
Would create: 10 issues

Run without --dry-run to create these issues.
```

### Creation Output
```
=== CREATING ISSUES ===

Creating REQ-001: Requirement Title
  ✓ TASK-001-01: Created (issue #123)
  ✓ TASK-001-02: Created (issue #124)
  ...
✓ REQ-001: Created (issue #125)

Creating REQ-002: Another Requirement
  ...

=== SUMMARY ===
✓ Created: 10 issues
⊘ Skipped: 0 issues
✗ Failed: 0 issues
✓ Added to project board: "My Board"
```

## Issue Format

### Requirements Issues
- **Title Format:** `[REQ-{id}] {title}`
- **Contains:**
  - Description
  - Checklist of all sub-tasks with links to their issues

### Sub-Task Issues
- **Title Format:** `[TASK-{id}] {title}`
- **Contains:**
  - Description
  - Implementation Steps
  - Test Cases (Gherkin format)

## Common Scenarios

### Scenario 1: First Time Creating Issues
```bash
/create-issues-from-requirements myproject --repo myorg/myrepo --dry-run
# Review output
/create-issues-from-requirements myproject --repo myorg/myrepo
```

### Scenario 2: Add to Project Board
```bash
/create-issues-from-requirements myproject --repo myorg/myrepo --board "Sprint Planning"
```

### Scenario 3: Update Requirements
```bash
# After updating requirements.json
/create-issues-from-requirements myproject --repo myorg/myrepo --update
```

### Scenario 4: Retry Failed Issues
```bash
# The skill automatically retries once on failure
# Run again if any issues failed
/create-issues-from-requirements myproject --repo myorg/myrepo
```

## Troubleshooting

### "Repository not accessible"
- Check the repository URL format: `owner/repo` or `organization/repo`
- Verify GitHub CLI authentication: `gh auth status`

### "Could not fetch existing issues"
- This is usually non-fatal; the skill will continue creating new issues
- Verify repository access permissions

### "Labels not found"
- The skill gracefully handles missing labels by creating issues without them
- You can manually create labels later and edit issues to add them

### Some Issues Failed
- Check the summary output for which issues failed
- The skill retries once automatically
- Failed issues are listed with error details
- Run the command again to retry

## File Structure

```
requirements.json
{
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Requirement Title",
      "description": "Detailed description",
      "sub_tasks": [
        {
          "id": "TASK-001-01",
          "title": "Sub-task Title",
          "description": "Sub-task description",
          "implementation": "Implementation steps...",
          "test": "Test cases (Gherkin format)..."
        }
      ]
    }
  ]
}
```

## Advanced Options

### Use Full Repository URL
```bash
/create-issues-from-requirements myproject --repo https://github.com/myorg/myrepo
```
The skill will normalize it to `myorg/myrepo` automatically.

### No Project Board
```bash
/create-issues-from-requirements myproject --repo myorg/myrepo
# Omit --board parameter if no board integration needed
```

## Skill Location

The skill is installed at:
```
/Users/admin/.agents/skills/create-issues-from-requirements/
```

Files:
- `SKILL.md` - Full technical documentation
- `create-issues.js` - Main implementation
- `run.sh` - Shell wrapper
- `README.md` - Feature overview
- `IMPLEMENTATION_SUMMARY.md` - Implementation details

## Getting Help

See detailed documentation in:
- `SKILL.md` - Complete technical documentation
- `README.md` - Feature overview
- `IMPLEMENTATION_SUMMARY.md` - Implementation details and design decisions

## For Integration With OpenCode

The skill is automatically available as a slash command:
```bash
/create-issues-from-requirements <project-name> --repo <owner/repo> [options]
```

Use `ctrl+p` in OpenCode to see available commands and skills.
