#!/usr/bin/env bash
# Script to detect or ask for the owner/organization
# Returns: OWNER name via stdout

# Try to detect owner from current repository
DETECTED_OWNER=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null)

if [ -n "$DETECTED_OWNER" ]; then
  echo "$DETECTED_OWNER"
else
  # If not in a repo or detection fails, this will be handled by the caller
  echo ""
fi
