---
name: extract-requirements
description: Use when extracting requirements from PDF files to create structured JSON with main requirements and sub-tasks
license: MIT
compatibility: opencode
version: 1.1.0
metadata:
  audience: developers
  tags: [pdf-extraction, requirements-engineering, json-generation]
---

# Extract Requirements

Extract structured requirements from PDF documents and generate a `requirements.json` file with main requirements and associated sub-tasks.

## Overview

This skill enables rapid conversion of unstructured PDF requirement documents into a standardized JSON format. It:

1. **Extracts PDF content** using semantic analysis
2. **Identifies main requirements** and associated sub-tasks
3. **Generates structured JSON** organized hierarchically
4. **Saves to Reports** directory with git repository context
5. **Ensures English output** by translating non-English PDFs

## When to Use

- Extracting requirements from specification documents (PDFs)
- Converting unstructured requirement lists into structured JSON
- Creating standardized requirements reports for project tracking
- Need JSON format with 2-level hierarchy (requirement → sub-tasks)
- PDF is readable and contains clear requirement sections

## Quick Reference

**Input:** PDF file path  
**Output:** `/Users/admin/dev/Reports/{repository_name}/requirements.json`  
**Key Step:** All titles and descriptions must be in English (auto-translated if needed)  
**Execution Time:** 2-5 minutes depending on PDF size  

**For step-by-step instructions:** See `IMPLEMENTATION.md` → "## Execution Steps" (8 numbered steps)

## Output Format

```json
{
  "repository_name": "project-name",
  "extraction_date": "2026-03-18",
  "total_requirements": 3,
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Requirement Title",
      "description": "Detailed description of what this requirement covers",
      "sub_tasks": [
        {
          "id": "TASK-001",
          "title": "Sub-task Title",
          "description": "Description of what needs to be done"
        }
      ]
    }
  ]
}
```

## Key Capabilities

- **Semantic analysis** - Extracts context beyond keywords
- **Multi-language support** - Automatically translates non-English PDFs to English
- **Git integration** - Detects repository name automatically
- **Hierarchical structure** - 2-level organization (requirement → sub-tasks)
- **Flexible input** - Works with various PDF formats and layouts

## Implementation

**For agents:** See `IMPLEMENTATION.md` for step-by-step execution guide  
**For prompts:** See `PROMPTS-REFERENCE.md` for token-optimized prompts  
**For examples:** Output examples in both documents

## Requirements & Constraints

- Working directory must be a git repository
- PDF file must be readable and text-extractable
- Write permission to `/Users/admin/dev/Reports/{repository_name}/`
- Minimum 1 requirement recommended (no practical limit)
- All JSON output will be in English regardless of source language
