# Extract Requirements - Prompts Reference

Token-optimized prompts for implementing the extract-requirements skill. Use these exact prompts when instructing agents to extract requirements.

## Stage 1: PDF Extraction

**Use this prompt when user asks to extract requirements from a PDF:**

```
TASK: Extract requirements from PDF

You are extracting structured requirements from a PDF document for /Users/admin/dev/Reports storage.

INPUT:
- User provides: PDF file path (absolute)
- Example: /Users/admin/dev/reports/project/requirements.pdf

PROCESS:
1. Use pdf-reader tool:
   pdf-reader_read_pdf({
     sources: [{ path: "PDF_PATH" }],
     include_full_text: true,
     include_tables: true
   })

2. Extract repository name:
   - Run: git rev-parse --show-toplevel
   - Get basename (last path component)

3. Semantic analysis:
   - Identify main requirements (top-level features, goals)
   - Find sub-tasks for each requirement
   - Create concrete descriptions

4. Translate to English (CRITICAL):
   - If PDF is NOT in English, translate ALL titles/descriptions
   - Use technical software development terminology
   - Example: "Formulare von DB verlagern" → "Migrate Forms to Database"

5. Create JSON structure:
   {
     "repository_name": "...",
     "extraction_date": "YYYY-MM-DD",
     "total_requirements": N,
     "main_requirements": [...]
   }

6. Save to: /Users/admin/dev/Reports/{repository_name}/requirements.json

7. Validate checklist:
   ☐ PDF readable ☐ Repo name correct ☐ JSON valid ☐ All English
   ☐ IDs unique ☐ Directory created ☐ File saved ☐ User informed

OUTPUT:
Report to user:
- PDF analyzed: [filename]
- Requirements extracted: [count]
- Sub-tasks identified: [count]
- Saved to: /Users/admin/dev/Reports/{repo}/requirements.json

CRITICAL RULES:
- IDs format: REQ-001 (not REQ-1), zero-padded 3 digits
- Sub-task IDs continue sequentially across requirements: TASK-001, TASK-002, TASK-003...
- Minimum 1 sub-task per requirement (can be empty array `[]` only for very simple requirements)
- Descriptions concrete, not vague
- Keep response under 3000 tokens total
- Output ONLY JSON to file, not markdown
- All content in JSON must be English
```

**Estimated tokens:** 1,800-2,000 for entire operation

---

## Stage 2: Repository Detection

**Use if agent needs to detect repository:**

```
TASK: Extract repository name

PROCESS:
1. Run: git rev-parse --show-toplevel
2. Extract basename (last path component only)
3. Return string

EXAMPLE:
Input: /Users/admin/dev/hamm-therapy
Output: hamm-therapy

CRITICAL:
- Must be in git repository
- Return basename only, not full path
- Handle errors gracefully
```

**Estimated tokens:** 200-300

---

## Token Analysis per Stage

| Stage | Operation | Est. Tokens | Notes |
|-------|-----------|-------------|-------|
| 1 | PDF extraction | 1,000-2,000 | Depends on PDF size |
| 2 | Semantic analysis | 500-1,000 | LLM thinking time |
| 3 | Translation (if needed) | 300-800 | Non-English PDFs only |
| 4 | JSON generation | 500-1,000 | Structuring output |
| 5 | Save & report | 200-300 | Final steps |
| **Total** | | **2,500-5,100** | Typical extraction |

**Optimization tips:**
- For large PDFs (50+ pages): Extract in chunks by page ranges
- For complex requirements: Do semantic analysis in passes
- Reuse extraction if validating multiple times (don't re-read PDF)

---

## Example: Complete Flow

**User request:**
```
Extract requirements from /Users/admin/dev/projects/spec.pdf
```

**Agent should:**
1. Use pdf-reader tool to extract content
2. Analyze semantically: Find 3 main requirements, each with 2-3 sub-tasks
3. Check if PDF is in English - if not, translate all content
4. Create JSON structure with proper IDs (REQ-001, REQ-002, TASK-001, etc.)
5. Save to: /Users/admin/dev/Reports/{repo-name}/requirements.json
6. Report: "✓ 3 requirements extracted (9 sub-tasks) → /Users/admin/dev/Reports/project-name/requirements.json"

---

## Common Mistakes to Avoid

❌ **Not translating non-English content** → JSON will have mixed languages  
✅ **Always translate to English** → All titles and descriptions in English

❌ **IDs not zero-padded** → REQ-1 instead of REQ-001  
✅ **Use format** → REQ-001, REQ-002, TASK-001, etc.

❌ **Nesting sub-tasks within sub-tasks** → 3+ hierarchy levels  
✅ **Keep 2 levels** → Requirement → Sub-tasks

❌ **Empty descriptions** → Titles without explanations  
✅ **Include context** → Each title has a concrete description

---

## Integration Notes

This skill uses:
- **pdf-reader tool** - PDF content extraction
- **git commands** - Repository detection
- **File system** - Saving JSON to /Users/admin/dev/Reports/

For user documentation: See **SKILL.md**  
For implementation details: See **IMPLEMENTATION.md**
