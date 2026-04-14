"""
JSON Enricher - Updates requirements.json with generated content
"""

import logging
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class JsonEnricher:
    """Enriches requirements.json with implementation and test content"""
    
    def __init__(self, logger_instance=None):
        """
        Initialize JSON enricher
        
        Args:
            logger_instance: Logger instance to use
        """
        self.logger = logger_instance or logger
    
    def enrich_requirements(
        self,
        requirements_data: Dict,
        subagent_responses: List[Dict],
        dry_run: bool = False,
    ) -> Dict:
        """
        Enrich requirements data with subagent responses
        
        Args:
            requirements_data: Original requirements.json data
            subagent_responses: List of subagent response dicts
            dry_run: If True, don't modify data, just return what would change
        
        Returns:
            Dict with enrichment stats:
            - enriched_count: number of subtasks enriched
            - skipped_count: number of skipped responses
            - total_subtasks: total subtasks processed
            - modified_data: enriched requirements (if not dry_run)
            - changes: list of changes made (if dry_run)
        """
        stats = {
            "enriched_count": 0,
            "skipped_count": 0,
            "total_subtasks": 0,
            "failed_requirements": [],
            "changes": [],
        }
        
        # Work with a copy
        enriched_data = self._deep_copy_dict(requirements_data)
        
        # Find requirements key (main_requirements or requirements)
        requirements_list = self._get_requirements_list(enriched_data)
        if not requirements_list:
            self.logger.error("Could not find requirements list in data")
            stats["error"] = "No requirements found"
            return stats
        
        # Normalize subagent_responses to extract result field if present
        normalized_responses = []
        for resp in subagent_responses:
            if resp.get("result"):
                # Response is wrapped in retry handler format
                normalized_responses.append(resp.get("result"))
            else:
                # Response is already the actual response
                normalized_responses.append(resp)
        
        # Process each requirement
        for req_idx, requirement in enumerate(requirements_list):
            req_id = requirement.get("id", f"REQ-{req_idx}")
            
            # Find response for this requirement
            response = self._find_response(normalized_responses, req_id)
            
            if not response:
                self.logger.warning(f"No response for requirement {req_id}")
                stats["failed_requirements"].append(req_id)
                continue
            
            if response.get("skipped"):
                self.logger.info(f"Requirement {req_id} skipped: {response.get('error')}")
                stats["failed_requirements"].append(req_id)
                continue
            
            # Get subtasks list (sub_tasks or subtasks)
            subtasks_key = "sub_tasks" if "sub_tasks" in requirement else "subtasks"
            subtasks = requirement.get(subtasks_key, [])
            
            if not subtasks:
                self.logger.debug(f"No subtasks for requirement {req_id}")
                continue
            
            # Enrich each subtask
            for task_idx, subtask in enumerate(subtasks):
                task_id = subtask.get("id", f"TASK-{req_idx}-{task_idx:02d}")
                
                # Find response for this subtask
                subtask_response = self._find_subtask_response(
                    response.get("subtasks", []),
                    task_id
                )
                
                if not subtask_response:
                    self.logger.debug(f"No response for subtask {task_id}")
                    stats["skipped_count"] += 1
                    stats["total_subtasks"] += 1
                    continue
                
                # Get implementation and test
                implementation = subtask_response.get("implementation", "").strip()
                test = subtask_response.get("test", "").strip()
                
                # Track changes
                old_impl = subtask.get("implementation", "")
                old_test = subtask.get("test", "")
                
                change_record = {
                    "task_id": task_id,
                    "implementation_changed": bool(implementation and implementation != old_impl),
                    "test_changed": bool(test and test != old_test),
                }
                
                # Update subtask
                if implementation:
                    subtask["implementation"] = implementation
                    if not dry_run:
                        change_record["implementation_added"] = True
                
                if test:
                    subtask["test"] = test
                    if not dry_run:
                        change_record["test_added"] = True
                
                if change_record["implementation_changed"] or change_record["test_changed"]:
                    stats["changes"].append(change_record)
                    stats["enriched_count"] += 1
                
                stats["total_subtasks"] += 1
        
        stats["modified_data"] = enriched_data if not dry_run else None
        
        self.logger.info(
            f"Enrichment complete: {stats['enriched_count']} enriched, "
            f"{stats['skipped_count']} skipped, "
            f"{len(stats['failed_requirements'])} failed requirements"
        )
        
        return stats
    
    def save_enriched_requirements(
        self,
        requirements_file: Path,
        enriched_data: Dict,
        backup: bool = True,
    ) -> tuple[bool, str]:
        """
        Save enriched data back to requirements.json file
        
        Args:
            requirements_file: Path to requirements.json
            enriched_data: Enriched requirements data
            backup: Whether to create backup of original file
        
        Returns:
            Tuple of (success, message)
        """
        try:
            requirements_file = Path(requirements_file)
            
            # Create backup if requested
            if backup and requirements_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = requirements_file.parent / f"{requirements_file.stem}.backup.{timestamp}{requirements_file.suffix}"
                
                shutil.copy2(requirements_file, backup_file)
                self.logger.info(f"Created backup: {backup_file}")
            
            # Write enriched data
            with open(requirements_file, "w", encoding="utf-8") as f:
                json.dump(enriched_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved enriched requirements to {requirements_file}")
            return (True, f"Successfully saved to {requirements_file}")
        
        except Exception as e:
            error_msg = f"Failed to save enriched requirements: {e}"
            self.logger.error(error_msg)
            return (False, error_msg)
    
    def _get_requirements_list(self, data: Dict) -> Optional[List]:
        """
        Get requirements list from data (handles both main_requirements and requirements keys)
        
        Args:
            data: Requirements data dict
        
        Returns:
            List of requirements or None
        """
        if "main_requirements" in data:
            return data["main_requirements"]
        elif "requirements" in data:
            return data["requirements"]
        else:
            return None
    
    def _find_response(self, responses: List[Dict], req_id: str) -> Optional[Dict]:
        """
        Find response for a requirement by ID
        
        Args:
            responses: List of responses
            req_id: Requirement ID to find
        
        Returns:
            Response dict or None
        """
        for response in responses:
            if response.get("requirement_id") == req_id:
                return response
        return None
    
    def _find_subtask_response(self, subtask_responses: List[Dict], task_id: str) -> Optional[Dict]:
        """
        Find response for a subtask by ID
        
        Args:
            subtask_responses: List of subtask responses
            task_id: Task ID to find
        
        Returns:
            Subtask response dict or None
        """
        for response in subtask_responses:
            if response.get("id") == task_id:
                return response
        return None
    
    def _deep_copy_dict(self, data: Dict) -> Dict:
        """
        Create deep copy of dictionary
        
        Args:
            data: Dict to copy
        
        Returns:
            Copied dict
        """
        return json.loads(json.dumps(data))
    
    def get_enrichment_stats(self, stats: Dict) -> str:
        """
        Format enrichment stats for reporting
        
        Args:
            stats: Stats dict from enrich_requirements
        
        Returns:
            Formatted string
        """
        return (
            f"Enrichment Report:\n"
            f"  ✅ Enriched: {stats['enriched_count']}\n"
            f"  ⏭️  Skipped: {stats['skipped_count']}\n"
            f"  📊 Total Subtasks: {stats['total_subtasks']}\n"
            f"  ❌ Failed Requirements: {len(stats['failed_requirements'])}"
        )
