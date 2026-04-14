#!/usr/bin/env bash
# Main orchestrator for extract-board-issues skill
# This handles the interactive flow through OpenCode with improved owner detection and board filtering

BOARD_INDEX="${1:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Extract Board Issues Skill ===${NC}\n"

# Step 1: Detect repository
echo -e "${YELLOW}[1/6] Detectando repositorio actual...${NC}"
REPO_URL=$(gh repo view --json url --jq '.url' 2>/dev/null) || {
  echo -e "${RED}Error: No estás en un repositorio git o gh cli no está configurado${NC}"
  exit 1
}

REPO_NAME=$(basename "$REPO_URL")
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login' 2>/dev/null)
echo -e "${GREEN}✓ Repositorio detectado: ${REPO_OWNER}/${REPO_NAME}${NC}\n"

# Step 2: Detect or ask for owner
echo -e "${YELLOW}[2/6] Detectando owner...${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DETECTED_OWNER=$("$SCRIPT_DIR/get-owner.sh")

if [ -n "$DETECTED_OWNER" ]; then
  OWNER="$DETECTED_OWNER"
  echo -e "${GREEN}✓ Owner detectado: $OWNER${NC}\n"
else
  # Fallback: ask user for owner
  echo -e "${YELLOW}No se pudo detectar el owner automáticamente.${NC}"
  echo -e "${YELLOW}Por favor, ingresa el owner (organización):${NC}"
  read -p "> " OWNER
  
  if [ -z "$OWNER" ]; then
    echo -e "${RED}Error: Owner no proporcionado${NC}"
    exit 1
  fi
  echo -e "${GREEN}✓ Owner configurado: $OWNER${NC}\n"
fi

# Step 3: Get all boards
echo -e "${YELLOW}[3/6] Obteniendo todos los boards del owner...${NC}"

ALL_BOARDS=$("$SCRIPT_DIR/get-all-boards.sh" "$OWNER")
ALL_BOARDS_COUNT=$(echo "$ALL_BOARDS" | jq 'length')

if [ "$ALL_BOARDS_COUNT" -eq 0 ]; then
  echo -e "${RED}No se encontraron boards en la organización: $OWNER${NC}"
  exit 1
fi

echo -e "${GREEN}✓ Se encontraron $ALL_BOARDS_COUNT board(s) en la organización${NC}\n"

# Step 4: Filter boards by repository name
echo -e "${YELLOW}[4/6] Filtrando boards por nombre del repositorio...${NC}"

FILTERED_BOARDS=$(echo "$ALL_BOARDS" | "$SCRIPT_DIR/filter-boards.sh" "$REPO_NAME")
FILTERED_COUNT=$(echo "$FILTERED_BOARDS" | jq 'length')

if [ "$FILTERED_COUNT" -gt 0 ]; then
  echo -e "${GREEN}✓ Se encontraron $FILTERED_COUNT board(s) asociado(s) con el proyecto: $REPO_NAME${NC}\n"
  BOARDS_TO_USE="$FILTERED_BOARDS"
  BOARDS_COUNT="$FILTERED_COUNT"
else
  echo -e "${YELLOW}⚠ No se encontraron boards para el proyecto: $REPO_NAME${NC}"
  echo -e "${YELLOW}Se mostrarán todos los boards disponibles en la organización.${NC}\n"
  BOARDS_TO_USE="$ALL_BOARDS"
  BOARDS_COUNT="$ALL_BOARDS_COUNT"
fi

# Step 5: Display boards and get user selection
echo -e "${YELLOW}[5/6] Seleccionar board:${NC}\n"

# Save boards to temp file for processing
echo "$BOARDS_TO_USE" | jq -r '.[] | "\(.id)|\(.title)"' > /tmp/boards_list.tmp

index=0
declare -a board_ids
declare -a board_names

while IFS='|' read -r board_id board_name; do
  ((index++))
  board_ids[$((index-1))]="$board_id"
  board_names[$((index-1))]="$board_name"
  echo "  $index) $board_name"
done < /tmp/boards_list.tmp

echo ""

# Step 6: Handle selection
if [ -z "$BOARD_INDEX" ]; then
  if [ "$BOARDS_COUNT" -le 5 ]; then
    # If 5 or fewer boards, show as options (will be handled by OpenCode question component)
    echo -e "${YELLOW}Por favor selecciona un board de la lista anterior.${NC}"
  else
    # If more than 5 boards, ask for number input
    echo -e "${YELLOW}Por favor proporciona el número del board (1-$BOARDS_COUNT):${NC}"
  fi
  rm -f /tmp/boards_list.tmp
  exit 0
fi

# Validate selection
if ! [[ "$BOARD_INDEX" =~ ^[0-9]+$ ]] || [ "$BOARD_INDEX" -lt 1 ] || [ "$BOARD_INDEX" -gt "$BOARDS_COUNT" ]; then
  echo -e "${RED}Selección inválida. Por favor ingresa un número entre 1 y $BOARDS_COUNT${NC}"
  rm -f /tmp/boards_list.tmp
  exit 1
fi

# Get selected board
SELECTED_BOARD_ID="${board_ids[$((BOARD_INDEX-1))]}"
SELECTED_BOARD_NAME="${board_names[$((BOARD_INDEX-1))]}"

rm -f /tmp/boards_list.tmp

echo -e "${GREEN}✓ Board seleccionado: $SELECTED_BOARD_NAME${NC}\n"

# Step 6: Extract issues
echo -e "${YELLOW}[6/6] Extrayendo issues del board...${NC}\n"
"$SCRIPT_DIR/extract-issues.sh" "$OWNER" "$REPO_NAME" "$SELECTED_BOARD_ID" "$SELECTED_BOARD_NAME"
