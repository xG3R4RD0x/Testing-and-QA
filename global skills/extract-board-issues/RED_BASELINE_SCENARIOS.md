# RED Phase: Baseline Test Scenarios

This document captures baseline behaviors BEFORE the improved skill exists. These scenarios establish what needs to be fixed.

## Scenario 1: Unclear Triggering Conditions

**Setup:** Agent receives vague request without clear context about what extract-board-issues is for.

**Request:** "I need to get some issues from GitHub and organize them."

**Baseline Behavior (Expected to Fail):**
- Agent confuses PROJECT BOARDS with REPOSITORY ISSUES
- Agent defaults to `gh issue list` or `gh api` without understanding board context
- Agent doesn't recognize when this skill is appropriate vs other tools

**Rationalization Captured:**
- "I'll just use `gh issue list` to get all issues"
- "The map-tasks-to-issues tool could handle this"
- "I'm not sure if I need a special tool for this"

**What Fixes This:** Clear description with "Use when..." trigger conditions specific to PROJECT BOARDS

---

## Scenario 2: Tool Confusion (extract-board-issues vs extract-requirements vs map-tasks-to-issues)

**Setup:** Agent needs to analyze board issues but doesn't understand where each tool fits in the workflow.

**Request:** "Extract GitHub board issues and map them to our requirements."

**Baseline Behavior (Expected to Fail):**
- Agent tries to do BOTH operations in one step
- Agent confuses which tool produces WHICH output
- Agent misunderstands data flow: PDF → requirements → board issues → mapping
- Agent attempts to use extract-requirements on board issues (wrong input source)

**Rationalizations Captured:**
- "These tools all extract data, so they're interchangeable"
- "I can use extract-requirements to get the board data"
- "I'll skip one step and just do the mapping directly"
- "The input/output formats don't matter as much as the data"

**What Fixes This:** Integration section showing exact workflow chain with clear role of each tool

---

## Scenario 3: Authentication & Prerequisite Failures

**Setup:** Script should validate environment but agent assumes everything is set up.

**Request:** "Extract board issues" (but `gh` not authenticated or board access denied)

**Baseline Behavior (Expected to Fail):**
- Agent runs extraction without checking auth status first
- Script fails silently or with cryptic error
- Agent doesn't validate prerequisites before running extraction
- Agent assumes board is accessible without checking permissions

**Rationalizations Captured:**
- "GitHub auth is probably already configured"
- "I don't need to check if the board exists first"
- "If it fails, I can debug it then"
- "Permission errors are GitHub's problem, not mine"

**What Fixes This:**
- Script validates auth upfront with `gh auth status`
- Script validates board access with preview query
- Clear error messages explaining what's wrong

---

## Scenario 4: Output Validation & Schema Compliance

**Setup:** Agent generates JSON but doesn't validate it matches expected downstream schema.

**Request:** "Extract board issues so we can map them with map-tasks-to-issues"

**Baseline Behavior (Expected to Fail):**
- JSON doesn't match schema expected by map-tasks-to-issues
- Missing fields (timestamps, state, etc.)
- Incorrect data types (timestamps as strings vs ISO 8601)
- Comments structure doesn't match spec
- Board metadata incomplete or missing

**Rationalizations Captured:**
- "The JSON format doesn't matter, map-tasks-to-issues will figure it out"
- "I can fix the format manually if needed"
- "Timestamps don't need to be ISO 8601, any format works"
- "I'll skip optional fields to save time"

**What Fixes This:**
- Script validates JSON schema before saving
- Clear documentation of EXACT output format required
- Examples showing correct vs incorrect formats
- Downstream validation (map-tasks-to-issues must accept output)

---

## Scenario 5: Board Selection Complexity

**Setup:** Organization has many boards; agent needs to select the right one.

**Request:** "Extract issues from our project board"

**Baseline Behavior (Expected to Fail):**
- Agent doesn't understand how to find/select correct board
- Agent assumes there's only one board or a "main" board
- Agent selects wrong board due to ambiguous naming
- Agent doesn't validate board has the issues they expect

**Rationalizations Captured:**
- "I'll just grab the first board in the list"
- "The board names are clear, so I'll guess which one is right"
- "I can always re-run if I pick the wrong board"
- "There's probably only one board anyway"

**What Fixes This:**
- Clear board filtering logic (by repo name)
- UX that shows multiple options clearly
- Confirmation before extraction
- Validation that selected board has issues

---

## Summary of Rationalizations to Address in SKILL.md

| Rationalization | Tool/Section to Fix |
|---|---|
| "Tools are interchangeable" | Integration section + When NOT to use |
| "I don't need to check auth first" | Prerequisites section + Script validation |
| "Output format doesn't matter" | Output Format section + Examples |
| "I'll just use gh issue list" | When to Use + Quick Reference |
| "I can guess which board" | Board Selection section + UX guidance |
| "Timestamps can be any format" | Output Format + Schema examples |
| "I'll fix problems manually later" | Red Flags section |

---

## CSO Keywords to Integrate

Based on baseline scenarios, these keywords should appear in SKILL.md for discoverability:

- "GitHub Project Board"
- "board-issues.json"
- "extract board"
- "extract issues"
- "board extraction"
- "project board extraction"
- "GraphQL issues"
- "gh api"
- "board selection"
- "issue comments"
- "workflow integration"

