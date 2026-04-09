# ✅ Create Issues from Requirements Skill - Complete

## Summary

Successfully created the "Create Issues from Requirements" skill that automates GitHub issue creation from `requirements.json` files.

## Skill Details

**Location:** `/Users/admin/.agents/skills/create-issues-from-requirements/`

**Files Created:**
- `SKILL.md` - Complete skill documentation (211 lines)
- `create-issues.js` - Main implementation (494 lines)
- `run.sh` - Shell wrapper for OpenCode integration
- `README.md` - Quick reference guide

## Features Implemented

✅ **Core Functionality**
- Reads `requirements.json` from `/Users/admin/dev/Reports/{project-name}/`
- Creates GitHub issues for main requirements and sub-tasks
- Automatically links sub-tasks as related issues to parent requirements
- Includes checklists in requirement issues with links to sub-task issues

✅ **Smart Deduplication**
- Checks for existing issues before creation
- Skips duplicates to prevent re-creation
- Supports `--update` flag for updating existing issues

✅ **Error Handling**
- Retry logic: attempts issue creation twice if it fails
- Gracefully handles missing labels by creating issues without them
- Partial success: continues even if some issues fail
- Detailed error reporting in summary

✅ **Project Board Integration**
- Optional project board support via `--board` parameter
- Attempts to add created issues to specified project board

✅ **Dry-Run Mode**
- Preview all changes before creating issues
- Shows summary of requirements and sub-tasks to be created
- Useful for validation before committing to issue creation

✅ **User Input Parameters**
- `<project-name>` - Required; determines path to requirements.json
- `--repo owner/repo` - Required; GitHub repository target
- `--board board-name` - Optional; project board name
- `--dry-run` - Optional; preview without creating
- `--update` - Optional; update existing issues

## Issue Format

### Requirement Issues
- **Title:** `[REQ-{id}] {title}`
- **Labels:** Applied if they exist (otherwise created without labels)
- **Body:**
  - Description of the requirement
  - Checklist section with links to each sub-task issue
  - No effort hours or cost information

**Example:** Issue #135 - REQ-001 "Migrate Forms from Configuration to Database"
- Includes 6 linked sub-tasks with checkboxes
- Clean, structured format for tracking

### Sub-Task Issues
- **Title:** `[TASK-{id}] {title}`
- **Labels:** Applied if they exist
- **Body:**
  - Description of the task
  - Implementation Steps section
  - Test Cases section (Gherkin format)
  - No effort hours or cost information

**Example:** Issue #129 - TASK-001-01 "Create appropriate data structure"
- Complete implementation guidance
- Comprehensive test scenarios

## Testing Results

✅ **Dry-Run Test**
```
Project: goetz-kundenportal-phoenix
Repository: xG3R4RD0x/repo-test
Project Board: Hamm-therapy-test

REQUIREMENTS TO CREATE:
7 main requirements
37 sub-tasks
44 total issues
```

✅ **Live Issue Creation Test**
Successfully created issues in repo-test:
- REQ-001 through REQ-003 (and more)
- All sub-tasks properly linked
- Checklists with working issue references
- Issues #129-148+ created with proper format

## Usage Examples

### 1. Dry-run to preview
```bash
/create-issues-from-requirements goetz-kundenportal-phoenix --repo repo-test --board "Hamm-therapy-test" --dry-run
```

### 2. Create issues in repository
```bash
/create-issues-from-requirements goetz-kundenportal-phoenix --repo xG3R4RD0x/repo-test --board "Hamm-therapy-test"
```

### 3. Create issues without project board
```bash
/create-issues-from-requirements my-project --repo myorg/myrepo
```

### 4. Update existing issues
```bash
/create-issues-from-requirements my-project --repo myorg/myrepo --update
```

## Design Decisions

1. **No Effort/Cost in Issues**: Intentionally excluded per requirements
2. **Graceful Label Handling**: Creates issues without labels if labels don't exist
3. **Retry Strategy**: Retries once on failure with informative feedback
4. **Hierarchical Structure**: Sub-tasks linked to requirements maintaining project hierarchy
5. **Bidirectional References**: Requirement issues have links to sub-tasks, enabling navigation

## Error Handling Example

When labels don't exist in the repository:
```
could not add label: 'subtask' not found
⚠ Created without labels (labels don't exist in repo)
✓ TASK-001-01: Created (issue #122)
```

Issues are still created successfully without labels.

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Access to target GitHub repository
- Valid `requirements.json` file structure
- (Optional) GitHub project board with specified name

## Files Location

```
/Users/admin/.agents/skills/create-issues-from-requirements/
├── SKILL.md              # Full documentation
├── README.md             # Quick reference
├── create-issues.js      # Main implementation
└── run.sh               # Shell wrapper
```

## Key Classes & Methods

**RequirementsIssueCreator**
- `validate()` - Validates prerequisites
- `loadRequirements()` - Parses requirements.json
- `checkExistingIssues()` - Finds duplicate issues
- `createIssueWithRetry()` - Creates issue with retry logic
- `createSubTasks()` - Creates sub-task issues
- `createRequirements()` - Creates requirement issues
- `buildRequirementBody()` - Formats requirement issue body with checklist
- `buildSubTaskBody()` - Formats sub-task issue body
- `addToProjectBoard()` - Adds issue to project board
- `printDryRunSummary()` - Displays preview
- `printSummary()` - Displays creation results

## Next Steps (Optional Enhancements)

- Pre-create required labels in repository
- Support for bulk operations on multiple projects
- Export summary report as JSON/CSV
- Webhook integration for automatic updates
- Support for custom issue templates
- API-based alternative to gh CLI

---

**Status:** ✅ Complete and tested  
**Created:** 2026-04-08  
**Tested Against:** goetz-kundenportal-phoenix requirements.json (7 requirements, 37 sub-tasks)
