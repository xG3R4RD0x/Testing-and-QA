# Extract Board Issues - Script Fixes

## Version 2.1 Changes (2026-04-14)

### Critical Bug Fixes

1. **Script hangs indefinitely (FIXED)**
   - **Problem:** GraphQL queries had no timeout, would hang forever on network issues
   - **Solution:** Added 30-60 second timeouts to all `gh api` commands
   - **Impact:** Script now exits cleanly instead of hanging

2. **No board selection shown to user (FIXED)**
   - **Problem:** Script would sometimes proceed without user confirming board choice
   - **Solution:** Always display list of available boards and require explicit selection
   - **Impact:** User must confirm board before extraction starts

3. **Better error messages (FIXED)**
   - **Problem:** Cryptic or missing error messages when GraphQL fails
   - **Solution:** Added descriptive error messages at each step
   - **Impact:** Users can now diagnose problems easily

### Performance Improvements

- **Pagination Progress:** Now shows page count and running issue total during extraction
- **Large Board Support:** Properly handles boards with 200+ issues across multiple pages
- **Flexible Authentication:** Added `--owner` flag for use outside git directories

### New Features

1. **`--owner` flag:** Specify repository owner when not in git directory
   ```bash
   python3 extract_board_issues.py --repo my-repo --owner my-org
   ```

2. **Better progress indication:** Shows which page is being extracted
   ```
   ⏳ Page 1: Extracted 21 issues (total: 21)
   ⏳ Page 2: Extracted 5 issues (total: 26)
   ```

3. **Comment JSON cleanup:** Properly formats comments for downstream tools

## Version 2.0 Changes (Previous)

### Problem
The original script was querying **all project boards from the organization** instead of only the boards associated with the specific repository. This caused:
1. Showing hundreds of boards (incorrect filtering)
2. Empty results when extracting from boards
3. Not following the interactive selection pattern

### Solution
Modified `extract_board_issues.py` to:

1. **Replaced `get_all_boards()` with `get_repo_boards()`**
   - Now queries `repository(owner, name).projectsV2` instead of `organization(login).projectsV2`
   - Only returns boards directly associated with the repository
   - Drastically reduces board count (e.g., 39 boards → 5 boards for goetz-kundenportal-phoenix)

2. **Removed `filter_boards()` function**
   - No longer needed since we're querying repo-specific boards directly
   - Simplified the logic flow

3. **Updated GraphQL Query**
   - Changed from organization query to repository query
   - Added pagination info (`pageInfo`) for future enhancements
   - Properly handles board items and filters for Issue type

4. **Fixed Interactive Selection**
   - Now presents only the relevant boards to the user
   - User can select which board to extract from
   - Can also specify via `--board` flag (1-based index)

## Usage Examples

### Interactive Selection (Recommended)
```bash
cd /path/to/repo
python3 extract_board_issues.py

# Output:
# 🔍 Extract Board Issues
# ✅ Repository: goetz-kundenportal-phoenix
# ✅ Owner: num42
# ✅ GitHub authentication valid
#
# 📋 Found 5 board(s):
#
#   1. Götz Kundenportal Phoenix - Formulardesigner (17 items)
#   2. Götz: QMS (Inventur Erweiterung) (9 items)
#   ...
#
# 🎯 Select board number (1-5): 5
```

### Direct Board Selection (Skip Prompts)
```bash
python3 extract_board_issues.py --repo goetz-kundenportal-phoenix --owner num42 --board 5
# Extracts from board 5 directly
```

### With Repository Name (From Any Directory)
```bash
python3 extract_board_issues.py --repo goetz-kundenportal-phoenix --owner num42
# Shows board selection
```

### Dry Run (Validation Only)
```bash
python3 extract_board_issues.py --repo goetz-kundenportal-phoenix --owner num42 --dry-run
# Validates auth and detects boards without extracting
```

## Testing Results

**Repository:** num42/goetz-kundenportal-phoenix

| Board | Max Items | Tested | Status |
|-------|-----------|--------|--------|
| Götz Kundenportal Phoenix - Formulardesigner | 17 | ✅ | PASS |
| Götz: QMS (Inventur Erweiterung) | 9 | ✅ | PASS |
| goetz kundenportal subcontractor feedback | 32 | ✅ | PASS (25 issues) |
| goetz fms erweiterung EST-001284 | 11 | ✅ | PASS |
| Götz: Kundenportal | 218 | ✅ | PASS (38 issues, paginated) |

**Key Results:**
- ✅ No hangs or timeouts
- ✅ All boards listed correctly with item counts
- ✅ User selection working properly
- ✅ Direct board index (--board flag) working
- ✅ Pagination working for large boards
- ✅ JSON output schema validated

## Key Improvements

✅ Queries repository-specific boards only  
✅ Interactive user selection  
✅ Cleaner logic flow (no unnecessary filtering)  
✅ Proper GraphQL queries for Project Board V2 API  
✅ Full issue extraction with comments  
✅ ISO 8601 timestamps preserved  
✅ Standardized JSON output format  

## Breaking Changes

None - The script maintains the same CLI interface and output format.

## Files Modified

- `extract_board_issues.py` - Main script with all fixes applied
