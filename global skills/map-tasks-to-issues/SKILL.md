---
name: map-tasks-to-issues
description: Mapea tasks de requirements con issues de GitHub usando similitud semántica y genera reportes en Excel
license: MIT
compatibility: opencode
metadata:
  audience: developers
  workflow: task-management
tags:
  - requirements
  - github
  - issues
  - mapping
  - excel
  - reporting
  - semantic-analysis
  - project-management
---

# map-tasks-to-issues

## Descripción

Este skill analiza tasks y issues de GitHub de 2 archivos JSON distintos y crea una tabla de reporte en Excel indicando qué issue de GitHub está asociado con qué task.

## Objetivo

Mapear automáticamente tasks de requirements.json con issues de board-issues.json usando comparación semántica (considerando mezcla de inglés y alemán), y generar un reporte profesional en Excel que muestre:

- Asociaciones entre tasks e issues con color coding (verde mappeado, rojo sin mapear)
- Status de cada issue
- Porcentaje de tareas completadas basado en el status
- Detalles de cada task e issue en columnas separadas
- Puntuaciones de similitud para validación manual
- Hoja resumen con estadísticas agregadas
- Hoja separada de tasks sin mapeo

## Características

✅ **Comparación Semántica Mejorada**:
- Usa Jaccard Index (50% peso)
- SequenceMatcher (30% peso)  
- N-gramas (20% peso)
- Traducción automática de términos alemanes-inglés

✅ **Soporte Multiidioma**:
- Maneja mezcla de alemán e inglés
- Mapea términos técnicos equivalentes
- Preserva significado semántico

✅ **Estadísticas Detalladas**:
- Tasa de completitud de issues (%)
- Cobertura de mapeo de tasks (%)
- Identificación de tasks sin mapeo

✅ **Reportes Profesionales en Excel**:
- Archivo Excel (.xlsx) con múltiples hojas
- Hoja "Task-Issue Mappings" con color-coding (verde=mappeado, rojo=sin mapear)
- Hoja "Summary" con estadísticas y métricas
- Hoja "Unmapped Tasks" con tasks sin asociación
- Encabezados congelados y ancho de columnas optimizado

## Parámetros de entrada

- `repository`: Nombre del repositorio (ej: `goetz-kundenportal-phoenix`)

## Archivos de entrada esperado

El skill busca automáticamente en `/Users/admin/dev/Reports/{repository}/`:
- `requirements.json` - Contiene los tasks de los requirements
- `board-issues.json` - Contiene los issues de GitHub del proyecto board

## Archivos de salida

Se generan en la misma ruta que los JSON:
1. `task-issue-mapping-{YYYY-MM-DD}.xlsx` - Reporte completo en Excel con 3 hojas:
   - "Task-Issue Mappings": Mapeos detallados con color-coding
   - "Summary": Estadísticas y métricas
   - "Unmapped Tasks": Tasks sin mapeo
2. `task-issue-mapping-{YYYY-MM-DD}-SUMMARY.txt` - Resumen de estadísticas en texto

## Algoritmo de Mapeo

**Similitud Semántica Ponderada**:
- **50%**: Jaccard Index (palabras comunes)
- **30%**: SequenceMatcher (similitud de secuencia)
- **20%**: N-gramas (substrings)

**Umbral de Mapeo**: 0.15 (15% similitud mínima)

## Uso

```bash
python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py <repository_name>

# Ejemplo
python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py goetz-kundenportal-phoenix
```

## Ejemplo de Output

```
🔍 Buscando archivos JSON en: /Users/admin/dev/Reports/goetz-kundenportal-phoenix

✅ Archivos encontrados:
   - requirements.json
   - board-issues.json

📋 Análisis de datos:
   - Tasks encontrados: 34
   - Issues encontrados: 17

🔗 Ejecutando mapeo semántico...

✅ Mapeo completado:
   - Tasks mapeados: 26/34
   - Cobertura: 76.47%
   - Issues cerrados: 10/17
   - Tasa de completitud: 58.82%

✨ Reportes generados:
   - task-issue-mapping-2026-03-20.xlsx
   - task-issue-mapping-2026-03-20-SUMMARY.txt
```

## Interpretación de Resultados

**Mapeos de Alta Confianza** (score > 0.3):
- Probable coincidencia correcta
- Validar si es necesario

**Mapeos de Media Confianza** (0.15 - 0.3):
- Posible coincidencia
- Revisar cuidadosamente

**Unmapped Tasks** (score < 0.15):
- Sin coincidencia encontrada
- Posiblemente nuevo trabajo no documentado en issues

## Requisitos Técnicos

- Python 3.7+
- `openpyxl` (instalable via `pip3 install openpyxl`) para reportes Excel
- Acceso a archivos JSON en `/Users/admin/dev/Reports/`
- Permisos de escritura en el directorio de reportes

## Tecnología

- **Lenguaje**: Python 3
- **Librerías principales**: 
  - `openpyxl` (Excel generation con styling)
  - `json`, `pathlib`, `difflib`, `re` (stdlib)
- **Entrada**: JSON files (requirements.json, board-issues.json)
- **Salida**: Excel (.xlsx) + TXT files
- **Fallback**: Si openpyxl no está instalado, genera CSV como fallback

