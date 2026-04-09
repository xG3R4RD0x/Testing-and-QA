#!/usr/bin/env python3
"""
Complete Tasks from Codebase Skill - LLM-Prompting Version

This skill enriches requirements.json with implementation plans by:
1. Analyzing the actual codebase (keywords, structure, patterns)
2. Building dynamic prompts with context specific to each requirement
3. Sending prompts to the user's agent (OpenCode, Copilot, Claude Code, etc.)
4. Parsing the agent's responses and structuring them in requirements.json

Usage:
  /complete-tasks requirements.json

The skill operates in 4 stages:
1. Stage 1: Prepare (load requirements, detect technical requirements)
2. Stage 2: Analyze with LLM (prompt user, collect responses, parse)
3. Stage 3: Generate Tests (same process for test scenarios)
4. Stage 4: Finalize (update JSON, create backup)
"""

import json
import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import shutil


class PromptBuilder:
    """Builds structured prompts for LLM analysis."""
    
    def __init__(self):
        self.max_prompt_tokens = 5000  # ~1250 words
    
    def build_requirement_prompt(
        self,
        requirement: Dict,
        subtasks: List[Dict],
        context: Dict,
        language: str,
        frameworks: List[str]
    ) -> str:
        """
        Build a comprehensive prompt for analyzing a requirement.
        
        Args:
            requirement: Requirement with title and description
            subtasks: List of subtasks to implement
            context: Codebase context (structure, configs, examples)
            language: Detected programming language
            frameworks: List of detected frameworks
        
        Returns:
            Formatted prompt ready for agent
        """
        prompt = f"""# Project Context

**Language:** {language}
**Frameworks:** {', '.join(frameworks)}

## Project Structure
{context.get('structure', '[Structure not available]')}

## Key Configuration Files
{context.get('config_files', '[Config files not available]')}

## Project Overview
{context.get('readme', '[README not available]')}

## Example Patterns from Codebase
{context.get('examples', '[No examples found]')}

---

# Requirement to Implement

**Title:** {requirement.get('title', 'Untitled')}

**Description:** {requirement.get('description', 'No description')}

## Subtasks to Implement

"""
        for i, subtask in enumerate(subtasks, 1):
            prompt += f"\n{i}. **{subtask.get('title', f'Subtask {i}')}**\n"
            desc = subtask.get('description', 'No description')
            prompt += f"   Description: {desc}\n"
        
        prompt += f"""

---

# Your Task

Based on the project context and existing code patterns shown above, provide 
a SPECIFIC implementation plan for this requirement.

For each subtask, provide detailed implementation guidance that includes:
- Specific file paths (relative to project root)
- Module/function/class names to create or modify
- Existing patterns to follow from the codebase
- Integration points with existing code

Do NOT provide actual code implementation, only step-by-step guidance.

## Required Response Format

Your response MUST follow this exact format (one section per subtask):

```
## Implementation for [Subtask 1 Title]
1. [Specific step with exact file paths and function names]
2. [Next step]
3. [Continue...]

## Implementation for [Subtask 2 Title]
1. [Specific step]
...
```

All subtasks MUST be included. Begin your response now:"""
        
        return prompt
    
    def build_tests_prompt(
        self,
        requirement: Dict,
        subtasks: List[Dict],
        implementation_plans: Dict[str, str]
    ) -> str:
        """
        Build a prompt for generating test scenarios.
        
        Args:
            requirement: Requirement with title
            subtasks: List of subtasks
            implementation_plans: Implementation plans for each subtask
        
        Returns:
            Formatted prompt for test generation
        """
        prompt = f"""# Requirement: {requirement.get('title', 'Untitled')}

## Subtasks and Implementation Plans

"""
        for subtask in subtasks:
            title = subtask.get('title', 'Untitled')
            plan = implementation_plans.get(title, 'No plan')
            prompt += f"\n### {title}\n{plan}\n\n"
        
        prompt += """---

# Task: Generate Test Scenarios

For each subtask above, create comprehensive Gherkin-style BDD test scenarios.

For each subtask, include:
1. A success scenario (happy path)
2. A failure scenario (error handling)
3. An edge case scenario (boundary conditions)

## Required Response Format

Your response MUST follow this exact format:

```
## Tests for [Subtask 1 Title]
Feature: [Subtask 1 Title]
  
  Scenario: Successfully [action]
    Given [precondition]
    When [action]
    Then [expected result]
  
  Scenario: [Subtask 1] fails with [error condition]
    Given [precondition with error]
    When [action that triggers error]
    Then [error handling]
  
  Scenario: [Subtask 1] handles edge case
    Given [edge case condition]
    When [action]
    Then [expected behavior]

## Tests for [Subtask 2 Title]
...
```

All subtasks MUST be included. Begin your response now:"""
        
        return prompt


class DynamicContextCollector:
    """Collects dynamic, relevant context from the codebase."""
    
    # Keyword to file pattern mappings
    KEYWORD_PATTERNS = {
        'auth': ['auth', 'user', 'login', 'password', 'session', 'token'],
        'database': ['migration', 'schema', 'model', 'query', 'repository'],
        'ui': ['component', 'page', 'view', 'template', 'form', 'list', 'live', 'liveview'],
        'api': ['controller', 'handler', 'route', 'endpoint', 'request', 'response'],
        'business': ['context', 'service', 'logic', 'calculation', 'processing'],
        'test': ['test', 'spec', 'mock'],
    }
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.file_index = self._build_file_index()
    
    def _build_file_index(self) -> Dict[str, List[Path]]:
        """Build an index of files by category for quick lookup."""
        index = {category: [] for category in self.KEYWORD_PATTERNS.keys()}
        
        try:
            for file_path in self.repo_path.rglob('*'):
                if file_path.is_file() and not self._should_ignore(file_path):
                    relative_path = file_path.relative_to(self.repo_path)
                    path_str = str(relative_path).lower()
                    
                    for category, keywords in self.KEYWORD_PATTERNS.items():
                        if any(keyword in path_str for keyword in keywords):
                            index[category].append(file_path)
        except Exception:
            pass  # Silently ignore indexing errors
        
        return index
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if file should be ignored."""
        ignored = {
            '.git', '.beam', '.defs', '__pycache__', '.pytest_cache',
            'node_modules', '.DS_Store', '.env', '.secret', '.key'
        }
        return any(ignored_dir in path.parts for ignored_dir in ignored)
    
    def collect_context_for_requirement(
        self,
        requirement: Dict,
        max_tokens: int = 5000
    ) -> Dict[str, str]:
        """
        Collect dynamic context based on requirement description.
        
        Args:
            requirement: Requirement with description
            max_tokens: Maximum tokens for context
        
        Returns:
            Dictionary with structure, configs, readme, and examples
        """
        context = {
            'structure': self._get_project_structure(),
            'config_files': self._get_config_files(),
            'readme': self._get_readme(),
            'examples': self._get_relevant_examples(requirement)
        }
        
        return context
    
    def _get_project_structure(self) -> str:
        """Get project structure (tree -L 3)."""
        try:
            result = subprocess.run(
                ['tree', '-L', '3', '-I', 'node_modules|.git|__pycache__|.beam'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.split('\n')[:50]  # Limit to 50 lines
                return '\n'.join(lines)
        except Exception:
            pass
        
        # Fallback: manual tree building
        return self._build_manual_tree()
    
    def _build_manual_tree(self, max_depth: int = 3) -> str:
        """Manually build a tree structure if tree command unavailable."""
        lines = []
        
        def traverse(path: Path, depth: int = 0, prefix: str = ""):
            if depth > max_depth or len(lines) > 50:
                return
            
            try:
                items = sorted(path.iterdir())
                items = [p for p in items if not self._should_ignore(p)]
                
                for i, item in enumerate(items[:20]):  # Limit items per level
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir():
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        traverse(item, depth + 1, next_prefix)
            except Exception:
                pass
        
        lines.append(self.repo_path.name)
        traverse(self.repo_path)
        return '\n'.join(lines[:50])
    
    def _get_config_files(self) -> str:
        """Extract content from important config files."""
        config_files = ['mix.exs', 'package.json', 'requirements.txt', 'setup.py', 'Gemfile']
        result = {}
        
        for config_file in config_files:
            config_path = self.repo_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:500]  # Limit to 500 chars
                        result[config_file] = content
                except Exception:
                    pass
        
        if result:
            output = ""
            for filename, content in result.items():
                output += f"\n### {filename}\n```\n{content}\n...\n```\n"
            return output
        
        return "[No config files found]"
    
    def _get_readme(self) -> str:
        """Extract content from README."""
        readme_files = ['README.md', 'README.txt', 'README']
        
        for readme_file in readme_files:
            readme_path = self.repo_path / readme_file
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()[:800]  # Limit to 800 chars
                        return content
                except Exception:
                    pass
        
        return "[No README found]"
    
    def _get_relevant_examples(self, requirement: Dict) -> str:
        """Get code examples relevant to the requirement."""
        keywords = self._extract_keywords(requirement)
        relevant_files = self._find_relevant_files(keywords)
        
        examples = []
        for file_path in relevant_files[:3]:  # Limit to 3 examples
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()[:300]  # Limit to 300 chars per file
                    relative_path = file_path.relative_to(self.repo_path)
                    examples.append(f"\n### {relative_path}\n```\n{content}\n...\n```")
            except Exception:
                pass
        
        return '\n'.join(examples) if examples else "[No relevant code examples found]"
    
    def _extract_keywords(self, requirement: Dict) -> List[str]:
        """Extract keywords from requirement description."""
        description = requirement.get('description', '').lower()
        title = requirement.get('title', '').lower()
        combined = f"{title} {description}"
        
        keywords = []
        for category, category_keywords in self.KEYWORD_PATTERNS.items():
            for keyword in category_keywords:
                if keyword in combined:
                    keywords.append(keyword)
                    break
        
        return keywords if keywords else ['context', 'service']  # Default keywords
    
    def _find_relevant_files(self, keywords: List[str]) -> List[Path]:
        """Find relevant files based on keywords."""
        relevant = set()
        
        for keyword in keywords:
            for category, files in self.file_index.items():
                for file_path in files:
                    if keyword in str(file_path).lower():
                        relevant.add(file_path)
        
        return sorted(list(relevant))[:5]  # Return up to 5 files


class ResponseParser:
    """Parses LLM responses into structured data."""
    
    def parse_implementation_response(
        self,
        response: str,
        expected_subtasks: List[str]
    ) -> Tuple[Dict[str, str], bool]:
        """
        Parse implementation response from LLM.
        
        Args:
            response: Raw response from LLM
            expected_subtasks: List of expected subtask titles
        
        Returns:
            (parsed_dict, all_present: bool)
        """
        parsed = {}
        
        # Find all "## Implementation for {title}" sections
        pattern = r'## Implementation for (.+?)(?=## Implementation for|$)'
        matches = re.finditer(pattern, response, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            # Extract title from first line only (before first newline)
            full_content = match.group(1)
            first_line = full_content.split('\n')[0].strip()
            steps = '\n'.join(full_content.split('\n')[1:]).strip()
            
            # Try to match with expected subtask
            matched_key = self._fuzzy_match_title(first_line, expected_subtasks)
            if matched_key:
                parsed[matched_key] = steps
        
        # Check if all expected subtasks are present
        all_present = len(parsed) == len(expected_subtasks)
        
        return parsed, all_present
    
    def _fuzzy_match_title(self, provided: str, expected: List[str]) -> Optional[str]:
        """Fuzzy match a provided title against expected titles."""
        provided_lower = provided.lower().strip()
        
        # Exact match
        for expected_title in expected:
            if provided_lower == expected_title.lower():
                return expected_title
        
        # Partial match
        for expected_title in expected:
            if provided_lower in expected_title.lower() or expected_title.lower() in provided_lower:
                return expected_title
        
        return None
    
    def parse_tests_response(self, response: str) -> Dict[str, str]:
        """
        Parse test scenarios response from LLM.
        
        Args:
            response: Raw response from LLM with test scenarios
        
        Returns:
            Dictionary mapping subtask titles to test scenarios
        """
        parsed = {}
        
        # Find all "## Tests for {title}" sections
        pattern = r'## Tests for (.+?)(?=## Tests for|$)'
        matches = re.finditer(pattern, response, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            # Extract title from first line only (before first newline)
            full_content = match.group(1)
            first_line = full_content.split('\n')[0].strip()
            tests = '\n'.join(full_content.split('\n')[1:]).strip()
            parsed[first_line] = tests
        
        return parsed


class InteractiveSession:
    """Manages interactive sessions with the user."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def request_requirement_analysis(
        self,
        requirement: Dict,
        prompt: str,
        req_index: int,
        total_reqs: int
    ) -> str:
        """
        Request user to send prompt to agent and paste response.
        
        Args:
            requirement: The requirement being analyzed
            prompt: The prompt to send to agent
            req_index: Current requirement index
            total_reqs: Total number of requirements
        
        Returns:
            User's pasted response from agent
        """
        self._print_section_header(f"REQ-{req_index:03d}: {requirement.get('title', 'Untitled')}", req_index, total_reqs)
        
        print("\n" + "="*80)
        print("COPY THE PROMPT BELOW AND SEND TO YOUR AGENT")
        print("="*80 + "\n")
        
        print(prompt)
        
        print("\n" + "="*80)
        print("PASTE THE AGENT'S RESPONSE BELOW")
        print("="*80)
        print("\nPaste the agent's response here (end with an empty line):\n")
        
        # Read response from stdin
        response_lines = []
        try:
            while True:
                line = input()
                if line.strip() == "":
                    if response_lines:
                        break
                else:
                    response_lines.append(line)
        except EOFError:
            pass  # Handle EOF gracefully
        
        response = '\n'.join(response_lines)
        return response
    
    def _print_section_header(self, title: str, index: int, total: int):
        """Print a formatted section header."""
        print(f"\n{'─'*80}")
        print(f"[{index}/{total}] {title}")
        print(f"{'─'*80}")
    
    def confirm_action(self, message: str) -> bool:
        """Get user confirmation."""
        while True:
            response = input(f"\n{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
    
    def log(self, message: str, status: str = "INFO"):
        """Log a message with status."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {status}: {message}")


class CompleteTasksSkillV2:
    """Main skill implementation with LLM prompting."""
    
    def __init__(self, requirements_path: str):
        """Initialize the skill."""
        self.requirements_path = Path(requirements_path)
        self.repo_name = self.requirements_path.parent.name
        self.repo_path = self._find_repo_path()
        
        # Load requirements
        with open(self.requirements_path, 'r', encoding='utf-8') as f:
            self.requirements_data = json.load(f)
        
        # Determine requirements key
        self._determine_requirements_key()
        
        # Initialize components
        self.prompt_builder = PromptBuilder()
        self.context_collector = DynamicContextCollector(self.repo_path)
        self.response_parser = ResponseParser()
        self.session = InteractiveSession()
        
        # Storage
        self.codebase_metadata = None
        self.analysis_results = {}
        self.tests_results = {}
    
    def _find_repo_path(self) -> Path:
        """Find the actual git repository path."""
        path_parts = self.requirements_path.parts
        
        if 'Reports' in path_parts:
            reports_idx = path_parts.index('Reports')
            if reports_idx > 0:
                dev_path = Path(*path_parts[:reports_idx])
                actual_repo = dev_path / self.repo_name
                if (actual_repo / '.git').exists():
                    return actual_repo
                return self.requirements_path.parent.parent
        
        # Standard: find git root
        current = self.requirements_path.parent
        while current != current.parent:
            if (current / '.git').exists():
                return current
            current = current.parent
        
        return self.requirements_path.parent.parent
    
    def _determine_requirements_key(self):
        """Determine if using 'main_requirements' or 'requirements' key."""
        if 'main_requirements' in self.requirements_data:
            self.req_key = 'main_requirements'
        elif 'requirements' in self.requirements_data:
            self.req_key = 'requirements'
        else:
            raise ValueError("requirements.json must have 'main_requirements' or 'requirements' key")
    
    def run(self):
        """Execute the full skill workflow."""
        try:
            self.session.log("Starting skill execution", "STARTUP")
            
            # Stage 1: Prepare
            self._stage_1_prepare()
            
            # Stage 2: Analyze with LLM
            self._stage_2_analyze_with_llm()
            
            # Stage 3: Generate Tests
            self._stage_3_generate_tests()
            
            # Stage 4: Finalize
            self._stage_4_finalize()
            
            self.session.log("Skill execution complete", "SUCCESS")
        except Exception as e:
            self.session.log(f"Error: {str(e)}", "ERROR")
            raise
    
    def _stage_1_prepare(self):
        """Stage 1: Prepare requirements and detect metadata."""
        self.session.log("Stage 1: Preparing requirements", "STAGE_1")
        
        # Detect technical requirements
        all_reqs = self.requirements_data[self.req_key]
        technical_reqs = [r for r in all_reqs if r.get('sub_tasks') or r.get('subtasks')]
        
        self.session.log(f"Found {len(technical_reqs)} technical requirements", "STAGE_1")
        
        # Detect language and frameworks (quick heuristic)
        self.codebase_metadata = self._detect_codebase_metadata()
        
        self.session.log(
            f"Detected: {self.codebase_metadata['language']}, "
            f"Frameworks: {', '.join(self.codebase_metadata['frameworks'])}",
            "STAGE_1"
        )
    
    def _detect_codebase_metadata(self) -> Dict:
        """Detect language, frameworks, and modules."""
        language = self._detect_language()
        frameworks = self._detect_frameworks()
        
        return {
            'language': language,
            'frameworks': frameworks,
        }
    
    def _detect_language(self) -> str:
        """Detect programming language by file extensions."""
        file_counts = {}
        
        for ext in self.repo_path.rglob('*'):
            if ext.is_file():
                suffix = ext.suffix.lower()
                if suffix:
                    file_counts[suffix] = file_counts.get(suffix, 0) + 1
        
        language_map = {
            '.ex': 'Elixir',
            '.exs': 'Elixir',
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.rs': 'Rust',
        }
        
        for ext, lang in language_map.items():
            if file_counts.get(ext, 0) > 5:
                return lang
        
        return 'Unknown'
    
    def _detect_frameworks(self) -> List[str]:
        """Detect frameworks used in the project."""
        frameworks = []
        
        # Check for Phoenix (Elixir)
        if (self.repo_path / 'mix.exs').exists():
            try:
                with open(self.repo_path / 'mix.exs', 'r') as f:
                    content = f.read()
                    if 'phoenix' in content:
                        frameworks.append('Phoenix')
                    if 'ecto' in content:
                        frameworks.append('Ecto')
            except Exception:
                pass
        
        # Check for Django (Python)
        if (self.repo_path / 'requirements.txt').exists():
            try:
                with open(self.repo_path / 'requirements.txt', 'r') as f:
                    content = f.read().lower()
                    if 'django' in content:
                        frameworks.append('Django')
            except Exception:
                pass
        
        # Check for Node.js
        if (self.repo_path / 'package.json').exists():
            try:
                with open(self.repo_path / 'package.json', 'r') as f:
                    content = json.load(f)
                    if 'dependencies' in content:
                        deps = content['dependencies']
                        if 'express' in deps:
                            frameworks.append('Express')
                        if 'react' in deps:
                            frameworks.append('React')
            except Exception:
                pass
        
        return frameworks if frameworks else ['Unknown']
    
    def _stage_2_analyze_with_llm(self):
        """Stage 2: Analyze each requirement with LLM prompting."""
        self.session.log("Stage 2: Analyzing requirements with LLM", "STAGE_2")
        
        all_reqs = self.requirements_data[self.req_key]
        technical_reqs = [r for r in all_reqs if r.get('sub_tasks') or r.get('subtasks')]
        
        for req_index, requirement in enumerate(technical_reqs, 1):
            req_id = requirement.get('id', f'REQ-{req_index:03d}')
            
            # Get subtasks
            subtasks = requirement.get('sub_tasks') or requirement.get('subtasks', [])
            if not subtasks:
                continue
            
            # Collect context
            context = self.context_collector.collect_context_for_requirement(requirement)
            
            # Build prompt
            prompt = self.prompt_builder.build_requirement_prompt(
                requirement,
                subtasks,
                context,
                self.codebase_metadata['language'],
                self.codebase_metadata['frameworks']
            )
            
            # Get response from user
            response = self._request_and_parse_response(
                requirement,
                prompt,
                subtasks,
                req_index,
                len(technical_reqs),
                is_test=False
            )
            
            # Store results
            self.analysis_results[req_id] = response
    
    def _request_and_parse_response(
        self,
        requirement: Dict,
        prompt: str,
        subtasks: List[Dict],
        req_index: int,
        total_reqs: int,
        is_test: bool = False,
        max_retries: int = 3
    ) -> Dict[str, str]:
        """Request response from user and parse it."""
        subtask_titles = [s.get('title', f'Subtask {i}') for i, s in enumerate(subtasks, 1)]
        
        for attempt in range(max_retries):
            response = self.session.request_requirement_analysis(
                requirement,
                prompt,
                req_index,
                total_reqs
            )
            
            if is_test:
                parsed = self.response_parser.parse_tests_response(response)
                if parsed:
                    self.session.log(f"Parsed {len(parsed)} test sections", "PARSE")
                    return parsed
            else:
                parsed, all_present = self.response_parser.parse_implementation_response(
                    response,
                    subtask_titles
                )
                
                if all_present:
                    self.session.log(f"Parsed {len(parsed)} implementation sections", "PARSE")
                    return parsed
                else:
                    missing = set(subtask_titles) - set(parsed.keys())
                    self.session.log(
                        f"Missing subtasks: {', '.join(missing)}. Retrying...",
                        "WARNING"
                    )
        
        # If we get here, return what we have
        self.session.log(f"Parsed {len(parsed)} sections after {max_retries} attempts", "WARNING")
        return parsed
    
    def _stage_3_generate_tests(self):
        """Stage 3: Generate test scenarios for each requirement."""
        self.session.log("Stage 3: Generating test scenarios", "STAGE_3")
        
        all_reqs = self.requirements_data[self.req_key]
        technical_reqs = [r for r in all_reqs if r.get('sub_tasks') or r.get('subtasks')]
        
        for req_index, requirement in enumerate(technical_reqs, 1):
            req_id = requirement.get('id', f'REQ-{req_index:03d}')
            
            if req_id not in self.analysis_results:
                continue
            
            # Get subtasks
            subtasks = requirement.get('sub_tasks') or requirement.get('subtasks', [])
            if not subtasks:
                continue
            
            # Build tests prompt
            prompt = self.prompt_builder.build_tests_prompt(
                requirement,
                subtasks,
                self.analysis_results[req_id]
            )
            
            # Get response
            response = self._request_and_parse_response(
                requirement,
                prompt,
                subtasks,
                req_index,
                len(technical_reqs),
                is_test=True
            )
            
            # Store results
            self.tests_results[req_id] = response
    
    def _stage_4_finalize(self):
        """Stage 4: Update JSON and finalize."""
        self.session.log("Stage 4: Finalizing and updating JSON", "STAGE_4")
        
        # Create backup
        backup_path = self.requirements_path.parent / f"requirements-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        shutil.copy(self.requirements_path, backup_path)
        self.session.log(f"Backup created: {backup_path.name}", "STAGE_4")
        
        # Update requirements
        all_reqs = self.requirements_data[self.req_key]
        subtasks_updated = 0
        requirements_updated = 0
        
        for requirement in all_reqs:
            req_id = requirement.get('id')
            subtasks = requirement.get('sub_tasks') or requirement.get('subtasks', [])
            
            if not subtasks or req_id not in self.analysis_results:
                continue
            
            analysis = self.analysis_results.get(req_id, {})
            tests = self.tests_results.get(req_id, {})
            
            for subtask in subtasks:
                subtask_title = subtask.get('title', 'Untitled')
                
                # Update implementation
                if subtask_title in analysis:
                    subtask['implementation'] = analysis[subtask_title]
                    subtasks_updated += 1
                
                # Update tests
                if subtask_title in tests:
                    subtask['test'] = tests[subtask_title]
            
            requirements_updated += 1
        
        # Save updated requirements
        with open(self.requirements_path, 'w', encoding='utf-8') as f:
            json.dump(self.requirements_data, f, indent=2, ensure_ascii=False)
        
        self.session.log(
            f"Updated {requirements_updated} requirements, {subtasks_updated} subtasks",
            "STAGE_4"
        )
        self.session.log(f"Saved: {self.requirements_path}", "STAGE_4")


def main():
    """Entry point for the skill."""
    if len(sys.argv) < 2:
        print("Usage: /complete-tasks requirements.json")
        sys.exit(1)
    
    requirements_path = sys.argv[1]
    
    try:
        skill = CompleteTasksSkillV2(requirements_path)
        skill.run()
        
        print("\n" + "="*80)
        print("✓ SKILL EXECUTION COMPLETE")
        print("="*80)
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
