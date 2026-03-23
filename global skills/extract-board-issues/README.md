# Extract Board Issues Skill - Guía de Uso

## Descripción General

Este skill extrae issues de GitHub Project Boards y los guarda en formato JSON estructurado. La versión mejorada detecta automáticamente el owner, obtiene todos los boards de la organización, filtra por nombre del repositorio y permite al usuario seleccionar cuál usar.

## Arquitectura

El skill está compuesto por varios scripts:

### Scripts Principales

1. **extract-board-issues.sh** (Original)
   - Versión completamente interactiva con `read`
   - Funciona en terminal local
   - Uso: `bash extract-board-issues.sh`

2. **extract-board-issues-main.sh** (OpenCode Compatible)
   - Versión que acepta el índice del board como argumento
   - Compatible con OpenCode
   - Detecta automáticamente el owner y filtra boards por nombre del repositorio
   - Uso: `bash extract-board-issues-main.sh [ÍNDICE]`
   - Ejemplo: `bash extract-board-issues-main.sh 1`

### Scripts Helper

3. **get-owner.sh**
   - Detecta automáticamente el owner del repositorio actual
   - Fallback: devuelve vacío si no se puede detectar
   - Salida: Login del owner o string vacío

4. **get-all-boards.sh**
   - Obtiene TODOS los boards de una organización
   - Parámetros: `$1=OWNER`
   - Salida: JSON con lista de todos los boards (id y title)

5. **filter-boards.sh**
   - Filtra boards por nombre del repositorio (case-insensitive)
   - Lee JSON desde stdin (array de boards)
   - Parámetros: `$1=REPO_NAME`
   - Salida: JSON con boards filtrados

6. **extract-issues.sh**
   - Extrae issues de un board específico
   - Parámetros: `$1=OWNER $2=REPO_NAME $3=BOARD_ID $4=BOARD_NAME`
   - Salida: Archivo JSON con issues

7. **list-boards.sh**
   - Lista los boards disponibles
   - Prepara datos para selección interactiva

## Flujo de Ejecución Mejorado

### Paso 1: Detección del Repositorio
- El script detecta automáticamente el repositorio actual
- Obtiene el nombre y owner del repositorio

### Paso 2: Detección del Owner
- Intenta detectar automáticamente el owner del repositorio
- Si falla, solicita al usuario que ingrese el owner manualmente

### Paso 3: Obtener Todos los Boards
- Obtiene TODOS los boards de la organización especificada
- No filtra por issues del repositorio

### Paso 4: Filtrar por Nombre del Repositorio
- Filtra los boards cuyo nombre contiene el nombre del repositorio
- La búsqueda es **case-insensitive**
- Si encuentra boards coincidentes, los muestra

### Paso 5: Fallback si No hay Coincidencias
- Si no hay boards que coincidan con el nombre del repositorio
- Muestra TODOS los boards disponibles en la organización
- Pregunta al usuario cuál board desea usar

### Paso 6: Presentación de Opciones
- **Si hay ≤5 boards**: Muestra los nombres de los boards como opciones
- **Si hay >5 boards**: Muestra la lista numerada en el chat y pide el número del board

## Cómo Usar en OpenCode

### Flujo Recomendado

1. El usuario ejecuta el skill desde OpenCode
2. OpenCode detecta automáticamente el owner
3. Se filtran los boards por nombre del repositorio
4. Si hay ≤5 boards coincidentes, se muestran como opciones
5. Si hay >5 boards o ninguno coincide, se muestra la lista numerada
6. El usuario selecciona un board
7. El script extrae los issues del board seleccionado
8. Se genera un archivo JSON con los datos

### Ejecución Manual

```bash
# Ver boards disponibles para el repositorio
bash extract-board-issues-main.sh

# Extraer issues del board 1
bash extract-board-issues-main.sh 1

# Extraer issues del board 2
bash extract-board-issues-main.sh 2
```

## Estructura de Salida

El JSON generado tiene la siguiente estructura:

```json
{
  "repository": "owner/repo-name",
  "board_name": "Board Name",
  "extracted_at": "2024-01-20T10:30:00Z",
  "total_issues": 17,
  "issues": [
    {
      "number": 342,
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

## Requisitos

- `gh` CLI configurado y autenticado
- Permisos para acceder al repositorio y sus boards
- `jq` instalado para procesar JSON

## Comportamiento

- **Detección automática del owner** con fallback manual
- **Búsqueda de todos los boards** de la organización
- **Filtrado inteligente** por nombre del repositorio (case-insensitive)
- **Fallback a lista completa** si no hay coincidencias
- **Interfaz adaptativa** (opciones si ≤5, lista numerada si >5)
- **Generación de JSON** con información completa de issues y comentarios
- **Timestamps** en formato ISO 8601 UTC

## Archivos Generados

Los archivos JSON se guardan en:
```
/Users/admin/dev/Reports/{nombre-repositorio}/board-issues-{YYYYMMDD-HHMMSS}.json
```

## Notas

- El skill busca boards en la **organización**, no solo en el repositorio
- El filtrado por nombre del repositorio es **case-insensitive**
- Si no hay boards coincidentes, muestra todos los boards disponibles
- El usuario puede seleccionar cualquier board de la organización
- El skill extrae todos los issues del board, incluyendo comentarios
