# Create Issues from Requirements Skill

Automated GitHub issue creation from structured `requirements.json` files.

## Quick Start

```bash
/create-issues-from-requirements goetz-kundenportal-phoenix --repo repo-test --board "Hamm-therapy-test" --dry-run
```

## Features

- ✓ Automatically creates GitHub issues from requirements.json
- ✓ Creates separate issues for requirements and sub-tasks
- ✓ Links sub-tasks as sub-issues to parent requirements
- ✓ Includes checklists in requirement issues
- ✓ Deduplication (skips existing issues)
- ✓ Retry logic for transient failures
- ✓ Project board integration
- ✓ Dry-run mode for previewing changes
- ✓ Detailed reporting and error handling

## Installation

The skill is located at:
```
/Users/admin/.agents/skills/create-issues-from-requirements/
```

## Files

- `SKILL.md` - Full documentation
- `create-issues.js` - Main implementation
- `run.sh` - Shell wrapper for OpenCode integration
- `README.md` - This file

## Prerequisites

- GitHub CLI (`gh`) installed and authenticated
- Access to target GitHub repository
- `requirements.json` file in `/Users/admin/dev/Reports/{project-name}/`

## Usage

See `SKILL.md` for complete documentation.

## Development

To test the skill:

1. **Dry-run mode (preview only)**:
   ```bash
   node create-issues.js goetz-kundenportal-phoenix --repo repo-test --board "Hamm-therapy-test" --dry-run
   ```

2. **Create issues**:
   ```bash
   node create-issues.js goetz-kundenportal-phoenix --repo repo-test --board "Hamm-therapy-test"
   ```

## Error Handling

- Sub-task creation failures are retried once before skipping
- All errors are logged and reported in summary
- Partial success is supported (some issues may fail while others succeed)

## Notes

- Effort hours and cost are intentionally excluded from issues
- Requirements and sub-tasks each get their own GitHub issue
- Sub-tasks are created before requirement issues for proper linking
- Project board integration is optional
