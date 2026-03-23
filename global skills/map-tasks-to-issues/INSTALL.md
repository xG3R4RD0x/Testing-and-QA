# Instalación y Configuración del Skill map-tasks-to-issues

## 📦 Instalación Rápida

El skill ya está instalado en:
```
/Users/admin/.agents/skills/map-tasks-to-issues/
```

## ✅ Verificar Instalación

```bash
python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py --help
```

## 🚀 Uso Rápido

### Opción 1: Usar Python directamente
```bash
python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py goetz-kundenportal-phoenix
```

### Opción 2: Usar el wrapper script (si lo deseas)
```bash
/Users/admin/.agents/skills/map-tasks-to-issues/map-tasks-to-issues goetz-kundenportal-phoenix
```

## 📁 Archivos Incluidos

```
/Users/admin/.agents/skills/map-tasks-to-issues/
├── README.md                    # Documentación completa
├── SKILL.md                     # Descripción del skill
├── INSTALL.md                   # Este archivo
├── map_tasks_to_issues.py       # Script principal (Python)
├── map_tasks_to_issues.exs      # Versión alternativa (Elixir)
├── map-tasks-to-issues          # Wrapper ejecutable
├── map-tasks-to-issues.exs      # Version anterior (Elixir)
└── install.sh                   # Script de instalación
```

## 📋 Requisitos

- **Python 3.7+** (recomendado 3.8+)
- Archivos JSON en formato correcto:
  - `requirements.json`
  - `board-issues.json`

## 🔧 Configuración

No se requiere configuración adicional. El script:
1. Busca los archivos JSON automáticamente
2. Detecta el repositorio por su nombre
3. Genera reportes en la misma ruta que los JSONs

## 📊 Ejemplo de Uso Real

```bash
# Mapear tasks a issues para el repositorio goetz-kundenportal-phoenix
$ python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py goetz-kundenportal-phoenix

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
   - task-issue-mapping-2026-03-20.csv
   - task-issue-mapping-2026-03-20-SUMMARY.txt

✅ ¡Proceso completado exitosamente!
```

## 🎯 Resultados

Los reportes se generan en:
```
/Users/admin/dev/Reports/{repository}/
├── task-issue-mapping-2026-03-20.csv
└── task-issue-mapping-2026-03-20-SUMMARY.txt
```

## 🆘 Solución de Problemas

### Error: "No se encontraron los archivos necesarios"

```bash
# Verifica que existan los archivos JSON
ls /Users/admin/dev/Reports/goetz-kundenportal-phoenix/*.json
```

Deben existir:
- `requirements.json`
- `board-issues.json`

### Error: "python3: command not found"

```bash
# Instala Python 3
brew install python3

# O usa la ruta completa a Python
/usr/bin/python3 /Users/admin/.agents/skills/map-tasks-to-issues/map_tasks_to_issues.py goetz-kundenportal-phoenix
```

### Los mapeos están muy bajos

Si el skill reporta pocos mapeos, es normal. El algoritmo es conservador. Puedes:

1. Revisar manualmente el CSV generado
2. Aumentar el umbral de similitud (mira README.md)
3. Agregar más términos de traducción alemán-inglés

## 💡 Tips de Uso

1. **Ejecuta regularmente** para monitorear cambios
2. **Compara reportes anteriores** para ver progreso
3. **Revisa manualmente los mapeos** con score bajo (0.15-0.25)
4. **Ajusta el umbral** si necesitas resultados diferentes

## 📚 Documentación Completa

- `README.md` - Documentación detallada del skill
- `SKILL.md` - Descripción técnica del skill

## 📞 Soporte

Para actualizar o mejorar el skill:
1. Edita `map_tasks_to_issues.py`
2. Prueba con: `python3 map_tasks_to_issues.py goetz-kundenportal-phoenix`
3. Verifica los reportes generados
4. Commit los cambios

---

**Versión**: 1.0.0  
**Fecha**: 2026-03-20  
**Autor**: OpenCode Skills
