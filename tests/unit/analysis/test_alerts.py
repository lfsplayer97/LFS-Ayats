"""
Unit tests for AlertSystem
"""

from src.analysis.alerts import (
    AlertSystem,
    Alert,
    AlertLevel,
    AlertHandler,
    ConsoleAlertHandler,
    LogAlertHandler,
    CallbackAlertHandler,
)


class TestAlertHandler(AlertHandler):
    """Test alert handler for testing purposes"""

    def __init__(self):
        self.handled_alerts = []

    def handle(self, alert: Alert):
        self.handled_alerts.append(alert)


class TestAlertSystem:
    """Test cases for AlertSystem"""

    def test_init(self):
        """Test alert system initialization"""
        system = AlertSystem()
        assert system.alert_history == []
        assert len(system.alert_handlers) > 0  # Default LogHandler

    def test_register_handler(self):
        """Test handler registration"""
        system = AlertSystem()
        handler = TestAlertHandler()
        initial_count = len(system.alert_handlers)

        system.register_handler(handler)
        assert len(system.alert_handlers) == initial_count + 1

    def test_unregister_handler(self):
        """Test handler unregistration"""
        system = AlertSystem()
        handler = TestAlertHandler()

        system.register_handler(handler)
        system.unregister_handler(handler)
        assert handler not in system.alert_handlers

    def test_trigger_alert(self):
        """Test triggering an alert"""
        system = AlertSystem()
        handler = TestAlertHandler()
        system.register_handler(handler)

        alert = Alert(AlertLevel.WARNING, "Test alert")
        result = system.trigger_alert(alert)

        assert result is True
        assert len(handler.handled_alerts) == 1
        assert handler.handled_alerts[0] == alert

    def test_trigger_alert_with_filtering(self):
        """Test alert filtering with minimum interval"""
        system = AlertSystem(enable_filtering=True)
        handler = TestAlertHandler()
        system.register_handler(handler)

        alert1 = Alert(AlertLevel.WARNING, "Test")
        alert2 = Alert(AlertLevel.WARNING, "Test")

        system.trigger_alert(alert1, min_interval=10.0)
        result = system.trigger_alert(alert2, min_interval=10.0)

        assert result is False  # Should be filtered

    def test_create_and_trigger(self):
        """Test creating and triggering an alert in one step"""
        system = AlertSystem()
        handler = TestAlertHandler()
        system.register_handler(handler)

        result = system.create_and_trigger(
            AlertLevel.INFO, "Test message", {"key": "value"}
        )

        assert result is True
        assert len(handler.handled_alerts) == 1
        assert handler.handled_alerts[0].message == "Test message"

    def test_check_conditions_temperature(self):
        """Test automatic condition checking for temperature"""
        system = AlertSystem()
        handler = TestAlertHandler()
        system.register_handler(handler)

        data = {"engine_temp": 110.0}
        alerts = system.check_conditions(data)

        assert len(alerts) > 0
        assert any("Sobreescalfament" in a.message for a in alerts)

    def test_check_conditions_fuel(self):
        """Test automatic condition checking for fuel"""
        system = AlertSystem()
        handler = TestAlertHandler()
        system.register_handler(handler)

        data = {"fuel": 3.0}
        alerts = system.check_conditions(data)

        assert len(alerts) > 0
        assert any("Combustible" in a.message for a in alerts)

    def test_get_history(self):
        """Test getting alert history"""
        system = AlertSystem()
        alert1 = Alert(AlertLevel.INFO, "Info alert")
        alert2 = Alert(AlertLevel.WARNING, "Warning alert")

        system.trigger_alert(alert1)
        system.trigger_alert(alert2)

        history = system.get_history()
        assert len(history) == 2

    def test_get_history_filtered_by_level(self):
        """Test getting filtered alert history"""
        system = AlertSystem()
        alert1 = Alert(AlertLevel.INFO, "Info alert")
        alert2 = Alert(AlertLevel.WARNING, "Warning alert")

        system.trigger_alert(alert1)
        system.trigger_alert(alert2)

        warnings = system.get_history(level=AlertLevel.WARNING)
        assert len(warnings) == 1
        assert warnings[0].level == AlertLevel.WARNING

    def test_get_history_with_limit(self):
        """Test getting limited alert history"""
        system = AlertSystem()

        for i in range(10):
            system.trigger_alert(Alert(AlertLevel.INFO, f"Alert {i}"))

        history = system.get_history(limit=5)
        assert len(history) == 5

    def test_get_statistics(self):
        """Test getting system statistics"""
        system = AlertSystem()
        system.trigger_alert(Alert(AlertLevel.INFO, "Info"))
        system.trigger_alert(Alert(AlertLevel.WARNING, "Warning"))

        stats = system.get_statistics()
        assert stats["total_alerts"] == 2
        assert "alert_counts" in stats

    def test_clear_history(self):
        """Test clearing alert history"""
        system = AlertSystem()
        system.trigger_alert(Alert(AlertLevel.INFO, "Test"))

        assert len(system.alert_history) > 0
        system.clear_history()
        assert len(system.alert_history) == 0

    def test_set_filtering(self):
        """Test enabling/disabling filtering"""
        system = AlertSystem()
        system.set_filtering(False)
        assert system.enable_filtering is False

        system.set_filtering(True)
        assert system.enable_filtering is True

    def test_max_history_limit(self):
        """Test maximum history limit"""
        system = AlertSystem(max_history=5)

        for i in range(10):
            system.trigger_alert(Alert(AlertLevel.INFO, f"Alert {i}"))

        assert len(system.alert_history) <= 5


class TestConsoleAlertHandler:
    """Test cases for ConsoleAlertHandler"""

    def test_handle(self, capsys):
        """Test console alert handling"""
        handler = ConsoleAlertHandler()
        alert = Alert(AlertLevel.WARNING, "Test warning")

        handler.handle(alert)

        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "Test warning" in captured.out


class TestLogAlertHandler:
    """Test cases for LogAlertHandler"""

    def test_handle(self):
        """Test log alert handling"""
        handler = LogAlertHandler()
        alert = Alert(AlertLevel.INFO, "Test info")

        # Should not raise exception
        handler.handle(alert)


class TestCallbackAlertHandler:
    """Test cases for CallbackAlertHandler"""

    def test_handle(self):
        """Test callback alert handling"""
        received_alerts = []

        def callback(alert):
            received_alerts.append(alert)

        handler = CallbackAlertHandler(callback)
        alert = Alert(AlertLevel.ERROR, "Test error")

        handler.handle(alert)

        assert len(received_alerts) == 1
        assert received_alerts[0] == alert

    def test_handle_with_exception(self):
        """Test callback with exception"""

        def failing_callback(alert):
            raise ValueError("Test error")

        handler = CallbackAlertHandler(failing_callback)
        alert = Alert(AlertLevel.INFO, "Test")

        # Should not raise exception
        handler.handle(alert)


class TestAlert:
    """Test cases for Alert model"""

    def test_init(self):
        """Test alert initialization"""
        alert = Alert(AlertLevel.WARNING, "Test message")
        assert alert.level == AlertLevel.WARNING
        assert alert.message == "Test message"
        assert alert.timestamp > 0
        assert alert.data == {}

    def test_init_with_data(self):
        """Test alert initialization with data"""
        alert = Alert(AlertLevel.ERROR, "Error occurred", data={"error_code": 500})
        assert alert.data["error_code"] == 500

    def test_str_representation(self):
        """Test alert string representation"""
        alert = Alert(AlertLevel.INFO, "Info message")
        str_repr = str(alert)
        assert "INFO" in str_repr
        assert "Info message" in str_repr
