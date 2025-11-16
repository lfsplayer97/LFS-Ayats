"""
Unit tests for TelemetryCollector thread safety features
Tests for race condition fixes, callback timeouts, and concurrent access
"""

import pytest
import time
import threading
from unittest.mock import Mock

from src.telemetry.collector import TelemetryCollector, CarTelemetry


class TestTelemetryCollectorThreadSafety:
    """Test cases for thread safety features"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock InSim client"""
        client = Mock()
        client.connected = True
        client.initialize = Mock()
        client.register_callback = Mock()
        client.receive_packet = Mock(return_value=None)
        return client

    @pytest.fixture
    def collector(self, mock_client):
        """Create a TelemetryCollector with automatic cleanup"""
        collector_instance = TelemetryCollector(mock_client, callback_timeout=0.5)
        yield collector_instance
        # Cleanup: shutdown the executor if it exists
        if hasattr(collector_instance, "callback_executor"):
            collector_instance.callback_executor.shutdown(wait=False)

    def test_concurrent_callback_registration(self, collector):
        """Test that multiple threads can register callbacks safely"""
        results = []
        errors = []

        def register_callbacks(thread_id):
            try:
                for i in range(10):
                    callback = Mock(__name__=f"callback_{thread_id}_{i}")
                    collector.register_callback("car_update", callback)
                    time.sleep(0.001)  # Small delay to encourage race conditions
                results.append(thread_id)
            except Exception as e:
                errors.append(e)

        # Start multiple threads registering callbacks
        threads = []
        for i in range(5):
            thread = threading.Thread(target=register_callbacks, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5, "Not all threads completed"

        # Verify all callbacks were registered
        assert (
            len(collector.callbacks["car_update"]) == 50
        ), "Not all callbacks were registered"

    def test_concurrent_callback_triggering(self, collector):
        """Test that callbacks can be triggered safely from multiple threads"""
        call_counts = {"count": 0}
        lock = threading.Lock()

        def counting_callback(data):
            with lock:
                call_counts["count"] += 1

        # Register callback
        collector.register_callback("car_update", counting_callback)

        # Trigger callbacks from multiple threads
        def trigger_callbacks(thread_id):
            for i in range(10):
                telemetry = CarTelemetry(plid=thread_id, speed=i)
                collector._trigger_callbacks("car_update", telemetry)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=trigger_callbacks, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Wait a bit for all callbacks to complete
        time.sleep(0.5)

        # All callbacks should have been called
        assert (
            call_counts["count"] == 50
        ), f"Expected 50 calls, got {call_counts['count']}"

    def test_callback_modification_during_iteration(self, collector):
        """Test that modifying callback list during iteration is safe"""
        executed_callbacks = []

        def callback_that_modifies_list(data):
            executed_callbacks.append("first")
            # Try to unregister another callback (would cause issues without copy)
            if len(collector.callbacks["car_update"]) > 1:
                collector.callbacks["car_update"].pop()

        def normal_callback(data):
            executed_callbacks.append("second")

        # Register callbacks
        collector.register_callback("car_update", callback_that_modifies_list)
        collector.register_callback("car_update", normal_callback)

        # Trigger callbacks - should not crash
        collector._trigger_callbacks("car_update", CarTelemetry())

        # Wait for callbacks to complete
        time.sleep(0.2)

        # At least the first callback should have executed
        assert "first" in executed_callbacks

    def test_callback_timeout(self, collector):
        """Test that slow callbacks timeout properly"""
        executed = {"slow": False, "fast": False}

        def slow_callback(data):
            time.sleep(2.0)  # Longer than timeout (0.5s)
            executed["slow"] = True

        def fast_callback(data):
            executed["fast"] = True

        # Register both callbacks
        collector.register_callback("car_update", slow_callback)
        collector.register_callback("car_update", fast_callback)

        # Trigger callbacks
        collector._trigger_callbacks("car_update", CarTelemetry())

        # Wait for fast callback to complete
        time.sleep(0.3)

        # Fast callback should complete, slow should timeout
        assert executed["fast"] is True, "Fast callback should have executed"

        # Wait a bit more to ensure slow callback times out
        time.sleep(0.5)

        # Slow callback should not have completed due to timeout
        assert executed["slow"] is False, "Slow callback should have timed out"

    def test_callback_exception_handling(self, collector):
        """Test that callback exceptions are handled gracefully"""
        successful_callback_called = {"called": False}

        def failing_callback(data):
            raise ValueError("Test error")

        def successful_callback(data):
            successful_callback_called["called"] = True

        # Register both callbacks
        collector.register_callback("car_update", failing_callback)
        collector.register_callback("car_update", successful_callback)

        # Trigger callbacks - should not crash
        collector._trigger_callbacks("car_update", CarTelemetry())

        # Wait for callbacks to complete
        time.sleep(0.2)

        # Successful callback should still execute despite error in first one
        assert (
            successful_callback_called["called"] is True
        ), "Successful callback should execute even after error"

    def test_no_race_condition_on_callback_list(self, collector):
        """Test that there are no race conditions when accessing callback list"""
        errors = []

        def register_and_trigger():
            try:
                for i in range(20):
                    callback = Mock(__name__=f"callback_{i}")
                    collector.register_callback("car_update", callback)
                    collector._trigger_callbacks("car_update", CarTelemetry())
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=register_and_trigger)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should complete without errors
        assert len(errors) == 0, f"Race conditions detected: {errors}"

    def test_custom_timeout_value(self, mock_client):
        """Test that custom timeout values work correctly"""
        # Create collector with very short timeout
        collector = TelemetryCollector(mock_client, callback_timeout=0.1)

        try:
            executed = {"flag": False}

            def slow_callback(data):
                time.sleep(0.5)
                executed["flag"] = True

            collector.register_callback("car_update", slow_callback)
            collector._trigger_callbacks("car_update", CarTelemetry())

            # Wait slightly longer than timeout
            time.sleep(0.2)

            # Callback should have timed out
            assert (
                executed["flag"] is False
            ), "Callback should have timed out with custom timeout"
        finally:
            collector.callback_executor.shutdown(wait=False)

    def test_custom_worker_count(self, mock_client):
        """Test that custom worker count is respected"""
        collector = TelemetryCollector(mock_client, max_callback_workers=2)

        try:
            # Verify executor was created with correct worker count
            assert (
                collector.callback_executor._max_workers == 2
            ), "Executor should have 2 workers"
        finally:
            collector.callback_executor.shutdown(wait=False)

    def test_stop_shuts_down_executor(self, collector):
        """Test that stop() properly shuts down the executor"""
        # Set collector as running
        collector.running = True
        collector.stop()

        # Executor should be shut down
        # Try to submit a task - should fail if shut down
        def dummy_task():
            pass

        # This should raise an error because executor is shut down
        with pytest.raises(RuntimeError):
            future = collector.callback_executor.submit(dummy_task)
            future.result()

    def test_callback_name_in_error_log(self, collector, caplog):
        """Test that callback name appears in error logs"""
        import logging

        caplog.set_level(logging.ERROR)

        def named_callback(data):
            raise ValueError("Test error")

        collector.register_callback("car_update", named_callback)
        collector._trigger_callbacks("car_update", CarTelemetry())

        # Wait for callback to execute
        time.sleep(0.2)

        # Check that callback name appears in log
        assert any(
            "named_callback" in record.message for record in caplog.records
        ), "Callback name should appear in error log"

    def test_callback_name_in_timeout_log(self, collector, caplog):
        """Test that callback name appears in timeout warnings"""
        import logging

        caplog.set_level(logging.WARNING)

        def slow_named_callback(data):
            time.sleep(2.0)

        collector.register_callback("car_update", slow_named_callback)
        collector._trigger_callbacks("car_update", CarTelemetry())

        # Wait for timeout
        time.sleep(0.7)

        # Check that callback name appears in warning
        assert any(
            "slow_named_callback" in record.message for record in caplog.records
        ), "Callback name should appear in timeout warning"

    def test_multiple_event_types_thread_safe(self, collector):
        """Test that different event types can be accessed safely"""
        errors = []

        def register_different_events(event_type):
            try:
                for i in range(10):
                    callback = Mock(__name__=f"callback_{event_type}_{i}")
                    collector.register_callback(event_type, callback)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        # Register to different event types concurrently
        event_types = ["car_update", "lap_complete", "split_time"]
        threads = []

        for event_type in event_types:
            thread = threading.Thread(
                target=register_different_events, args=(event_type,)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Should complete without errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all callbacks were registered
        for event_type in event_types:
            assert (
                len(collector.callbacks[event_type]) == 10
            ), f"Wrong number of callbacks for {event_type}"
