#!/usr/bin/env python3
"""
Complete Tasks Orchestrator - Main entry point for skill
"""

import logging
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import modular components
from .retry_handler import RetryHandler
from .knowledge_base_manager import KnowledgeBaseManager
from .codebase_analyzer import CodebaseAnalyzer
from .payload_builder import PayloadBuilder
from .agent_dispatcher import AgentDispatcher
from .json_enricher import JsonEnricher


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class CompleteTasksOrchestrator:
    """
    Main orchestrator for complete-tasks-from-codebase skill
    
    Workflow:
    1. Load requirements.json
    2. Detect KB and cache it (temporary)
    3. Analyze codebase tech stack
    4. Dispatch subagents (one per requirement)
    5. Collect responses and enrich JSON
    6. Cleanup temporary cache
    """
    
    def __init__(self):
        """Initialize orchestrator with all components"""
        self.logger = logger
        self.retry_handler = RetryHandler(max_retries=1, logger_instance=logger)
        self.kb_manager = KnowledgeBaseManager(logger_instance=logger)
        self.codebase_analyzer = CodebaseAnalyzer(logger_instance=logger)
        self.payload_builder = PayloadBuilder(logger_instance=logger)
        self.agent_dispatcher = AgentDispatcher(logger_instance=logger)
        self.json_enricher = JsonEnricher(logger_instance=logger)
        
        self.project_root = None
        self.requirements_file = None
        self.knowledge_base = None
        self.codebase_analysis = None
    
    def run(self, requirements_file: str, dispatch_callback=None) -> Dict:
        """
        Main entry point - run complete enrichment workflow
        
        Args:
            requirements_file: Path to requirements.json
            dispatch_callback: Callable that dispatches to actual agent
                              (if None, will use mock dispatch for testing)
        
        Returns:
            Dict with execution results
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting Complete Tasks Orchestration")
        self.logger.info("=" * 70)
        
        result = {
            "success": False,
            "stages": {},
            "summary": {},
            "errors": [],
        }
        
        try:
            # Stage 1: Initialization
            result["stages"]["initialization"] = self._stage_initialization(requirements_file)
            if not result["stages"]["initialization"]["success"]:
                raise Exception("Initialization failed")
            
            # Stage 2: Knowledge Base Detection
            result["stages"]["kb_detection"] = self._stage_kb_detection()
            
            # Stage 3: Codebase Analysis
            result["stages"]["codebase_analysis"] = self._stage_codebase_analysis()
            
            # Stage 4: Subagent Dispatch
            result["stages"]["subagent_dispatch"] = self._stage_subagent_dispatch(
                dispatch_callback
            )
            
            # Stage 5: JSON Enrichment
            result["stages"]["enrichment"] = self._stage_enrichment(
                result["stages"]["subagent_dispatch"]["responses"]
            )
            
            # Stage 6: Cleanup & Report
            result["stages"]["cleanup"] = self._stage_cleanup()
            
            # Build summary
            result["success"] = True
            result["summary"] = self._build_summary(result["stages"])
            
            self.logger.info("=" * 70)
            self.logger.info("Orchestration Complete ✅")
            self.logger.info("=" * 70)
            self._print_summary(result["summary"])
            
            return result
        
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            result["errors"].append(str(e))
            result["success"] = False
            
            # Still cleanup on error
            try:
                self.kb_manager.cleanup_cache()
            except:
                pass
            
            return result
    
    def _stage_initialization(self, requirements_file: str) -> Dict:
        """Stage 1: Initialize and load requirements"""
        self.logger.info("Stage 1: Initialization")
        
        try:
            req_path = Path(requirements_file).resolve()
            
            if not req_path.exists():
                raise FileNotFoundError(f"Requirements file not found: {req_path}")
            
            # Load requirements
            with open(req_path, "r", encoding="utf-8") as f:
                requirements_data = json.load(f)
            
            self.logger.info(f"Loaded requirements: {req_path}")
            
            # Extract project info from path
            # Expected: /Reports/{project-name}/requirements.json
            project_name = None
            project_root = None
            
            # Try to extract from path
            if "/Reports/" in str(req_path):
                parts = str(req_path).split("/Reports/")
                if len(parts) == 2:
                    project_name = parts[1].split("/")[0]
                    # Project root is at /dev/{project-name}, not /dev/Reports/{project-name}
                    dev_parent = req_path.parent.parent.parent  # Go up from /Reports/{project}
                    if (dev_parent / project_name).exists():
                        project_root = dev_parent / project_name
            
            # Fallback: use name from requirements or parent
            if not project_name:
                project_name = requirements_data.get("repository_name", req_path.parent.name)
            
            if not project_root:
                # Look for project root by checking for common files
                for parent in req_path.parents:
                    if (parent / "mix.exs").exists() or (parent / "package.json").exists() or \
                       (parent / "setup.py").exists() or (parent / "Gemfile").exists():
                        project_root = parent
                        break
                
                # If still not found, use Reports parent
                if not project_root:
                    project_root = req_path.parent.parent
            
            self.project_root = project_root
            self.requirements_file = req_path
            
            # Count requirements
            req_list = requirements_data.get("main_requirements", requirements_data.get("requirements", []))
            req_count = len(req_list)
            
            self.logger.info(f"Project: {project_name}")
            self.logger.info(f"Project Root: {project_root}")
            self.logger.info(f"Requirements found: {req_count}")
            
            return {
                "success": True,
                "project_name": project_name,
                "project_root": str(project_root),
                "requirements_file": str(req_path),
                "requirement_count": req_count,
            }
        
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _stage_kb_detection(self) -> Dict:
        """Stage 2: Detect and cache knowledge base"""
        self.logger.info("Stage 2: Knowledge Base Detection")
        
        try:
            kb_info = self.kb_manager.detect_and_cache(self.project_root)
            self.knowledge_base = kb_info
            
            self.logger.info(
                f"KB Detection: {'Available' if kb_info['available'] else 'Not found'} "
                f"({kb_info['file_count']} files)"
            )
            
            return {
                "success": True,
                "available": kb_info["available"],
                "file_count": kb_info["file_count"],
                "files_found": kb_info["files_found"],
                "cache_path": kb_info.get("cache_path"),
            }
        
        except Exception as e:
            self.logger.error(f"KB detection failed: {e}")
            return {"success": False, "error": str(e), "available": False}
    
    def _stage_codebase_analysis(self) -> Dict:
        """Stage 3: Analyze codebase"""
        self.logger.info("Stage 3: Codebase Analysis")
        
        try:
            analysis = self.codebase_analyzer.analyze(self.project_root)
            self.codebase_analysis = analysis
            
            stack = analysis.get("detected_stack", {})
            self.logger.info(
                f"Detected: {stack.get('framework', 'Unknown')} "
                f"({stack.get('language', 'Unknown')})"
            )
            
            return {
                "success": True,
                "framework": stack.get("framework"),
                "language": stack.get("language"),
                "orm": stack.get("orm"),
                "test_framework": stack.get("test_framework"),
                "confidence": analysis.get("confidence"),
            }
        
        except Exception as e:
            self.logger.error(f"Codebase analysis failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _stage_subagent_dispatch(self, dispatch_callback) -> Dict:
        """Stage 4: Dispatch subagents"""
        self.logger.info("Stage 4: Subagent Dispatch")
        
        try:
            # Load requirements
            with open(self.requirements_file, "r", encoding="utf-8") as f:
                requirements_data = json.load(f)
            
            req_list = requirements_data.get(
                "main_requirements",
                requirements_data.get("requirements", [])
            )
            
            responses = []
            dispatch_count = 0
            failed_count = 0
            
            # Dispatch each requirement
            for requirement in req_list:
                req_id = requirement.get("id")
                self.logger.info(f"Dispatching {req_id}")
                
                # Get subtasks
                subtasks_key = "sub_tasks" if "sub_tasks" in requirement else "subtasks"
                subtasks = requirement.get(subtasks_key, [])
                
                # Build payload
                payload = self.payload_builder.build_requirement_payload(
                    requirement=requirement,
                    subtasks=subtasks,
                    project_info={
                        "name": requirements_data.get("repository_name", "unknown"),
                        "root_path": self.project_root,
                        "reports_path": self.requirements_file.parent,
                    },
                    knowledge_base=self.knowledge_base or {},
                    codebase_analysis=self.codebase_analysis or {},
                )
                
                # Dispatch with retry
                if dispatch_callback:
                    # Use provided callback
                    dispatch_func = lambda: dispatch_callback(payload)
                else:
                    # Use mock dispatch for testing
                    dispatch_func = lambda: self._mock_dispatch(payload)
                
                result = self.retry_handler.execute_with_retry_dict(
                    dispatch_func,
                    req_id,
                )
                
                responses.append(result)
                
                if result["success"]:
                    dispatch_count += 1
                else:
                    failed_count += 1
            
            self.logger.info(
                f"Dispatch complete: {dispatch_count} successful, {failed_count} failed"
            )
            
            return {
                "success": True,
                "total_dispatched": len(req_list),
                "successful": dispatch_count,
                "failed": failed_count,
                "responses": responses,
            }
        
        except Exception as e:
            self.logger.error(f"Subagent dispatch failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "responses": [],
            }
    
    def _stage_enrichment(self, responses: List[Dict]) -> Dict:
        """Stage 5: Enrich JSON with responses"""
        self.logger.info("Stage 5: JSON Enrichment")
        
        try:
            # Load requirements
            with open(self.requirements_file, "r", encoding="utf-8") as f:
                requirements_data = json.load(f)
            
            # Enrich
            stats = self.json_enricher.enrich_requirements(
                requirements_data,
                responses,
                dry_run=False,
            )
            
            # Save
            success, message = self.json_enricher.save_enriched_requirements(
                self.requirements_file,
                stats["modified_data"],
                backup=True,
            )
            
            if not success:
                raise Exception(message)
            
            self.logger.info(f"Enriched: {stats['enriched_count']} subtasks")
            
            return {
                "success": True,
                "enriched": stats["enriched_count"],
                "skipped": stats["skipped_count"],
                "total_subtasks": stats["total_subtasks"],
                "failed_requirements": stats["failed_requirements"],
            }
        
        except Exception as e:
            self.logger.error(f"Enrichment failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _stage_cleanup(self) -> Dict:
        """Stage 6: Cleanup temporary cache"""
        self.logger.info("Stage 6: Cleanup")
        
        try:
            success = self.kb_manager.cleanup_cache()
            
            if success:
                self.logger.info("Cache cleanup successful")
            else:
                self.logger.warning("Cache cleanup had issues")
            
            return {"success": success}
        
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _build_summary(self, stages: Dict) -> Dict:
        """Build execution summary"""
        return {
            "project": stages.get("initialization", {}).get("project_name"),
            "requirements_processed": stages.get("subagent_dispatch", {}).get("successful", 0),
            "subtasks_enriched": stages.get("enrichment", {}).get("enriched", 0),
            "total_subtasks": stages.get("enrichment", {}).get("total_subtasks", 0),
            "kb_available": stages.get("kb_detection", {}).get("available", False),
            "framework_detected": stages.get("codebase_analysis", {}).get("framework"),
        }
    
    def _print_summary(self, summary: Dict):
        """Print execution summary"""
        print("\n" + "=" * 70)
        print("EXECUTION SUMMARY")
        print("=" * 70)
        print(f"Project: {summary.get('project', 'Unknown')}")
        print(f"Framework: {summary.get('framework_detected', 'Unknown')}")
        print(f"KB Available: {'Yes' if summary.get('kb_available') else 'No'}")
        print(f"Requirements Processed: {summary.get('requirements_processed', 0)}")
        print(f"Subtasks Enriched: {summary.get('subtasks_enriched', 0)}")
        print(f"Total Subtasks: {summary.get('total_subtasks', 0)}")
        print("=" * 70 + "\n")
    
    def _mock_dispatch(self, payload: Dict) -> Dict:
        """Mock dispatch for testing (returns empty responses)"""
        req_id = payload.get("requirement", {}).get("id")
        subtasks = payload.get("subtasks", [])
        
        return {
            "success": True,
            "requirement_id": req_id,
            "subtasks": [
                {
                    "id": subtask.get("id"),
                    "implementation": "",
                    "test": "",
                }
                for subtask in subtasks
            ],
        }


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 complete_tasks_orchestrator.py <path-to-requirements.json> [dispatch_callback_module]")
        sys.exit(1)
    
    requirements_file = sys.argv[1]
    
    orchestrator = CompleteTasksOrchestrator()
    result = orchestrator.run(requirements_file, dispatch_callback=None)
    
    if result["success"]:
        print(json.dumps(result, indent=2))
        sys.exit(0)
    else:
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
