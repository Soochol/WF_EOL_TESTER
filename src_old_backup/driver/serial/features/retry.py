"""
Retry logic implementation for serial operations.

Provides exponential backoff retry mechanism with configurable parameters.
Focuses solely on retry logic and failure recovery strategies.
"""

import random
import time
from typing import Any, Callable, Optional, Type, Union

from loguru import logger

from ..core.interfaces import IRetryManager
from ..exceptions import (
    SerialCommunicationError, 
    SerialConnectionError,
    SerialTimeoutError
)


class RetryManager(IRetryManager):
    """Exponential backoff retry manager for serial operations."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 0.1, 
                 max_delay: float = 5.0, jitter: bool = True):
        """
        Initialize retry manager.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff (seconds)
            max_delay: Maximum delay between retries (seconds)
            jitter: Whether to add random jitter to delays
        """
        self._max_retries = max(0, max_retries)
        self._base_delay = max(0.01, base_delay)  # Minimum 10ms
        self._max_delay = max(self._base_delay, max_delay)
        self._jitter = jitter
        
        # Statistics
        self._total_attempts = 0
        self._total_successes = 0
        self._total_failures = 0
        self._total_retries = 0
        
        # Retryable exception types
        self._retryable_exceptions = {
            SerialCommunicationError,
            SerialTimeoutError,
            ConnectionError,
            OSError
        }
        
        # Non-retryable exception types
        self._non_retryable_exceptions = {
            ValueError,
            TypeError,
            AttributeError
        }
    
    def with_retry(self, operation: Callable[[], Any], **kwargs) -> Any:
        """
        Execute operation with retry logic.
        
        Args:
            operation: Function to execute with retries
            **kwargs: Retry configuration overrides
            
        Returns:
            Result of successful operation
            
        Raises:
            Last exception if all retries fail
        """
        # Override configuration for this operation
        max_retries = kwargs.get('max_retries', self._max_retries)
        base_delay = kwargs.get('base_delay', self._base_delay)
        max_delay = kwargs.get('max_delay', self._max_delay)
        jitter = kwargs.get('jitter', self._jitter)
        
        last_exception = None
        attempt = 0
        
        self._total_attempts += 1
        
        while attempt <= max_retries:
            try:
                result = operation()
                
                if attempt > 0:
                    self._total_retries += attempt
                    logger.info(f"Operation succeeded after {attempt} retries")
                
                self._total_successes += 1
                return result
            
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable(e):
                    logger.debug(f"Non-retryable exception: {type(e).__name__}: {e}")
                    self._total_failures += 1
                    raise
                
                if attempt >= max_retries:
                    logger.warning(f"Operation failed after {max_retries} retries: {e}")
                    self._total_failures += 1
                    break
                
                # Calculate delay for next attempt
                delay = self._calculate_delay(attempt, base_delay, max_delay, jitter)
                
                logger.warning(
                    f"Attempt {attempt + 1} failed: {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.3f}s..."
                )
                
                time.sleep(delay)
                attempt += 1
        
        # All retries exhausted
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Retry operation failed without exception")
    
    def configure(self, max_retries: int, base_delay: float) -> None:
        """
        Configure retry parameters.
        
        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
        """
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if base_delay <= 0:
            raise ValueError("base_delay must be positive")
        
        old_max = self._max_retries
        old_delay = self._base_delay
        
        self._max_retries = max_retries
        self._base_delay = base_delay
        
        logger.info(
            f"Retry configuration updated: max_retries {old_max} → {max_retries}, "
            f"base_delay {old_delay} → {base_delay}"
        )
    
    def add_retryable_exception(self, exception_type: Type[Exception]) -> None:
        """
        Add exception type to retryable list.
        
        Args:
            exception_type: Exception class to treat as retryable
        """
        if not issubclass(exception_type, Exception):
            raise ValueError("Must be an Exception subclass")
        
        self._retryable_exceptions.add(exception_type)
        logger.debug(f"Added retryable exception: {exception_type.__name__}")
    
    def add_non_retryable_exception(self, exception_type: Type[Exception]) -> None:
        """
        Add exception type to non-retryable list.
        
        Args:
            exception_type: Exception class to treat as non-retryable
        """
        if not issubclass(exception_type, Exception):
            raise ValueError("Must be an Exception subclass")
        
        self._non_retryable_exceptions.add(exception_type)
        
        # Remove from retryable if present
        self._retryable_exceptions.discard(exception_type)
        
        logger.debug(f"Added non-retryable exception: {exception_type.__name__}")
    
    def get_stats(self) -> dict:
        """
        Get retry statistics.
        
        Returns:
            dict: Retry performance metrics
        """
        success_rate = (self._total_successes / self._total_attempts * 100 
                       if self._total_attempts > 0 else 0)
        
        avg_retries = (self._total_retries / self._total_successes 
                      if self._total_successes > 0 else 0)
        
        return {
            'max_retries': self._max_retries,
            'base_delay': self._base_delay,
            'max_delay': self._max_delay,
            'jitter_enabled': self._jitter,
            'total_attempts': self._total_attempts,
            'total_successes': self._total_successes,
            'total_failures': self._total_failures,
            'total_retries': self._total_retries,
            'success_rate_percent': success_rate,
            'average_retries_per_success': avg_retries,
            'retryable_exceptions': [exc.__name__ for exc in self._retryable_exceptions],
            'non_retryable_exceptions': [exc.__name__ for exc in self._non_retryable_exceptions]
        }
    
    def reset_stats(self) -> None:
        """Reset retry statistics."""
        self._total_attempts = 0
        self._total_successes = 0
        self._total_failures = 0
        self._total_retries = 0
        logger.debug("Retry statistics reset")
    
    def _is_retryable(self, exception: Exception) -> bool:
        """
        Check if exception should be retried.
        
        Args:
            exception: Exception to check
            
        Returns:
            bool: True if exception is retryable
        """
        # Check non-retryable exceptions first (higher priority)
        for exc_type in self._non_retryable_exceptions:
            if isinstance(exception, exc_type):
                return False
        
        # Check retryable exceptions
        for exc_type in self._retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Default: don't retry unknown exceptions
        return False
    
    def _calculate_delay(self, attempt: int, base_delay: float, 
                        max_delay: float, jitter: bool) -> float:
        """
        Calculate delay for retry attempt using exponential backoff.
        
        Args:
            attempt: Current attempt number (0-based)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            jitter: Whether to add random jitter
            
        Returns:
            float: Delay in seconds
        """
        # Exponential backoff: delay = base_delay * (2 ^ attempt)
        delay = base_delay * (2 ** attempt)
        
        # Cap at maximum delay
        delay = min(delay, max_delay)
        
        # Add jitter if enabled (±25% random variation)
        if jitter:
            jitter_range = delay * 0.25
            jitter_offset = random.uniform(-jitter_range, jitter_range)
            delay = max(0.01, delay + jitter_offset)  # Ensure minimum 10ms
        
        return delay
    
    def create_retryable_operation(self, operation: Callable[[], Any], 
                                 **retry_config) -> Callable[[], Any]:
        """
        Create a retryable version of an operation.
        
        Args:
            operation: Original operation function
            **retry_config: Retry configuration overrides
            
        Returns:
            Callable: Retryable version of operation
        """
        def retryable_wrapper():
            return self.with_retry(operation, **retry_config)
        
        # Preserve function metadata
        retryable_wrapper.__name__ = f"retryable_{getattr(operation, '__name__', 'operation')}"
        retryable_wrapper.__doc__ = f"Retryable version of {operation}"
        
        return retryable_wrapper