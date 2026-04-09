# OPENCODE-INTEGRATION.md

## Agent-Agnostic Integration Guide

This document explains how the refactored skill integrates with different agent systems: OpenCode, Claude Code, Codex, and generic LLM APIs.

---

## Architecture

The skill uses a **universal payload format** that works across all agent systems. The agent adapter layer automatically detects the environment and handles dispatch appropriately.

```
┌─────────────────────────┐
│  Complete Tasks Skill    │
│   (Orchestrator.py)      │
└────────┬────────────────┘
         │ Universal Payload
         ▼
┌─────────────────────────┐
│  Agent Dispatcher       │
│  (Detects Environment)  │
└────────┬────────────────┘
         │
    ┌────┴──────────────────────────┐
    │                               │
    ▼                               ▼
┌──────────────┐           ┌────────────────┐
│ OpenCode     │           │ Claude Code    │
│ Subagent     │           │ Task Tool      │
│ System       │           │                │
└──────────────┘           └────────────────┘
    │                               │
    └────────┬──────────────────────┘
             ▼
    Universal JSON Payload
    + Prompt Context
```

---

## Environments

### 1. OpenCode

OpenCode is the primary target environment.

**Entry Point:** `index.py` → `complete-tasks-from-codebase-v2.py`

**Dispatch Method:**
- OpenCode's native subagent system
- Skill dispatches subagents automatically with universal payload
- Subagents return JSON responses
- Orchestrator collects and enriches requirements.json

**Environment Detection:**
```python
if os.getenv("OPENCODE_SKILL"):
    environment = "opencode"
```

**Integration:**
1. Skill runs as OpenCode skill
2. Reads requirements.json path from command line
3. Creates universal payload
4. Dispatches subagent via OpenCode's native mechanism
5. Receives response and enriches JSON

**Example Usage:**
```bash
/complete-tasks /Users/admin/dev/Reports/project-name/requirements.json
```

---

### 2. Claude Code

Claude Code integration via the Task tool.

**Environment Detection:**
```python
if os.getenv("CLAUDE_CODE") or os.getenv("CLAUDE_API_KEY"):
    environment = "claude-code"
```

**Dispatch Method:**
```python
def dispatch_claude_code(payload: Dict) -> Dict:
    """
    Dispatch via Claude Code's Task tool
    
    In Claude Code, this would call:
    @task("agent-name")
    def enrich_requirement(payload):
        # Subagent receives payload
        # Returns implementation + test for each subtask
    
    response = await enrich_requirement(payload)
    return response
    """
```

**Expected Claude Code Skill Flow:**
1. User invokes complete-tasks skill
2. Skill detects Claude Code environment
3. Skill uses Claude Code's Task tool to dispatch subtasks
4. Each subagent receives universal payload
5. Responses collected and JSON enriched

---

### 3. Codex

Generic Codex agent integration.

**Environment Detection:**
```python
if os.getenv("CODEX_API_KEY"):
    environment = "codex"
```

**Dispatch Method:**
```python
def dispatch_codex(payload: Dict, api_endpoint: str) -> Dict:
    """
    Dispatch via Codex HTTP API
    
    POST /api/execute
    {
      "agent": "subagent-name",
      "payload": {...universal payload...}
    }
    """
```

---

### 4. Generic LLM API

Fallback for any HTTP API-based agent system.

**Environment Detection:**
```python
if os.getenv("LLM_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
    environment = "generic"
```

**Dispatch Method:**
```python
def dispatch_generic_api(payload: Dict, api_endpoint: str) -> Dict:
    """
    POST to LLM API endpoint with payload
    
    Returns JSON response with implementation + test
    """
    response = requests.post(
        api_endpoint,
        json=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    return response.json()
```

---

## Universal Payload Structure

All agents receive the same payload structure:

```json
{
  "skill_version": "2.0.0",
  "operation": "enrich_requirement",
  
  "project": {
    "name": "project-name",
    "root_path": "/path/to/project",
    "reports_path": "/path/to/Reports/project"
  },
  
  "knowledge_base": {
    "available": true,
    "summary": "# Project docs...",
    "file_count": 5,
    "files_found": ["ARCHITECTURE.md", "PATTERNS.md"]
  },
  
  "codebase_analysis": {
    "detected_stack": {
      "framework": "Phoenix",
      "language": "Elixir",
      "orm": "Ecto",
      "test_framework": "ExUnit"
    },
    "key_patterns": {
      "migration_structure": "lib/*/migrations/",
      "liveview_structure": "lib/*_web/live/"
    }
  },
  
  "requirement": {
    "id": "REQ-001",
    "title": "Requirement title",
    "description": "..."
  },
  
  "subtasks": [
    {
      "id": "TASK-001-01",
      "title": "Subtask title",
      "description": "..."
    }
  ],
  
  "instructions": {
    "analysis_depth": "smart",
    "generate_implementation": true,
    "generate_test": true,
    "output_format": "json",
    "validation": "minimal"
  }
}
```

---

## Agent Response Format

All agents must return responses in this format:

```json
{
  "requirement_id": "REQ-001",
  "status": "success",
  "subtasks": [
    {
      "id": "TASK-001-01",
      "implementation": "## Overview\n...\n## Implementation Steps\n1. ...",
      "test": "Feature: ...\n  Scenario: ..."
    },
    {
      "id": "TASK-001-02",
      "implementation": "...",
      "test": "..."
    }
  ]
}
```

---

## Implementing Support for New Environments

To add support for a new agent environment:

### 1. Add Detection in `agent_dispatcher.py`

```python
def _detect_environment(self) -> str:
    """Detect environment"""
    # Add your environment check
    if os.getenv("MY_AGENT_ENV"):
        return "my-agent"
    
    return "generic"
```

### 2. Add Dispatch Method

```python
def dispatch_my_agent(self, payload: Dict) -> Dict:
    """
    Dispatch to my agent system
    
    Args:
        payload: Universal payload dict
    
    Returns:
        Response dict from agent
    """
    try:
        # Implement dispatch logic
        response = my_agent_system.dispatch(payload)
        return response
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "skipped": True
        }
```

### 3. Create Dispatch Callback

```python
def get_dispatch_callback_for_my_agent():
    """Create dispatch callback for my agent"""
    def callback(payload):
        dispatcher = AgentDispatcher()
        return dispatcher.dispatch_my_agent(payload)
    return callback
```

### 4. Test Integration

```python
# Test with sample payload
orchestrator = CompleteTasksOrchestrator()
callback = get_dispatch_callback_for_my_agent()
result = orchestrator.run(
    requirements_file="/path/to/requirements.json",
    dispatch_callback=callback
)
```

---

## Retry Logic Integration

All environments use the same retry mechanism:

```
1st Attempt:
  ✅ Success → Use response
  ❌ Failure → Try again

2nd Attempt (Retry):
  ✅ Success → Use response
  ❌ Failure → Skip (mark as processed)
```

The `RetryHandler` class handles this automatically:

```python
retry_handler = RetryHandler(max_retries=1)

# Dispatch with automatic retry
result = retry_handler.execute_with_retry_dict(
    func=dispatch_function,
    requirement_id="REQ-001"
)

# Result includes:
# - success: bool
# - result: response or None
# - error: error message or None
# - attempts: number of attempts made
# - skipped: True if failed after retries
```

---

## Payload Serialization

For HTTP-based agents, payloads are serialized as JSON:

```python
from lib.payload_builder import PayloadBuilder

builder = PayloadBuilder()

# Build payload
payload = builder.build_requirement_payload(...)

# Serialize to JSON string (compact)
json_str = builder.to_json_string(payload, pretty=False)

# Serialize pretty (for debugging)
json_str_pretty = builder.to_json_string(payload, pretty=True)

# Parse back
parsed = builder.from_json_string(json_str)

# Validate
is_valid, errors = builder.validate_payload(payload)
```

---

## Environment Variables

The skill respects these environment variables for agent detection:

```bash
# OpenCode
export OPENCODE_SKILL=1

# Claude Code
export CLAUDE_CODE=1
export CLAUDE_API_KEY=sk-...

# Codex
export CODEX_API_KEY=...

# Generic LLM API
export LLM_API_KEY=...
export ANTHROPIC_API_KEY=sk-...
```

---

## Testing Integration

### Test with Mock Dispatch

```python
def mock_dispatch(payload):
    """Mock dispatch for testing"""
    return {
        "success": True,
        "requirement_id": payload.get("requirement", {}).get("id"),
        "subtasks": [
            {
                "id": task.get("id"),
                "implementation": "Mock implementation",
                "test": "Feature: Mock test"
            }
            for task in payload.get("subtasks", [])
        ]
    }

orchestrator = CompleteTasksOrchestrator()
result = orchestrator.run(
    requirements_file="/path/to/requirements.json",
    dispatch_callback=mock_dispatch
)
```

### Test with Real Dispatch

```python
# Define your real dispatch function
def my_real_dispatch(payload):
    # Your actual agent dispatch logic
    pass

# Run orchestrator with real dispatch
result = orchestrator.run(
    requirements_file="/path/to/requirements.json",
    dispatch_callback=my_real_dispatch
)
```

---

## Performance Considerations

**Payload Size:** ~8-15 KB per requirement
**Network Overhead:** Minimal (one dispatch per requirement)
**Retry Impact:** Max 2x dispatch calls per requirement
**Total Time:** 5-10 seconds for typical project

---

## Logging and Debugging

Enable debug logging to see payload details:

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now you'll see:
# - Payload summaries for each dispatch
# - Environment detection info
# - Retry attempts
# - Response parsing details
```

---

## Common Issues and Solutions

### Issue: Environment Not Detected

```python
# Add explicit environment setup
os.environ["OPENCODE_SKILL"] = "1"

# Then run
orchestrator.run(requirements_file)
```

### Issue: Invalid Payload Structure

```python
# Validate before dispatch
from lib.payload_builder import PayloadBuilder

builder = PayloadBuilder()
is_valid, errors = builder.validate_payload(payload)

if not is_valid:
    print(f"Payload errors: {errors}")
```

### Issue: Subagent Response Format Wrong

```python
# Ensure response matches format:
{
  "requirement_id": "REQ-001",  # Required
  "status": "success",           # Required
  "subtasks": [                  # Required list
    {
      "id": "TASK-001-01",       # Required
      "implementation": "...",   # Optional but encouraged
      "test": "..."              # Optional but encouraged
    }
  ]
}
```

---

## Support

For integration issues:
1. Check environment variables are set
2. Review payload structure with PROMPTS-REFERENCE.md
3. Enable debug logging to see details
4. Test with mock dispatch first
5. Verify response format matches specification

---

**Last Updated:** 2026-04-09  
**Version:** 2.0.0
