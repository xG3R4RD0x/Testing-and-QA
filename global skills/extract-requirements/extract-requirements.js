#!/usr/bin/env node

/**
 * Extract Requirements from PDF
 * Usage: node extract-requirements.js <pdf-path>
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

async function extractRepositoryName() {
  try {
    const result = execSync('git rev-parse --show-toplevel', { encoding: 'utf8' }).trim();
    const repoName = path.basename(result);
    return repoName;
  } catch (error) {
    console.error('Error: Not a git repository or git not available');
    process.exit(1);
  }
}

function getReportsPath(repositoryName) {
  return path.join('/Users/admin/dev/Reports', repositoryName);
}

function ensureReportsDirectory(reportsPath) {
  if (!fs.existsSync(reportsPath)) {
    fs.mkdirSync(reportsPath, { recursive: true });
  }
}

function parseRequirementsFromText(text) {
  // This is a semantic analysis placeholder
  // The actual analysis will be done by the OpenCode agent using the pdf-reader tool
  // This function structures the data once the agent has extracted it
  
  const lines = text.split('\n').filter(line => line.trim());
  const requirements = [];
  let currentRequirement = null;

  for (const line of lines) {
    const trimmed = line.trim();
    
    // Detect main requirement (usually lines starting with numbers or specific keywords)
    if (/^(?:REQ|Requirement|Feature|Requirement|Goal|Objective|\d+\.)/.test(trimmed)) {
      if (currentRequirement) {
        requirements.push(currentRequirement);
      }
      currentRequirement = {
        id: `REQ-${String(requirements.length + 1).padStart(3, '0')}`,
        title: trimmed.replace(/^(?:REQ|Requirement|Feature|Goal|Objective|\d+\.)\s*/, ''),
        description: '',
        sub_tasks: []
      };
    }
    // Detect sub-tasks (usually indented or with bullet points)
    else if (currentRequirement && /^(?:\s+-|\s+\*|\s+\d+\.|Task|Sub-task)/.test(line)) {
      const taskTitle = trimmed.replace(/^(?:-|\*|\d+\.|Task:|Sub-task:)\s*/, '');
      currentRequirement.sub_tasks.push({
        id: `TASK-${String(currentRequirement.sub_tasks.length + 1).padStart(3, '0')}`,
        title: taskTitle,
        description: ''
      });
    }
    // Add to description
    else if (currentRequirement && trimmed && !currentRequirement.title.includes(trimmed)) {
      if (currentRequirement.sub_tasks.length > 0) {
        // Add to last sub-task description
        currentRequirement.sub_tasks[currentRequirement.sub_tasks.length - 1].description += 
          (currentRequirement.sub_tasks[currentRequirement.sub_tasks.length - 1].description ? ' ' : '') + trimmed;
      } else {
        // Add to requirement description
        currentRequirement.description += (currentRequirement.description ? ' ' : '') + trimmed;
      }
    }
  }

  if (currentRequirement) {
    requirements.push(currentRequirement);
  }

  return requirements;
}

function generateJSON(requirements, repositoryName) {
  return {
    repository_name: repositoryName,
    extraction_date: new Date().toISOString().split('T')[0],
    total_requirements: requirements.length,
    main_requirements: requirements
  };
}

async function main() {
  const pdfPath = process.argv[2];

  if (!pdfPath) {
    console.error('Usage: extract-requirements.js <pdf-path>');
    process.exit(1);
  }

  if (!fs.existsSync(pdfPath)) {
    console.error(`Error: PDF file not found: ${pdfPath}`);
    process.exit(1);
  }

  console.log(`Extracting repository name...`);
  const repositoryName = await extractRepositoryName();
  console.log(`Repository: ${repositoryName}`);

  const reportsPath = getReportsPath(repositoryName);
  console.log(`Reports path: ${reportsPath}`);

  ensureReportsDirectory(reportsPath);

  const requirementsJsonPath = path.join(reportsPath, 'requirements.json');

  console.log(`\n📋 Extract Requirements Helper`);
  console.log(`\nNote: This script is a helper. The actual PDF analysis should be done by the OpenCode agent using the pdf-reader tool.`);
  console.log(`\nTo complete the extraction:`);
  console.log(`1. Use the pdf-reader tool to extract text from: ${pdfPath}`);
  console.log(`2. Analyze the extracted content semantically`);
  console.log(`3. Structure it as main requirements with sub-tasks`);
  console.log(`4. Call this script with the structured data or save the JSON directly to: ${requirementsJsonPath}`);
  
  console.log(`\nExample JSON output would be saved to: ${requirementsJsonPath}`);

  process.exit(0);
}

main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});
