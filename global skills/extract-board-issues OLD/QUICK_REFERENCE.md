# Extract Board Issues Skill - Quick Reference

## What Changed?

The skill now:
1. **Auto-detects owner** with manual fallback
2. **Gets ALL boards** from the organization
3. **Filters boards** by repository name (case-insensitive)
4. **Shows filtered results** or falls back to all boards
5. **Adapts UI** based on board count (≤5 = options, >5 = numbered list)

## Quick Start

```bash
# From your repository directory
cd /path/to/repo

# Run the skill
bash /Users/admin/.agents/skills/extract-board-issues/extract-board-issues-main.sh

# Follow the prompts - it auto-detects everything!
# If asked for owner, enter the organization name (e.g., "num42")

# Once you see the board list, select one:
bash /Users/admin/.agents/skills/extract-board-issues/extract-board-issues-main.sh 1
```

## New Scripts

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `get-owner.sh` | Detect owner | none | Owner name or empty |
| `get-all-boards.sh` | Get all boards | owner name | JSON array of boards |
| `filter-boards.sh` | Filter by repo name | JSON array + repo name | Filtered JSON array |

## Behavior Matrix

| Scenario | Filtered Boards Found | Fallback | UI Type |
|----------|----------------------|----------|---------|
| Exact matches | Yes | N/A | Options if ≤5, List if >5 |
| Partial matches | Yes | N/A | Options if ≤5, List if >5 |
| No matches | No | Show ALL boards | List (usually >5) |

## Example Scenarios

### Scenario 1: Perfect Match (≤5 boards)
```
Repo: "kundenportal-phoenix"
Filter: "kundenportal"
Result: 3 boards found
├── Götz Kundenportal Phoenix - Formulardesigner
├── Götz: Kundenportal
└── kundenportal test
→ Shows as OPTIONS for selection
```

### Scenario 2: No Direct Match (>5 boards)
```
Repo: "goetz-kundenportal-phoenix"
Filter: "goetz-kundenportal-phoenix"
Result: 0 boards found
→ Shows ALL 39 organization boards
→ User selects by number: 1-39
```

### Scenario 3: Partial Match (>5 boards)
```
Repo: "fms-portal"
Filter: "fms"
Result: 8 boards found
├── 1) FMS Erweiterung
├── 2) FMS System Update
├── 3) FMS Mobile App
├── ... (5 more)
→ Shows NUMBERED LIST
→ User enters number: 1-8
```

## Case-Insensitive Matching

✅ Works:
- Repo: `kundenportal` matches `Kundenportal Phoenix`, `KUNDENPORTAL`, `KundenPortal`
- Repo: `fms` matches `FMS System`, `fms app`, `FMS-Mobile`

❌ Doesn't work:
- Repo: `kundenportal` won't match `development`, `grpc-renderer`

## Troubleshooting

### Owner not detected
```bash
# Manually specify owner
cd /path/to/repo
bash extract-board-issues-main.sh
# Enter owner when prompted
```

### No boards showing
```bash
# Check if gh cli is installed and authenticated
gh auth status

# Verify owner has boards
gh project list --owner "my-org"
```

### Wrong board selected
```bash
# Re-run the script
bash extract-board-issues-main.sh
# Select different number
bash extract-board-issues-main.sh 3
```

## Files

```
/Users/admin/.agents/skills/extract-board-issues/
├── get-owner.sh                    (NEW)
├── get-all-boards.sh              (NEW)
├── filter-boards.sh               (NEW)
├── extract-board-issues-main.sh   (UPDATED)
├── extract-issues.sh
├── extract-board-issues.sh
├── get-boards.sh
├── list-boards.sh
├── README.md                      (UPDATED)
├── SKILL.md                       (UPDATED)
└── QUICK_REFERENCE.md             (THIS FILE)
```

## Output Location

```
/Users/admin/dev/Reports/{repository-name}/board-issues-{YYYYMMDD-HHMMSS}.json
```

## Tips

1. **First run**: Let it auto-detect owner
2. **See available boards**: Run without arguments
3. **Selected wrong board?**: Just run again with different number
4. **Need all boards?**: They're shown if no filtered matches
5. **Case doesn't matter**: "KUNDENPORTAL" works same as "kundenportal"

---

**Version**: 2.0  
**Updated**: March 23, 2026  
**Status**: ✅ Fully tested and operational
