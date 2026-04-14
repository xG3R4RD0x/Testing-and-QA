#!/usr/bin/env bash
# Helper script to get organization boards with repo issues
# Used by the interactive extract-board-issues wrapper

REPO_OWNER="$1"
REPO_NAME="$2"

GRAPHQL_QUERY='
  query($org: String!) {
    organization(login: $org) {
      projectsV2(first: 50) {
        nodes {
          id
          title
          items(first: 1) {
            nodes {
              content {
                ... on Issue {
                  repository {
                    nameWithOwner
                  }
                }
              }
            }
          }
        }
      }
    }
  }
'

BOARDS_RESPONSE=$(gh api graphql -F org="$REPO_OWNER" -f query="$GRAPHQL_QUERY" 2>/dev/null)

# Filter boards that have at least one issue from the current repo
echo "$BOARDS_RESPONSE" | jq -r --arg repo_ref "$REPO_OWNER/$REPO_NAME" '
  .data.organization.projectsV2.nodes[] |
  select(.items.nodes[] |
    select(.content.repository.nameWithOwner == $repo_ref)
  ) |
  @json
' | jq -s '.'
