"""
Unit tests for Telemetry Buffer
"""

from unittest.mock import Mock
from src.telemetry.buffer import TelemetryBuffer


class TestTelemetryBuffer:
    """Test cases for TelemetryBuffer"""

    def test_init(self):
        """Test buffer initialization"""
        buffer = TelemetryBuffer(max_size=100)

        assert buffer.max_size == 100
        assert buffer.size() == 0
        assert buffer.is_empty()
        assert not buffer.is_full()

    def test_add_item(self):
        """Test adding item to buffer"""
        buffer = TelemetryBuffer(max_size=10)

        result = buffer.add({"speed": 100})

        assert result is True
        assert buffer.size() == 1
        assert not buffer.is_empty()

    def test_add_item_with_timestamp(self):
        """Test that timestamp is added to dict items"""
        buffer = TelemetryBuffer(max_size=10)

        data = {"speed": 100}
        buffer.add(data)

        # Check that buffered_at was added
        assert "buffered_at" in data

    def test_get_item(self):
        """Test getting item from buffer (FIFO)"""
        buffer = TelemetryBuffer(max_size=10)

        buffer.add({"id": 1})
        buffer.add({"id": 2})

        item1 = buffer.get()
        item2 = buffer.get()

        assert item1["id"] == 1
        assert item2["id"] == 2
        assert buffer.is_empty()

    def test_get_from_empty_buffer(self):
        """Test getting from empty buffer returns None"""
        buffer = TelemetryBuffer(max_size=10)

        result = buffer.get()

        assert result is None

    def test_buffer_max_size(self):
        """Test that buffer respects max size"""
        buffer = TelemetryBuffer(max_size=3)

        # Add 5 items
        for i in range(5):
            buffer.add({"id": i})

        # Buffer should only have 3 items (last 3)
        assert buffer.size() == 3
        assert buffer.is_full()

        # First items should have been dropped
        item = buffer.get()
        assert item["id"] == 2  # Items 0 and 1 were dropped

    def test_dropped_count(self):
        """Test that dropped items are counted"""
        buffer = TelemetryBuffer(max_size=2)

        # Add 4 items (2 will be dropped)
        for i in range(4):
            buffer.add({"id": i})

        stats = buffer.get_stats()
        assert stats["dropped_count"] == 2

    def test_flush_to_exporter_with_method(self):
        """Test flushing to exporter with export method"""
        buffer = TelemetryBuffer(max_size=10)

        # Add items
        for i in range(3):
            buffer.add({"id": i})

        # Create mock exporter
        exporter = Mock()
        exporter.export = Mock()

        # Flush
        count = buffer.flush_to_exporter(exporter)

        assert count == 3
        assert buffer.is_empty()
        assert exporter.export.call_count == 3

    def test_flush_to_exporter_callable(self):
        """Test flushing to callable exporter"""
        buffer = TelemetryBuffer(max_size=10)

        # Add items
        for i in range(3):
            buffer.add({"id": i})

        # Create mock callable exporter (using spec to avoid export attribute)
        exporter = Mock(spec=["__call__"])

        # Flush
        count = buffer.flush_to_exporter(exporter)

        assert count == 3
        assert buffer.is_empty()
        assert exporter.call_count == 3

    def test_flush_to_callback(self):
        """Test flushing to callback function"""
        buffer = TelemetryBuffer(max_size=10)

        # Add items
        for i in range(3):
            buffer.add({"id": i})

        # Create callback
        callback = Mock()

        # Flush
        count = buffer.flush_to_callback(callback)

        assert count == 3
        assert buffer.is_empty()
        assert callback.call_count == 3

    def test_flush_handles_exporter_error(self):
        """Test that flush handles exporter errors gracefully"""
        buffer = TelemetryBuffer(max_size=10)

        buffer.add({"id": 1})
        buffer.add({"id": 2})

        # Create exporter that fails on second item
        exporter = Mock()
        exporter.export = Mock(side_effect=[None, Exception("Export error")])

        count = buffer.flush_to_exporter(exporter)

        # Only first item should be flushed
        assert count == 1
        # Second item should still be in buffer
        assert buffer.size() == 1

    def test_flush_handles_callback_error(self):
        """Test that flush handles callback errors gracefully"""
        buffer = TelemetryBuffer(max_size=10)

        buffer.add({"id": 1})
        buffer.add({"id": 2})

        # Create callback that fails on second item
        callback = Mock(side_effect=[None, Exception("Callback error")])

        count = buffer.flush_to_callback(callback)

        # Only first item should be flushed
        assert count == 1
        assert buffer.size() == 1

    def test_clear(self):
        """Test clearing buffer"""
        buffer = TelemetryBuffer(max_size=10)

        for i in range(5):
            buffer.add({"id": i})

        count = buffer.clear()

        assert count == 5
        assert buffer.is_empty()
        assert buffer.size() == 0

    def test_is_full(self):
        """Test is_full method"""
        buffer = TelemetryBuffer(max_size=2)

        assert not buffer.is_full()

        buffer.add({"id": 1})
        assert not buffer.is_full()

        buffer.add({"id": 2})
        assert buffer.is_full()

    def test_get_stats(self):
        """Test get_stats method"""
        buffer = TelemetryBuffer(max_size=10)

        for i in range(5):
            buffer.add({"id": i})

        stats = buffer.get_stats()

        assert stats["size"] == 5
        assert stats["max_size"] == 10
        assert stats["dropped_count"] == 0
        assert stats["utilization"] == 0.5

    def test_thread_safety(self):
        """Test that buffer operations are thread-safe"""
        import threading

        buffer = TelemetryBuffer(max_size=1000)

        def add_items():
            for i in range(100):
                buffer.add({"id": i})

        # Create multiple threads adding items
        threads = [threading.Thread(target=add_items) for _ in range(5)]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        # Should have 500 items added
        assert buffer.size() == 500

    def test_non_dict_items(self):
        """Test adding non-dict items"""
        buffer = TelemetryBuffer(max_size=10)

        # Add non-dict items
        buffer.add("string item")
        buffer.add(123)
        buffer.add([1, 2, 3])

        assert buffer.size() == 3

        # Get items back
        assert buffer.get() == "string item"
        assert buffer.get() == 123
        assert buffer.get() == [1, 2, 3]

    def test_flush_to_exporter_invalid_exporter(self):
        """Test flushing with invalid exporter (not callable and no export method)"""
        buffer = TelemetryBuffer(max_size=10)
        buffer.add({"id": 1})

        # Create invalid exporter (not callable, no export method)
        invalid_exporter = object()

        # Flush should fail and item should remain in buffer
        count = buffer.flush_to_exporter(invalid_exporter)

        assert count == 0
        assert buffer.size() == 1  # Item should still be in buffer

    def test_clear_empty_buffer(self):
        """Test clearing an already empty buffer"""
        buffer = TelemetryBuffer(max_size=10)

        count = buffer.clear()

        assert count == 0
        assert buffer.is_empty()

    def test_clear_resets_dropped_count(self):
        """Test that clear resets the dropped count"""
        buffer = TelemetryBuffer(max_size=2)

        # Add items to exceed capacity
        for i in range(5):
            buffer.add({"id": i})

        stats_before = buffer.get_stats()
        assert stats_before["dropped_count"] > 0

        # Clear buffer
        buffer.clear()

        stats_after = buffer.get_stats()
        assert stats_after["dropped_count"] == 0

    def test_get_stats_empty_buffer(self):
        """Test get_stats on empty buffer"""
        buffer = TelemetryBuffer(max_size=10)

        stats = buffer.get_stats()

        assert stats["size"] == 0
        assert stats["max_size"] == 10
        assert stats["dropped_count"] == 0
        assert stats["utilization"] == 0.0

    def test_get_stats_utilization(self):
        """Test stats utilization calculation at different levels"""
        buffer = TelemetryBuffer(max_size=100)

        # Empty
        assert buffer.get_stats()["utilization"] == 0.0

        # 25%
        for i in range(25):
            buffer.add({"id": i})
        assert buffer.get_stats()["utilization"] == 0.25

        # 50%
        for i in range(25):
            buffer.add({"id": i})
        assert buffer.get_stats()["utilization"] == 0.5

        # 100%
        for i in range(50):
            buffer.add({"id": i})
        assert buffer.get_stats()["utilization"] == 1.0

    def test_flush_to_callback_empty_buffer(self):
        """Test flushing empty buffer to callback"""
        buffer = TelemetryBuffer(max_size=10)
        callback = Mock()

        count = buffer.flush_to_callback(callback)

        assert count == 0
        assert callback.call_count == 0

    def test_flush_to_exporter_empty_buffer(self):
        """Test flushing empty buffer to exporter"""
        buffer = TelemetryBuffer(max_size=10)
        exporter = Mock()
        exporter.export = Mock()

        count = buffer.flush_to_exporter(exporter)

        assert count == 0
        assert exporter.export.call_count == 0

    def test_add_preserves_existing_buffered_at(self):
        """Test that existing buffered_at timestamp is not overwritten"""
        buffer = TelemetryBuffer(max_size=10)

        existing_timestamp = "2024-01-01T00:00:00"
        data = {"speed": 100, "buffered_at": existing_timestamp}
        buffer.add(data)

        # Existing timestamp should be preserved
        assert data["buffered_at"] == existing_timestamp
