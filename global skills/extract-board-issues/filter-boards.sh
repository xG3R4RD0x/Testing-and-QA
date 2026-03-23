#!/usr/bin/env bash
# Helper script to filter boards by repository name (case-insensitive)
# Arguments:
#   $1 = REPO_NAME (the repository name to filter by)
#   stdin = JSON array of boards from get-all-boards.sh
# Returns: JSON array of filtered boards

REPO_NAME="$1"

if [ -z "$REPO_NAME" ]; then
  cat
  exit 0
fi

# Convert repo name to lowercase for comparison
REPO_NAME_LOWER=$(echo "$REPO_NAME" | tr '[:upper:]' '[:lower:]')

# Filter boards that contain the repo name (case-insensitive)
jq --arg repo_lower "$REPO_NAME_LOWER" '
  map(
    .title as $title |
    if ($title | ascii_downcase | contains($repo_lower)) then
      .
    else
      empty
    end
  )
'
