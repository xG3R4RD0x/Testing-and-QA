# Extract Requirements Skill - Agent Implementation Guide

## Overview

This skill enables agents to extract requirements from PDF files and structure them into a JSON format.

## How the Agent Should Use This Skill

### Step 1: Get the PDF Path
The user provides the path to the PDF file containing requirements.

### Step 2: Use the pdf-reader Tool
Call the `pdf-reader_read_pdf` tool with:
- `sources`: Array with the PDF path
- `include_full_text`: true (to get complete content)
- `include_tables`: true (if tables contain requirements)

Example:
```
pdf-reader_read_pdf({
  sources: [{ path: "/path/to/requirements.pdf" }],
  include_full_text: true,
  include_tables: true
})
```

### Step 3: Semantic Analysis
Once the PDF content is extracted:
1. Read through all the text carefully
2. Identify main requirements (top-level features, goals, or requirements)
3. For each requirement, identify associated sub-tasks
4. Create meaningful descriptions for each item
5. Assign sequential IDs (REQ-001, REQ-002, etc.)

### Step 4: Structure the JSON
Create a JSON object following this structure:
```json
{
  "repository_name": "extracted-from-git",
  "extraction_date": "YYYY-MM-DD",
  "total_requirements": number,
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Requirement name",
      "description": "Detailed description",
      "sub_tasks": [
        {
          "id": "TASK-001",
          "title": "Sub-task name",
          "description": "Sub-task description"
        }
      ]
    }
  ]
}
```

### Step 5: Extract Repository Name
Run a git command to get the repository name:
```bash
git rev-parse --show-toplevel
```
Then extract just the directory name (the last part of the path).

### Step 6: Create Reports Directory
Ensure the directory exists: `/Users/admin/dev/Reports/{repository_name}/`

### Step 7: Save the JSON File
Write the structured JSON to: `/Users/admin/dev/Reports/{repository_name}/requirements.json`

### Step 8: Provide Feedback
Report to the user:
- The PDF file analyzed
- Number of requirements extracted
- Number of sub-tasks
- The path where the JSON file was saved
- The repository name

## Example Workflow

A user might ask:
```
Extract requirements from /Users/admin/dev/goetz-kundenportal-phoenix/requirements.pdf
```

The agent would:
1. Use pdf-reader to extract the PDF content
2. Analyze it semantically to identify 6 main requirements
3. Within those, find 46 sub-tasks
4. Create the JSON structure with proper IDs and descriptions
5. Determine the repository name is `goetz-kundenportal-phoenix`
6. Save to `/Users/admin/dev/Reports/goetz-kundenportal-phoenix/requirements.json`
7. Report back to the user with the count and location

## JSON Structure Details

### Main Requirements
Each requirement should have:
- `id`: Unique identifier (REQ-001, REQ-002, etc.)
- `title`: Clear, concise title of the requirement
- `description`: Detailed explanation of what this requirement covers
- `sub_tasks`: Array of related tasks/components

### Sub-Tasks
Each sub-task should have:
- `id`: Unique identifier within the requirement (TASK-001, TASK-002, etc.)
- `title`: Clear, concise title of the task
- `description`: Detailed explanation of what needs to be done

### Optional Fields
You may also include:
- `estimated_effort`: Story points or time estimate (e.g., "2 PT", "1 day")
- `estimated_cost`: Budget or cost estimate
- `priority`: Priority level (high, medium, low)
- `status`: Current status (planned, in-progress, completed)

## Tips for Better Requirements

1. **Be Specific**: Use concrete, measurable descriptions
2. **Keep it Hierarchical**: Main requirements should contain related sub-tasks
3. **Use Clear Titles**: Titles should be self-explanatory without reading description
4. **Include Context**: Descriptions should explain the "why" not just the "what"
5. **Consistent IDs**: Always use the format REQ-### and TASK-### with zero-padding

## Example JSON Output

```json
{
  "repository_name": "goetz-kundenportal-phoenix",
  "extraction_date": "2026-03-18",
  "total_requirements": 2,
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Formulare von Konfiguration in DB verlagern",
      "description": "Migrate forms from configuration files to database with proper data structure, UUID references, and admin management interface",
      "estimated_effort": "1.0 PT",
      "sub_tasks": [
        {
          "id": "TASK-001",
          "title": "Erstellen einer passenden Datenstruktur",
          "description": "Create appropriate database schema for forms storage"
        },
        {
          "id": "TASK-002",
          "title": "Seeding der bestehenden Formulare",
          "description": "Migrate and seed existing forms into new database structure"
        }
      ]
    },
    {
      "id": "REQ-002",
      "title": "Versionierung von Formularen",
      "description": "Implement form versioning system with draft management and backwards compatibility",
      "estimated_effort": "0.5 PT",
      "sub_tasks": [
        {
          "id": "TASK-003",
          "title": "FormuarVersionID + Version UUID+Int-Version",
          "description": "Implement versioning with FormuarVersionID (UUID) and numeric version numbers"
        }
      ]
    }
  ]
}
```
