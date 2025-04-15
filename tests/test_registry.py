"""
Tests for the provider registry.
"""

import pytest
from tempidentity.providers.registry import ProviderRegistry
from tempidentity.providers.email.base import EmailProvider
from tempidentity.providers.sms.base import SMSProvider


# Create mock provider classes for testing
class MockEmailProvider(EmailProvider):
    name = "mock_email"
    display_name = "Mock Email"
    description = "Mock email provider for testing"
    
    def create_email(self) -> tuple:
        return True, "test@example.com", "password"
    
    def check_messages(self) -> list:
        return []
    
    def wait_for_messages(self, timeout=60, check_interval=5) -> list:
        return []
    
    def get_message_content(self, message_id) -> dict:
        return {}


class MockSMSProvider(SMSProvider):
    name = "mock_sms"
    display_name = "Mock SMS"
    description = "Mock SMS provider for testing"
    
    def get_available_services(self) -> list:
        return [{"id": "service1", "name": "Service 1", "price": "1.00"}]
    
    def create_number(self, service_name) -> tuple:
        return True, "+1234567890"
    
    def check_sms(self) -> None:
        return None
    
    def wait_for_sms(self, timeout=300, check_interval=10) -> None:
        return None
    
    def cancel_number(self) -> bool:
        return True


def test_registry_initialization():
    """Test that the registry initializes properly."""
    registry = ProviderRegistry()
    assert registry.email_providers == {}
    assert registry.sms_providers == {}
    assert registry._initialized is False


def test_register_providers():
    """Test registering providers."""
    registry = ProviderRegistry()
    
    # Register providers
    registry.register_email_provider(MockEmailProvider)
    registry.register_sms_provider(MockSMSProvider)
    
    # Check registration
    assert "mock_email" in registry.email_providers
    assert registry.email_providers["mock_email"] == MockEmailProvider
    assert "mock_sms" in registry.sms_providers
    assert registry.sms_providers["mock_sms"] == MockSMSProvider


def test_get_providers():
    """Test getting providers."""
    registry = ProviderRegistry()
    
    # Register providers
    registry.register_email_provider(MockEmailProvider)
    registry.register_sms_provider(MockSMSProvider)
    
    # Get providers
    email_provider = registry.get_email_provider("mock_email")
    sms_provider = registry.get_sms_provider("mock_sms")
    
    assert email_provider == MockEmailProvider
    assert sms_provider == MockSMSProvider
    
    # Try getting non-existent provider
    assert registry.get_email_provider("non_existent") is None
    assert registry.get_sms_provider("non_existent") is None


def test_create_providers():
    """Test creating provider instances."""
    registry = ProviderRegistry()
    
    # Register providers
    registry.register_email_provider(MockEmailProvider)
    registry.register_sms_provider(MockSMSProvider)
    
    # Create provider instances
    email_provider = registry.create_email_provider("mock_email")
    sms_provider = registry.create_sms_provider("mock_sms")
    
    assert isinstance(email_provider, MockEmailProvider)
    assert isinstance(sms_provider, MockSMSProvider)
    
    # Try creating non-existent provider
    assert registry.create_email_provider("non_existent") is None
    assert registry.create_sms_provider("non_existent") is None


def test_get_all_providers():
    """Test getting all providers."""
    registry = ProviderRegistry()
    
    # Register providers
    registry.register_email_provider(MockEmailProvider)
    registry.register_sms_provider(MockSMSProvider)
    
    # Get all providers
    email_providers = registry.get_all_email_providers()
    sms_providers = registry.get_all_sms_providers()
    
    assert len(email_providers) == 1
    assert "mock_email" in email_providers
    assert email_providers["mock_email"] == MockEmailProvider
    
    assert len(sms_providers) == 1
    assert "mock_sms" in sms_providers
    assert sms_providers["mock_sms"] == MockSMSProvider