"""
Pytest configuration file.
"""

import pytest
from tempidentity.providers.registry import ProviderRegistry


@pytest.fixture
def empty_registry():
    """
    Fixture that provides an empty provider registry.
    """
    return ProviderRegistry()