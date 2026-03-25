# Complete Tasks from Codebase Skill - V2 (LLM-Prompting)

## Overview

This skill enriches `requirements.json` with implementation plans by having the user interact with their agent (OpenCode, GitHub Copilot, Claude Code, etc.) through a structured prompting workflow.

**Key Differences from V1:**
- ✅ Generates prompts dynamically with codebase context
- ✅ One prompt per requirement (groups all subtasks)
- ✅ User provides responses from their agent
- ✅ Implementation plans are specific to the actual codebase
- ✅ Automatic retry if subtasks are missing

## Usage

### Basic Command

```bash
/complete-tasks requirements.json
```

### Workflow

The skill operates in 4 stages:

#### Stage 1: Preparation
- Loads `requirements.json`
- Detects programming language and frameworks
- Identifies technical requirements (those with subtasks)

#### Stage 2: Implementation Analysis
For each technical requirement:
1. Collects relevant codebase context (~5K tokens)
2. Builds a prompt with:
   - Project structure and configuration
   - Code examples matching the requirement
   - Requirement title, description, and subtasks
3. **User action**: Copy/paste prompt to your agent chat
4. **User action**: Paste agent's response back to the skill
5. Parses response and stores implementation plans
6. Automatically retries if any subtasks are missing

#### Stage 3: Test Generation
For each requirement with implementation:
1. Builds a prompt for test scenario generation
2. **User action**: Copy/paste prompt to your agent
3. **User action**: Paste agent's response
4. Parses and stores test scenarios

#### Stage 4: Finalization
- Updates `requirements.json` with implementation and test sections
- Creates automatic backup
- Prints summary

## Example Interaction

```
$ /complete-tasks requirements.json

[Stage 1]
✓ Loaded 15 requirements
✓ Detected 10 technical requirements
✓ Detected: Elixir, Phoenix, Ecto

[Stage 2: Analyzing with LLM]

────────────────────────────────────────
[1/10] REQ-001: User Authentication System
────────────────────────────────────────

Collecting context...
✓ Found 4 relevant code examples
✓ Context size: 2800 tokens

================================================================================
COPY THE PROMPT BELOW AND SEND TO YOUR AGENT
================================================================================

# Project Context

**Language:** Elixir
**Frameworks:** Phoenix, Ecto

## Project Structure
hamm-therapy/
├── lib/
│   ├── hamm_therapy/
│   │   ├── auth/
│   │   └── user_context.ex
│   └── hamm_therapy_web/
├── mix.exs
└── README.md

[... more context ...]

---

# Requirement to Implement

**Title:** User Authentication System
**Description:** Implement secure user authentication with JWT tokens

## Subtasks to Implement

1. **User Registration**
   Description: Allow users to create accounts

2. **User Login**
   Description: Authenticate users and issue JWT tokens

[... format instructions ...]

================================================================================
PASTE THE AGENT'S RESPONSE BELOW
================================================================================

Paste the agent's response here (end with an empty line):

[User pastes agent's response]

## Implementation for User Registration
1. Create lib/hamm_therapy/accounts/user.ex with Ecto schema
2. Define changeset for password hashing in lib/hamm_therapy/accounts/user.ex
3. Create lib/hamm_therapy/accounts.ex context module
4. Add create_user/1 function that validates and creates user
5. Add test in test/hamm_therapy/accounts_test.exs

## Implementation for User Login
1. Create JWT token module in lib/hamm_therapy/token.ex
2. Add login_user/2 function in accounts context
3. Create login endpoint in lib/hamm_therapy_web/controllers/auth_controller.ex
4. Add plug authentication middleware
5. Create login tests

[blank line to finish]

Parsing response...
✓ Implementation for User Registration: ✓
✓ Implementation for User Login: ✓

Stored analysis for REQ-001

Processing REQ-002...
[continues for other requirements]

[Stage 3: Generating Tests]
[Similar process for test scenarios]

[Stage 4: Finalize]
✓ Updated 10 requirements
✓ Added 20 subtask implementations
✓ Added 20 test scenarios
✓ Backup saved: requirements-backup-20260325-143022.json
✓ Updated: requirements.json

================================================================================
✓ SKILL EXECUTION COMPLETE
================================================================================
```

## How the Agent Responds

When you paste the prompt into your agent chat (OpenCode, Copilot, Claude Code, etc.), the agent will:

1. **Analyze the codebase context** you provided
2. **Understand your requirements and subtasks**
3. **Generate implementation steps** that are specific to your project
4. **Format the response** exactly as requested

Example agent response format:

```
## Implementation for Subtask 1 Title
1. Create file lib/module/file.ex with the following structure
2. Define function process_data/1 that uses existing pattern from lib/auth.ex
3. Add validation using Ecto changesets
4. Integrate with LiveView component in lib/module_web/live/view.ex
5. Write tests following pattern in test/module/file_test.exs
6. Ensure authorization checks using Bodyguard

## Implementation for Subtask 2 Title
1. Create migration file in priv/repo/migrations/
2. Use existing schema patterns from lib/module/schema.ex
...
```

## Important Notes

### What You Get
- ✅ Specific file paths (relative to project root)
- ✅ Function/module names to create or use
- ✅ References to existing patterns to follow
- ✅ Integration points with current code

### What You Don't Get (Intentionally)
- ❌ Actual code implementation (steps, not code)
- ❌ Copy-paste ready solutions
- ❌ Generated code files

This design ensures you stay in control and understand each step.

### Handling Incomplete Responses

If the agent doesn't respond with all subtasks, the skill will:
1. Show which subtasks are missing
2. Ask you to retry
3. Automatically parse the new response

### Token Optimization

The skill:
- ✅ Sends only ~5K tokens of codebase context per prompt
- ✅ Includes smart examples relevant to the requirement
- ✅ Keeps the prompt focused and actionable

## Tips for Best Results

1. **Use the exact prompt provided** - Don't modify it
2. **Paste the full agent response** - Include all subtask sections
3. **End with a blank line** - The skill needs this to know you're done
4. **Have the codebase available** - Agent can reference files and patterns better
5. **Be specific in requirements** - More detail = better implementation plans

## Troubleshooting

### "Missing subtasks" error
The agent didn't respond with all subtasks. Copy the prompt again and retry.

### Agent can't find the code
Make sure your codebase context shows the relevant files and structure.

### Prompt too generic
Check that requirement descriptions are specific enough for the agent to target the right code areas.

## Architecture

The skill is built with modular components:

- **PromptBuilder**: Constructs prompts with requirement + context
- **DynamicContextCollector**: Gathers relevant code examples
- **ResponseParser**: Extracts subtask implementations from agent response
- **InteractiveSession**: Manages user interaction flow
- **CompleteTasksSkillV2**: Orchestrates all stages

## Compatibility

Works with:
- ✅ OpenCode
- ✅ GitHub Copilot
- ✅ Claude Code
- ✅ Any LLM-powered agent

The skill uses **pure prompting** - no APIs, no agent detection, just text exchange.
