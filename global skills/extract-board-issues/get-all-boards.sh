#!/usr/bin/env bash
# Helper script to get ALL organization boards
# Arguments:
#   $1 = OWNER (organization login)
# Returns: JSON array of all boards with id and title

OWNER="$1"

if [ -z "$OWNER" ]; then
  echo "[]"
  exit 0
fi

GRAPHQL_QUERY='
  query($org: String!) {
    organization(login: $org) {
      projectsV2(first: 100) {
        nodes {
          id
          title
        }
      }
    }
  }
'

RESPONSE=$(gh api graphql -F org="$OWNER" -f query="$GRAPHQL_QUERY" 2>/dev/null)

# Extract and return the boards array
echo "$RESPONSE" | jq '.data.organization.projectsV2.nodes' 2>/dev/null || echo "[]"
