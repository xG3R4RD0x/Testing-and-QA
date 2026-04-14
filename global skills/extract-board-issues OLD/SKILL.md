---
name: extract-board-issues
description: Extrae issues de un GitHub Project Board y los guarda en un archivo JSON estructurado
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: issue-management
---

# Extract Board Issues Skill

Extrae issues de GitHub Project Boards y los guarda en un archivo JSON estructurado, con detección automática del owner, búsqueda de todos los boards de la organización, y filtrado inteligente por nombre del repositorio.

## Funcionalidad

Esta skill:
1. Detecta automáticamente el repositorio actual usando `gh cli`
2. Detecta automáticamente el owner de la organización (con fallback manual)
3. Obtiene TODOS los boards de la organización especificada
4. Filtra los boards por nombre del repositorio (case-insensitive)
5. Si hay coincidencias, muestra solo esos boards
6. Si no hay coincidencias, muestra TODOS los boards disponibles
7. El usuario selecciona el board deseado (opciones si ≤5, menú numérico si >5)
8. Extrae todos los issues con información completa: título, descripción y comentarios
9. Guarda los datos en un archivo JSON estructurado en `/Users/admin/dev/Reports/{nombre-repositorio}/`

## Estructura del JSON

```json
{
  "repository": "owner/repo-name",
  "board_name": "Board Name or Todos los issues del repositorio",
  "extracted_at": "2024-01-20T10:30:00Z",
  "total_issues": 42,
  "issues": [
    {
      "number": 123,
      "title": "Issue Title",
      "body": "Issue description...",
      "state": "OPEN",
      "created_at": "2024-01-20T10:00:00Z",
      "updated_at": "2024-01-20T10:30:00Z",
      "comments": [
        {
          "author": "username",
          "body": "Comment text...",
          "created_at": "2024-01-20T10:00:00Z"
        }
      ]
    }
  ]
}
```

## Comportamiento

### Flujo de Detección del Owner

- El script intenta detectar automáticamente el owner del repositorio actual
- Si falla, solicita al usuario que ingrese el owner manualmente
- El owner es necesario para obtener los boards de la organización

### Búsqueda y Filtrado de Boards

- El script obtiene **TODOS los boards** de la organización
- Filtra los boards cuyo nombre contiene el nombre del repositorio
- La búsqueda de filtrado es **case-insensitive**
- Si encuentra boards coincidentes, los muestra

### Fallback si No hay Coincidencias

- Si no hay boards que coincidan con el nombre del repositorio
- Muestra **TODOS los boards disponibles** en la organización
- El usuario puede seleccionar cualquier board de la lista

### Presentación al Usuario

- **Si hay ≤5 boards**: Muestra los nombres como opciones seleccionables
- **Si hay >5 boards**: Muestra lista numerada en el chat, pide número de selección

## Uso

Invoca esta skill cuando necesites extraer y estructurar issues de GitHub Project Boards con selección inteligente.

### Ejecución en OpenCode

El skill está diseñado para funcionar de forma interactiva en OpenCode:

1. El skill detecta automáticamente el repositorio y owner
2. Obtiene todos los boards de la organización
3. Filtra por nombre del repositorio
4. OpenCode presenta las opciones al usuario:
   - Si ≤5 boards: muestra opciones directas
   - Si >5 boards: muestra lista numerada
5. El usuario selecciona el board deseado
6. El skill extrae los issues y genera el JSON

### Ejecución Manual en Terminal

```bash
# Mostrar boards disponibles y opciones de selección
bash extract-board-issues-main.sh

# Extraer issues del board seleccionado (ej: board 1)
bash extract-board-issues-main.sh 1

# Extraer issues del board 3
bash extract-board-issues-main.sh 3
```

### Opción Interactiva Original

Para la versión completamente interactiva con `read`:

```bash
bash extract-board-issues.sh
```

## Scripts Incluidos

- **get-owner.sh**: Detecta automáticamente el owner
- **get-all-boards.sh**: Obtiene todos los boards de una organización
- **filter-boards.sh**: Filtra boards por nombre del repositorio (case-insensitive)
- **extract-issues.sh**: Extrae issues del board seleccionado
- **extract-board-issues-main.sh**: Orquestador principal
- **extract-board-issues.sh**: Versión interactiva original
