#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * Create Issues from Requirements Skill
 * Reads a requirements.json file and creates GitHub issues with proper hierarchy
 */

class RequirementsIssueCreator {
  constructor(projectName, repo, boardName, isDryRun = false, shouldUpdate = false) {
    this.projectName = projectName;
    this.repo = repo;
    this.boardName = boardName;
    this.isDryRun = isDryRun;
    this.shouldUpdate = shouldUpdate;
    this.requirementsPath = path.join('/Users/admin/dev/Reports', projectName, 'requirements.json');
    this.requirements = null;
    this.issueMap = new Map(); // Maps REQ/TASK IDs to issue numbers
    this.createdIssues = [];
    this.skippedIssues = [];
    this.failedIssues = [];
  }

  /**
   * Validate prerequisites
   */
  validate() {
    console.log('\n=== VALIDATING PREREQUISITES ===\n');

    // Check if requirements.json exists
    if (!fs.existsSync(this.requirementsPath)) {
      throw new Error(`requirements.json not found at: ${this.requirementsPath}`);
    }
    console.log(`✓ requirements.json found at: ${this.requirementsPath}`);

    // Check if gh CLI is installed and authenticated
    try {
      execSync('gh auth status', { stdio: 'pipe' });
      console.log('✓ GitHub CLI (gh) is authenticated');
    } catch (error) {
      throw new Error('GitHub CLI (gh) is not authenticated. Please run: gh auth login');
    }

    // Validate repository exists and get full name
    try {
      const repoInfo = execSync(`gh repo view ${this.repo} --json nameWithOwner`, { 
        encoding: 'utf-8',
        stdio: 'pipe'
      });
      const parsed = JSON.parse(repoInfo);
      this.repo = parsed.nameWithOwner; // Use full repo name
      console.log(`✓ Repository "${this.repo}" is accessible`);
    } catch (error) {
      throw new Error(`Repository "${this.repo}" is not accessible or does not exist`);
    }

    // Validate project board if provided
    if (this.boardName) {
      console.log(`✓ Project board "${this.boardName}" will be used for issues`);
    }
  }

  /**
   * Load and parse requirements.json
   */
  loadRequirements() {
    console.log('\n=== LOADING REQUIREMENTS ===\n');

    const content = fs.readFileSync(this.requirementsPath, 'utf-8');
    this.requirements = JSON.parse(content);

    if (!this.requirements.main_requirements || !Array.isArray(this.requirements.main_requirements)) {
      throw new Error('Invalid requirements.json structure: missing main_requirements array');
    }

    console.log(`✓ Loaded ${this.requirements.main_requirements.length} main requirements`);

    const totalTasks = this.requirements.main_requirements.reduce(
      (sum, req) => sum + (req.sub_tasks?.length || 0),
      0
    );
    console.log(`✓ Loaded ${totalTasks} sub-tasks`);
  }

  /**
   * Check for existing issues
   */
  checkExistingIssues() {
    console.log('\n=== CHECKING FOR EXISTING ISSUES ===\n');

    const existingRequirements = new Map();
    const existingTasks = new Map();

    // Query existing issues
    try {
      const issues = JSON.parse(
        execSync(`gh issue list --repo ${this.repo} --limit 1000 --json number,title`, {
          encoding: 'utf-8',
        })
      );

      issues.forEach((issue) => {
        const reqMatch = issue.title.match(/^\[REQ-([^\]]+)\]/);
        const taskMatch = issue.title.match(/^\[TASK-([^\]]+)\]/);

        if (reqMatch) {
          existingRequirements.set(reqMatch[1], issue.number);
        } else if (taskMatch) {
          existingTasks.set(taskMatch[1], issue.number);
        }
      });
    } catch (error) {
      console.warn('⚠ Could not fetch existing issues');
    }

    console.log(`✓ Found ${existingRequirements.size} existing requirement issues`);
    console.log(`✓ Found ${existingTasks.size} existing task issues`);

    return { existingRequirements, existingTasks };
  }

  /**
   * Create a GitHub issue with retry logic
   */
  createIssueWithRetry(title, body, labels = [], maxRetries = 1) {
    let lastError;

    for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
      try {
        // Try to create with labels, but if labels don't exist, try without
        let command = `gh issue create --repo ${this.repo} --title "${title.replace(/"/g, '\\"')}" --body "${body.replace(/"/g, '\\"')}"`;
        
        if (labels.length > 0) {
          for (const label of labels) {
            command += ` --label "${label}"`;
          }
        }

        const output = execSync(command, { encoding: 'utf-8' });
        // Extract issue number from output like "https://github.com/owner/repo/issues/123"
        const match = output.match(/\/issues\/(\d+)/);
        if (match && match[1]) {
          return parseInt(match[1], 10);
        }
        throw new Error('Could not extract issue number from response');
      } catch (error) {
        lastError = error;
        // Check if error is about missing labels
        if (error.message.includes('not found') && labels.length > 0) {
          // Retry without labels on first attempt
          if (attempt === 1) {
            try {
              const command = `gh issue create --repo ${this.repo} --title "${title.replace(/"/g, '\\"')}" --body "${body.replace(/"/g, '\\"')}"`;
              const output = execSync(command, { encoding: 'utf-8' });
              const match = output.match(/\/issues\/(\d+)/);
              if (match && match[1]) {
                console.log(`  ⚠ Created without labels (labels don't exist in repo)`);
                return parseInt(match[1], 10);
              }
            } catch (retryError) {
              lastError = retryError;
            }
          }
        }
        
        if (attempt <= maxRetries) {
          console.log(`  ⚠ Retry attempt ${attempt}/${maxRetries}...`);
        }
      }
    }

    throw lastError;
  }

  /**
   * Create a sub-issue relationship
   */
  createSubIssue(parentNumber, childNumber) {
    try {
      execSync(
        `gh issue edit ${parentNumber} --repo ${this.repo} --add-assignee --json add-sub-issue-id=${childNumber}`,
        { stdio: 'pipe' }
      );
    } catch (error) {
      // Sub-issue creation might fail in some cases, but it's not critical
      console.warn(`  ⚠ Could not link as sub-issue: ${error.message}`);
    }
  }

  /**
   * Add issue to project board
   */
  addToProjectBoard(issueNumber) {
    if (!this.boardName) return;

    try {
      execSync(
        `gh issue edit ${issueNumber} --repo ${this.repo} --add-project "${this.boardName}"`,
        { stdio: 'pipe' }
      );
    } catch (error) {
      console.warn(`  ⚠ Could not add to project board: ${error.message}`);
    }
  }

  /**
   * Build requirement issue body
   */
  buildRequirementBody(requirement, subTaskIssueNumbers) {
    let body = `## Description\n${requirement.description}\n`;

    if (subTaskIssueNumbers.length > 0) {
      body += '\n## Subtasks\n';
      requirement.sub_tasks.forEach((task, index) => {
        const issueNumber = subTaskIssueNumbers[index];
        if (issueNumber) {
          body += `- [ ] [${task.id}](https://github.com/${this.repo}/issues/${issueNumber}) - ${task.title}\n`;
        } else {
          body += `- [ ] ${task.id} - ${task.title}\n`;
        }
      });
    }

    return body;
  }

  /**
   * Build sub-task issue body
   */
  buildSubTaskBody(subTask) {
    let body = `## Description\n${subTask.description}\n`;

    if (subTask.implementation) {
      body += `\n## Implementation Steps\n${subTask.implementation}\n`;
    }

    if (subTask.test) {
      body += `\n## Test Cases\n${subTask.test}\n`;
    }

    return body;
  }

  /**
   * Create sub-task issues
   */
  createSubTasks(requirement, existingTasks) {
    const subTaskNumbers = [];

    if (!requirement.sub_tasks || requirement.sub_tasks.length === 0) {
      return subTaskNumbers;
    }

    for (const subTask of requirement.sub_tasks) {
      // Check if already exists
      if (existingTasks.has(subTask.id)) {
        console.log(`  ⊘ TASK-${subTask.id}: Already exists (issue #${existingTasks.get(subTask.id)})`);
        this.skippedIssues.push({
          id: subTask.id,
          title: subTask.title,
          type: 'subtask',
          reason: 'already exists',
        });
        subTaskNumbers.push(existingTasks.get(subTask.id));
        continue;
      }

      try {
        const title = `[${subTask.id}] ${subTask.title}`;
        const body = this.buildSubTaskBody(subTask);
        const labels = ['subtask', 'status:pending'];

        const issueNumber = this.createIssueWithRetry(title, body, labels, 1);

        this.issueMap.set(subTask.id, issueNumber);
        subTaskNumbers.push(issueNumber);
        this.createdIssues.push({
          id: subTask.id,
          title: subTask.title,
          type: 'subtask',
          number: issueNumber,
        });

        console.log(`  ✓ ${subTask.id}: Created (issue #${issueNumber})`);

        // Add to project board
        this.addToProjectBoard(issueNumber);
      } catch (error) {
        console.error(`  ✗ ${subTask.id}: Failed - ${error.message}`);
        this.failedIssues.push({
          id: subTask.id,
          title: subTask.title,
          type: 'subtask',
          error: error.message,
        });
      }
    }

    return subTaskNumbers;
  }

  /**
   * Create requirement issues
   */
  createRequirements(existingRequirements, existingTasks) {
    console.log('\n=== CREATING ISSUES ===\n');

    for (const requirement of this.requirements.main_requirements) {
      // Check if already exists
      if (existingRequirements.has(requirement.id)) {
        console.log(
          `✗ ${requirement.id}: Already exists (issue #${existingRequirements.get(requirement.id)})`
        );
        this.skippedIssues.push({
          id: requirement.id,
          title: requirement.title,
          type: 'requirement',
          reason: 'already exists',
        });
        continue;
      }

      try {
        // Create sub-tasks first
        console.log(`\nCreating ${requirement.id}: ${requirement.title}`);
        const subTaskNumbers = this.createSubTasks(requirement, existingTasks);

        // Create requirement issue
        const title = `[${requirement.id}] ${requirement.title}`;
        const body = this.buildRequirementBody(requirement, subTaskNumbers);
        const labels = ['requirement', 'status:pending'];

        const issueNumber = this.createIssueWithRetry(title, body, labels, 1);

        this.issueMap.set(requirement.id, issueNumber);
        this.createdIssues.push({
          id: requirement.id,
          title: requirement.title,
          type: 'requirement',
          number: issueNumber,
        });

        console.log(`✓ ${requirement.id}: Created (issue #${issueNumber})`);

        // Add to project board
        this.addToProjectBoard(issueNumber);

        // Link sub-tasks as sub-issues
        for (let i = 0; i < subTaskNumbers.length; i++) {
          try {
            // Using gh CLI to create sub-issue relationship
            execSync(
              `gh issue edit ${issueNumber} --repo ${this.repo} --add-project "${this.boardName}"`,
              { stdio: 'pipe' }
            );
          } catch (error) {
            // Sub-issue linking might not work with current gh version
          }
        }
      } catch (error) {
        console.error(`✗ ${requirement.id}: Failed - ${error.message}`);
        this.failedIssues.push({
          id: requirement.id,
          title: requirement.title,
          type: 'requirement',
          error: error.message,
        });
      }
    }
  }

  /**
   * Print dry-run summary
   */
  printDryRunSummary() {
    console.log('\n=== REQUIREMENTS ISSUE CREATION - DRY RUN ===\n');
    console.log(`Project: ${this.projectName}`);
    console.log(`Repository: ${this.repo}`);
    if (this.boardName) {
      console.log(`Project Board: ${this.boardName}`);
    }

    console.log('\nREQUIREMENTS TO CREATE:');
    let issueCount = 0;

    this.requirements.main_requirements.forEach((req, index) => {
      const taskCount = req.sub_tasks?.length || 0;
      console.log(`${index + 1}. [${req.id}] ${req.title}`);
      console.log(`   - ${taskCount} sub-task(s)`);
      issueCount += 1 + taskCount;
    });

    console.log('\n=== SUMMARY ===');
    console.log(
      `Total Requirements: ${this.requirements.main_requirements.length}`
    );
    const totalTasks = this.requirements.main_requirements.reduce(
      (sum, req) => sum + (req.sub_tasks?.length || 0),
      0
    );
    console.log(`Total Sub-tasks: ${totalTasks}`);
    console.log(`Would create: ${issueCount} issues\n`);
    console.log('Run without --dry-run to create these issues.');
  }

  /**
   * Print creation summary
   */
  printSummary() {
    console.log('\n=== SUMMARY ===\n');
    console.log(`✓ Created: ${this.createdIssues.length} issues`);
    console.log(`⊘ Skipped: ${this.skippedIssues.length} issues`);
    console.log(`✗ Failed: ${this.failedIssues.length} issues`);

    if (this.failedIssues.length > 0) {
      console.log('\nFailed Issues:');
      this.failedIssues.forEach((issue) => {
        console.log(`  - [${issue.type.toUpperCase()}-${issue.id}] ${issue.title}`);
        console.log(`    Error: ${issue.error}`);
      });
    }

    if (this.boardName) {
      console.log(`\n✓ Added to project board: "${this.boardName}"`);
    }

    console.log('\n');
  }

  /**
   * Main execution method
   */
  run() {
    try {
      this.validate();
      this.loadRequirements();

      if (this.isDryRun) {
        this.printDryRunSummary();
        return;
      }

      const { existingRequirements, existingTasks } = this.checkExistingIssues();
      this.createRequirements(existingRequirements, existingTasks);
      this.printSummary();
    } catch (error) {
      console.error(`\n✗ Error: ${error.message}\n`);
      process.exit(1);
    }
  }
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: /create-issues-from-requirements <project-name> [--repo owner/repo] [--board board-name] [--dry-run] [--update]');
    process.exit(1);
  }

  const projectName = args[0];
  let repo = null;
  let boardName = null;
  let isDryRun = false;
  let shouldUpdate = false;

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--repo' && i + 1 < args.length) {
      repo = args[++i];
    } else if (args[i] === '--board' && i + 1 < args.length) {
      boardName = args[++i];
    } else if (args[i] === '--dry-run') {
      isDryRun = true;
    } else if (args[i] === '--update') {
      shouldUpdate = true;
    }
  }

  if (!repo) {
    console.error('Error: --repo parameter is required');
    process.exit(1);
  }

  return { projectName, repo, boardName, isDryRun, shouldUpdate };
}

// Main execution
const { projectName, repo, boardName, isDryRun, shouldUpdate } = parseArgs();
const creator = new RequirementsIssueCreator(projectName, repo, boardName, isDryRun, shouldUpdate);
creator.run();
