"""
Complete Tasks from Codebase - Modular Library
Refactored skill for automatic requirement enrichment with agent-agnostic dispatch
"""

__version__ = "2.0.0"
__author__ = "OpenCode Skills"

from .complete_tasks_orchestrator import CompleteTasksOrchestrator
from .knowledge_base_manager import KnowledgeBaseManager
from .codebase_analyzer import CodebaseAnalyzer
from .payload_builder import PayloadBuilder
from .agent_dispatcher import AgentDispatcher
from .json_enricher import JsonEnricher
from .retry_handler import RetryHandler

__all__ = [
    "CompleteTasksOrchestrator",
    "KnowledgeBaseManager",
    "CodebaseAnalyzer",
    "PayloadBuilder",
    "AgentDispatcher",
    "JsonEnricher",
    "RetryHandler",
]
