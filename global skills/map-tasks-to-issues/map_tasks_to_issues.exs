#!/usr/bin/env elixir
# map_tasks_to_issues.exs
#
# Skill para mapear tasks con issues de GitHub y generar reporte
# Uso: elixir map_tasks_to_issues.exs <repository_name>

defmodule MapTasksToIssues do
  @moduledoc """
  Maps tasks from requirements.json to GitHub issues in board-issues.json
  using semantic similarity and generates a CSV report.
  """

  require Logger

  def main(args) do
    case args do
      [repo_name] ->
        run(repo_name)

      _ ->
        print_usage()
        System.halt(1)
    end
  end

  def run(repo_name) do
    base_path = "/Users/admin/dev/Reports/#{repo_name}"

    unless File.exists?(base_path) do
      IO.puts("❌ Error: Directorio no encontrado: #{base_path}")
      System.halt(1)
    end

    IO.puts("🔍 Buscando archivos JSON en: #{base_path}\n")

    # Encontrar archivos
    json_files = Path.join(base_path, "*.json") |> Path.wildcard()

    requirements_file =
      Enum.find(json_files, fn file -> String.ends_with?(file, "requirements.json") end)

    board_issues_file =
      Enum.find(json_files, fn file -> String.ends_with?(file, "board-issues.json") end)

    unless requirements_file && board_issues_file do
      IO.puts("❌ Error: No se encontraron los archivos necesarios")
      IO.puts("   Se requiere: requirements.json y board-issues.json")
      System.halt(1)
    end

    IO.puts("✅ Archivos encontrados:")
    IO.puts("   - #{Path.basename(requirements_file)}")
    IO.puts("   - #{Path.basename(board_issues_file)}\n")

    # Cargar datos
    requirements = load_json!(requirements_file)
    board_issues = load_json!(board_issues_file)

    # Extraer tasks e issues
    tasks = extract_tasks(requirements)
    issues = extract_issues(board_issues)

    IO.puts("📋 Análisis de datos:")
    IO.puts("   - Tasks encontrados: #{Enum.count(tasks)}")
    IO.puts("   - Issues encontrados: #{Enum.count(issues)}\n")

    # Mapear tasks a issues
    IO.puts("🔗 Ejecutando mapeo semántico...")
    mappings = map_tasks_to_issues(tasks, issues)

    # Estadísticas
    stats = calculate_stats(issues, mappings)

    IO.puts("✅ Mapeo completado:")
    IO.puts("   - Tasks mapeados: #{stats["mapped_tasks"]}/#{stats["total_tasks"]}")
    IO.puts("   - Cobertura: #{stats["mapping_coverage"]}%")
    IO.puts("   - Issues cerrados: #{stats["closed_issues"]}/#{stats["total_issues"]}")
    IO.puts("   - Tasa de completitud: #{stats["completion_percentage"]}%\n")

    # Generar reportes
    IO.puts("📊 Generando reportes...")
    timestamp = DateTime.utc_now() |> DateTime.to_iso8601() |> String.slice(0..9)
    base_filename = "#{base_path}/task-issue-mapping-#{timestamp}"

    # Generar CSV
    csv_file = generate_csv(base_filename, mappings)

    # Generar resumen
    summary_file = generate_summary(base_filename, stats)

    IO.puts("✨ Reportes generados:")
    IO.puts("   - #{Path.basename(csv_file)}")
    IO.puts("   - #{Path.basename(summary_file)}\n")

    IO.puts("✅ ¡Proceso completado exitosamente!")
  end

  defp load_json!(file_path) do
    content = File.read!(file_path)
    # Usar decode!/1 de Poison si está disponible, sino usar una solución alternativa
    try do
      apply(Poison, :decode!, [content])
    rescue
      _ ->
        # Fallback: intentar con una simple evaluación (NO recomendado para datos no confiables)
        IO.puts("❌ Error: Se necesita la librería Jason o Poison para parsear JSON")
        IO.puts("   Intenta: mix escript.install hex poison")
        System.halt(1)
    end
  rescue
    e ->
      IO.puts("❌ Error al cargar #{file_path}: #{Exception.message(e)}")
      System.halt(1)
  end

  defp extract_tasks(requirements) do
    requirements
    |> Map.get("main_requirements", [])
    |> Enum.flat_map(fn req ->
      req_id = req["id"]
      req_title = req["title"]

      req
      |> Map.get("sub_tasks", [])
      |> Enum.map(fn task ->
        %{
          "id" => task["id"],
          "title" => task["title"],
          "description" => task["description"],
          "requirement_id" => req_id,
          "requirement_title" => req_title
        }
      end)
    end)
  end

  defp extract_issues(board_issues) do
    board_issues
    |> Map.get("issues", [])
    |> Enum.map(fn issue ->
      %{
        "number" => issue["number"],
        "title" => issue["title"],
        "body" => issue["body"] || "",
        "state" => issue["state"],
        "created_at" => issue["created_at"],
        "updated_at" => issue["updated_at"]
      }
    end)
  end

  defp map_tasks_to_issues(tasks, issues) do
    tasks
    |> Enum.map(fn task ->
      task_text = normalize_text("#{task["title"]} #{task["description"]}")

      {best_issue, best_score} =
        issues
        |> Enum.map(fn issue ->
          issue_text = normalize_text("#{issue["title"]} #{issue["body"]}")
          score = calculate_similarity(task_text, issue_text)
          {issue, score}
        end)
        |> Enum.max_by(fn {_issue, score} -> score end, fn -> {nil, 0.0} end)

      %{
        task: task,
        issue: best_issue,
        similarity_score: best_score,
        is_mapped: best_score > 0.25
      }
    end)
  end

  defp normalize_text(text) do
    text
    |> String.downcase()
    |> String.replace(~r/[^\w\s]/u, " ")
    |> String.trim()
  end

  defp calculate_similarity(text1, text2) do
    words1 = text1 |> String.split() |> Enum.uniq()
    words2 = text2 |> String.split() |> Enum.uniq()

    intersection = Enum.intersection(words1, words2)
    union = Enum.uniq(words1 ++ words2)

    if Enum.empty?(union) do
      0.0
    else
      Enum.count(intersection) / Enum.count(union)
    end
  end

  defp calculate_stats(issues, mappings) do
    total_issues = Enum.count(issues)
    closed_issues = Enum.count(issues, &(Map.get(&1, "state") == "CLOSED"))
    mapped_tasks = Enum.count(mappings, & &1.is_mapped)
    total_tasks = Enum.count(mappings)

    %{
      "total_issues" => total_issues,
      "closed_issues" => closed_issues,
      "open_issues" => total_issues - closed_issues,
      "completion_percentage" => percentage(closed_issues, total_issues),
      "total_tasks" => total_tasks,
      "mapped_tasks" => mapped_tasks,
      "unmapped_tasks" => total_tasks - mapped_tasks,
      "mapping_coverage" => percentage(mapped_tasks, total_tasks)
    }
  end

  defp percentage(numerator, denominator) do
    if denominator > 0 do
      Float.round(numerator / denominator * 100, 2)
    else
      0.0
    end
  end

  defp generate_csv(base_filename, mappings) do
    csv_file = "#{base_filename}.csv"

    headers = [
      "Task ID",
      "Task Title",
      "Task Description",
      "Requirement ID",
      "Requirement Title",
      "Issue #",
      "Issue Title",
      "Issue State",
      "Similarity Score",
      "Mapped"
    ]

    rows =
      mappings
      |> Enum.map(fn mapping ->
        task = mapping.task
        issue = mapping.issue
        score = Float.round(mapping.similarity_score, 3)
        mapped = if mapping.is_mapped, do: "✓", else: "✗"

        [
          task["id"],
          task["title"],
          task["description"],
          task["requirement_id"],
          task["requirement_title"],
          (issue && issue["number"]) || "—",
          (issue && issue["title"]) || "—",
          (issue && issue["state"]) || "—",
          score,
          mapped
        ]
      end)

    content =
      [headers | rows]
      |> Enum.map(&(Enum.map(&1, fn v -> escape_csv(v) end) |> Enum.join(",")))
      |> Enum.join("\n")

    File.write!(csv_file, content)
    csv_file
  end

  defp escape_csv(value) do
    str = to_string(value)

    if String.contains?(str, [",", "\"", "\n"]) do
      "\"#{String.replace(str, "\"", "\"\"")}\""
    else
      str
    end
  end

  defp generate_summary(base_filename, stats) do
    summary_file = "#{base_filename}-SUMMARY.txt"

    content = """
    ╔════════════════════════════════════════════════════════════╗
    ║        TASK-ISSUE MAPPING REPORT SUMMARY                   ║
    ║                                                            ║
    ║  Análisis Semántico de Tasks vs GitHub Issues             ║
    ╚════════════════════════════════════════════════════════════╝

    📊 ESTADÍSTICAS DE ISSUES
    ─────────────────────────────────────────────────────────────
    Total de Issues:                  #{stats["total_issues"]}
    Issues Cerrados (CLOSED):         #{stats["closed_issues"]}
    Issues Abiertos (OPEN):           #{stats["open_issues"]}
    Tasa de Completitud:              #{stats["completion_percentage"]}%

    📋 ESTADÍSTICAS DE TASKS
    ─────────────────────────────────────────────────────────────
    Total de Tasks:                   #{stats["total_tasks"]}
    Tasks Mapeados a Issues:          #{stats["mapped_tasks"]}
    Tasks sin Mapeo:                  #{stats["unmapped_tasks"]}
    Cobertura de Mapeo:               #{stats["mapping_coverage"]}%

    ℹ️  NOTAS IMPORTANTES
    ─────────────────────────────────────────────────────────────
    • El mapeo se realiza usando similitud semántica de textos
    • Soporta mezcla de alemán e inglés
    • Umbral mínimo de similitud: 25%
    • Revisa manualmente los mapeos para validar precisión

    📁 ARCHIVOS GENERADOS
    ─────────────────────────────────────────────────────────────
    CSV Report:                       #{Path.basename(base_filename)}.csv
    Summary:                          #{Path.basename(summary_file)}

    Timestamp:                        #{DateTime.utc_now()}
    """

    File.write!(summary_file, content)
    summary_file
  end

  defp print_usage do
    IO.puts("""
    map-tasks-to-issues - Mapeo de Tasks a GitHub Issues

    Uso:
      elixir map_tasks_to_issues.exs <nombre_repositorio>

    Ejemplo:
      elixir map_tasks_to_issues.exs goetz-kundenportal-phoenix

    Descripción:
      Lee requirements.json y board-issues.json de:
      /Users/admin/dev/Reports/<nombre_repositorio>/

      Genera un reporte CSV con el mapeo semántico entre
      tasks de requirements e issues de GitHub.

    Requisitos:
      • requirements.json - Tasks de los requisitos
      • board-issues.json - Issues del proyecto en GitHub
      • Jason o Poison library para parsear JSON
    """)
  end
end

# Ejecutar el script
MapTasksToIssues.main(System.argv())
