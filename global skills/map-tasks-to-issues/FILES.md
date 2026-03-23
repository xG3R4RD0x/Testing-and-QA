# Lista de Archivos del Skill map-tasks-to-issues

## 📁 Archivos Documentación

### SKILL.md (3.5 KB)
**Descripción**: Definición oficial del skill para OpenCode
**Contenido**:
- Nombre y descripción del skill
- Objetivo principal
- Parámetros de entrada/salida
- Características principales
- Uso básico
- Tecnología utilizada

**Para quién**: Integradores de OpenCode, administradores

---

### README.md (9.7 KB)
**Descripción**: Documentación técnica completa
**Contenido**:
- Descripción general
- Requisitos previos
- Estructura de entrada/salida
- Algoritmo de mapeo (detallado)
- Estadísticas y métricas
- Interpretación de resultados
- Solución de problemas
- Personalización
- Casos de uso

**Para quién**: Desarrolladores, usuarios técnicos

---

### INSTALL.md (4 KB)
**Descripción**: Guía de instalación rápida
**Contenido**:
- Instalación rápida
- Verificación de instalación
- Uso rápido (2 opciones)
- Archivos incluidos
- Requisitos
- Configuración
- Ejemplo de uso real
- Resultados esperados
- Solución de problemas

**Para quién**: Usuarios finales

---

### INDEX.md (3 KB)
**Descripción**: Estructura general del proyecto
**Contenido**:
- Descripción breve
- Objetivo principal
- Estructura de archivos
- Inicio rápido
- Características técnicas
- Capacidades
- Casos de uso
- Flujo de uso típico
- Información del skill

**Para quién**: Orientación general

---

### FILES.md
**Descripción**: Este archivo - lista de todos los archivos
**Contenido**: Descripción de cada archivo y su propósito

**Para quién**: Referencia de archivos

---

## 💻 Archivos de Código

### map_tasks_to_issues.py (15 KB) ✅ PRINCIPAL
**Lenguaje**: Python 3.7+
**Descripción**: Script principal ejecutable

**Funcionalidades principales**:
```python
class TaskIssueMapper:
  - __init__(repository_name)
  - validate_files()
  - load_json(file_path)
  - extract_tasks(requirements)
  - extract_issues(board_issues)
  - normalize_text(text)
  - calculate_similarity(text1, text2)
  - map_tasks_to_issues(tasks, issues)
  - calculate_stats(issues, mappings)
  - generate_csv(base_filename, mappings)
  - generate_summary(base_filename, stats)
  - run()
```

**Líneas clave**:
- Línea ~60: Diccionario de traducción alemán-inglés
- Línea ~95: Función de similitud (Jaccard + SequenceMatcher + Bigrams)
- Línea ~115: Umbral de mapeo (0.15)
- Línea ~200: Generación de CSV
- Línea ~250: Generación de resumen

**Flujo de ejecución**:
1. Validar archivos JSON existen
2. Cargar datos desde JSON
3. Extraer tasks y issues
4. Ejecutar mapeo semántico
5. Calcular estadísticas
6. Generar reportes (CSV + TXT)

---

### map_tasks_to_issues.exs (11 KB) - ALTERNATIVA ELIXIR
**Lenguaje**: Elixir
**Descripción**: Versión alternativa sin dependencias

**Estado**: Respaldo (la versión Python es la principal)

---

### map-tasks-to-issues (375 B) - WRAPPER BASH
**Lenguaje**: Bash
**Descripción**: Script wrapper ejecutable

**Contenido**:
```bash
#!/bin/bash
# Wrapper que ejecuta map_tasks_to_issues.py
python3 "$SCRIPT" "$@"
```

**Uso**: `/Users/admin/.agents/skills/map-tasks-to-issues/map-tasks-to-issues <repo>`

---

### install.sh (705 B) - SCRIPT DE INSTALACIÓN
**Lenguaje**: Bash
**Descripción**: Script de instalación y verificación

**Funciones**:
- Crear directorio del skill
- Hacer scripts ejecutables
- Mostrar archivos instalados
- Mostrar instrucciones de uso

**Uso**: `bash /Users/admin/.agents/skills/map-tasks-to-issues/install.sh`

---

## 📊 Archivos de Reporte Generados

### task-issue-mapping-{YYYY-MM-DD}.csv (7.6 KB ejemplo)
**Descripción**: Reporte completo de mapeos en formato CSV

**Estructura**:
```
Task ID,Task Title,Task Description,Requirement ID,Requirement Title,Issue #,Issue Title,Issue State,Similarity Score,Mapped
TASK-001-01,Erstellen...,Create...,REQ-001,Formulare...,338,Formular...,CLOSED,0.188,✓
...
```

**Filas**: Una por cada task (ej: 34 filas)
**Columnas**: 10 columnas

**Cómo abrirlo**:
- Excel: Abrir directamente
- Google Sheets: Importar como CSV
- Terminal: `cat task-issue-mapping-2026-03-20.csv`
- Python: `pandas.read_csv(...)`

---

### task-issue-mapping-{YYYY-MM-DD}-SUMMARY.txt (2.1 KB ejemplo)
**Descripción**: Resumen ejecutivo de estadísticas

**Contenido**:
```
ESTADÍSTICAS DE ISSUES
  Total: 17
  Cerrados: 10
  Abiertos: 7
  Tasa Completitud: 58.82%

ESTADÍSTICAS DE TASKS
  Total: 34
  Mapeados: 26
  Sin Mapeo: 8
  Cobertura: 76.47%

NOTAS IMPORTANTES
ARCHIVOS GENERADOS
Timestamp
```

**Cómo usarlo**:
- Compartir con stakeholders
- Incluir en reportes ejecutivos
- Monitorear cambios en el tiempo
- Base para dashboards

---

## 🗂️ Estructura Completa del Directorio

```
/Users/admin/.agents/skills/map-tasks-to-issues/
│
├─ 📄 DOCUMENTACIÓN
│  ├─ SKILL.md          (3.5 KB)  ← Definición del skill
│  ├─ README.md         (9.7 KB)  ← Documentación técnica
│  ├─ INSTALL.md        (4 KB)    ← Guía de instalación
│  ├─ INDEX.md          (3 KB)    ← Estructura general
│  ├─ FILES.md          (Este)    ← Lista de archivos
│  └─ FILES.md (copia)
│
├─ 💻 CÓDIGO EJECUTABLE
│  ├─ map_tasks_to_issues.py       (15 KB)  ✅ PRINCIPAL
│  ├─ map_tasks_to_issues.exs      (11 KB)  (respaldo Elixir)
│  ├─ map-tasks-to-issues          (375 B)  (wrapper)
│  ├─ map-tasks-to-issues.exs      (10 KB)  (alternativa)
│  └─ install.sh                   (705 B)  (instalación)
│
└─ 📊 REPORTES GENERADOS (en /Users/admin/dev/Reports/{repo}/)
   ├─ task-issue-mapping-2026-03-20.csv        (7.6 KB)
   └─ task-issue-mapping-2026-03-20-SUMMARY.txt (2.1 KB)
```

## 📈 Tamaños Totales

**Documentación**: ~24 KB
**Código**: ~26 KB
**Reportes por ejecución**: ~10 KB

## 🔄 Ciclo de Vida de Archivos

### Al instalar:
1. Se copian todos los archivos de documentación
2. Se copian todos los archivos de código
3. Se hacen ejecutables los scripts (.py, .sh, .exs)

### Al ejecutar:
1. Se leen requirements.json y board-issues.json
2. Se procesan en memoria
3. Se generan task-issue-mapping-*.csv y .txt en el mismo directorio que los JSON

### Al actualizar:
1. Se edita map_tasks_to_issues.py si es necesario
2. Se prueba con: `python3 map_tasks_to_issues.py <repo>`
3. Se verifica que los reportes se generen correctamente

## 🔐 Permisos de Archivos

```
Documentación (.md):     644 (rw-r--r--)
Scripts (.py, .sh):      755 (rwxr-xr-x)
```

## 📝 Cómo Actualizar Documentación

1. **SKILL.md**: Cambiar descripción general del skill
2. **README.md**: Agregar secciones técnicas, algoritmo, ejemplos
3. **INSTALL.md**: Cambiar instrucciones de instalación
4. **INDEX.md**: Actualizar referencias y estructura general

## 🎯 Roadmap de Archivos Futuros

Podrían agregarse:
- `config.yaml` - Configuración de parámetros
- `requirements.txt` - Dependencias Python (si las hubiera)
- `Makefile` - Automatización de tareas
- `tests/` - Suite de pruebas
- `examples/` - Ejemplos de uso
- `assets/` - Imágenes y diagrama

---

**Versión**: 1.0.0
**Fecha**: 2026-03-20
**Total archivos**: 12 (5 doc + 4 código + 3 respaldo)
**Tamaño total**: ~50 KB (sin reportes)
