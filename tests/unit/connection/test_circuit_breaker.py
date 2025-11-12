"""
Unit tests for Circuit Breaker
"""

import pytest
import time
from unittest.mock import Mock
from src.connection.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
    circuit_breaker,
)


class TestCircuitBreaker:
    """Test cases for CircuitBreaker"""

    def test_init(self):
        """Test circuit breaker initialization"""
        breaker = CircuitBreaker(failure_threshold=3, timeout=10)

        assert breaker.failure_threshold == 3
        assert breaker.timeout == 10
        assert breaker.failure_count == 0
        assert breaker.state == CircuitState.CLOSED
        assert breaker.last_failure_time is None

    def test_successful_call(self):
        """Test successful function call"""
        breaker = CircuitBreaker()
        mock_func = Mock(return_value="success")

        result = breaker.call(mock_func, "arg1", kwarg="kwarg1")

        assert result == "success"
        assert breaker.failure_count == 0
        assert breaker.state == CircuitState.CLOSED
        mock_func.assert_called_once_with("arg1", kwarg="kwarg1")

    def test_failure_increments_count(self):
        """Test that failures increment failure count"""
        breaker = CircuitBreaker(failure_threshold=3)
        mock_func = Mock(side_effect=Exception("Test error"))

        for i in range(2):  # 2 failures, below threshold
            with pytest.raises(Exception):
                breaker.call(mock_func)

        assert breaker.failure_count == 2
        assert breaker.state == CircuitState.CLOSED

    def test_circuit_opens_after_threshold(self):
        """Test that circuit opens after failure threshold"""
        breaker = CircuitBreaker(failure_threshold=3)
        mock_func = Mock(side_effect=Exception("Test error"))

        # Cause 3 failures to reach threshold
        for i in range(3):
            with pytest.raises(Exception):
                breaker.call(mock_func)

        assert breaker.failure_count == 3
        assert breaker.state == CircuitState.OPEN

    def test_circuit_blocks_when_open(self):
        """Test that circuit blocks calls when open"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=10)
        mock_func = Mock(side_effect=Exception("Test error"))

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Next call should be blocked
        with pytest.raises(CircuitBreakerOpenError):
            breaker.call(mock_func)

        # Original function should not have been called
        assert mock_func.call_count == 2  # Only the first 2 calls

    def test_circuit_transitions_to_half_open(self):
        """Test circuit transitions to half-open after timeout"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        mock_func = Mock(side_effect=Exception("Test error"))

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Wait for timeout
        time.sleep(0.2)

        # Next call should transition to HALF_OPEN
        mock_func_success = Mock(return_value="success")
        result = breaker.call(mock_func_success)

        assert result == "success"
        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0

    def test_half_open_closes_on_success(self):
        """Test that half-open circuit closes on successful call"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        mock_func_fail = Mock(side_effect=Exception("Test error"))

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                breaker.call(mock_func_fail)

        # Wait and try success
        time.sleep(0.2)
        mock_func_success = Mock(return_value="success")
        breaker.call(mock_func_success)

        assert breaker.state == CircuitState.CLOSED

    def test_half_open_reopens_on_failure(self):
        """Test that half-open circuit reopens on failure"""
        breaker = CircuitBreaker(failure_threshold=2, timeout=0.1)
        mock_func_fail = Mock(side_effect=Exception("Test error"))

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                breaker.call(mock_func_fail)

        # Wait and try again (should fail and reopen)
        time.sleep(0.2)
        with pytest.raises(Exception):
            breaker.call(mock_func_fail)

        assert breaker.state == CircuitState.OPEN

    def test_reset(self):
        """Test manual reset of circuit breaker"""
        breaker = CircuitBreaker(failure_threshold=2)
        mock_func = Mock(side_effect=Exception("Test error"))

        # Open the circuit
        for i in range(2):
            with pytest.raises(Exception):
                breaker.call(mock_func)

        assert breaker.state == CircuitState.OPEN

        # Reset
        breaker.reset()

        assert breaker.state == CircuitState.CLOSED
        assert breaker.failure_count == 0
        assert breaker.last_failure_time is None

    def test_is_open_property(self):
        """Test is_open property"""
        breaker = CircuitBreaker(failure_threshold=1)
        assert not breaker.is_open

        mock_func = Mock(side_effect=Exception("Test error"))
        with pytest.raises(Exception):
            breaker.call(mock_func)

        assert breaker.is_open

    def test_is_closed_property(self):
        """Test is_closed property"""
        breaker = CircuitBreaker()
        assert breaker.is_closed

        breaker.state = CircuitState.OPEN
        assert not breaker.is_closed

    def test_decorator(self):
        """Test circuit breaker decorator"""

        @circuit_breaker(failure_threshold=2, timeout=10)
        def failing_function():
            raise Exception("Test error")

        # Cause failures
        for i in range(2):
            with pytest.raises(Exception):
                failing_function()

        # Circuit should be open
        with pytest.raises(CircuitBreakerOpenError):
            failing_function()

        # Check that decorator attached the breaker
        assert hasattr(failing_function, "circuit_breaker")
        assert failing_function.circuit_breaker.is_open

    def test_decorator_with_success(self):
        """Test circuit breaker decorator with successful function"""

        @circuit_breaker(failure_threshold=2, timeout=10)
        def success_function(x, y):
            return x + y

        result = success_function(2, 3)
        assert result == 5
        assert success_function.circuit_breaker.is_closed
