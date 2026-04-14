#!/usr/bin/env bash
# Helper script to extract issues from a board or all repo issues
# Arguments:
#   $1 = REPO_OWNER
#   $2 = REPO_NAME
#   $3 = BOARD_ID (or "all" for all repo issues)

REPO_OWNER="$1"
REPO_NAME="$2"
BOARD_ID="$3"
BOARD_NAME="$4"

OUTPUT_DIR="/Users/admin/dev/Reports/$REPO_NAME"
mkdir -p "$OUTPUT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${YELLOW}Extrayendo issues...${NC}"

if [ "$BOARD_ID" = "all" ]; then
  # Get all issues from repository
  ISSUES_JSON=$(gh api graphql -F owner="$REPO_OWNER" -F name="$REPO_NAME" -f query='
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        issues(first: 100) {
          nodes {
            number
            title
            body
            state
            createdAt
            updatedAt
            comments(first: 20) {
              nodes {
                author { login }
                body
                createdAt
              }
            }
          }
        }
      }
    }
  ' 2>/dev/null)
  
  ISSUE_COUNT=$(echo "$ISSUES_JSON" | jq '.data.repository.issues.nodes | length')
  ISSUES_ARRAY=$(echo "$ISSUES_JSON" | jq '.data.repository.issues.nodes')
else
  # Get issues from selected board
  ISSUES_JSON=$(gh api graphql -F boardId="$BOARD_ID" -f query='
    query($boardId: ID!) {
      node(id: $boardId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              content {
                ... on Issue {
                  number
                  title
                  body
                  state
                  createdAt
                  updatedAt
                  comments(first: 20) {
                    nodes {
                      author { login }
                      body
                      createdAt
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  ' 2>/dev/null)
  
  ISSUE_COUNT=$(echo "$ISSUES_JSON" | jq '[.data.node.items.nodes[].content] | map(select(. != null)) | length')
  ISSUES_ARRAY=$(echo "$ISSUES_JSON" | jq '[.data.node.items.nodes[].content | select(. != null)]')
fi

echo -e "${GREEN}✓ Se encontraron $ISSUE_COUNT issue(s)${NC}"

# Build JSON structure
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

JSON_OUTPUT=$(echo "$ISSUES_ARRAY" | jq --arg repo "$REPO_OWNER/$REPO_NAME" --arg board "$BOARD_NAME" --arg timestamp "$TIMESTAMP" '
  {
    repository: $repo,
    board_name: $board,
    extracted_at: $timestamp,
    total_issues: length,
    issues: map({
      number: .number,
      title: .title,
      body: .body,
      state: .state,
      created_at: .createdAt,
      updated_at: .updatedAt,
      comments: [
        (.comments.nodes // [])[] | {
          author: .author.login,
          body: .body,
          created_at: .createdAt
        }
      ]
    })
  }
')

# Save JSON file
OUTPUT_FILE="$OUTPUT_DIR/board-issues-$(date +%Y%m%d-%H%M%S).json"
echo "$JSON_OUTPUT" | jq '.' > "$OUTPUT_FILE"

# Output summary
echo -e "${BLUE}=== Resumen ===${NC}"
echo -e "Repositorio: ${GREEN}$REPO_OWNER/$REPO_NAME${NC}"
echo -e "Origen: ${GREEN}$BOARD_NAME${NC}"
echo -e "Issues extraídos: ${GREEN}$ISSUE_COUNT${NC}"
echo -e "Archivo: ${GREEN}$OUTPUT_FILE${NC}"
echo -e "${GREEN}✓ Extracción completada${NC}"
