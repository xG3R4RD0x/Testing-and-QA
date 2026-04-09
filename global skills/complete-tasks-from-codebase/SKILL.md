---
name: complete-tasks-from-codebase
description: Analyze your codebase and automatically enrich requirements.json with implementation steps and test scenarios using intelligent agent dispatch
license: MIT
compatibility: opencode
version: 2.0.0
metadata:
  audience: developers
  workflow: requirements-management
tags:
  - requirements
  - testing
  - gherkin
  - bdd
  - implementation
  - code-analysis
  - automation
  - agent-agnostic
---

# Complete Tasks from Codebase v2.0.0

Refactored skill for automatic requirement enrichment with:
- **Non-interactive automatic dispatch** - Zero user interaction after invocation
- **Agent-agnostic** - Works with OpenCode, Claude Code, Codex, and other LLM agents
- **Smart codebase analysis** - Retrieves only relevant code patterns per task
- **Knowledge base first** - Uses existing docs before dynamic analysis
- **Parallel execution** - One subagent per requirement for speed
- **Temporary caching** - KB cache auto-deleted after completion

## When to Use This Skill

Use this skill when you:
- Have a `requirements.json` file that needs enrichment
- Want automatically generated implementation steps for each subtask
- Need tailored Gherkin BDD test scenarios
- Want analysis based on your actual codebase patterns
- Need non-interactive, fully-automatic processing
- Want it to work across any agent system

## How to Use This Skill

### Basic Command

```
/complete-tasks <path-to-requirements.json>
```

### Example

```
/complete-tasks /Users/admin/dev/Reports/goetz-kundenportal-phoenix/requirements.json
```

## Refactored Architecture (v2.0.0)

### 5-Stage Workflow

**Stage 1: Initialization**
- Load requirements.json
- Detect project name and root directory
- Validate structure

**Stage 2: Knowledge Base Detection**
- Scans project for existing documentation:
  - ARCHITECTURE.md, PATTERNS.md, TECH-STACK.md
  - GUIDELINES.md, API-SPEC.md, DATABASE-SCHEMA.md
  - Any .md files in docs/ directories
- Creates temporary cache (auto-deleted after)
- Summarizes KB for payload

**Stage 3: Codebase Analysis**
- Detects programming language and framework
- Identifies ORM, test framework, patterns
- Extracts key file structures
- Compiles tech stack info

**Stage 4: Subagent Dispatch (Automatic)**
- For each requirement:
  - Collects all subtasks
  - Builds universal JSON payload with all context
  - Automatically dispatches to subagent
  - Retries once on failure, then skips
  - Collects response

**Stage 5: JSON Enrichment**
- Updates each subtask with:
  - `implementation`: Step-by-step implementation guide
  - `test`: Gherkin BDD test scenarios
- Minimal validation (non-empty check)
- Saves with timestamped backup

**Stage 6: Cleanup**
- Deletes temporary KB cache
- Reports completion stats

## Universal Payload Format

Each subagent receives a single JSON payload containing everything needed:

```json
{
  "skill_version": "2.0.0",
  "operation": "enrich_requirement",
  "project": {
    "name": "goetz-kundenportal-phoenix",
    "root_path": "/path/to/project",
    "reports_path": "/path/to/Reports/project"
  },
  "knowledge_base": {
    "available": true,
    "summary": "# ARCHITECTURE.md...",
    "file_count": 5
  },
  "codebase_analysis": {
    "detected_stack": {
      "framework": "Phoenix",
      "language": "Elixir",
      "orm": "Ecto"
    },
    "key_patterns": {
      "migration_structure": "lib/*/migrations/",
      "liveview_structure": "lib/*_web/live/"
    }
  },
  "requirement": {
    "id": "REQ-001",
    "title": "Requirement Title",
    "description": "..."
  },
  "subtasks": [
    {
      "id": "TASK-001-01",
      "title": "Subtask title",
      "description": "..."
    }
  ]
}
```

## Supported Technologies

### Languages & Frameworks
- **Elixir**: Phoenix v1.8, Ecto
- **Python**: Django, Flask, FastAPI, SQLAlchemy
- **JavaScript/TypeScript**: Express, Fastify, TypeORM
- **Ruby**: Rails, ActiveRecord
- **Java**: Spring, Hibernate
- **Go**: Gin, Echo

### Test Frameworks
- ExUnit (Elixir)
- pytest (Python)
- Jest (JavaScript)
- RSpec (Ruby)
- JUnit (Java)

## Key Features

✅ **Fully Automatic** - No user prompts or interaction required

✅ **Non-Interactive** - Dispatch happens automatically with retry logic

✅ **Agent-Agnostic** - Universal payload works with any LLM agent system

✅ **Smart Analysis** - Detects tech stack and extracts relevant patterns only

✅ **KB-First** - Uses existing docs before analyzing code

✅ **Parallel Processing** - One subagent per requirement (not per subtask)

✅ **Automatic Retry** - 1x retry on failure, then gracefully skip

✅ **Temporary Cache** - Knowledge base cache auto-deleted after completion

✅ **Safe Operations** - Timestamped backups of original requirements.json

## Requirements

Your `requirements.json` file should have this structure:

```json
{
  "repository_name": "my-project",
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Feature Title",
      "description": "Feature description",
      "effort_hours": 1.0,
      "sub_tasks": [
        {
          "id": "TASK-001-01",
          "title": "Subtask Title",
          "description": "Subtask description"
        }
      ]
    }
  ]
}
```

Alternative key names supported:
- `requirements` instead of `main_requirements`
- `subtasks` instead of `sub_tasks`

## Output Format

After running the skill, each subtask gets two new fields:

```json
{
  "id": "TASK-001-01",
  "title": "Create database schema",
  "description": "...",
  "implementation": "## Overview\nCreate database schema for forms...\n\n## Implementation Steps\n1. ...",
  "test": "Feature: Create database schema\n  Scenario: ..."
}
```

## Retry Logic

The skill implements intelligent retry handling:

```
Attempt 1: Dispatch subagent
  ✅ Success → Use response
  ❌ Fails → Go to Attempt 2

Attempt 2: Retry same dispatch
  ✅ Success → Use response
  ❌ Fails → Skip requirement (marked as processed)
```

Result: Maximum 2 attempts, graceful failure

## Troubleshooting

### Skill not recognized

1. Verify skill directory exists:
   ```
   /Users/admin/.agents/skills/complete-tasks-from-codebase/
   ```

2. Check SKILL.md frontmatter has correct name

3. Restart your agent environment

### Requirements file not found

Ensure you provide **absolute path**:
```
/complete-tasks /Users/admin/dev/Reports/my-project/requirements.json
```

### Invalid JSON error

Verify requirements.json has:
- Valid JSON syntax
- Either `main_requirements` or `requirements` key
- List of requirement objects with `id`, `title`, `description`

### No KB detected

This is normal! The skill falls back to dynamic codebase analysis if no KB found

## Project Structure

```
/Users/admin/.agents/skills/complete-tasks-from-codebase/
├─ lib/
│  ├─ __init__.py
│  ├─ complete_tasks_orchestrator.py    (Main orchestration)
│  ├─ knowledge_base_manager.py         (KB detection & caching)
│  ├─ codebase_analyzer.py              (Tech stack detection)
│  ├─ payload_builder.py                (Universal payload creation)
│  ├─ agent_dispatcher.py               (Agent-agnostic dispatch)
│  ├─ json_enricher.py                  (Updates requirements.json)
│  └─ retry_handler.py                  (Retry logic)
├─ complete-tasks-from-codebase-v2.py   (Main entry point)
├─ index.py                             (OpenCode entry point)
├─ SKILL.md                             (This file)
├─ README.md                            (Architecture guide)
├─ PROMPTS-REFERENCE.md                 (Subagent prompt templates)
└─ OPENCODE-INTEGRATION.md              (Agent adaptation)
```

## Performance

- **Speed**: ~5-10 seconds for typical project (14+ requirements)
- **Token Usage**: ~20,000-25,000 tokens for 14 requirements + 44 subtasks
- **Cache**: Temporary (deleted after)
- **Backup**: Automatic timestamped backup

## Support

For issues or questions:
- Check README.md for architecture details
- Review PROMPTS-REFERENCE.md for payload examples
- See OPENCODE-INTEGRATION.md for agent integration details

---

**Version:** 2.0.0  
**Status:** Production Ready ✅  
**Released:** 2026-04-09
