"""
Agent Dispatcher - Agent-agnostic dispatch system
"""

import logging
import json
import os
import sys
from typing import Dict, List, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentDispatcher:
    """
    Agent-agnostic dispatcher that adapts to different agent environments
    Supports: OpenCode, Claude Code, Codex, and other LLM-based agent systems
    """
    
    def __init__(self, logger_instance=None):
        """
        Initialize agent dispatcher
        
        Args:
            logger_instance: Logger instance to use
        """
        self.logger = logger_instance or logger
        self.agent_environment = self._detect_environment()
    
    def _detect_environment(self) -> str:
        """
        Detect which agent environment we're running in
        
        Returns:
            Environment name: 'opencode', 'claude-code', 'codex', 'generic'
        """
        # Check for OpenCode environment
        if os.getenv("OPENCODE_SKILL"):
            return "opencode"
        
        # Check for Claude Code environment
        if os.getenv("CLAUDE_CODE") or os.getenv("CLAUDE_API_KEY"):
            return "claude-code"
        
        # Check for Codex environment
        if os.getenv("CODEX_API_KEY"):
            return "codex"
        
        # Check for environment variables
        if os.getenv("LLM_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
            return "generic"
        
        self.logger.debug("Could not detect specific agent environment, using generic")
        return "generic"
    
    def dispatch_with_callback(
        self,
        payload: Dict,
        callback: Callable[[Dict], Dict],
        requirement_id: str,
    ) -> Dict:
        """
        Dispatch requirement to agent using callback function
        
        This is the primary dispatch mechanism. The callback function should:
        1. Accept the payload dict
        2. Send it to the appropriate agent system
        3. Return the parsed response dict
        
        Args:
            payload: Universal payload dict
            callback: Callable that executes the agent dispatch
            requirement_id: ID of requirement being processed
        
        Returns:
            Response dict from agent
        """
        try:
            self.logger.debug(
                f"Dispatching {requirement_id} to agent "
                f"(environment: {self.agent_environment})"
            )
            
            # Validate payload before dispatch
            is_valid, errors = self._validate_payload(payload)
            if not is_valid:
                return {
                    "success": False,
                    "requirement_id": requirement_id,
                    "error": f"Invalid payload: {', '.join(errors)}",
                    "skipped": True,
                }
            
            # Call the dispatch callback
            response = callback(payload)
            
            # Validate response
            if not response:
                return {
                    "success": False,
                    "requirement_id": requirement_id,
                    "error": "Agent returned no response",
                    "skipped": True,
                }
            
            # Ensure response has required fields
            if "requirement_id" not in response:
                response["requirement_id"] = requirement_id
            
            if "success" not in response:
                response["success"] = True
            
            self.logger.info(
                f"Dispatch successful for {requirement_id} "
                f"({len(response.get('subtasks', []))} subtasks)"
            )
            
            return response
        
        except Exception as e:
            self.logger.error(f"Dispatch failed for {requirement_id}: {e}")
            return {
                "success": False,
                "requirement_id": requirement_id,
                "error": str(e),
                "skipped": True,
            }
    
    def format_payload_for_prompt(self, payload: Dict) -> str:
        """
        Format payload as system prompt context for agent
        
        Args:
            payload: Universal payload dict
        
        Returns:
            Formatted string for inclusion in system prompt
        """
        parts = []
        
        # Project context
        project = payload.get("project", {})
        parts.append(f"Project: {project.get('name', 'Unknown')}")
        
        # Tech stack
        stack = payload.get("codebase_analysis", {}).get("detected_stack", {})
        if stack:
            parts.append(
                f"Tech Stack: {stack.get('framework', 'Unknown')} "
                f"({stack.get('language', 'Unknown')})"
            )
        
        # Requirement info
        req = payload.get("requirement", {})
        parts.append(f"Requirement: {req.get('title', 'Unknown')}")
        
        # KB availability
        kb = payload.get("knowledge_base", {})
        if kb.get("available"):
            parts.append("Knowledge Base: Available")
        
        return "\n".join(parts)
    
    def dispatch_opencode(self, payload: Dict) -> Dict:
        """
        OpenCode-specific dispatch (via subagent system)
        
        Note: This is a reference implementation. Actual OpenCode dispatch
        is handled by the orchestrator using OpenCode's native subagent system.
        
        Args:
            payload: Universal payload dict
        
        Returns:
            Response dict
        """
        self.logger.debug("OpenCode dispatch (reference implementation)")
        
        # In actual implementation, this would be called by orchestrator
        # via OpenCode's native subagent dispatch mechanism
        
        return {
            "success": False,
            "requirement_id": payload.get("requirement", {}).get("id"),
            "error": "OpenCode dispatch should use native subagent system",
            "skipped": True,
        }
    
    def dispatch_claude_code(self, payload: Dict) -> Dict:
        """
        Claude Code-specific dispatch (via Task tool)
        
        Args:
            payload: Universal payload dict
        
        Returns:
            Response dict
        """
        self.logger.debug("Claude Code dispatch (via Task tool)")
        
        # This would integrate with Claude Code's Task tool
        # Implementation depends on how Claude Code's Task tool works
        
        return {
            "success": False,
            "requirement_id": payload.get("requirement", {}).get("id"),
            "error": "Claude Code dispatch not yet implemented",
            "skipped": True,
        }
    
    def dispatch_generic_api(self, payload: Dict, api_endpoint: str) -> Dict:
        """
        Generic HTTP API dispatch
        
        Args:
            payload: Universal payload dict
            api_endpoint: API endpoint URL
        
        Returns:
            Response dict
        """
        self.logger.debug(f"Generic API dispatch to {api_endpoint}")
        
        try:
            import requests
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "CompleteTasksSkill/2.0.0",
            }
            
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=60,
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"API dispatch successful")
                return result
            else:
                return {
                    "success": False,
                    "requirement_id": payload.get("requirement", {}).get("id"),
                    "error": f"API returned {response.status_code}: {response.text}",
                    "skipped": True,
                }
        
        except ImportError:
            self.logger.error("requests library not available")
            return {
                "success": False,
                "requirement_id": payload.get("requirement", {}).get("id"),
                "error": "requests library required for API dispatch",
                "skipped": True,
            }
        except Exception as e:
            self.logger.error(f"API dispatch failed: {e}")
            return {
                "success": False,
                "requirement_id": payload.get("requirement", {}).get("id"),
                "error": str(e),
                "skipped": True,
            }
    
    def _validate_payload(self, payload: Dict) -> tuple[bool, List[str]]:
        """
        Validate payload structure
        
        Args:
            payload: Payload dict to validate
        
        Returns:
            Tuple of (is_valid, list of errors)
        """
        errors = []
        
        required_keys = ["skill_version", "operation", "requirement", "subtasks"]
        for key in required_keys:
            if key not in payload:
                errors.append(f"Missing {key}")
        
        if payload.get("requirement", {}).get("id") is None:
            errors.append("Requirement missing id")
        
        if not payload.get("subtasks"):
            errors.append("No subtasks provided")
        
        return (len(errors) == 0, errors)
    
    def get_environment_info(self) -> Dict:
        """
        Get information about current agent environment
        
        Returns:
            Dict with environment details
        """
        return {
            "detected_environment": self.agent_environment,
            "opencode_skill": os.getenv("OPENCODE_SKILL"),
            "has_api_key": bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("LLM_API_KEY")),
        }
