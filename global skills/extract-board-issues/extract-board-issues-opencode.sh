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
  
  # This script cannot handle interactive input in OpenCode
  # Instead, we just inform the user and exit with information for manual invocation
  echo -e "${YELLOW}Para proceder de forma interactiva, ejecuta:${NC}"
  echo -e "${GREEN}bash $SCRIPT_DIR/extract-board-issues.sh${NC}"
  echo
  echo -e "${YELLOW}Opciones:${NC}"
  echo -e "  - Presiona 's' para extraer todos los issues del repositorio"
  echo -e "  - Presiona 'n' para cancelar"
  exit 0
fi

echo -e "${GREEN}✓ Se encontraron $BOARD_COUNT board(s)${NC}\n"

# Display boards
echo "$BOARDS_JSON" | jq -r '.[] | "\(.id)|\(.title)"' > /tmp/boards_list.tmp

echo -e "${YELLOW}Selecciona un board:${NC}"
index=0
while IFS='|' read -r board_id board_name; do
  ((index++))
  echo "  $index) $board_name"
done < /tmp/boards_list.tmp

# For OpenCode, we need to use an external mechanism to get user input
# Since this script is executed within OpenCode, we output the boards and exit
# The OpenCode orchestrator should use the 'question' tool to ask the user
# and then call this script again with the selection

echo
echo -e "${YELLOW}Este script necesita input interactivo que no está disponible en este contexto.${NC}"
echo -e "${YELLOW}Para usar la versión interactiva, ejecuta:${NC}"
echo -e "${GREEN}bash $SCRIPT_DIR/extract-board-issues.sh${NC}"

rm -f /tmp/boards_list.tmp
