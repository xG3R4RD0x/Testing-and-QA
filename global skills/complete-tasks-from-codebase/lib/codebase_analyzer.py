"""
Codebase Analyzer - Detects tech stack and extracts patterns
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CodebaseAnalyzer:
    """Analyzes codebase to detect tech stack and patterns"""
    
    # Framework detection patterns
    FRAMEWORKS = {
        "Phoenix": {
            "files": ["mix.exs"],
            "content": ["phoenix"],
            "language": "Elixir",
        },
        "Django": {
            "files": ["manage.py", "settings.py"],
            "content": ["django"],
            "language": "Python",
        },
        "Flask": {
            "files": ["app.py", "wsgi.py"],
            "content": ["flask"],
            "language": "Python",
        },
        "Express": {
            "files": ["package.json"],
            "content": ["express"],
            "language": "JavaScript",
        },
        "Rails": {
            "files": ["Gemfile", "config/routes.rb"],
            "content": ["rails"],
            "language": "Ruby",
        },
        "Spring": {
            "files": ["pom.xml", "build.gradle"],
            "content": ["spring"],
            "language": "Java",
        },
        "FastAPI": {
            "files": ["main.py"],
            "content": ["fastapi"],
            "language": "Python",
        },
    }
    
    # Test framework detection
    TEST_FRAMEWORKS = {
        "ExUnit": ["test/", "test_helper.exs"],
        "pytest": ["tests/", "pytest.ini"],
        "Jest": ["jest.config.js", "package.json"],
        "RSpec": ["spec/", "spec_helper.rb"],
        "JUnit": ["src/test/java"],
    }
    
    # ORM/Database detection
    ORMS = {
        "Ecto": ["lib/*/repo.ex", "mix.exs"],
        "SQLAlchemy": ["requirements.txt", "models/"],
        "ActiveRecord": ["Gemfile", "app/models/"],
        "TypeORM": ["package.json", "src/entities/"],
        "Hibernate": ["pom.xml"],
    }
    
    def __init__(self, logger_instance=None):
        """
        Initialize codebase analyzer
        
        Args:
            logger_instance: Logger instance to use
        """
        self.logger = logger_instance or logger
    
    def analyze(self, project_root: Path) -> Dict:
        """
        Analyze codebase and extract tech stack information
        
        Args:
            project_root: Path to project root
        
        Returns:
            Dict with detected_stack and key_patterns
        """
        try:
            project_root = Path(project_root)
            
            if not project_root.exists():
                self.logger.warning(f"Project root not found: {project_root}")
                return {
                    "detected_stack": {},
                    "key_patterns": {},
                    "confidence": 0,
                }
            
            # Detect tech stack
            detected_stack = self._detect_stack(project_root)
            
            # Extract key patterns
            key_patterns = self._extract_patterns(project_root, detected_stack)
            
            # Calculate confidence
            confidence = self._calculate_confidence(detected_stack)
            
            self.logger.info(
                f"Codebase analysis: {detected_stack.get('framework', 'Unknown')} "
                f"({detected_stack.get('language', 'Unknown')}) - "
                f"confidence: {confidence}%"
            )
            
            return {
                "detected_stack": detected_stack,
                "key_patterns": key_patterns,
                "confidence": confidence,
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing codebase: {e}")
            return {
                "detected_stack": {},
                "key_patterns": {},
                "confidence": 0,
                "error": str(e),
            }
    
    def _detect_stack(self, project_root: Path) -> Dict:
        """
        Detect programming language and framework
        
        Args:
            project_root: Project root path
        
        Returns:
            Dict with language, framework, version info
        """
        detected = {
            "language": None,
            "framework": None,
            "version": None,
            "orm": None,
            "test_framework": None,
        }
        
        # Check for framework-specific files
        for framework, config in self.FRAMEWORKS.items():
            if self._check_framework(project_root, config):
                detected["framework"] = framework
                detected["language"] = config["language"]
                self.logger.debug(f"Detected framework: {framework}")
                break
        
        # Detect ORM
        orm = self._detect_orm(project_root)
        if orm:
            detected["orm"] = orm
        
        # Detect test framework
        test_fw = self._detect_test_framework(project_root)
        if test_fw:
            detected["test_framework"] = test_fw
        
        return detected
    
    def _check_framework(self, project_root: Path, framework_config: Dict) -> bool:
        """
        Check if framework is present in project
        
        Args:
            project_root: Project root path
            framework_config: Framework configuration dict
        
        Returns:
            True if framework detected
        """
        # Check for specific files
        for filename in framework_config.get("files", []):
            filepath = project_root / filename
            if filepath.exists():
                return True
        
        # Check for content in common files
        for content_marker in framework_config.get("content", []):
            if self._search_content(project_root, content_marker):
                return True
        
        return False
    
    def _detect_orm(self, project_root: Path) -> Optional[str]:
        """
        Detect ORM used in project
        
        Args:
            project_root: Project root path
        
        Returns:
            ORM name or None
        """
        for orm, patterns in self.ORMS.items():
            for pattern in patterns:
                for filepath in project_root.glob(pattern):
                    if filepath.exists():
                        self.logger.debug(f"Detected ORM: {orm}")
                        return orm
        
        return None
    
    def _detect_test_framework(self, project_root: Path) -> Optional[str]:
        """
        Detect test framework used in project
        
        Args:
            project_root: Project root path
        
        Returns:
            Test framework name or None
        """
        for test_fw, patterns in self.TEST_FRAMEWORKS.items():
            for pattern in patterns:
                for filepath in project_root.glob(pattern):
                    if filepath.exists():
                        self.logger.debug(f"Detected test framework: {test_fw}")
                        return test_fw
        
        return None
    
    def _search_content(self, project_root: Path, search_term: str) -> bool:
        """
        Search for content in common config files
        
        Args:
            project_root: Project root path
            search_term: Term to search for
        
        Returns:
            True if found
        """
        common_files = [
            "package.json",
            "mix.exs",
            "requirements.txt",
            "Gemfile",
            "pom.xml",
            "build.gradle",
        ]
        
        for filename in common_files:
            filepath = project_root / filename
            if filepath.exists():
                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    if search_term.lower() in content.lower():
                        return True
                except Exception as e:
                    self.logger.debug(f"Failed to read {filename}: {e}")
        
        return False
    
    def _extract_patterns(self, project_root: Path, detected_stack: Dict) -> Dict:
        """
        Extract key file patterns based on detected stack
        
        Args:
            project_root: Project root path
            detected_stack: Detected stack info
        
        Returns:
            Dict with key patterns
        """
        patterns = {}
        
        framework = detected_stack.get("framework", "").lower()
        
        if "phoenix" in framework:
            patterns.update({
                "migration_structure": "lib/*/migrations/",
                "schema_structure": "lib/*/schemas/",
                "liveview_structure": "lib/*_web/live/",
                "controller_structure": "lib/*_web/controllers/",
                "component_structure": "lib/*_web/components/",
                "test_structure": "test/",
                "context_structure": "lib/*/",
            })
        
        elif "django" in framework:
            patterns.update({
                "migration_structure": "*/migrations/",
                "model_structure": "*/models.py",
                "view_structure": "*/views.py",
                "test_structure": "tests/",
                "settings_structure": "*/settings.py",
            })
        
        elif "rails" in framework:
            patterns.update({
                "migration_structure": "db/migrate/",
                "model_structure": "app/models/",
                "controller_structure": "app/controllers/",
                "view_structure": "app/views/",
                "test_structure": "spec/ or test/",
            })
        
        elif "express" in framework or "fastapi" in framework:
            patterns.update({
                "route_structure": "routes/ or src/routes/",
                "controller_structure": "controllers/ or src/controllers/",
                "model_structure": "models/ or src/models/",
                "test_structure": "tests/ or __tests__/",
            })
        
        elif "spring" in framework:
            patterns.update({
                "entity_structure": "src/main/java/*/entity/",
                "repository_structure": "src/main/java/*/repository/",
                "service_structure": "src/main/java/*/service/",
                "controller_structure": "src/main/java/*/controller/",
                "test_structure": "src/test/java/",
            })
        
        return patterns
    
    def _calculate_confidence(self, detected_stack: Dict) -> int:
        """
        Calculate confidence score for detection
        
        Args:
            detected_stack: Detected stack dict
        
        Returns:
            Confidence percentage (0-100)
        """
        score = 0
        
        if detected_stack.get("framework"):
            score += 40
        if detected_stack.get("language"):
            score += 30
        if detected_stack.get("orm"):
            score += 20
        if detected_stack.get("test_framework"):
            score += 10
        
        return score
