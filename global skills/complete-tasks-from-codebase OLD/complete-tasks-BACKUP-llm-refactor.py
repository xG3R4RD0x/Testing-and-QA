#!/usr/bin/env python3
"""
Complete Tasks from Codebase Skill - Main Implementation

This is the executable skill for OpenCode that enriches requirements.json with:
- test: Gherkin test scenarios
- implementation: Step-by-step guidance for subtasks

Usage:
  /complete-tasks <path-to-requirements.json>

The skill operates in 3 stages:
1. Stage 1: Analyze codebase structure (compact JSON analysis)
2. Stage 2: Loop through requirements and subtasks, generating tests + implementation
3. Stage 3: Update JSON file with enriched content
"""

import json
import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class CompleteTasksSkill:
    """Main skill implementation for enriching requirements with tests and implementation guidance."""
    
    def __init__(self, requirements_path: str, use_llm_translation: bool = True):
        """Initialize the skill with a requirements.json file path."""
        self.requirements_path = Path(requirements_path)
        self.use_llm_translation = use_llm_translation
        
        # Extract repo name from path
        # Expected structure: /path/Reports/{repo_name}/requirements.json
        path_parts = self.requirements_path.parts
        self.repo_name = self.requirements_path.parent.name
        
        # Try to find the actual git repository
        # First, check if we're in a Reports/{repo_name} structure
        if 'Reports' in path_parts:
            reports_idx = path_parts.index('Reports')
            # The repo should be at parent of Reports
            if reports_idx > 0:
                dev_path = Path(*path_parts[:reports_idx])
                actual_repo = dev_path / self.repo_name
                if (actual_repo / '.git').exists():
                    self.repo_path = actual_repo
                else:
                    self.repo_path = self.requirements_path.parent.parent
            else:
                self.repo_path = self.requirements_path.parent.parent
        else:
            # Standard structure: find git root
            current = self.requirements_path.parent
            found = False
            while current != current.parent:
                if (current / '.git').exists():
                    self.repo_path = current
                    found = True
                    break
                current = current.parent
            if not found:
                self.repo_path = self.requirements_path.parent.parent
        
        # Validate file exists
        if not self.requirements_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {requirements_path}")
        
        # Load requirements
        with open(self.requirements_path, 'r', encoding='utf-8') as f:
            self.requirements_data = json.load(f)
        
        # Initialize containers
        self.codebase_analysis = None
        self.enriched_data = None
        self.processed_requirements = []
        
    def validate_requirements_structure(self) -> bool:
        """Validate that requirements.json has the correct structure."""
        # Support both 'main_requirements' and 'requirements' keys
        if 'main_requirements' in self.requirements_data:
            self.req_key = 'main_requirements'
        elif 'requirements' in self.requirements_data:
            self.req_key = 'requirements'
        else:
            raise ValueError(
                f"Invalid requirements structure. Expected either 'main_requirements' or 'requirements'. "
                f"Found: {list(self.requirements_data.keys())}"
            )
        
        if not isinstance(self.requirements_data[self.req_key], list):
            raise ValueError(f"{self.req_key} must be a list")
        
        return True
    
    def log(self, message: str, stage: str = "INFO") -> None:
        """Log messages for user visibility."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {stage}: {message}")
    
    def detect_language(self, text: str) -> str:
        """
        Simple language detection for German vs English.
        Returns 'de' for German, 'en' for English.
        """
        if not text or len(text.strip()) < 5:
            return 'en'  # Default to English
        
        text_lower = text.lower()
        
        # German common words and patterns (including variations)
        german_words = {
            'der', 'die', 'das', 'ist', 'ein', 'eine', 'von', 'zu', 'mit', 'für',
            'und', 'oder', 'nicht', 'aber', 'wenn', 'dann', 'es', 'sich', 'einen',
            'dem', 'den', 'des', 'wie', 'hier', 'doch', 'auch', 'sehr', 'erst',
            'werden', 'hätte', 'hätte', 'über', 'unter', 'zwischen', 'während',
            'implementation', 'anforderungen', 'schritt', 'schritte', 'erstelle',
            'implementiere', 'erzeuge', 'überprüfe', 'integrier', 'dokumentiere',
            'patienten', 'ohne', 'therapieplan', 'verwaltungsbereich', 'patientenübersicht',
            'vorgefiltert', 'sortiert', 'listen', 'formulare', 'eintrag', 'löschung',
            'auflistung', 'ableitung', 'erstellung', 'validierung', 'integrier', 'bearbeitung',
            'schaltflächen', 'ändern', 'zuweisung', 'beschränkung', 'veröffentlichung',
            'softdelete', 'rücksprache', 'technische', 'feature', 'feedback', 'gespräche',
            'nachsorge', 'überarbeitung', 'erweiterung', 'kategorien', 'status', 'entwurf',
            'aktiv', 'veraltet', 'verhalten', 'export', 'rohdaten', 'druckansicht',
            'abrechnung', 'abrechnungszeitraum', 'filterung', 'filtermöglichkeit',
            'projektmanagement', 'automatisierte', 'testerstellung', 'web-version',
            'überführung', 'produktionsqualität', 'grundsystem', 'demo', 'medientypen',
            'audio', 'video', 'pdf', 'upload', 'inhalt', 'inhalte', 'formular',
            'liveview', 'context', 'ecto', 'schema', 'exunit', 'controller',
            'middleware', 'plugs', 'testlauf', 'kontrollierten'
        }
        
        # English common words and patterns
        english_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'being',
            'and', 'or', 'not', 'but', 'if', 'then', 'it', 'itself', 'one',
            'with', 'of', 'to', 'for', 'from', 'as', 'at', 'by', 'in', 'on',
            'implementation', 'requirements', 'step', 'steps', 'create', 'implement',
            'generate', 'check', 'integrate', 'document', 'test', 'testing',
            'patients', 'without', 'therapy', 'plan', 'admin', 'area', 'filter',
            'sort', 'lists', 'form', 'entry', 'deletion', 'listing', 'derivation',
            'creation', 'validation', 'integration', 'editing', 'buttons', 'change',
            'assignment', 'restriction', 'publication', 'soft', 'delete', 'review',
            'consultation', 'technical', 'feature', 'feedback', 'conversation',
            'aftercare', 'revision', 'extension', 'categories', 'status', 'draft',
            'active', 'outdated', 'behavior', 'export', 'raw', 'data', 'print',
            'billing', 'billing', 'period', 'filtering', 'filter', 'option',
            'project', 'management', 'automated', 'test', 'creation', 'web'
        }
        
        # Count word matches
        words = re.findall(r'\b\w+\b', text_lower)
        
        german_count = sum(1 for word in words if word in german_words)
        english_count = sum(1 for word in words if word in english_words)
        
        # Check for German umlauts and special characters
        if re.search(r'[äöüß]', text_lower):
            german_count += 5  # Strong indicator of German
        
        # German articles are strong indicators
        if re.search(r'\b(der|die|das)\s', text_lower):
            german_count += 3
        
        # Decide based on counts
        if german_count > english_count:
            return 'de'
        return 'en'
    
    def is_german(self, text: str) -> bool:
        """Check if text is primarily in German."""
        lang = self.detect_language(text)
        return lang == 'de'
    
    def translate_to_english(self, text: str) -> str:
        """Translate text to English using LLM if needed."""
        # Check if already in English
        if not self.is_german(text):
            return text
        
        # Skip translation if LLM translation is disabled
        if not self.use_llm_translation:
            return text
        
        try:
            # Call LLM for translation
            prompt = f"""Translate the following German text to English. 
Keep the same structure and meaning. Return ONLY the translated text without any explanation.

German text:
{text}

English translation:"""
            
            # Use subprocess to call Claude via OpenCode's LLM
            result = subprocess.run(
                ['opencode', 'call-llm', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                translated = result.stdout.strip()
                return translated
            else:
                # If LLM call fails, return original text
                self.log(f"Translation failed, returning original text", "WARN")
                return text
        except Exception as e:
            self.log(f"Translation error: {str(e)}", "WARN")
            return text
    
    def create_backup(self) -> str:
        """Create a timestamped backup of the original requirements file."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = self.requirements_path.parent / f"requirements-backup-{timestamp}.json"
        
        with open(self.requirements_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.log(f"Backup created: {backup_path.name}", "BACKUP")
        return str(backup_path)
    
    # ========================================================================
    # STAGE 1: CODEBASE ANALYSIS
    # ========================================================================
    
    def stage_1_analyze_codebase(self) -> Dict[str, Any]:
        """
        Stage 1: Analyze codebase structure.
        
        This returns a compact JSON analysis that will be reused in all Stage 2 prompts.
        In a real OpenCode implementation, this prompt would be sent to the LLM.
        
        For now, we generate a reasonable analysis based on the project structure.
        """
        self.log("Starting Stage 1: Codebase Analysis", "STAGE_1")
        
        analysis = self._analyze_project_structure()
        self.codebase_analysis = analysis
        
        self.log(
            f"Detected: {analysis['language']}, Frameworks: {', '.join(analysis['frameworks'])}",
            "STAGE_1"
        )
        
        return analysis
    
    def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze the project structure to create codebase analysis."""
        # This is a heuristic analysis. In production, this would be the LLM response.
        
        # Detect language by file extensions
        language = self._detect_language()
        frameworks = self._detect_frameworks(language)
        key_modules = self._find_key_modules()
        patterns = self._detect_patterns(language, frameworks)
        dependencies = self._extract_dependencies(language)
        test_framework = self._detect_test_framework(language)
        code_style = self._detect_code_style(language, frameworks)
        
        return {
            "language": language,
            "frameworks": frameworks,
            "key_modules": key_modules,
            "architecture_patterns": patterns,
            "key_dependencies": dependencies,
            "test_framework": test_framework,
            "code_style": code_style
        }
    
    def _detect_language(self) -> str:
        """Detect the primary programming language."""
        file_counts = {}
        
        for ext in self.repo_path.rglob('*'):
            if ext.is_file():
                suffix = ext.suffix.lower()
                if suffix:
                    file_counts[suffix] = file_counts.get(suffix, 0) + 1
        
        # Language detection based on file extensions
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
        
        # Default based on first file found
        most_common = max(file_counts.items(), key=lambda x: x[1], default=('.unknown', 0))
        ext = most_common[0]
        return language_map.get(ext, 'Unknown')
    
    def _detect_frameworks(self, language: str) -> List[str]:
        """Detect frameworks used in the project."""
        frameworks = []
        
        # Check for Phoenix (Elixir)
        if (self.repo_path / 'mix.exs').exists():
            with open(self.repo_path / 'mix.exs', 'r') as f:
                content = f.read()
                if 'phoenix' in content:
                    frameworks.append('Phoenix')
                if 'ecto' in content:
                    frameworks.append('Ecto')
                if 'liveview' in content:
                    frameworks.append('LiveView')
                if 'oban' in content:
                    frameworks.append('Oban')
        
        # Check for Django (Python)
        if (self.repo_path / 'requirements.txt').exists():
            with open(self.repo_path / 'requirements.txt', 'r') as f:
                content = f.read().lower()
                if 'django' in content:
                    frameworks.append('Django')
                if 'flask' in content:
                    frameworks.append('Flask')
        
        # Check for package.json (Node.js)
        if (self.repo_path / 'package.json').exists():
            with open(self.repo_path / 'package.json', 'r') as f:
                content = json.load(f)
                if 'dependencies' in content:
                    deps = content['dependencies']
                    if 'express' in deps:
                        frameworks.append('Express')
                    if 'react' in deps:
                        frameworks.append('React')
                    if 'next' in deps:
                        frameworks.append('Next.js')
        
        return frameworks if frameworks else ['Unknown']
    
    def _find_key_modules(self) -> List[str]:
        """Find key modules/packages in the project."""
        modules = []
        
        # For Elixir projects
        lib_dir = self.repo_path / 'lib'
        if lib_dir.exists():
            for item in lib_dir.iterdir():
                if item.is_dir():
                    rel_path = item.relative_to(self.repo_path)
                    modules.append(str(rel_path))
        
        # For Python projects
        src_dir = self.repo_path / 'src'
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_dir():
                    rel_path = item.relative_to(self.repo_path)
                    modules.append(str(rel_path))
        
        # For Node.js projects
        src_dir = self.repo_path / 'src'
        if (self.repo_path / 'package.json').exists() and src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_dir():
                    rel_path = item.relative_to(self.repo_path)
                    modules.append(str(rel_path))
        
        return modules[:7]  # Return top 7 modules
    
    def _detect_patterns(self, language: str, frameworks: List[str]) -> List[str]:
        """Detect architectural patterns."""
        patterns = []
        
        if 'Phoenix' in frameworks:
            patterns.append('MVC with LiveView for real-time UI updates')
        if 'Django' in frameworks:
            patterns.append('MTV (Model-Template-View) architecture')
        if 'Express' in frameworks:
            patterns.append('REST API with middleware pattern')
        if 'React' in frameworks:
            patterns.append('Component-based reactive UI')
        
        if 'Ecto' in frameworks:
            patterns.append('Context modules for domain isolation')
        
        if len(patterns) == 0:
            patterns.append('Modular architecture')
        
        return patterns
    
    def _extract_dependencies(self, language: str = None) -> Dict[str, str]:
        """Extract key dependencies from the project."""
        deps = {}
        
        # From mix.exs (Elixir)
        if (self.repo_path / 'mix.exs').exists():
            with open(self.repo_path / 'mix.exs', 'r') as f:
                content = f.read()
                # Simple regex to find dependency declarations
                matches = re.findall(r'\{:(\w+),\s*"~>\s*([\d.]+)"', content)
                for name, version in matches[:6]:
                    deps[name] = f"~> {version}"
        
        # From requirements.txt (Python)
        if (self.repo_path / 'requirements.txt').exists():
            with open(self.repo_path / 'requirements.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if '==' in line:
                        name, version = line.split('==')
                        deps[name] = version
                        if len(deps) >= 6:
                            break
        
        return deps if deps else {}
    
    def _detect_test_framework(self, language: str) -> str:
        """Detect the test framework used."""
        if (self.repo_path / 'mix.exs').exists():
            return 'ExUnit'
        if (self.repo_path / 'pytest.ini').exists() or (self.repo_path / 'setup.cfg').exists():
            return 'pytest'
        if (self.repo_path / 'package.json').exists():
            return 'Jest'
        return 'Unknown'
    
    def _detect_code_style(self, language: str, frameworks: List[str]) -> str:
        """Detect code style conventions."""
        if language == 'Elixir':
            return 'Elixir conventions with pipes, pattern matching'
        if language == 'Python':
            return 'PEP 8 style guide'
        if language == 'JavaScript' or language == 'TypeScript':
            return 'ESLint/Prettier conventions'
        if language == 'Java':
            return 'Google Java Style Guide'
        return 'Standard conventions'
    
    # ========================================================================
    # STAGE 2: REQUIREMENTS AND SUBTASKS ENRICHMENT
    # ========================================================================
    
    def stage_2_enrich_requirements(self) -> Dict[str, Any]:
        """
        Stage 2: Loop through requirements and subtasks, generating tests and implementation.
        
        This stage processes each requirement and its subtasks, generating:
        - test: Gherkin test scenarios
        - implementation: Step-by-step guidance for subtasks
        """
        self.log("Starting Stage 2: Requirements Enrichment", "STAGE_2")
        
        # Deep copy the requirements structure
        self.enriched_data = json.loads(json.dumps(self.requirements_data))
        
        # Get the correct requirements key
        req_list = self.enriched_data.get(self.req_key, [])
        
        for req_idx, requirement in enumerate(req_list, 1):
            req_id = requirement.get('id', f'REQ-{req_idx:03d}')
            req_title = requirement.get('title', 'Untitled')
            
            self.log(f"Processing requirement {req_id}: {req_title}", "STAGE_2")
            
            # Generate tests for the requirement if not already present or if error
            test_val = requirement.get('test', '')
            if not test_val or 'Error' in str(test_val):
                requirement['test'] = self._generate_requirement_tests(
                    req_id, req_title, requirement.get('description', '')
                )
            
            # Process subtasks - support both 'sub_tasks' and 'subtasks'
            subtasks_key = 'sub_tasks' if 'sub_tasks' in requirement else 'subtasks'
            subtasks_list = requirement.get(subtasks_key, [])
            
            if subtasks_list:
                for task_idx, subtask in enumerate(subtasks_list, 1):
                    task_id = subtask.get('id', f'{req_id}-{task_idx:03d}')
                    task_title = subtask.get('title', 'Untitled')
                    
                    self.log(f"  Processing subtask {task_id}: {task_title}", "STAGE_2")
                    
                    # Generate implementation guidance if not present or if error
                    impl_val = subtask.get('implementation', '')
                    if not impl_val or 'Error' in str(impl_val):
                        subtask['implementation'] = self._generate_subtask_implementation(
                            task_id,
                            task_title,
                            subtask.get('description', ''),
                            req_title,
                            subtasks_list,
                            task_idx
                        )
                    
                    # Generate tests for the subtask if not present or if error
                    test_val = subtask.get('test', '')
                    if not test_val or 'Error' in str(test_val):
                        subtask['test'] = self._generate_subtask_tests(
                            task_id, task_title, subtask.get('description', '')
                        )
        
        
        self.log("Stage 2 complete: All requirements and subtasks enriched", "STAGE_2")
        return self.enriched_data
    
    def _generate_requirement_tests(self, req_id: str, title: str, description: str) -> str:
        """Generate Gherkin test scenarios for a requirement in English."""
        # Translate title and description if needed
        title_en = self.translate_to_english(title)
        description_en = self.translate_to_english(description)
        
        gherkin = f"""Feature: {title_en}
  Description: {description_en}
  
  Scenario: Successful {title_en.lower()} with valid inputs
    Given the system is ready to handle {title_en.lower()}
    When the user performs the required {title_en.lower()} action
    Then the system processes the request successfully
    And the result is confirmed
  
  Scenario: {title_en} fails with invalid data
    Given invalid data is provided for {title_en.lower()}
    When the user attempts the {title_en.lower()} action
    Then the system rejects the request
    And an appropriate error message is displayed
  
  Scenario: Edge case in {title_en}
    Given boundary conditions exist for {title_en.lower()}
    When the user performs the {title_en.lower()} at the boundary
    Then the system handles it gracefully
    And appropriate validation occurs"""
        
        return gherkin
    
    def _generate_subtask_implementation(
        self,
        task_id: str,
        task_title: str,
        description: str,
        req_title: str,
        all_subtasks: List[Dict],
        task_index: int
    ) -> str:
        """Generate implementation guidance for a subtask based on actual codebase analysis."""
        language = self.codebase_analysis.get('language', 'Unknown') if self.codebase_analysis else 'Unknown'
        frameworks = self.codebase_analysis.get('frameworks', []) if self.codebase_analysis else []
        key_modules = self.codebase_analysis.get('key_modules', []) if self.codebase_analysis else []
        patterns = self.codebase_analysis.get('architecture_patterns', []) if self.codebase_analysis else []
        
        impl = f"""## Overview
{task_title} is a core component of {req_title}. {description}

## Key Files
"""
        
        # Suggest files based on actual codebase modules and frameworks
        if key_modules:
            # Determine the most relevant module based on the task
            main_module = key_modules[0] if key_modules else "lib"
            ext = self._get_file_extension()
            
            # Framework-specific suggestions
            if 'Phoenix' in frameworks:
                impl += f"- {main_module}/contexts/: Context module for {task_title}\n"
                impl += f"- {main_module}/services/: Service layer implementation\n"
                impl += f"- test/{main_module}/: Test file for this functionality\n"
            elif 'Django' in frameworks:
                impl += f"- {main_module}/models.py: Model definition\n"
                impl += f"- {main_module}/views.py: View/Handler implementation\n"
                impl += f"- {main_module}/services.py: Business logic\n"
            elif 'Express' in frameworks or 'React' in frameworks:
                impl += f"- src/{main_module}/: Core module implementation\n"
                impl += f"- src/{main_module}/handlers.{ext}: Request handlers\n"
                impl += f"- tests/{main_module}/__tests__.{ext}: Test suite\n"
            else:
                impl += f"- {main_module}/implementation.{ext}: Core implementation\n"
                impl += f"- test/{main_module}/: Test file\n"
        else:
            impl += f"- lib/: Core implementation\n"
            impl += f"- test/: Test file\n"
        
        # Generate specific implementation steps based on patterns
        impl += f"\n## Implementation Steps\n"
        
        steps = self._generate_framework_specific_steps(
            task_title, req_title, language, frameworks, patterns
        )
        
        for i, step in enumerate(steps, 1):
            impl += f"{i}. {step}\n"
        
        # Add cross-references to other subtasks if applicable
        other_tasks = [t.get('title') for i, t in enumerate(all_subtasks) if i != task_index - 1]
        if other_tasks:
            impl += f"\n## Dependencies\n"
            for other_task in other_tasks[:3]:  # Limit to 3 references
                impl += f"- Coordinate with: {other_task}\n"
        
        return impl
    
    def _generate_framework_specific_steps(
        self,
        task_title: str,
        req_title: str,
        language: str,
        frameworks: List[str],
        patterns: List[str]
    ) -> List[str]:
        """Generate framework-specific implementation steps."""
        steps = []
        
        if 'Phoenix' in frameworks:
            # Phoenix/Elixir specific steps
            steps = [
                f"Create a context module for {task_title} in lib/{self.repo_name}/",
                f"Define the data schema using Ecto in the schema file",
                f"Implement the main functions in the context (create, read, update, delete as needed)",
                f"Add business logic and validation in the context functions",
                f"Create tests in test/{self.repo_name}/ using ExUnit",
                f"Integrate with the appropriate controller or LiveView component",
                f"Add any necessary plugs or middleware for {req_title}",
            ]
        elif 'Django' in frameworks:
            # Django specific steps
            steps = [
                f"Define the model for {task_title} in models.py",
                f"Create migrations for the new model",
                f"Implement the service/business logic in services.py",
                f"Create views or viewsets for {task_title}",
                f"Add URL routes for the new endpoints",
                f"Write tests in tests/ using Django TestCase",
                f"Add any necessary serializers for API endpoints",
            ]
        elif 'Express' in frameworks:
            # Express/Node.js specific steps
            steps = [
                f"Create request handlers in src/{self.repo_name}/handlers.ts",
                f"Implement the service layer with the business logic for {task_title}",
                f"Add input validation using a validation middleware",
                f"Implement error handling for {task_title}",
                f"Create unit tests in tests/{self.repo_name}/__tests__.ts",
                f"Integrate handlers into the route definitions",
                f"Add TypeScript type definitions for {task_title}",
            ]
        elif 'React' in frameworks:
            # React specific steps
            steps = [
                f"Create a custom hook for {task_title} logic if needed",
                f"Implement component for {task_title}",
                f"Add state management (useState, Context, or Redux) as required",
                f"Implement event handlers and data fetching",
                f"Add styling and responsive design",
                f"Write component tests using React Testing Library",
                f"Integrate with the parent components of {req_title}",
            ]
        else:
            # Generic steps for unknown frameworks
            steps = [
                f"Create the core implementation for {task_title}",
                f"Define the data structures and interfaces needed",
                f"Implement the main logic according to {req_title} requirements",
                f"Add input validation and error handling",
                f"Write comprehensive unit tests",
                f"Integrate with existing components",
                f"Document the implementation with examples",
            ]
        
        return steps
    
    def _generate_subtask_tests(self, task_id: str, task_title: str, description: str) -> str:
        """Generate Gherkin test scenarios for a subtask in English."""
        # Translate title and description if needed
        task_title_en = self.translate_to_english(task_title)
        description_en = self.translate_to_english(description)
        
        gherkin = f"""Feature: {task_title_en}
  Description: {description_en}
  
  Scenario: Successfully execute {task_title_en.lower()}
    Given preconditions for {task_title_en.lower()} are met
    When the {task_title_en.lower()} action is performed
    Then the expected result is achieved
    And the state is updated correctly
  
  Scenario: {task_title_en} fails with bad inputs
    Given invalid input for {task_title_en.lower()}
    When the action is attempted with bad data
    Then an error is properly handled
    And the system remains in a valid state
  
  Scenario: Edge case handling for {task_title_en.lower()}
    Given boundary conditions exist
    When the action is performed at the boundary
    Then the system behaves correctly
    And appropriate safeguards are in place"""
        
        return gherkin
    
    def _get_file_extension(self) -> str:
        """Get the file extension for the detected language."""
        if not self.codebase_analysis:
            return 'ts'
        
        lang = self.codebase_analysis.get('language', '').lower()
        ext_map = {
            'elixir': 'ex',
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java',
            'go': 'go',
            'ruby': 'rb',
        }
        return ext_map.get(lang, 'ts')
    
    def generate_issue_body(
        self,
        description: str,
        implementation: str,
        test_scenarios: str,
        subtasks: List[Dict] = None
    ) -> str:
        """
        Generate the complete issue body with preserved description and added implementation + test sections.
        
        Format:
        - Original description (preserved)
        - ## Implementation section
        - ## Tests section
        - ## Subtasks section (if applicable, as markdown checklist)
        """
        body = description + "\n\n"
        
        # Add Implementation section
        body += "## Implementation\n\n"
        body += implementation + "\n\n"
        
        # Add Tests section
        body += "## Tests\n\n"
        body += test_scenarios + "\n\n"
        
        # Add Subtasks as markdown checklist if they exist
        if subtasks:
            body += "## Subtasks\n\n"
            for subtask in subtasks:
                title = subtask.get('title', 'Untitled')
                body += f"- [ ] {title}\n"
            body += "\n"
        
        return body
    
    # ========================================================================
    # STAGE 3: UPDATE JSON FILE
    # ========================================================================
    
    def stage_3_update_json_file(self) -> None:
        """
        Stage 3: Write enriched data back to the requirements.json file.
        """
        self.log("Starting Stage 3: JSON File Update", "STAGE_3")
        
        if self.enriched_data is None:
            raise RuntimeError("No enriched data to write. Run stage_2_enrich_requirements first.")
        
        # Write the enriched data with proper formatting
        with open(self.requirements_path, 'w', encoding='utf-8') as f:
            json.dump(self.enriched_data, f, indent=2, ensure_ascii=False)
        
        self.log(f"Requirements file updated: {self.requirements_path}", "STAGE_3")
        
        # Print summary
        req_count = len(self.enriched_data.get('main_requirements', []))
        task_count = sum(
            len(r.get('sub_tasks', [])) for r in self.enriched_data.get('main_requirements', [])
        )
        
        self.log(f"Enriched {req_count} requirements with {task_count} subtasks", "SUMMARY")
    
    # ========================================================================
    # MAIN EXECUTION
    # ========================================================================
    
    def run(self) -> Dict[str, Any]:
        """Execute the skill in all 3 stages."""
        try:
            # Validate structure
            self.validate_requirements_structure()
            
            # Create backup
            self.create_backup()
            
            # Stage 1: Analyze codebase
            self.stage_1_analyze_codebase()
            
            # Stage 2: Enrich requirements
            self.stage_2_enrich_requirements()
            
            # Stage 3: Update JSON
            self.stage_3_update_json_file()
            
            self.log("SKILL EXECUTION COMPLETE", "SUCCESS")
            
            # Count total subtasks from either 'sub_tasks' or 'subtasks'
            total_subtasks = 0
            req_list = self.enriched_data.get(self.req_key, [])
            for r in req_list:
                subtasks = r.get('subtasks', r.get('sub_tasks', []))
                total_subtasks += len(subtasks)
            
            return {
                "success": True,
                "requirements_path": str(self.requirements_path),
                "requirements_enriched": len(req_list),
                "total_subtasks": total_subtasks,
                "codebase_analysis": self.codebase_analysis
            }
        
        except Exception as e:
            self.log(f"ERROR: {str(e)}", "ERROR")
            raise


def main():
    """Entry point for the skill."""
    if len(sys.argv) < 2:
        print("Usage: python complete-tasks.py <path-to-requirements.json>")
        sys.exit(1)
    
    requirements_path = sys.argv[1]
    
    try:
        skill = CompleteTasksSkill(requirements_path)
        result = skill.run()
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"FATAL ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
