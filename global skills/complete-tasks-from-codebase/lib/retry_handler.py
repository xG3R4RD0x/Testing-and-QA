"""
Retry Handler - Implements 1x retry logic with skip on failure
"""

import logging
from typing import Callable, TypeVar, Tuple, Optional

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryHandler:
    """Handles retry logic for subagent dispatch"""
    
    def __init__(self, max_retries: int = 1, logger_instance=None):
        """
        Initialize retry handler
        
        Args:
            max_retries: Number of retries after initial failure (default: 1)
            logger_instance: Logger instance to use
        """
        self.max_retries = max_retries
        self.logger = logger_instance or logger
    
    def execute_with_retry(
        self,
        func: Callable[..., T],
        *args,
        operation_name: str = "operation",
        **kwargs
    ) -> Tuple[bool, Optional[T], Optional[str]]:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            operation_name: Name of operation for logging
            **kwargs: Keyword arguments for function
        
        Returns:
            Tuple of (success: bool, result: Optional[T], error: Optional[str])
            - success: True if succeeded, False if skipped after retries
            - result: Result from successful execution, None if failed
            - error: Error message if failed
        """
        attempt = 1
        last_error = None
        
        while attempt <= self.max_retries + 1:
            try:
                self.logger.debug(
                    f"{operation_name}: Attempt {attempt}/{self.max_retries + 1}"
                )
                result = func(*args, **kwargs)
                self.logger.info(f"{operation_name}: Success on attempt {attempt}")
                return (True, result, None)
            
            except Exception as e:
                last_error = str(e)
                self.logger.warning(
                    f"{operation_name}: Failed on attempt {attempt}: {last_error}"
                )
                
                if attempt < self.max_retries + 1:
                    attempt += 1
                    continue
                else:
                    break
        
        # All retries exhausted
        error_msg = f"Failed after {self.max_retries + 1} attempts: {last_error}"
        self.logger.error(f"{operation_name}: {error_msg}")
        return (False, None, error_msg)
    
    def execute_with_retry_dict(
        self,
        func: Callable,
        requirement_id: str,
        *args,
        **kwargs
    ) -> dict:
        """
        Execute function with retry, returning dict format for tracking
        
        Args:
            func: Function to execute
            requirement_id: ID of requirement being processed
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Dict with keys: success, result, error, requirement_id, attempts
        """
        attempt = 1
        last_error = None
        
        while attempt <= self.max_retries + 1:
            try:
                result = func(*args, **kwargs)
                return {
                    "success": True,
                    "result": result,
                    "error": None,
                    "requirement_id": requirement_id,
                    "attempts": attempt,
                }
            except Exception as e:
                last_error = str(e)
                self.logger.warning(
                    f"Requirement {requirement_id}: Attempt {attempt} failed: {last_error}"
                )
                
                if attempt < self.max_retries + 1:
                    attempt += 1
                else:
                    break
        
        return {
            "success": False,
            "result": None,
            "error": f"Failed after {self.max_retries + 1} attempts: {last_error}",
            "requirement_id": requirement_id,
            "attempts": self.max_retries + 1,
            "skipped": True,
        }
