"""
InSim Connection Module
Management of connections to the Live for Speed server via the InSim protocol
"""

__version__ = "0.1.0"

from .insim_client import InSimClient, ConnectionState, TinySubtype
from .packet_handler import PacketHandler
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpenError, CircuitState

__all__ = [
    "InSimClient",
    "ConnectionState",
    "TinySubtype",
    "PacketHandler",
    "CircuitBreaker",
    "CircuitBreakerOpenError",
    "CircuitState",
]
