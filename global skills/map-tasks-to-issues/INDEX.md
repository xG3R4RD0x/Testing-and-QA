# Skill: map-tasks-to-issues

## 📍 Ubicación
```
/Users/admin/.agents/skills/map-tasks-to-issues/
```

## 📋 Descripción Breve

Mapea automáticamente **tasks** de requirements.json con **issues** de GitHub (board-issues.json) usando análisis semántico multiidioma (alemán-inglés). Genera reportes en CSV y texto.

## 🎯 Objetivo Principal

- Validar cobertura: ¿cada task tiene un issue asociado?
- Identificar gaps de implementación
- Generar reportes de progreso basados en status de issues
- Apoyar decisiones de priorización

## 📁 Estructura de Archivos

### Documentación
| Archivo | Descripción |
|---------|-------------|
| **SKILL.md** | Definición técnica del skill para OpenCode |
| **README.md** | Documentación completa y detallada (9.7 KB) |
| **INSTALL.md** | Guía de instalación y configuración rápida |
| **INDEX.md** | Este archivo - estructura general |

### Código
| Archivo | Lenguaje | Descripción | Estado |
|---------|----------|-------------|--------|
| **map_tasks_to_issues.py** | Python 3 | Implementación principal ✅ | Activo |
| map_tasks_to_issues.exs | Elixir | Alternativa (sin dependencias) | Respaldo |
| map-tasks-to-issues.exs | Elixir | Versión anterior | Respaldo |
| map-tasks-to-issues | Bash | Wrapper ejecutable | Respaldo |
| install.sh | Bash | Script de instalación | Respaldo |

### Reportes Generados (Ejemplos)
```
/Users/admin/dev/Reports/goetz-kundenportal-phoenix/
├── task-issue-mapping-2026-03-20.csv          (7.6 KB)
└── task-issue-mapping-2026-03-20-SUMMARY.txt  (2.1 KB)
```

## 🚀 Inicio Rápido

```bash
# Ejecutar el mapeo
python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py goetz-kundenportal-phoenix

# Resultado esperado:
# ✨ Genera: task-issue-mapping-2026-03-20.csv
#            task-issue-mapping-2026-03-20-SUMMARY.txt
```

## 🔧 Características Técnicas

| Característica | Detalles |
|---|---|
| **Lenguaje** | Python 3.7+ |
| **Algoritmo** | Similitud semántica ponderada (Jaccard 50%, SequenceMatcher 30%, Bigrams 20%) |
| **Multiidioma** | Alemán ↔ Inglés con traducción automática |
| **Entrada** | 2 archivos JSON (requirements.json, board-issues.json) |
| **Salida** | CSV + resumen de texto |
| **Tiempo ejecución** | < 1 segundo |
| **Dependencias** | Ninguna (solo stdlib Python) |

## 📊 Estadísticas de Ejemplo

```
Último reporte (2026-03-20):
├─ Tasks totales: 34
├─ Tasks mapeados: 26 (76.47%)
├─ Issues totales: 17
├─ Issues cerrados: 10 (58.82%)
└─ Cobertura general: 76.47%
```

## 📖 Documentación

1. **Para entender el skill**: Lee `SKILL.md` (resumen ejecutivo)
2. **Para usarlo**: Consulta `INSTALL.md` (guía rápida)
3. **Para profundizar**: Lee `README.md` (documentación completa)
4. **Para modificarlo**: Edita `map_tasks_to_issues.py` y revisa las secciones personalizables

## 🎓 Archivos por Audiencia

### Usuarios
→ `INSTALL.md` - Instalación y uso básico

### Desarrolladores
→ `README.md` - Arquitectura, algoritmo, personalización

### Administradores/Integradores
→ `SKILL.md` - Especificación técnica

## ✨ Capacidades

✅ Mapeo automático con similitud semántica
✅ Soporte multiidioma (alemán + inglés)
✅ Generación de reportes profesionales
✅ Estadísticas de cobertura
✅ Sin dependencias externas
✅ Ejecución rápida (< 1 segundo)
✅ Salida en formatos estándar (CSV, TXT)

## 🎯 Casos de Uso

1. **Validar Requisitos**: ¿Todos los requirements tienen un issue en GitHub?
2. **Reportar Progreso**: ¿Cuántos requirements están completados?
3. **Identificar Gaps**: ¿Qué tasks no tienen issue asignado?
4. **Seguimiento**: Ejecutar regularmente para monitorear cobertura
5. **Decisiones**: Priorizar work items según status de issues

## 🔄 Flujo de Uso Típico

```
1. Extraer Requirements (PDF → requirements.json)
   ↓
2. Extraer Issues de GitHub (board-issues.json)
   ↓
3. Ejecutar map-tasks-to-issues
   ↓
4. Revisar reports:
   - task-issue-mapping-{date}.csv
   - task-issue-mapping-{date}-SUMMARY.txt
   ↓
5. Analizar resultados:
   - Cobertura de mapeo
   - Tasa de completitud
   - Tasks sin mapeo
```

## 📌 Información del Skill

- **Nombre**: map-tasks-to-issues
- **Versión**: 1.0.0
- **Tipo**: Data Analysis & Reporting
- **Lenguaje Primario**: Python 3
- **Última Actualización**: 2026-03-20
- **Mantenedor**: OpenCode Skills

## 🔗 Referencias Relacionadas

- Requisitos: `/Users/admin/dev/Reports/goetz-kundenportal-phoenix/requirements.json`
- Issues: `/Users/admin/dev/Reports/goetz-kundenportal-phoenix/board-issues.json`
- Reportes: `/Users/admin/dev/Reports/goetz-kundenportal-phoenix/task-issue-mapping-*.{csv,txt}`

## 📞 Soporte

Para preguntas o mejoras:
1. Consulta `README.md` (sección Solución de Problemas)
2. Revisa los comentarios en `map_tasks_to_issues.py`
3. Ejecuta con `--help` para más información (función planning)

---

**Status**: ✅ Completado y funcional
**Testado con**: goetz-kundenportal-phoenix (34 tasks, 17 issues)
**Resultado**: 76.47% cobertura de mapeo
