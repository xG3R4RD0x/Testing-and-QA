# Extract Requirements - Agent Implementation Guide

## Overview

Agents use this skill to extract requirements from PDF documents and generate a structured `requirements.json` file. This guide provides step-by-step instructions for implementation.

## Execution Steps

### Step 1: Get Repository Name

Extract the repository name from the current git repository:

```bash
git rev-parse --show-toplevel
# Extract the basename (last path component)
# Example: /Users/admin/dev/hamm-therapy → hamm-therapy
```

### Step 2: Extract PDF Content

Use the `pdf-reader_read_pdf` tool to extract the PDF:

```
pdf-reader_read_pdf({
  sources: [{ path: "/path/to/requirements.pdf" }],
  include_full_text: true,
  include_tables: true
})
```

### Step 3: Semantic Analysis

Analyze the extracted PDF content:

1. **Identify main requirements** - Look for top-level features, goals, or requirements sections
2. **Find sub-tasks** - For each requirement, identify associated tasks or components
3. **Create descriptions** - Write clear, concrete descriptions that explain purpose and scope
4. **Assign IDs** - Use format REQ-001, REQ-002, etc. (zero-padded to 3 digits)
5. **Note dependencies** - Track any relationships between requirements

### Step 4: Handle Non-English Content

**Critical:** If the PDF is NOT in English, you MUST translate all titles and descriptions to English:

1. Identify the source language
2. Translate each requirement title to concise English
3. Translate descriptions to technical English using standard software development terminology
4. Use consistent terminology throughout (e.g., "feature", "module", "component", "integration", "authentication")
5. Preserve technical meaning - ensure translation accurately represents original intent

**Example:**
```
German → English Translation
- Title: "Formulare von Konfiguration in DB verlagern"
  → "Migrate Forms from Configuration to Database"
- Description: "Migrieren Sie Formulare von Konfigurationsdateien..."
  → "Migrate forms from configuration files to database with appropriate data structure..."
```

### Step 5: Create Reports Directory

Ensure the Reports directory exists:

```bash
mkdir -p /Users/admin/dev/Reports/{repository_name}/
```

### Step 6: Structure JSON

Create the JSON object with this exact structure:

```json
{
  "repository_name": "extracted-from-git",
  "extraction_date": "YYYY-MM-DD",
  "total_requirements": number,
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Requirement name (English)",
      "description": "Detailed description of what this requirement covers",
      "sub_tasks": [
        {
          "id": "TASK-001",
          "title": "Sub-task name (English)",
          "description": "Description of what needs to be done"
        }
      ]
    }
  ]
}
```

### Step 7: Save JSON File

Write the structured JSON to the Reports directory:

```
/Users/admin/dev/Reports/{repository_name}/requirements.json
```

### Step 8: Report Results

Inform the user of:
- PDF file analyzed
- Number of requirements extracted
- Number of sub-tasks identified
- Exact file path where JSON was saved
- Repository name

## Validation Checklist

Before saving, verify:

- [ ] PDF file exists and is readable
- [ ] Repository name extracted correctly
- [ ] Reports directory created successfully
- [ ] JSON is valid (no syntax errors)
- [ ] All requirement IDs are unique (REQ-001, REQ-002, etc.)
- [ ] All sub-task IDs are unique within their requirement
- [ ] No empty descriptions
- [ ] All titles and descriptions are in English
- [ ] File saved successfully to correct path
- [ ] User informed of save location

## Common Issues & Solutions

### Issue: "PDF extraction gives garbled text"
**Solution:** 
- Verify PDF is not corrupted: `file /path/to/pdf`
- Try extracting specific pages with pdf-reader
- Some PDFs may have special encoding that needs manual handling

### Issue: "Requirements too deeply nested"
**Solution:**
- Keep 2 levels maximum (requirement → sub-tasks)
- Don't nest sub-tasks within sub-tasks
- If you have 3+ levels, flatten to 2 levels using composite titles

### Issue: "Sub-task IDs not sequential"
**Solution:**
- Use format: TASK-001, TASK-002, etc.
- Zero-pad to 3 digits
- **Continue numbering across all requirements** (don't reset per requirement)
- Example: REQ-001 has TASK-001,002; REQ-002 has TASK-003,004 (not 001,002)

### Issue: "Can't determine repository name"
**Solution:**
- Verify working directory is inside a git repository
- Run `git rev-parse --show-toplevel` to test
- If not a git repo, specify repository name manually

### Issue: "Not sure if content is truly a requirement"
**Solution:**
- Separate main requirements from implementation details
- Requirements should describe WHAT needs to be done
- Subtasks can contain HOW details
- When in doubt, prefer fewer larger requirements over many small ones

## JSON Schema Details

### Main Requirement Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | Yes | Format: REQ-001, REQ-002, etc. |
| `title` | string | Yes | Concise, English, action-oriented (e.g., "Implement User Authentication") |
| `description` | string | Yes | Technical, English, explains purpose and scope |
| `sub_tasks` | array | Yes | Minimum 1 sub-task per requirement (can be empty `[]` for simple requirements) |

### Sub-Task Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `id` | string | Yes | Format: TASK-001, TASK-002, etc. **Continue numbering across all requirements** (TASK-001, TASK-002, TASK-003, etc.) |
| `title` | string | Yes | Concise, English |
| `description` | string | Yes | Technical, explains what needs to be done |

**Important:** Sub-task IDs should continue sequentially across all requirements in the same JSON file. Example:
```
REQ-001
  TASK-001
  TASK-002
REQ-002
  TASK-003  ← Continues from TASK-002
  TASK-004
```

## Tips for Quality Extraction

1. **Be specific** - Avoid vague requirements like "improve system"
2. **Use action verbs** - Titles should start with verbs (Implement, Create, Add, Migrate, etc.)
3. **Include context** - Descriptions should explain the "why" and "what", not just "what"
4. **Keep requirements independent** - Each requirement should be independently valuable
5. **Group related tasks** - Sub-tasks should be directly related to their parent requirement
6. **Consistent naming** - Use consistent terminology across all requirements

## Example: Complete Extraction

**Input PDF:** project-specs.pdf (contains requirements in mixed English/German)

**Extraction Process:**
1. Extract PDF text using pdf-reader → 5,000 words
2. Identify main requirements → Find 3 main sections
3. Identify sub-tasks → Each requirement has 2-3 associated tasks
4. Translate German content → Convert to English technical terminology
5. Create JSON structure → Organize hierarchically
6. Save to `/Users/admin/dev/Reports/project-name/requirements.json`

**Result JSON:**
```json
{
  "repository_name": "project-name",
  "extraction_date": "2026-04-01",
  "total_requirements": 3,
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Implement User Authentication System",
      "description": "Build secure login and session management with OAuth 2.0 support",
      "sub_tasks": [
        {
          "id": "TASK-001",
          "title": "Design database schema for users",
          "description": "Create tables for user accounts, sessions, and credentials"
        },
        {
          "id": "TASK-002",
          "title": "Implement login endpoint",
          "description": "Create POST /auth/login with validation and error handling"
        }
      ]
    }
  ]
}
```

## See Also

- **SKILL.md** - User-facing documentation
- **PROMPTS-REFERENCE.md** - Token-optimized prompts for implementation
