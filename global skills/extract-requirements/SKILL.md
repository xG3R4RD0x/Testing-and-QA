---
name: extract-requirements
description: Extract and structure requirements from PDF files into JSON format with main requirements and sub-tasks
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: requirements-management
---

# Extract Requirements Skill

## What I do

I help you extract and structure requirements from PDF documents. My workflow:

1. **Analyze PDF** - Read and semantically analyze the PDF file using the pdf-reader tool to understand requirements and their associated tasks
2. **Structure Data** - Parse the content and organize it into main requirements with associated sub-tasks
3. **Generate JSON** - Create a structured JSON file with clear hierarchy and metadata
4. **Save Report** - Store the `requirements.json` in `/Users/admin/dev/Reports/{repository_name}/`

## When to use me

Use this skill when you need to:
- Extract requirements from project specification PDFs
- Convert unstructured requirement documents into structured JSON
- Create a standardized requirements list for your project
- Generate reports that map requirements to sub-tasks

## How to use me

Call me with a PDF file path:

```
Load the extract-requirements skill and analyze this PDF: /path/to/requirements.pdf
```

The skill will:
1. Extract the repository name from your current git repository
2. Read and analyze the PDF file
3. Identify main requirements and associated sub-tasks
4. Generate a `requirements.json` file in the appropriate Reports directory
5. Output the results and save location

## Output Format

The generated `requirements.json` follows this structure:

```json
{
  "repository_name": "project-name",
  "extraction_date": "2026-03-18",
  "total_requirements": 5,
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Requirement Title",
      "description": "Detailed description of the requirement",
      "sub_tasks": [
        {
          "id": "TASK-001",
          "title": "Sub-task Title",
          "description": "Description of the sub-task"
        }
      ]
    }
  ]
}
```

## Key Features

- **Semantic Analysis** - Understands requirement context, not just keywords
- **Flexible Structure** - Works with unstructured PDF documents
- **Automatic Organization** - Hierarchically organizes requirements and tasks
- **Git Integration** - Automatically determines repository name from git
- **Structured Output** - Clean JSON format for downstream tools

## Requirements

- Repository must be a git repository
- PDF file must be readable and contain structured content
- Write access to `/Users/admin/dev/Reports/{repository_name}/`
