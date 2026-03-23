#!/usr/bin/env bash
# install.sh - Instalación del skill map-tasks-to-issues

set -e

SKILL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SKILL_NAME="map-tasks-to-issues"

echo "🔧 Instalando skill: $SKILL_NAME"
echo ""

# Hacer el script principal ejecutable
chmod +x "$SKILL_DIR/map_tasks_to_issues.exs"

echo "✅ Archivos del skill:"
ls -lh "$SKILL_DIR/"

echo ""
echo "✨ Instalación completada!"
echo ""
echo "📖 Para usar el skill:"
echo "   elixir $SKILL_DIR/map_tasks_to_issues.exs <repository_name>"
echo ""
echo "📚 Ejemplo:"
echo "   elixir $SKILL_DIR/map_tasks_to_issues.exs goetz-kundenportal-phoenix"
echo ""
echo "📋 Para más información, lee: $SKILL_DIR/README.md"
