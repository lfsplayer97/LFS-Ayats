from __future__ import annotations

import pytest

from src.insim_client import InSimClient, InSimConfig


@pytest.fixture()
def insim_config() -> InSimConfig:
    """Return a default configuration for unit tests."""

    return InSimConfig(host="127.0.0.1", port=12345)


@pytest.fixture()
def insim_client_factory(insim_config: InSimConfig):
    """Provide a factory that builds :class:`InSimClient` instances."""

    def factory(**kwargs) -> InSimClient:
        return InSimClient(insim_config, **kwargs)

    return factory
