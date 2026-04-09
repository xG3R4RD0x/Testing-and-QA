# Complete Prompts Reference

This document contains the EXACT PROMPTS to use for each stage of the skill.

## Stage 1: Codebase Analysis

Use this prompt to analyze the project structure. Run it ONCE at the beginning.

```
TASK: Analyze project codebase structure (token-optimized)

You are analyzing a Git project to understand its architecture and patterns.
This analysis will be used to generate implementation guidance and test cases.

PROJECT LOCATION: {repo_path}
REPOSITORY NAME: {repo_name}

Analyze the project and provide output in EXACTLY this JSON format (max 450 tokens):

{
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
  "key_dependencies": {
    "library_name": "version"
  },
  "test_framework": "testing framework used",
  "code_style": "dominant code style/conventions"
}

CRITICAL RULES:
- Key modules: List 5-7 main directories/packages (e.g., lib/accounts, lib/web/live)
- Frameworks: List actual frameworks detected (Phoenix, Express, Django, etc.)
- Patterns: Describe architectural patterns in 1 sentence each (MVC, REST, Event-driven, etc.)
- Dependencies: List only 5-6 most important, with versions
- Keep response UNDER 450 tokens - this is critical for token efficiency
- Output ONLY the JSON, no additional text
```

**Expected Output:**
```json
{
  "language": "Elixir",
  "frameworks": ["Phoenix", "LiveView", "Ecto"],
  "key_modules": [
    "lib/hamm_therapy/accounts",
    "lib/hamm_therapy_web/live",
    "lib/hamm_therapy/repo",
    "lib/hamm_therapy_web/controllers"
  ],
  "architecture_patterns": [
    "MVC with LiveView for real-time updates",
    "Context modules for domain isolation",
    "Ecto for data persistence"
  ],
  "key_dependencies": {
    "phoenix": "~> 1.7",
    "ecto": "~> 3.10",
    "oban": "~> 2.15"
  },
  "test_framework": "ExUnit",
  "code_style": "Elixir conventions with Tailwind CSS"
}
```

---

## Stage 2A: Generate Requirement Tests

For EACH requirement, use this prompt to generate Gherkin test scenarios.

```
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
- Scenario names must be descriptive (2-5 words)
- Keep scenarios concise (4-6 lines each)
- Output ONLY the Gherkin code block, no explanation
```

**Example Input:**
```
CODEBASE ANALYSIS:
{
  "language": "Elixir",
  "frameworks": ["Phoenix", "LiveView"],
  ...
}

REQUIREMENT:
ID: REQ-001
Title: User Authentication System
Description: Implement user login and session management
```

**Expected Output:**
```gherkin
Feature: User Authentication System
  
  Scenario: User successfully logs in with valid credentials
    Given a user with email "john@example.com" exists
    When the user submits the login form with password "SecurePass123!"
    Then the user is redirected to the dashboard
    And a session token is created
    
  Scenario: Login fails with incorrect password
    Given user "john@example.com" exists with password "CorrectPass"
    When the user submits login with password "WrongPassword"
    Then error message "Invalid credentials" is displayed
    And no session token is created
    
  Scenario: Login fails with non-existent email
    Given no user with email "unknown@example.com" exists
    When the user submits the login form
    Then error message "User not found" is displayed
```

---

## Stage 2B: Generate Subtask Implementation

For EACH subtask, use this prompt to generate implementation guidance.

```
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
```

**Example Input:**
```
CODEBASE ANALYSIS:
{
  "language": "Elixir",
  "frameworks": ["Phoenix", "LiveView"],
  "key_modules": ["lib/hamm_therapy_web/live", "lib/hamm_therapy/accounts", ...],
  ...
}

REQUIREMENT: User Authentication System
SUBTASK ID: TASK-001-001
SUBTASK TITLE: Create login form
SUBTASK DESCRIPTION: Build a form component for users to enter email and password

OTHER SUBTASKS IN THIS REQUIREMENT:
- TASK-001-002: Password validation
- TASK-001-003: Session management
```

**Expected Output:**
```
## Overview
Create a Phoenix LiveView component that displays a login form with email and password fields.
This component will integrate with the accounts context module and handle form submission.

## Key Files
- lib/hamm_therapy_web/live/auth_live/login.ex: Create LiveView component
- lib/hamm_therapy_web/live/auth_live/login.html.heex: Create template
- lib/hamm_therapy/accounts.ex: Add authenticate_user/2 function
- test/hamm_therapy_web/live/auth_live/login_test.exs: Test component

## Implementation Steps
1. Create new LiveView module with mount/3 callback
2. Add form template with email and password fields
3. Implement handle_event/3 for form submission
4. Add authentication logic to accounts context
5. Handle authentication errors gracefully
6. Redirect to dashboard on successful login
7. Add proper error messages to form
8. Test form validation and submission

## Key Considerations
- Use HTML5 input validation for email format
- Never log passwords in error messages
- Form state should be managed in LiveView assigns
- Follow Phoenix conventions for component naming
- Validate form inputs on both client and server

## Cross-References
See TASK-001-003 for session management setup before completing this form.
```

---

## Stage 2C: Generate Subtask Tests

For EACH subtask, use this prompt to generate Gherkin test scenarios.

```
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
```

**Example Input:**
```
REQUIREMENT: User Authentication System
SUBTASK: Create login form
SUBTASK ID: TASK-001-001

IMPLEMENTATION GUIDANCE:
## Overview
Create a Phoenix LiveView component that displays a login form...

## Key Files
- lib/hamm_therapy_web/live/auth_live/login.ex: Create LiveView component
- lib/hamm_therapy_web/live/auth_live/login.html.heex: Create template
...
```

**Expected Output:**
```gherkin
Feature: Create Login Form
  
  Scenario: Form displays all required fields
    Given the user is on the login page
    When the page loads
    Then an email input field is visible
    And a password input field is visible
    And a "Login" button is visible
    
  Scenario: Form submission with invalid email
    Given the user is on the login form
    When the user enters "invalid-email" in email field
    And clicks the "Login" button
    Then error message "Invalid email format" is displayed
    And no form submission occurs
    
  Scenario: Form submission with empty fields
    Given the user is on the login form
    When the user clicks "Login" without entering credentials
    Then error message "Email and password are required" is shown
```

---

## Complete Processing Sequence

```
1. Get repo_path and repo_name (auto-detect from git)
2. Load requirements.json

3. STAGE 1 - Run once:
   codebase_analysis = ChatLLM(PROMPT_STAGE_1_ANALYSIS)
   Save codebase_analysis in context

4. STAGE 2 - Loop through each requirement:
   
   FOR each requirement in main_requirements:
     
     4A. Generate requirement test:
         req_test = ChatLLM(
           PROMPT_STAGE_2A_REQUIREMENT_TESTS,
           codebase_analysis=codebase_analysis,
           req_id=requirement.id,
           req_title=requirement.title,
           req_description=requirement.description
         )
         requirement["test"] = req_test
     
     4B. For each subtask:
         
         4B-i. Generate implementation:
               impl = ChatLLM(
                 PROMPT_STAGE_2B_SUBTASK_IMPLEMENTATION,
                 codebase_analysis=codebase_analysis,
                 req_title=requirement.title,
                 task_id=subtask.id,
                 task_title=subtask.title,
                 task_description=subtask.description,
                 other_subtasks_list=format_other_subtasks(requirement)
               )
               subtask["implementation"] = impl
         
         4B-ii. Generate test:
                test = ChatLLM(
                  PROMPT_STAGE_2C_SUBTASK_TESTS,
                  codebase_analysis=codebase_analysis,
                  req_title=requirement.title,
                  task_title=subtask.title,
                  task_id=subtask.id,
                  implementation_guidance=impl
                )
                subtask["test"] = test

5. STAGE 3 - Save results:
   Create backup: copy requirements.json to requirements-backup-{timestamp}.json
   Write updated requirements.json
   Display summary
```

---

## Variable Substitutions

When using prompts, replace these variables:

| Variable | Source | Example |
|----------|--------|---------|
| `{repo_path}` | Git root directory | `/Users/admin/dev/hamm-therapy` |
| `{repo_name}` | Repository name | `hamm-therapy` |
| `{codebase_analysis}` | Output from Stage 1 | JSON object (see example above) |
| `{req_id}` | Requirement ID | `REQ-001` |
| `{req_title}` | Requirement title | `User Authentication System` |
| `{req_description}` | Requirement description | `Implement user login and session management` |
| `{task_id}` | Subtask ID | `TASK-001-001` |
| `{task_title}` | Subtask title | `Create login form` |
| `{task_description}` | Subtask description | `Build a form component for users...` |
| `{other_subtasks_list}` | List of other subtasks in requirement | `- TASK-001-002: Password validation\n- TASK-001-003: Session management` |
| `{implementation_guidance}` | Output from Stage 2B | Full implementation guidance text |

---

## Token Estimates

| Stage | Per Item | Total (14 req + 44 subtasks) |
|-------|----------|------|
| Stage 1 (Analysis) | - | ~500 tokens (run once) |
| Stage 2A (Req Test) | 150-200 tokens | 14 × 175 = 2,450 tokens |
| Stage 2B (Impl) | 150-200 tokens | 44 × 175 = 7,700 tokens |
| Stage 2C (Task Test) | 150-200 tokens | 44 × 175 = 7,700 tokens |
| **TOTAL** | | **~18,350 tokens** |

---

## Notes

- All prompts request output in structured format (JSON or Gherkin) for token efficiency
- Codebase analysis is reused for all requirements
- Keep implementation and test generation focused and concise
- Cross-references should use subtask IDs for clarity

