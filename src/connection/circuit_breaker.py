"""
Circuit Breaker Pattern Implementation
Prevents cascading failures by temporarily blocking operations after repeated failures.

Reference: https://martinfowler.com/bliki/CircuitBreaker.html
"""

import time
import logging
from enum import Enum
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation, requests pass through
    OPEN = "open"          # Failure threshold reached, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and blocking requests"""
    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.
    
    The circuit breaker prevents cascading failures by temporarily blocking
    operations after a threshold of failures is reached.
    
    States:
        - CLOSED: Normal operation, all requests pass through
        - OPEN: Too many failures, requests are blocked
        - HALF_OPEN: Testing if service recovered, limited requests allowed
    
    Args:
        failure_threshold: Number of failures before opening circuit
        timeout: Seconds to wait before attempting to close circuit
        
    Example:
        >>> breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        >>> result = breaker.call(risky_function, arg1, arg2)
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of consecutive failures before opening
            timeout: Seconds before attempting to close circuit again
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED
        logger.info(
            f"CircuitBreaker initialized: threshold={failure_threshold}, "
            f"timeout={timeout}s"
        )
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Result from function execution
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Any exception raised by the function
        """
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. "
                    f"Retry after {self.timeout - (time.time() - self.last_failure_time):.1f}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self) -> None:
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker recovered, transitioning to CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                logger.warning(
                    f"Circuit breaker opening after {self.failure_count} failures"
                )
                self.state = CircuitState.OPEN
    
    def reset(self) -> None:
        """Manually reset circuit breaker to closed state"""
        logger.info("Circuit breaker manually reset")
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open"""
        return self.state == CircuitState.OPEN
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed"""
        return self.state == CircuitState.CLOSED


def circuit_breaker(failure_threshold: int = 5, timeout: float = 60.0):
    """
    Decorator to apply circuit breaker pattern to a function.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        timeout: Seconds before attempting to close circuit
        
    Example:
        >>> @circuit_breaker(failure_threshold=3, timeout=30)
        ... def risky_operation():
        ...     # operation that might fail
        ...     pass
    """
    breaker = CircuitBreaker(failure_threshold, timeout)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)
        wrapper.circuit_breaker = breaker
        return wrapper
    return decorator
