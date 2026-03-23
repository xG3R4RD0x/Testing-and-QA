#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Extract Board Issues Skill ===${NC}\n"

# Step 1: Detect current repository
echo -e "${YELLOW}[1/6] Detectando repositorio actual...${NC}"
REPO_URL=$(gh repo view --json url --jq '.url' 2>/dev/null) || {
  echo -e "${RED}Error: No estás en un repositorio git o gh cli no está configurado${NC}"
  exit 1
}

REPO_NAME=$(basename "$REPO_URL")
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null)
echo -e "${GREEN}✓ Repositorio detectado: ${REPO_OWNER}/${REPO_NAME}${NC}\n"

# Step 2: Get organization boards with issues from current repo
echo -e "${YELLOW}[2/6] Buscando boards de la organización...${NC}"

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

BOARDS_JSON=$(echo "$BOARDS_RESPONSE" | jq -r --arg repo_ref "$REPO_OWNER/$REPO_NAME" '
  .data.organization.projectsV2.nodes[] |
  select(.items.nodes[] |
    select(.content.repository.nameWithOwner == $repo_ref)
  ) |
  @json
' | jq -s '.')

BOARD_COUNT=$(echo "$BOARDS_JSON" | jq 'length')

if [ "$BOARD_COUNT" -eq 0 ]; then
  echo -e "${YELLOW}No se encontraron boards con issues de este repositorio${NC}\n"
  
  read -p "¿Deseas proceder con todos los issues del repositorio? (s/n): " -n 1 -r
  echo
  
  if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}Operación cancelada${NC}"
    exit 0
  fi
  
  USE_ALL_ISSUES=true
  SELECTED_BOARD_NAME="Todos los issues del repositorio"
else
  echo -e "${GREEN}✓ Se encontraron $BOARD_COUNT board(s)${NC}\n"
  
  # Display boards
  echo "$BOARDS_JSON" | jq -r '.[] | "\(.id)|\(.title)"' > /tmp/boards_list.tmp
  
  index=0
  while IFS='|' read -r board_id board_name; do
    ((index++))
    echo "  $index) $board_name"
  done < /tmp/boards_list.tmp
  
  echo ""
  read -p "Selecciona un número: " BOARD_INDEX
  
  if ! [[ "$BOARD_INDEX" =~ ^[0-9]+$ ]] || [ "$BOARD_INDEX" -lt 1 ] || [ "$BOARD_INDEX" -gt "$BOARD_COUNT" ]; then
    echo -e "${RED}Selección inválida${NC}"
    rm -f /tmp/boards_list.tmp
    exit 1
  fi
  
  SELECTED_BOARD_LINE=$(sed -n "${BOARD_INDEX}p" /tmp/boards_list.tmp)
  SELECTED_BOARD_ID=$(echo "$SELECTED_BOARD_LINE" | cut -d'|' -f1)
  SELECTED_BOARD_NAME=$(echo "$SELECTED_BOARD_LINE" | cut -d'|' -f2)
  
  rm -f /tmp/boards_list.tmp
  
  USE_ALL_ISSUES=false
fi

echo -e "${GREEN}✓ Seleccionado: $SELECTED_BOARD_NAME${NC}\n"

# Step 3: Extract issues from board or repository
echo -e "${YELLOW}[3/6] Extrayendo issues...${NC}"

if [ "$USE_ALL_ISSUES" = true ]; then
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
  ISSUES_JSON=$(gh api graphql -F boardId="$SELECTED_BOARD_ID" -f query='
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

echo -e "${GREEN}✓ Se encontraron $ISSUE_COUNT issue(s)${NC}\n"

# Step 4-5: Create output directory and build JSON
OUTPUT_DIR="/Users/admin/dev/Reports/$REPO_NAME"
mkdir -p "$OUTPUT_DIR"
echo -e "${YELLOW}[4/6] Creando estructura JSON...${NC}"

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

JSON_OUTPUT=$(echo "$ISSUES_ARRAY" | jq --arg repo "$REPO_OWNER/$REPO_NAME" --arg board "$SELECTED_BOARD_NAME" --arg timestamp "$TIMESTAMP" '
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

echo -e "${GREEN}✓ JSON estructurado correctamente${NC}\n"

# Step 6: Save JSON file
echo -e "${YELLOW}[5/6] Guardando archivo...${NC}"
OUTPUT_FILE="$OUTPUT_DIR/board-issues-$(date +%Y%m%d-%H%M%S).json"
echo "$JSON_OUTPUT" | jq '.' > "$OUTPUT_FILE"
echo -e "${GREEN}✓ Archivo guardado${NC}\n"

# Final summary
echo -e "${BLUE}=== Resumen ===${NC}"
echo -e "Repositorio: ${GREEN}$REPO_OWNER/$REPO_NAME${NC}"
echo -e "Origen: ${GREEN}$SELECTED_BOARD_NAME${NC}"
echo -e "Issues extraídos: ${GREEN}$ISSUE_COUNT${NC}"
echo -e "Archivo: ${GREEN}$OUTPUT_FILE${NC}\n"
echo -e "${GREEN}✓ Extracción completada${NC}"
