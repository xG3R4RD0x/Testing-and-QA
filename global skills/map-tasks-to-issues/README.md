# Skill: map-tasks-to-issues

## 📋 Descripción General

El skill `map-tasks-to-issues` mapea automáticamente **tasks** de un archivo `requirements.json` con **issues** de GitHub en `board-issues.json`, utilizando análisis semántico de similitud textual.

### Características Principales

✅ **Comparación Semántica**: Usa similitud de Jaccard para encontrar coincidencias entre tasks e issues
✅ **Multiidioma**: Soporta alemán e inglés en los textos
✅ **Generación de Reportes en Excel**: Crea archivos .xlsx con múltiples hojas y color-coding
✅ **Estadísticas Detalladas**: Calcula porcentajes de cobertura y completitud
✅ **Validación de Datos**: Detecta automáticamente archivos JSON requeridos

---

## 🚀 Uso

### Requisitos Previos

- Python 3.7 o superior
- Archivos JSON en el formato correcto
- Acceso a directorio `/Users/admin/dev/Reports/<repository>/`

### Ejecución Básica

```bash
# Desde cualquier directorio
python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py goetz-kundenportal-phoenix
```

### Parámetros

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `repository_name` | string | Nombre del repositorio | `goetz-kundenportal-phoenix` |

---

## 📂 Estructura de Archivos Esperados

### requirements.json

```json
{
  "repository_name": "goetz-kundenportal-phoenix",
  "main_requirements": [
    {
      "id": "REQ-001",
      "title": "Formulare von Konfiguration in DB verlagern",
      "description": "Move forms from configuration to database",
      "sub_tasks": [
        {
          "id": "TASK-001-01",
          "title": "Erstellen einer passenden Datenstruktur",
          "description": "Create appropriate database structure"
        }
      ]
    }
  ]
}
```

### board-issues.json

```json
{
  "repository": "num42/goetz-kundenportal-phoenix",
  "issues": [
    {
      "number": 342,
      "title": "permissions für drafts",
      "body": "Formulare mit Version NULL (draft)...",
      "state": "OPEN",
      "created_at": "2026-01-19T13:30:07Z",
      "updated_at": "2026-02-11T08:05:59Z"
    }
  ]
}
```

---

## 📊 Archivos de Salida

El skill genera los siguientes archivos en `/Users/admin/dev/Reports/{repository}/`:

### 1. task-issue-mapping-{YYYY-MM-DD}.xlsx

**Archivo Excel profesional con 3 hojas**:

#### Hoja 1: "Task-Issue Mappings"
- Mapeos detallados con color-coding:
  - **Verde (#D4EDDA)**: Tasks mapeados correctamente
  - **Rojo (#F8D7DA)**: Tasks sin mapeo
- Encabezados congelados para navegación fácil
- Columnas: Task ID, Task Title, Task Description, Requirement ID, Requirement Title, Issue #, Issue Title, Issue Body, Issue State, Similarity Score, Mapped

#### Hoja 2: "Summary"
- Estadísticas de Issues: Total, Cerrados, Abiertos, Tasa de Completitud
- Estadísticas de Tasks: Total, Mapeados, Sin Mapeo, Cobertura
- Información del algoritmo y fecha de generación

#### Hoja 3: "Unmapped Tasks"
- Lista de tasks sin mapeo para revisión manual
- Columnas: Task ID, Task Title, Task Description, Requirement ID, Requirement Title
- Fondo rojo para visibilidad

### 2. task-issue-mapping-{YYYY-MM-DD}-SUMMARY.txt

Archivo de resumen con estadísticas:

```
ESTADÍSTICAS DE ISSUES
├─ Total: 17
├─ Cerrados: 10
├─ Abiertos: 7
└─ Tasa Completitud: 58.82%

ESTADÍSTICAS DE TASKS
├─ Total: 34
├─ Mapeados: 26
├─ Sin Mapeo: 8
└─ Cobertura: 76.47%
```

---

## 🔧 Algoritmo de Mapeo

### Similitud Semántica Ponderada

El skill utiliza un sistema de puntuación híbrido que combina tres métricas:

**1. Jaccard Index (50% peso)**
```
Similitud = |Palabras en común| / |Total palabras únicas|
```
Excelente para detectar tareas relacionadas con vocabulario compartido.

**2. SequenceMatcher (30% peso)**
```
Ratio = 2 * |Caracteres coincidentes| / |Total caracteres|
```
Captura similitud directa de secuencias de caracteres.

**3. N-gramas (20% peso)**
Detecta substrings de 2 caracteres coincidentes, útil para palabras parecidas.

**Puntuación Final**:
```
Score = (Jaccard × 0.5) + (SequenceMatcher × 0.3) + (Bigrams × 0.2)
```

### Soporte Multiidioma

El algoritmo maneja automáticamente:
- ✅ Caracteres alemanes (ä, ö, ü, ß)
- ✅ Traducción de términos clave alemanes-inglés
- ✅ Nombres técnicos en ambos idiomas
- ✅ Variaciones de palabras

**Mapeo de Términos Clave**:
```
Alemán → Inglés
formulare → form
tabelle → table
bearbeiter → editor
version → version
draft/entwurf → draft
verwalten → manage
oberfläche → interface
benutzer → user
...y más
```

### Umbral de Mapeo

- **Score > 0.25**: Considerado "mapeado" (✓)
- **Score ≤ 0.25**: Sin mapeo (✗)

---

## 📈 Estadísticas Generadas

### Por Issues

- **Total de Issues**: Cantidad total de issues en el board
- **Issues Cerrados**: Conteo de issues con estado CLOSED
- **Issues Abiertos**: Conteo de issues con estado OPEN
- **Tasa de Completitud**: Porcentaje de issues cerrados

### Por Tasks

- **Total de Tasks**: Todos los sub-tasks de todos los requisitos
- **Tasks Mapeados**: Tasks que encontraron coincidencia con un issue
- **Tasks sin Mapeo**: Tasks que no tuvieron coincidencia
- **Cobertura de Mapeo**: Porcentaje de tasks mapeados

---

## 🎯 Interpretación de Resultados

### Similitud Alta (> 0.6)

La coincidencia es muy probable. Valida manualmente para confirmar.

```
Task: "Erstellen einer passenden Datenstruktur"
Issue: "Formular Tabellen und Views anlegen"
Score: 0.72 ✓ Alta confianza
```

### Similitud Media (0.3 - 0.6)

Posible coincidencia. Revisa cuidadosamente.

```
Task: "Database schema design"
Issue: "Create form tables"
Score: 0.45 ⚠️ Revisar manualmente
```

### Similitud Baja (< 0.3)

Probablemente no relacionado. Marca como no mapeado.

```
Task: "Fix typo in documentation"
Issue: "Add new payment method"
Score: 0.15 ✗ No relacionado
```

---

## 🐛 Solución de Problemas

### "No se encontraron los archivos necesarios"

**Causa**: Falta `requirements.json` o `board-issues.json`

**Solución**:
```bash
ls /Users/admin/dev/Reports/goetz-kundenportal-phoenix/*.json
```

Asegúrate de que existan ambos archivos con estos nombres exactos.

### CSV vacío

**Causa**: No hay tasks o issues en los archivos JSON

**Solución**: Verifica que los archivos JSON tengan la estructura correcta

### Excel no se genera

**Causa**: `openpyxl` no está instalado

**Solución**: 
```bash
pip3 install openpyxl
```

Si no puedes instalar openpyxl, el script automáticamente generará CSV como fallback.

### Mapeos incorrectos

**Causa**: El umbral de similitud (0.25) es muy bajo

**Solución**: Revisa manualmente las coincidencias. Considera cambiar el umbral en el código si necesario.

---

## 📝 Ejemplo Completo de Ejecución

```bash
$ python3 map_tasks_to_issues.py goetz-kundenportal-phoenix

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

📊 Generando reportes...

✨ Reportes generados:
   - task-issue-mapping-2026-03-20.xlsx
   - task-issue-mapping-2026-03-20-SUMMARY.txt

✅ ¡Proceso completado exitosamente!
```

---

## 🔄 Casos de Uso

### 1. Validar Cobertura de Requirements

Verifica qué tasks ya tienen un issue asociado en GitHub:

```bash
elixir map_tasks_to_issues.exs goetz-kundenportal-phoenix
# Revisa la columna "Mapped" en el CSV
```

### 2. Identificar Gaps de Implementación

Tasks sin mapeo = sin issue = posiblemente sin trabajo en progreso

### 3. Generar Reportes de Progreso

Usa "Tasa de Completitud" para informar progreso general del proyecto

### 4. Validar Alineación Requirements-Code

Asegúrate de que cada task tiene un issue correspondiente

---

## 🛠️ Personalización

### Cambiar el Umbral de Similitud

Edita `map_tasks_to_issues.py` línea ~115:

```python
'is_mapped': best_score > 0.15  # Cambiar 0.15 a otro valor
```

- Valores más altos (0.3, 0.4) = mapeos más conservadores
- Valores más bajos (0.1, 0.05) = mapeos más permisivos

### Ajustar Pesos de Similitud

Edita la función `calculate_similarity` línea ~95:

```python
# Actual (50% Jaccard, 30% SequenceMatcher, 20% Bigrams)
return (jaccard * 0.5) + (ratio * 0.3) + (bigram_sim * 0.2)

# Ejemplo: priorizar Jaccard (60%, 25%, 15%)
return (jaccard * 0.6) + (ratio * 0.25) + (bigram_sim * 0.15)
```

### Agregar/Modificar Términos de Traducción

Edita la función `normalize_text` línea ~60:

```python
replacements = {
    'neue_palabra_aleman': 'english_word',
    'otra_palabra': 'translation',
    # ...más términos
}
```

### Agregar Nuevos Campos al CSV

Modifica la función `generate_csv` línea ~200 para incluir columnas adicionales

---

## 📚 Referencias

- [Jaccard Index - Wikipedia](https://en.wikipedia.org/wiki/Jaccard_index)
- [Elixir String Module](https://hexdocs.pm/elixir/String.html)
- [Jason - JSON Parser](https://hexdocs.pm/jason/)

---

## 📄 Licencia

Parte de OpenCode Skills - Uso interno

---

## ✨ Mejoras Futuras

- [x] ✅ Generar archivos Excel (.xlsx) con formato profesional
- [ ] Interfaz web interactiva para revisar/ajustar mapeos
- [ ] Usar modelos NLP para similitud semántica mejorada
- [ ] Machine Learning para aprender de mapeos manuales
- [ ] Exportar a formatos adicionales (PDF, HTML)
- [ ] Integración con GitHub API para datos en tiempo real
- [ ] Cache de resultados para ejecutiones posteriores
- [ ] Análisis de tendencias de cobertura en el tiempo
- [ ] Alertas cuando cobertura cae por debajo de umbral
- [ ] Dashboard web para visualizar mapeos
