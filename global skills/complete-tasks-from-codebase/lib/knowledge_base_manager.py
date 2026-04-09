"""
Knowledge Base Manager - Detects and caches project documentation
"""

import logging
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class KnowledgeBaseManager:
    """Manages detection, caching, and retrieval of project knowledge bases"""
    
    # Files to look for in project root
    KB_FILES = [
        "ARCHITECTURE.md",
        "PATTERNS.md",
        "TECH-STACK.md",
        "API-SPEC.md",
        "DATABASE-SCHEMA.md",
        "PROJECT-STRUCTURE.md",
        "GUIDELINES.md",
        "AGENTS.md",
        "README.md",
    ]
    
    # Directories to scan for docs
    KB_DIRECTORIES = [
        "docs",
        "doc",
        ".docs",
        "documentation",
    ]
    
    def __init__(self, logger_instance=None):
        """
        Initialize knowledge base manager
        
        Args:
            logger_instance: Logger instance to use
        """
        self.logger = logger_instance or logger
        self.temp_cache_dir = None
        self.cache_metadata = {}
    
    def detect_and_cache(self, project_root: Path) -> Dict:
        """
        Detect available KB files and create temporary cache
        
        Args:
            project_root: Path to project root
        
        Returns:
            Dict with keys:
            - available: bool
            - cache_path: str or None
            - summary: str (combined KB content)
            - file_count: int
            - files_found: list of filenames
        """
        try:
            project_root = Path(project_root)
            if not project_root.exists():
                self.logger.warning(f"Project root not found: {project_root}")
                return {
                    "available": False,
                    "cache_path": None,
                    "summary": "",
                    "file_count": 0,
                    "files_found": [],
                }
            
            # Find all KB files
            kb_files = self._find_kb_files(project_root)
            
            if not kb_files:
                self.logger.info("No knowledge base files found")
                return {
                    "available": False,
                    "cache_path": None,
                    "summary": "",
                    "file_count": 0,
                    "files_found": [],
                }
            
            # Create temporary cache
            cache_path = self._create_temp_cache(project_root, kb_files)
            summary = self._create_summary(kb_files)
            
            self.logger.info(
                f"Knowledge base cached: {len(kb_files)} files, "
                f"cache at {cache_path}"
            )
            
            return {
                "available": True,
                "cache_path": str(cache_path),
                "summary": summary,
                "file_count": len(kb_files),
                "files_found": list(kb_files.keys()),
            }
        
        except Exception as e:
            self.logger.error(f"Error detecting KB: {e}")
            return {
                "available": False,
                "cache_path": None,
                "summary": "",
                "file_count": 0,
                "files_found": [],
                "error": str(e),
            }
    
    def _find_kb_files(self, project_root: Path) -> Dict[str, Path]:
        """
        Find all KB files in project
        
        Args:
            project_root: Root path of project
        
        Returns:
            Dict mapping filename to full path
        """
        kb_files = {}
        
        # Check for specific KB files in root
        for filename in self.KB_FILES:
            filepath = project_root / filename
            if filepath.exists() and filepath.is_file():
                kb_files[filename] = filepath
                self.logger.debug(f"Found KB file: {filename}")
        
        # Check for docs directories
        for dirname in self.KB_DIRECTORIES:
            doc_dir = project_root / dirname
            if doc_dir.exists() and doc_dir.is_dir():
                for markdown_file in doc_dir.glob("**/*.md"):
                    rel_path = markdown_file.relative_to(project_root)
                    kb_files[str(rel_path)] = markdown_file
                    self.logger.debug(f"Found KB file: {rel_path}")
        
        return kb_files
    
    def _create_temp_cache(self, project_root: Path, kb_files: Dict[str, Path]) -> Path:
        """
        Create temporary cache directory and copy KB files
        
        Args:
            project_root: Project root path
            kb_files: Dict of KB files to cache
        
        Returns:
            Path to cache directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project_root.name
        cache_dir = Path(tempfile.gettempdir()) / f"kb-cache-{project_name}-{timestamp}"
        
        cache_dir.mkdir(exist_ok=True)
        
        # Copy KB files
        for filename, filepath in kb_files.items():
            try:
                # Create subdirectories if needed
                dest_path = cache_dir / filename
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(filepath, dest_path)
            except Exception as e:
                self.logger.warning(f"Failed to cache {filename}: {e}")
        
        # Store metadata
        self.temp_cache_dir = cache_dir
        self.cache_metadata = {
            "project_root": str(project_root),
            "created_at": datetime.now().isoformat(),
            "file_count": len(kb_files),
            "files": list(kb_files.keys()),
            "cache_dir": str(cache_dir),
        }
        
        # Save metadata
        metadata_file = cache_dir / ".metadata.json"
        with open(metadata_file, "w") as f:
            json.dump(self.cache_metadata, f, indent=2)
        
        return cache_dir
    
    def _create_summary(self, kb_files: Dict[str, Path]) -> str:
        """
        Create summary of KB content for payload
        
        Args:
            kb_files: Dict of KB files
        
        Returns:
            Combined summary text (truncated to ~2000 chars)
        """
        MAX_SUMMARY_LENGTH = 2000
        
        summary_parts = []
        
        # Priority order for files
        priority_order = [
            "ARCHITECTURE.md",
            "PATTERNS.md",
            "TECH-STACK.md",
            "AGENTS.md",
            "GUIDELINES.md",
        ]
        
        # Add files in priority order
        for filename in priority_order:
            if filename in kb_files:
                try:
                    content = kb_files[filename].read_text(encoding="utf-8")
                    # Take first 500 chars of each file
                    summary_parts.append(f"# {filename}\n{content[:500]}\n")
                except Exception as e:
                    self.logger.warning(f"Failed to read {filename}: {e}")
        
        summary = "\n".join(summary_parts)
        
        # Truncate if too long
        if len(summary) > MAX_SUMMARY_LENGTH:
            summary = summary[:MAX_SUMMARY_LENGTH] + "\n... (truncated)"
        
        return summary
    
    def cleanup_cache(self) -> bool:
        """
        Delete temporary cache directory
        
        Returns:
            True if successful, False otherwise
        """
        if not self.temp_cache_dir:
            self.logger.debug("No temp cache to clean up")
            return True
        
        try:
            if self.temp_cache_dir.exists():
                shutil.rmtree(self.temp_cache_dir)
                self.logger.info(f"Cleaned up temp cache: {self.temp_cache_dir}")
                self.temp_cache_dir = None
                return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup cache: {e}")
            return False
        
        return True
    
    def get_cache_summary(self) -> Dict:
        """
        Get summary of current cache state
        
        Returns:
            Dict with cache metadata
        """
        return {
            "cache_dir": str(self.temp_cache_dir) if self.temp_cache_dir else None,
            "metadata": self.cache_metadata,
        }
