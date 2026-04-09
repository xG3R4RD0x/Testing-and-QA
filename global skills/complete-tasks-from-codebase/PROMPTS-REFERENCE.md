# PROMPTS-REFERENCE.md

## Subagent Prompt Templates for Complete Tasks from Codebase

This document provides templates and guidance for how subagents should handle the universal payload and generate high-quality implementation and test content.

---

## System Prompt Template

Use this as the base system prompt for subagents:

```
You are an expert software engineer specializing in code implementation and test generation.

Your task is to analyze a requirement and its subtasks, then generate:
1. Detailed implementation steps tailored to the project's tech stack
2. Gherkin BDD test scenarios for each subtask

Input: You will receive a JSON payload with:
- Requirement details (id, title, description)
- List of subtasks to enrich
- Project information (name, root path)
- Detected technology stack (framework, language, ORM, test framework)
- Knowledge base summary (if available)
- Key code patterns from the project

Output: Return a JSON response with implementation and test content for each subtask.

Guidelines:
- Generate practical, executable step-by-step implementations
- Use framework conventions detected in the payload
- Reference patterns found in the codebase
- Create realistic Gherkin scenarios with 3+ scenarios per feature
- Tailor content to the specific tech stack
- Consider the knowledge base context when provided
- Keep implementation steps focused but comprehensive
```

---

## User Prompt Template

Create the user prompt dynamically from the payload:

```
Enrich the following requirement for the project "{project_name}":

# Requirement
ID: {requirement_id}
Title: {requirement_title}
Description: {requirement_description}

## Subtasks to Enrich
{subtask_list_formatted}

## Project Context
- Framework: {framework}
- Language: {language}
- ORM: {orm}
- Test Framework: {test_framework}

## Key Code Patterns
{key_patterns_formatted}

## Knowledge Base
{knowledge_base_summary_or_unavailable}

## Task
For EACH subtask, provide:

1. **implementation**: A detailed markdown guide with:
   - Overview (what needs to be built)
   - Implementation Steps (5-8 numbered steps)
   - Key files to create/modify
   - Code patterns to follow
   - References to related subtasks

2. **test**: Gherkin BDD scenarios with:
   - Happy path (main success scenario)
   - Validation/error handling
   - Edge cases or boundary conditions

Return as JSON with structure:
{
  "requirement_id": "{requirement_id}",
  "status": "success",
  "subtasks": [
    {
      "id": "{task_id}",
      "implementation": "...",
      "test": "..."
    }
  ]
}
```

---

## Example: Phoenix Elixir Project

### System Prompt

```
You are an expert Elixir/Phoenix developer.

Your task: Analyze requirements and generate implementation steps and tests
tailored to Phoenix v1.8, Ecto ORM, and ExUnit testing framework.

Consider:
- LiveView components and events
- Ecto schemas and migrations
- Context layer patterns
- Testing with ExUnit
- Phoenix v1.8 best practices

Output: JSON with implementation (markdown) and test (Gherkin) content.
```

### User Prompt Example

```
Enrich the following requirement for the project "goetz-kundenportal-phoenix":

# Requirement
ID: REQ-001
Title: Migrate Forms from Configuration to Database
Description: Move form configuration management from static configuration to 
database storage with proper data structure and seeding of existing forms

## Subtasks to Enrich
1. TASK-001-01: Create appropriate data structure
   Description: Design and implement the database schema for storing forms with 
   proper relationships and constraints

2. TASK-001-02: Seed existing forms into database
   Description: Migrate all existing forms from configuration files into the 
   new database structure

3. TASK-001-03: Implement FormularID as UUID reference
   Description: Create reference table with FormularID as UUID to maintain 
   relationships without storing actual form content

## Project Context
- Framework: Phoenix v1.8
- Language: Elixir
- ORM: Ecto
- Test Framework: ExUnit

## Key Code Patterns
- migration_structure: lib/my_app/repo/migrations/
- schema_structure: lib/my_app/schemas/
- context_structure: lib/my_app/
- liveview_structure: lib/my_app_web/live/
- test_structure: test/

## Knowledge Base Available
Files found:
- ARCHITECTURE.md: Details project structure
- PATTERNS.md: Coding conventions
- TECH-STACK.md: Dependency versions

Knowledge Base Summary:
# Project Architecture
Phoenix v1.8 web application for form management. Forms are managed 
through database with versioning support...

# Key Patterns
- Always use Contexts for domain logic
- Schemas should validate data
- Tests use ExUnit factories
```

---

## Expected Response Format

Subagents should return JSON in this format:

```json
{
  "requirement_id": "REQ-001",
  "status": "success",
  "subtasks": [
    {
      "id": "TASK-001-01",
      "implementation": "## Overview\nCreate database schema for storing form definitions...\n\n## Implementation Steps\n1. Create migration file\n2. Define schema...",
      "test": "Feature: Create appropriate data structure\n\n  Scenario: Successfully create form schema\n    Given a new database\n    When migration runs\n    Then form table exists with required columns\n\n  Scenario: Validate schema constraints\n    Given existing form record\n    When invalid data inserted\n    Then database constraint prevents insertion"
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

## Implementation Content Guidelines

### Structure

```markdown
## Overview
Brief description of what needs to be implemented (1-2 sentences)

## Key Files
- Path to file 1 (create/modify)
- Path to file 2 (create/modify)

## Implementation Steps
1. Create migration file: 
   `priv/repo/migrations/{timestamp}_create_forms.exs`
   
2. Define schema in `lib/my_app/schemas/form.ex`:
   [code example or pattern reference]

3. Add context functions in `lib/my_app/forms.ex`:
   [code example or pattern reference]

4. Create tests...

5. Add LiveView integration...

## Key Considerations
- Use Ecto changesets for validation
- Consider performance implications
- Reference related tasks: TASK-001-02, TASK-001-03

## Testing Approach
- Use ExUnit for unit tests
- Mock external dependencies
- Test both happy path and edge cases
```

### For Phoenix Specifically

```
## Key Files
- lib/my_app/repo/migrations/{timestamp}_migration_name.exs
- lib/my_app/schemas/form.ex
- lib/my_app/forms.ex (context module)
- test/my_app/schemas/form_test.exs
- test/my_app/forms_test.exs

## Implementation Steps
1. Create Ecto migration
   - Add columns with appropriate types
   - Add constraints and indexes
   - Consider data types (use :uuid for ids)

2. Define Ecto schema
   - Use embedded_schema if appropriate
   - Add validations in changeset
   - Consider relationships

3. Implement context functions
   - CRUD operations
   - Query functions with preloads
   - Business logic

4. Write comprehensive tests
   - Test schema validations
   - Test context functions
   - Test error conditions

5. Integration with LiveView
   - Update list/show/edit views
   - Handle form changes
   - Update broadcasts if needed
```

---

## Test Content Guidelines

### Gherkin Best Practices

```gherkin
Feature: Requirement Title

  Scenario: Happy path - successful scenario name
    Given precondition 1
    And precondition 2
    When action is performed
    Then expected outcome
    And another verification

  Scenario: Error handling - specific error case
    Given state that triggers error
    When invalid action attempted
    Then appropriate error response returned
    And state remains unchanged

  Scenario: Edge case - boundary condition
    Given edge case condition
    When boundary action performed
    Then system handles gracefully
```

### For Phoenix/Ecto

```gherkin
Feature: Create appropriate data structure

  Scenario: Successfully create form with all fields
    Given a new form schema
    When valid form attributes provided
    Then form record created in database
    And form has UUID id
    And timestamps set correctly

  Scenario: Validate required fields
    Given form schema validation rules
    When required field is missing
    Then changeset has errors
    And record not persisted

  Scenario: Handle concurrent form creation
    Given multiple concurrent requests
    When forms created simultaneously
    Then all forms have unique IDs
    And database constraints prevent duplicates
```

---

## Payload Field References

When generating content, reference these from the payload:

```python
# From codebase_analysis.detected_stack
framework = payload["codebase_analysis"]["detected_stack"]["framework"]
language = payload["codebase_analysis"]["detected_stack"]["language"]
orm = payload["codebase_analysis"]["detected_stack"]["orm"]
test_framework = payload["codebase_analysis"]["detected_stack"]["test_framework"]

# From codebase_analysis.key_patterns
patterns = payload["codebase_analysis"]["key_patterns"]
# Example: patterns["liveview_structure"] = "lib/*_web/live/"

# From knowledge_base
kb_available = payload["knowledge_base"]["available"]
kb_summary = payload["knowledge_base"]["summary"]

# From requirement
req_id = payload["requirement"]["id"]
req_title = payload["requirement"]["title"]
req_description = payload["requirement"]["description"]

# From subtasks
subtasks = payload["subtasks"]  # List of {id, title, description}
```

---

## Error Handling in Responses

If generation fails, return:

```json
{
  "requirement_id": "REQ-001",
  "status": "error",
  "error": "Detailed error message",
  "skipped": true
}
```

The orchestrator will:
- Log the error
- Mark requirement as failed
- Continue with next requirement

---

## Tips for High-Quality Output

1. **Match Framework Conventions**
   - Reference detected framework
   - Use framework-specific patterns
   - Follow framework best practices

2. **Use Knowledge Base**
   - Incorporate KB patterns when available
   - Reference KB conventions
   - Adapt to documented standards

3. **Practical Implementation Steps**
   - Number each step clearly
   - Include file paths
   - Reference key code patterns
   - Consider dependencies between tasks

4. **Comprehensive Test Scenarios**
   - Happy path (main success case)
   - Error handling (validation, constraints)
   - Edge cases (boundaries, concurrency)
   - At least 3 scenarios per feature

5. **Reference Related Tasks**
   - Note dependencies between subtasks
   - Reference related TASK IDs
   - Suggest implementation order

---

## Testing Your Subagent

1. Extract payload from orchestrator output
2. Test with different tech stacks
3. Verify output structure matches expected format
4. Check that implementation steps are practical
5. Validate Gherkin syntax in test scenarios

---

**Last Updated:** 2026-04-09  
**Version:** 2.0.0
