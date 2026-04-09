# Create Issues from Requirements Skill - Documentation Index

This skill automates creation of GitHub issues from structured `requirements.json` files.

## 📖 Documentation Files (Read in This Order)

### 1. **QUICK_START.md** ⭐ START HERE
   Quick reference guide with common scenarios and troubleshooting.
   - What the skill does
   - Basic usage examples
   - Common troubleshooting
   - Expected output

### 2. **SKILL.md**
   Complete technical specification and documentation.
   - Purpose and when to use
   - Requirements and file structure
   - Command syntax with examples
   - Workflow description
   - Issue format specification
   - Error handling details

### 3. **IMPLEMENTATION_SUMMARY.md**
   Implementation details and design decisions.
   - Summary of features
   - Testing results
   - Design decisions
   - Architecture and class methods
   - Potential enhancements

### 4. **README.md**
   Feature overview and installation guide.
   - Features list
   - Installation instructions
   - Prerequisites
   - Development notes

## 💻 Code Files

### **create-issues.js** (494 lines)
Main Node.js implementation with:
- `RequirementsIssueCreator` class
- Issue creation with retry logic
- Error handling and reporting
- GitHub CLI integration

### **run.sh**
Shell wrapper for OpenCode integration.

## 🚀 Quick Usage

```bash
# Dry-run (preview changes)
/create-issues-from-requirements myproject --repo owner/repo --dry-run

# Create issues
/create-issues-from-requirements myproject --repo owner/repo --board "Board Name"

# Update existing issues
/create-issues-from-requirements myproject --repo owner/repo --update
```

## 📋 Command Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `<project-name>` | Yes | Project name (path to requirements.json) |
| `--repo` | Yes | GitHub repository (owner/repo) |
| `--board` | No | Project board name to add issues to |
| `--dry-run` | No | Preview changes without creating |
| `--update` | No | Update existing issues instead of skipping |

## ✅ Requirements

- GitHub CLI (`gh`) installed and authenticated
- Access to target GitHub repository
- Valid `requirements.json` file in `/Users/admin/dev/Reports/{project-name}/`

## 📂 Directory Structure

```
/Users/admin/.agents/skills/create-issues-from-requirements/
├── INDEX.md (this file)
├── QUICK_START.md ⭐ (start here)
├── SKILL.md (technical docs)
├── IMPLEMENTATION_SUMMARY.md (implementation details)
├── README.md (feature overview)
├── create-issues.js (main code)
└── run.sh (wrapper script)
```

## 🎯 What This Skill Does

1. **Reads** `requirements.json` from project directory
2. **Creates** GitHub issues for each requirement and sub-task
3. **Links** sub-tasks to parent requirements with checklists
4. **Deduplicates** to prevent duplicate issues
5. **Integrates** with GitHub project boards (optional)
6. **Reports** summary of created/skipped/failed issues

## 🔄 Typical Workflow

1. Have a `requirements.json` file ready
2. Run with `--dry-run` to preview changes
3. Review the preview
4. Run without `--dry-run` to create issues
5. Monitor the summary output
6. Use `--update` flag if you need to re-run with updates

## ❌ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Repository not accessible" | Check format: `owner/repo` |
| "GitHub CLI is not authenticated" | Run: `gh auth login` |
| "Labels not found" | Skill creates issues without labels (still works) |
| "requirements.json not found" | Check path: `/Users/admin/dev/Reports/{project}/requirements.json` |

## 💡 Tips

- Always run with `--dry-run` first to preview
- Use meaningful GitHub repository names
- Consider creating labels in your repo before bulk creation
- The skill handles failures gracefully and continues with other issues
- Deduplication means you can safely re-run the command

## 📞 Support

For detailed information:
- Technical questions → Read **SKILL.md**
- Quick reference → Read **QUICK_START.md**
- Implementation details → Read **IMPLEMENTATION_SUMMARY.md**
- Features overview → Read **README.md**

---

**Version:** 1.0  
**Status:** Production Ready  
**Last Updated:** 2026-04-08
