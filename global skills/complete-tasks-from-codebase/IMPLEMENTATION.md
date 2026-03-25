#!/usr/bin/env python3
"""
Complete Tasks from Codebase Skill - Implementation Guide

This file documents the EXACT PROMPTS and FLOW for OpenCode Chat Integration.
The skill operates in 3 stages, with token-optimized prompts.

To implement in OpenCode:
1. Use these prompts in your chat flow
2. Save codebase_analysis from Stage 1 for use in Stage 2
3. Loop through requirements in Stage 2
4. Update JSON in Stage 3
"""

# ============================================================================
# STAGE 1: CODEBASE ANALYSIS
# ============================================================================
# This prompt analyzes the project structure and creates a compact, reusable
# analysis that minimizes tokens while providing enough context.

PROMPT_STAGE_1_ANALYSIS = """
TASK: Analyze project codebase structure (token-optimized)

You are analyzing a Git project to understand its architecture and patterns.
This analysis will be used to generate implementation guidance and test cases.

PROJECT LOCATION: {repo_path}
REPOSITORY NAME: {repo_name}

Analyze the project and provide output in EXACTLY this JSON format (max 450 tokens):

{{
  "language": "primary language detected",
  "frameworks": ["framework1", "framework2"],
  "key_modules": [
    "relative/path/to/module1",
    "relative/path/to/module2",
    "relative/path/to/module3"
  ],
  "architecture_patterns": [
    "Brief description of pattern 1",
    "Brief description of pattern 2"
  ],
  "key_dependencies": {{
    "library_name": "version"
  }},
  "test_framework": "testing framework used",
  "code_style": "dominant code style/conventions"
}}

CRITICAL RULES:
- Key modules: List 5-7 main directories/packages (e.g., lib/accounts, lib/web/live)
- Frameworks: List actual frameworks detected (Phoenix, Express, Django, etc.)
- Patterns: Describe architectural patterns in 1 sentence each (MVC, REST, Event-driven, etc.)
- Dependencies: List only 5-6 most important, with versions
- Keep response UNDER 450 tokens - this is critical for token efficiency
- Output ONLY the JSON, no additional text
"""

# ============================================================================
# STAGE 2A: REQUIREMENT TEST GENERATION
# ============================================================================
# For each requirement, generate Gherkin test scenarios

PROMPT_STAGE_2A_REQUIREMENT_TESTS = """
TASK: Generate Gherkin test cases for requirement

CODEBASE ANALYSIS:
{codebase_analysis}

REQUIREMENT:
ID: {req_id}
Title: {req_title}
Description: {req_description}

Generate Gherkin test scenarios for this requirement.

Create EXACTLY 3 scenarios:
1. Happy Path - Success case with realistic data
2. Error Handling - Error condition or validation failure
3. Edge Case - Boundary condition or unusual scenario

FORMAT (must be valid Gherkin):

```gherkin
Feature: {req_title}
  
  Scenario: {Happy path scenario name}
    Given {precondition with data example}
    When {user action}
    Then {expected outcome}
    
  Scenario: {Error scenario name}
    Given {error condition with data}
    When {action that triggers error}
    Then {error handling/message}
    
  Scenario: {Edge case scenario name}
    Given {boundary condition with data}
    When {action at boundary}
    Then {expected behavior}
```

RULES:
- Each scenario must have Given/When/Then steps
- Include specific data values (e.g., "email user@example.com")
- Scenario names must be descriptive (current: 2-5 words)
- Keep scenarios concise (4-6 lines each)
- Output ONLY the Gherkin code block, no explanation
"""

# ============================================================================
# STAGE 2B: SUBTASK IMPLEMENTATION GENERATION
# ============================================================================
# For each subtask, generate implementation guidance

PROMPT_STAGE_2B_SUBTASK_IMPLEMENTATION = """
TASK: Generate implementation guidance for subtask

CODEBASE ANALYSIS:
{codebase_analysis}

REQUIREMENT: {req_title}
SUBTASK ID: {task_id}
SUBTASK TITLE: {task_title}
SUBTASK DESCRIPTION: {task_description}

OTHER SUBTASKS IN THIS REQUIREMENT:
{other_subtasks_list}

Generate implementation guidance in EXACTLY this format (max 280 tokens):

## Overview
{2-3 sentences explaining what needs to be built}

## Key Files
- {relative/path/file1.ext}: {what to change/create}
- {relative/path/file2.ext}: {what to change/create}

## Implementation Steps
1. {Action step}
2. {Action step}
3. {Action step}
4. {Action step}
5. {Action step}

## Key Considerations
- {Pattern, best practice, or gotcha relevant to this project}
- {Dependency or integration point if relevant}
- {Performance, architecture, or code style note}

## Cross-References
{IF depends on another subtask: "See {TASK_ID} for {feature} setup before implementing this"}
{IF depends on requirement: "This builds on {REQ_ID}"}

RULES:
- Key Files: Use actual paths from codebase analysis
- Steps: 5-8 numbered action steps (not bullet points)
- No detailed code, focus on WHAT and WHERE, not HOW
- If this depends on another subtask, reference it by ID
- Keep under 280 tokens total
- Output ONLY the formatted response, no explanation
"""

# ============================================================================
# STAGE 2C: SUBTASK TEST GENERATION
# ============================================================================
# For each subtask, generate test scenarios based on implementation

PROMPT_STAGE_2C_SUBTASK_TESTS = """
TASK: Generate Gherkin test cases for subtask

CODEBASE ANALYSIS:
{codebase_analysis}

REQUIREMENT: {req_title}
SUBTASK: {task_title}
SUBTASK ID: {task_id}

IMPLEMENTATION GUIDANCE:
{implementation_guidance}

Generate Gherkin test scenarios for this subtask.

Create EXACTLY 3 scenarios (based on the implementation guidance):
1. Happy Path - Normal operation succeeds
2. Error Handling - Error or validation failure
3. Edge Case - Boundary condition or unusual case

FORMAT (must be valid Gherkin):

```gherkin
Feature: {task_title}
  
  Scenario: {Happy path scenario name}
    Given {precondition with specific data}
    When {action}
    Then {expected outcome}
    
  Scenario: {Error scenario name}
    Given {error condition with data}
    When {action causes error}
    Then {error handling}
    
  Scenario: {Edge case scenario name}
    Given {boundary condition with data}
    When {action at boundary}
    Then {expected behavior}
```

RULES:
- Each scenario: Given/When/Then steps
- Include data examples (values, IDs, etc.)
- Scenario names: 2-5 words, descriptive
- Concise: 4-6 lines per scenario
- Align with implementation guidance provided
- Output ONLY the Gherkin code block
"""

# ============================================================================
# PROCESSING LOGIC (Pseudocode)
# ============================================================================
"""
MAIN PROCESSING FLOW:

1. Load requirements.json
2. Get codebase analysis (Stage 1)
   analysis = call_prompt(PROMPT_STAGE_1_ANALYSIS)

3. For each requirement in main_requirements:
   
   a. Generate requirement test (Stage 2A)
      req_test = call_prompt(
         PROMPT_STAGE_2A_REQUIREMENT_TESTS,
         codebase_analysis=analysis,
         req_id=requirement.id,
         req_title=requirement.title,
         req_description=requirement.description
      )
      requirement["test"] = req_test
   
   b. For each subtask in requirement.sub_tasks:
      
      i. Generate subtask implementation (Stage 2B)
         impl = call_prompt(
            PROMPT_STAGE_2B_SUBTASK_IMPLEMENTATION,
            codebase_analysis=analysis,
            req_title=requirement.title,
            task_id=subtask.id,
            task_title=subtask.title,
            task_description=subtask.description,
            other_subtasks_list=format_other_subtasks(requirement)
         )
         subtask["implementation"] = impl
      
      ii. Generate subtask test (Stage 2C)
         test = call_prompt(
            PROMPT_STAGE_2C_SUBTASK_TESTS,
            codebase_analysis=analysis,
            req_title=requirement.title,
            task_title=subtask.title,
            task_id=subtask.id,
            implementation_guidance=impl
         )
         subtask["test"] = test

4. Save updated requirements.json
5. Create backup
6. Display summary
"""

# ============================================================================
# CONTEXT STRUCTURE (for keeping in conversation)
# ============================================================================
"""
Between prompts, maintain this minimal context (very token-efficient):

{
  "stage": "processing",  // "analysis", "processing", "complete"
  "codebase_analysis": {  // Full analysis JSON from Stage 1
    "language": "...",
    "frameworks": [...],
    ...
  },
  "progress": {
    "requirements_total": 14,
    "requirements_processed": 3,
    "current_requirement_id": "REQ-004"
  }
}

This context is passed to each prompt and updated after each requirement.
Keeps prompts focused and token-efficient.
"""

# ============================================================================
# EXPECTED OUTPUT EXAMPLES
# ============================================================================

EXAMPLE_REQUIREMENT_TEST = """
Feature: User Authentication System
  
  Scenario: User successfully logs in with valid credentials
    Given a user with email "john@example.com" exists
    When the user submits login form with password "SecurePass123!"
    Then the user is redirected to dashboard
    And a session token is created
    
  Scenario: Login fails with incorrect password
    Given user "john@example.com" exists
    When the user submits login with password "WrongPassword"
    Then error message "Invalid credentials" is displayed
    And no session token is created
    
  Scenario: Login fails with non-existent email
    Given no user with email "unknown@example.com" exists
    When the user submits login form
    Then error message "User not found" is displayed
"""

EXAMPLE_SUBTASK_IMPLEMENTATION = """
## Overview
Create a Phoenix LiveView component that displays a filtered list of patients.
This component will integrate with the existing patient context module and use Ecto queries.

## Key Files
- lib/hamm_therapy_web/live/admin_live/patient_list.ex: Create LiveView component
- lib/hamm_therapy/accounts.ex: Add get_patients_by_status/1 function
- lib/hamm_therapy_web/live/admin_live/patient_list.html.heex: Create template
- test/hamm_therapy_web/live/admin_live/patient_list_test.exs: Add tests

## Implementation Steps
1. Create new LiveView module with mount/3 and handle_event/3 callbacks
2. Add database query function to Accounts context to filter patients
3. Build HTML template with patient list display
4. Add filter buttons/dropdown for status selection
5. Implement real-time updates using LiveView socket assigns
6. Style component with Tailwind CSS
7. Add pagination if patient count is large
8. Test filtering with multiple scenarios

## Key Considerations
- Use Ecto queries at database level for performance
- LiveView state persists in assigns, not in database
- Follow existing Hamm-therapy naming conventions (snake_case)
- Consider caching frequently accessed patient lists
- Filter state should be URL-encoded for shareable links

## Cross-References
See TASK-003-002 for database schema setup before implementing this filter.
"""

EXAMPLE_SUBTASK_TEST = """
Feature: Patient Status Filtering
  
  Scenario: Display patients with pending therapy plans
    Given there are 15 patients total
    And 5 patients have status "pending_plan"
    When user clicks filter "Pending Plans"
    Then exactly 5 patients are displayed
    And each patient shows pending status indicator
    
  Scenario: Filter returns no results
    Given no patients have status "archived"
    When user selects filter "Archived Patients"
    Then message "No patients match this filter" is shown
    And "Clear Filters" button is visible
    
  Scenario: Filter works with large patient database
    Given there are 10,000 patients in system
    When user applies filter "Active Therapy"
    Then results load within 2 seconds
    And pagination shows "Showing 1-50 of 847"
"""

# ============================================================================
# INTEGRATION CHECKLIST
# ============================================================================
"""
To integrate into OpenCode Chat:

[ ] Parse git repository path from current context
[ ] Load requirements.json from /Users/admin/dev/Reports/{repo_name}/
[ ] Execute Stage 1 prompt to get codebase_analysis
[ ] Loop through main_requirements:
    [ ] Execute Stage 2A (requirement test)
    [ ] For each sub_task:
        [ ] Execute Stage 2B (implementation)
        [ ] Execute Stage 2C (test)
    [ ] Save codebase_analysis in context for next requirement
[ ] Write updated requirements.json back to disk
[ ] Create timestamped backup before updating
[ ] Validate JSON before writing
[ ] Display completion summary in chat
"""

print(__doc__)
