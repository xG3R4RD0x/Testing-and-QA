#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Extract Board Issues Skill ===${NC}\n"

# Step 1: Detect current repository
echo -e "${YELLOW}[1/5] Detectando repositorio actual...${NC}"
REPO_URL=$(gh repo view --json url --jq '.url' 2>/dev/null) || {
  echo -e "${RED}Error: No estás en un repositorio git o gh cli no está configurado${NC}"
  exit 1
}

REPO_NAME=$(basename "$REPO_URL")
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null)
echo -e "${GREEN}✓ Repositorio detectado: ${REPO_OWNER}/${REPO_NAME}${NC}\n"

# Step 2: Get organization boards
echo -e "${YELLOW}[2/5] Buscando boards de la organización...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOARDS_JSON=$("$SCRIPT_DIR/get-boards.sh" "$REPO_OWNER" "$REPO_NAME")
BOARD_COUNT=$(echo "$BOARDS_JSON" | jq 'length')

if [ "$BOARD_COUNT" -eq 0 ]; then
  echo -e "${YELLOW}No se encontraron boards con issues de este repositorio${NC}\n"
  exit 0
fi

echo -e "${GREEN}✓ Se encontraron $BOARD_COUNT board(s)${NC}\n"

# Step 3: Display boards and prepare for selection
echo -e "${YELLOW}Boards disponibles:${NC}"

# Save boards to temporary file for reference
echo "$BOARDS_JSON" | jq -r '.[] | "\(.id)|\(.title)"' > /tmp/boards_list.tmp

index=0
declare -a board_options
while IFS='|' read -r board_id board_name; do
  ((index++))
  echo "  $index) $board_name"
  board_options+=("$board_name")
done < /tmp/boards_list.tmp

# For OpenCode interactive use, output information about boards
# The OpenCode user will need to use the question tool to select
cat > /tmp/opencode_boards_data.json <<EOF
{
  "repo_owner": "$REPO_OWNER",
  "repo_name": "$REPO_NAME",
  "boards_count": $BOARD_COUNT,
  "boards": $(cat /tmp/boards_list.tmp | while IFS='|' read -r board_id board_name; do
    echo "{\"id\": \"$board_id\", \"name\": \"$board_name\"}"
  done | jq -s '.')
}
EOF

echo
echo -e "${YELLOW}Data saved to:${NC} /tmp/opencode_boards_data.json"
echo -e "${YELLOW}Boards list:${NC} /tmp/boards_list.tmp"
echo
echo -e "${GREEN}Ready for selection${NC}"

# Keep the temp files for the next step
# They will be used by the extract step
