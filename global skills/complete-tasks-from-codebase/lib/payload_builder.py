"""
Payload Builder - Constructs universal JSON payloads for subagents
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PayloadBuilder:
    """Builds universal JSON payloads for agent-agnostic dispatch"""
    
    SKILL_VERSION = "2.0.0"
    
    def __init__(self, logger_instance=None):
        """
        Initialize payload builder
        
        Args:
            logger_instance: Logger instance to use
        """
        self.logger = logger_instance or logger
    
    def build_requirement_payload(
        self,
        requirement: Dict,
        subtasks: List[Dict],
        project_info: Dict,
        knowledge_base: Dict,
        codebase_analysis: Dict,
    ) -> Dict:
        """
        Build universal payload for requirement enrichment
        
        Args:
            requirement: Requirement object (id, title, description, etc)
            subtasks: List of subtask objects
            project_info: Project information (name, root_path, reports_path)
            knowledge_base: KB info (available, summary, etc)
            codebase_analysis: Codebase analysis (detected_stack, key_patterns)
        
        Returns:
            Universal payload dict
        """
        payload = {
            "skill_version": self.SKILL_VERSION,
            "operation": "enrich_requirement",
            
            "project": {
                "name": project_info.get("name", "unknown"),
                "root_path": str(project_info.get("root_path", "")),
                "reports_path": str(project_info.get("reports_path", "")),
            },
            
            "knowledge_base": {
                "available": knowledge_base.get("available", False),
                "summary": knowledge_base.get("summary", ""),
                "file_count": knowledge_base.get("file_count", 0),
                "files_found": knowledge_base.get("files_found", []),
            },
            
            "codebase_analysis": {
                "detected_stack": codebase_analysis.get("detected_stack", {}),
                "key_patterns": codebase_analysis.get("key_patterns", {}),
                "confidence": codebase_analysis.get("confidence", 0),
            },
            
            "requirement": {
                "id": requirement.get("id", ""),
                "title": requirement.get("title", ""),
                "description": requirement.get("description", ""),
                "effort_hours": requirement.get("effort_hours"),
                "effort_cost_eur": requirement.get("effort_cost_eur"),
            },
            
            "subtasks": [
                {
                    "id": subtask.get("id", ""),
                    "title": subtask.get("title", ""),
                    "description": subtask.get("description", ""),
                }
                for subtask in subtasks
            ],
            
            "instructions": {
                "analysis_depth": "smart",
                "generate_implementation": True,
                "generate_test": True,
                "output_format": "json",
                "validation": "minimal",
            },
        }
        
        return payload
    
    def to_json_string(self, payload: Dict, pretty: bool = False) -> str:
        """
        Convert payload to JSON string
        
        Args:
            payload: Payload dict
            pretty: Whether to pretty-print (for debugging)
        
        Returns:
            JSON string
        """
        try:
            if pretty:
                return json.dumps(payload, indent=2, ensure_ascii=False)
            else:
                return json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
        except Exception as e:
            self.logger.error(f"Failed to serialize payload: {e}")
            return "{}"
    
    def from_json_string(self, json_str: str) -> Optional[Dict]:
        """
        Parse JSON string to payload dict
        
        Args:
            json_str: JSON string
        
        Returns:
            Parsed dict or None if invalid
        """
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON payload: {e}")
            return None
    
    def validate_payload(self, payload: Dict) -> tuple[bool, List[str]]:
        """
        Validate payload structure
        
        Args:
            payload: Payload dict
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        # Required top-level keys
        required_keys = [
            "skill_version",
            "operation",
            "project",
            "requirement",
            "subtasks",
        ]
        
        for key in required_keys:
            if key not in payload:
                errors.append(f"Missing required key: {key}")
        
        # Validate requirement
        requirement = payload.get("requirement", {})
        if not requirement.get("id"):
            errors.append("Requirement missing 'id'")
        if not requirement.get("title"):
            errors.append("Requirement missing 'title'")
        
        # Validate subtasks
        subtasks = payload.get("subtasks", [])
        if not subtasks:
            errors.append("No subtasks provided")
        
        for i, subtask in enumerate(subtasks):
            if not subtask.get("id"):
                errors.append(f"Subtask {i} missing 'id'")
            if not subtask.get("title"):
                errors.append(f"Subtask {i} missing 'title'")
        
        # Validate project info
        project = payload.get("project", {})
        if not project.get("name"):
            errors.append("Project info missing 'name'")
        if not project.get("root_path"):
            errors.append("Project info missing 'root_path'")
        
        return (len(errors) == 0, errors)
    
    def get_payload_summary(self, payload: Dict) -> Dict:
        """
        Get summary of payload for logging
        
        Args:
            payload: Payload dict
        
        Returns:
            Summary dict
        """
        return {
            "skill_version": payload.get("skill_version"),
            "operation": payload.get("operation"),
            "project": payload.get("project", {}).get("name"),
            "requirement_id": payload.get("requirement", {}).get("id"),
            "requirement_title": payload.get("requirement", {}).get("title"),
            "subtask_count": len(payload.get("subtasks", [])),
            "kb_available": payload.get("knowledge_base", {}).get("available"),
            "detected_framework": payload.get("codebase_analysis", {}).get("detected_stack", {}).get("framework"),
        }
