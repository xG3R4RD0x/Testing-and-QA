#!/usr/bin/env elixir
# map-tasks-to-issues.exs
#
# Skill: map-tasks-to-issues
# Mapea tasks de requirements.json con issues de board-issues.json
# y genera un reporte en Excel

defmodule TaskIssueMapper do
  @moduledoc """
  Maps tasks from requirements to GitHub issues with semantic matching
  """

  require Logger

  def run(repo_name) when is_binary(repo_name) do
    base_path = "/Users/admin/dev/Reports/#{repo_name}"

    unless File.exists?(base_path) do
      raise "Directorio no encontrado: #{base_path}"
    end

    Logger.info("📂 Buscando archivos JSON en: #{base_path}")

    # Buscar archivos JSON
    json_files = Path.join(base_path, "*.json") |> Path.wildcard()
    Logger.info("Archivos JSON encontrados: #{Enum.count(json_files)}")
    Enum.each(json_files, &IO.inspect/1)

    # Buscar y cargar requirements.json
    requirements_file =
      Enum.find(json_files, fn file -> String.contains?(file, "requirements.json") end)

    requirements = load_json_file!(requirements_file, "requirements.json")

    # Buscar y cargar board-issues.json
    board_issues_file =
      Enum.find(json_files, fn file -> String.contains?(file, "board-issues.json") end)

    board_issues = load_json_file!(board_issues_file, "board-issues.json")

    Logger.info(
      "✅ Archivos cargados: #{Path.basename(requirements_file)} y #{Path.basename(board_issues_file)}"
    )

    # Extraer tasks e issues
    tasks = extract_tasks(requirements)
    issues = extract_issues(board_issues)

    Logger.info("📋 Tasks encontrados: #{Enum.count(tasks)}")
    Logger.info("🔗 Issues encontrados: #{Enum.count(issues)}")

    # Mapear tasks a issues usando similitud semántica
    mappings = map_tasks_to_issues(tasks, issues)

    Logger.info("🎯 Mapeos creados: #{Enum.count(mappings)}")

    # Calcular estadísticas
    stats = calculate_statistics(issues, mappings)

    # Generar reporte Excel
    timestamp = DateTime.utc_now() |> DateTime.to_iso8601() |> String.slice(0..9)
    output_file = Path.join(base_path, "task-issue-mapping-report-#{timestamp}.xlsx")

    generate_excel_report(output_file, tasks, issues, mappings, stats)

    Logger.info("✨ Reporte generado: #{output_file}")

    output_file
  end

  defp load_json_file!(file_path, file_type) do
    unless File.exists?(file_path) do
      raise "Archivo no encontrado: #{file_path}"
    end

    file_path
    |> File.read!()
    |> Jason.decode!()
  end

  defp extract_tasks(requirements) do
    requirements
    |> Map.get("main_requirements", [])
    |> Enum.flat_map(fn req ->
      req_id = req["id"]
      req_title = req["title"]

      sub_tasks = req["sub_tasks"] || []

      Enum.map(sub_tasks, fn task ->
        %{
          "id" => task["id"],
          "title" => task["title"],
          "description" => task["description"],
          "requirement_id" => req_id,
          "requirement_title" => req_title,
          "status" => "pending"
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

      best_match =
        issues
        |> Enum.map(fn issue ->
          issue_text = normalize_text("#{issue["title"]} #{issue["body"]}")
          similarity = calculate_similarity(task_text, issue_text)
          {issue, similarity}
        end)
        |> Enum.max_by(fn {_issue, similarity} -> similarity end, fn -> {nil, 0} end)

      case best_match do
        {issue, similarity} when similarity > 0.3 ->
          %{
            "task_id" => task["id"],
            "task_title" => task["title"],
            "task_description" => task["description"],
            "requirement_id" => task["requirement_id"],
            "requirement_title" => task["requirement_title"],
            "issue_number" => issue["number"],
            "issue_title" => issue["title"],
            "issue_body" => issue["body"],
            "issue_state" => issue["state"],
            "similarity" => similarity,
            "mapped" => true
          }

        _ ->
          %{
            "task_id" => task["id"],
            "task_title" => task["title"],
            "task_description" => task["description"],
            "requirement_id" => task["requirement_id"],
            "requirement_title" => task["requirement_title"],
            "issue_number" => nil,
            "issue_title" => nil,
            "issue_body" => nil,
            "issue_state" => nil,
            "similarity" => 0,
            "mapped" => false
          }
      end
    end)
  end

  defp normalize_text(text) do
    text
    |> String.downcase()
    |> String.trim()
  end

  defp calculate_similarity(text1, text2) do
    words1 = String.split(text1) |> Enum.uniq()
    words2 = String.split(text2) |> Enum.uniq()

    intersection = Enum.intersection(words1, words2)
    union = Enum.uniq(words1 ++ words2)

    if Enum.empty?(union) do
      0.0
    else
      Enum.count(intersection) / Enum.count(union)
    end
  end

  defp calculate_statistics(issues, mappings) do
    total_issues = Enum.count(issues)
    closed_issues = Enum.count(issues, &(Map.get(&1, "state") == "CLOSED"))
    mapped_tasks = Enum.count(mappings, & &1["mapped"])
    total_tasks = Enum.count(mappings)

    %{
      "total_issues" => total_issues,
      "closed_issues" => closed_issues,
      "open_issues" => total_issues - closed_issues,
      "completion_percentage" =>
        if(total_issues > 0, do: Float.round(closed_issues / total_issues * 100, 2), else: 0),
      "mapped_tasks" => mapped_tasks,
      "unmapped_tasks" => total_tasks - mapped_tasks,
      "total_tasks" => total_tasks,
      "mapping_coverage" =>
        if(total_tasks > 0, do: Float.round(mapped_tasks / total_tasks * 100, 2), else: 0)
    }
  end

  defp generate_excel_report(output_file, tasks, issues, mappings, stats) do
    Logger.info("📊 Generando reporte Excel...")

    # Crear directorio si no existe
    File.mkdir_p!(Path.dirname(output_file))

    # Aquí irá la lógica para generar Excel
    # Por ahora, crear un archivo CSV como alternativa

    generate_csv_report(output_file, mappings, stats)
  end

  defp generate_csv_report(output_file, mappings, stats) do
    # Cambiar extensión a .csv
    csv_file = String.replace(output_file, ".xlsx", ".csv")

    # Encabezados
    headers = [
      "Task ID",
      "Task Title",
      "Task Description",
      "Requirement ID",
      "Requirement Title",
      "Issue Number",
      "Issue Title",
      "Issue Body",
      "Issue State",
      "Mapped",
      "Similarity Score"
    ]

    # Convertir mapeos a CSV
    rows =
      mappings
      |> Enum.map(fn mapping ->
        [
          mapping["task_id"],
          mapping["task_title"],
          mapping["task_description"],
          mapping["requirement_id"],
          mapping["requirement_title"],
          mapping["issue_number"] || "N/A",
          mapping["issue_title"] || "N/A",
          mapping["issue_body"] || "N/A",
          mapping["issue_state"] || "N/A",
          if(mapping["mapped"], do: "YES", else: "NO"),
          Float.round(mapping["similarity"], 3)
        ]
      end)

    # Escribir archivo CSV
    content =
      [headers | rows]
      |> Enum.map(&Enum.join(&1, ","))
      |> Enum.join("\n")

    File.write!(csv_file, content)

    # Crear archivo de resumen
    summary_file = String.replace(csv_file, ".csv", "-SUMMARY.txt")

    summary_content = """
    ╔════════════════════════════════════════════════════════════╗
    ║           TASK-ISSUE MAPPING REPORT SUMMARY                ║
    ╚════════════════════════════════════════════════════════════╝

    📊 ISSUE STATISTICS
    ─────────────────────────────────────────────────────────────
    Total Issues:           #{stats["total_issues"]}
    Closed Issues:          #{stats["closed_issues"]}
    Open Issues:            #{stats["open_issues"]}
    Completion Rate:        #{stats["completion_percentage"]}%

    📋 TASK MAPPING STATISTICS
    ─────────────────────────────────────────────────────────────
    Total Tasks:            #{stats["total_tasks"]}
    Mapped Tasks:           #{stats["mapped_tasks"]}
    Unmapped Tasks:         #{stats["unmapped_tasks"]}
    Mapping Coverage:       #{stats["mapping_coverage"]}%

    📁 OUTPUT FILES
    ─────────────────────────────────────────────────────────────
    CSV Report:             #{Path.basename(csv_file)}
    Summary:                #{Path.basename(summary_file)}

    Generated: #{DateTime.utc_now()}
    """

    File.write!(summary_file, summary_content)

    Logger.info("📄 Archivos generados:")
    Logger.info("   - #{Path.basename(csv_file)}")
    Logger.info("   - #{Path.basename(summary_file)}")

    csv_file
  end
end

# Ejecutar el skill
case System.argv() do
  [repo_name] ->
    try do
      TaskIssueMapper.run(repo_name)
      IO.puts("✅ Skill completado exitosamente")
    rescue
      e ->
        IO.puts("❌ Error: #{Exception.message(e)}")
        System.halt(1)
    end

  _ ->
    IO.puts("Uso: map-tasks-to-issues.exs <repository_name>")
    IO.puts("")
    IO.puts("Ejemplo: map-tasks-to-issues.exs goetz-kundenportal-phoenix")
    System.halt(1)
end
