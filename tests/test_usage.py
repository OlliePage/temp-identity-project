"""
Tests demonstrating the usage of TempIdentity.

These tests serve as documentation and examples of how to use the TempIdentity package.
"""

import pytest
from unittest.mock import MagicMock, patch

from tempidentity.providers.registry import registry
from tempidentity.core import (
    load_config, save_config, create_temp_email, 
    check_email_messages, get_email_message_content,
    get_sms_services, create_temp_sms, wait_for_sms_code
)


class TestBasicUsage:
    """Basic usage patterns for TempIdentity."""

    def test_create_email_basic_flow(self):
        """
        Demonstrates the basic flow of creating a temporary email.
        
        This shows:
        1. How to create a temporary email
        2. How the return values are structured
        """
        # Mock the email provider to avoid actual API calls
        mock_provider = MagicMock()
        mock_provider.create_email.return_value = (True, "test@example.com", "password123")
        
        with patch('tempidentity.core.registry.create_email_provider', return_value=mock_provider):
            # Create a temporary email
            success, email, password, _ = create_temp_email()
            
            # Check results
            assert success is True
            assert email == "test@example.com"
            assert password == "password123"
    
    def test_email_check_messages_flow(self):
        """
        Demonstrates how to check for messages in a temporary email inbox.
        
        This shows:
        1. How to create an email
        2. How to check for messages
        3. The structure of message objects
        """
        # Sample message data
        sample_messages = [
            {
                "id": "msg1",
                "subject": "Test Subject",
                "from": {"address": "sender@example.com", "name": "Sender"},
                "createdAt": "2023-01-01T12:00:00Z",
                "text": "This is a test message."
            }
        ]
        
        # Mock the email provider
        mock_provider = MagicMock()
        mock_provider.check_messages.return_value = sample_messages
        
        with patch('tempidentity.core.registry.create_email_provider', return_value=mock_provider):
            # Check messages
            messages = check_email_messages("mail.gw", "test@example.com", "password", False)
            
            # Verify structure
            assert len(messages) == 1
            assert messages[0]["subject"] == "Test Subject"
            assert messages[0]["from"]["address"] == "sender@example.com"
            assert "text" in messages[0]
    
    def test_sms_basic_flow(self):
        """
        Demonstrates the basic flow of creating a temporary SMS number.
        
        This shows:
        1. How to get available SMS services
        2. How to create a temporary phone number
        3. How to wait for SMS verification codes
        """
        # Sample service data
        sample_services = [
            {"id": "service1", "name": "Service 1", "price": "1.00"},
            {"id": "service2", "name": "Service 2", "price": "2.00"}
        ]
        
        # Mock the SMS provider
        mock_provider = MagicMock()
        mock_provider.get_available_services.return_value = sample_services
        mock_provider.create_number.return_value = (True, "+1234567890")
        mock_provider.wait_for_sms.return_value = "123456"
        
        # Need to patch config loading as well
        mock_config = {
            "providers": {
                "textverified": {"api_key": "test-api-key"}
            }
        }
        
        with patch('tempidentity.core.registry.create_sms_provider', return_value=mock_provider):
            with patch('tempidentity.core.load_config', return_value=mock_config):
                # Get available services
                services = get_sms_services()
                assert len(services) == 2
                assert services[0]["id"] == "service1"
                
                # Create a temporary phone number
                success, phone_number, _ = create_temp_sms("service1")
                assert success is True
                assert phone_number == "+1234567890"
                
                # Wait for SMS code
                code = wait_for_sms_code("textverified", 60)
                assert code == "123456"


class TestConfiguration:
    """Tests demonstrating configuration patterns."""
    
    def test_configuration_flow(self, tmpdir):
        """
        Demonstrates how to configure TempIdentity.
        
        This shows:
        1. How to load configuration
        2. How to modify configuration
        3. How to save configuration
        """
        # Create a test config
        test_config = {
            "preferred_email_service": "mail.gw",
            "preferred_sms_service": "textverified",
            "providers": {
                "mail.gw": {},
                "textverified": {"api_key": "test-api-key"}
            },
            "default_wait_time": 120,
            "save_history": True,
            "history_limit": 20
        }
        
        # Modify the configuration
        test_config["default_wait_time"] = 180
        test_config["providers"]["textverified"]["api_key"] = "new-api-key"
        
        # Check structure of the configuration
        assert test_config["preferred_email_service"] == "mail.gw"
        assert test_config["providers"]["textverified"]["api_key"] == "new-api-key"
        assert test_config["default_wait_time"] == 180


class TestProviders:
    """Tests demonstrating provider usage patterns."""
    
    def test_provider_discovery(self):
        """
        Demonstrates how providers are discovered and registered.
        
        This shows:
        1. How to get all available providers
        2. How to check for specific providers
        """
        # Get all email and SMS providers
        email_providers = registry.get_all_email_providers()
        sms_providers = registry.get_all_sms_providers()
        
        # Check that we have at least one provider of each type
        assert len(email_providers) >= 1
        assert len(sms_providers) >= 1
        
        # Check that we have the expected built-in providers
        assert "mail.gw" in email_providers
        assert "textverified" in sms_providers
    
    def test_create_provider_instances(self):
        """
        Demonstrates how to create provider instances.
        
        This shows:
        1. How to create an email provider instance
        2. How to create an SMS provider instance
        3. How to pass configuration to providers
        """
        # Create configuration
        email_config = {}
        sms_config = {"api_key": "test-api-key"}
        
        # Create provider instances (with mocking to avoid actual instantiation)
        with patch('tempidentity.providers.registry.ProviderRegistry.get_email_provider') as mock_get_email:
            with patch('tempidentity.providers.registry.ProviderRegistry.get_sms_provider') as mock_get_sms:
                # Setup mocks
                mock_email_class = MagicMock()
                mock_sms_class = MagicMock()
                mock_get_email.return_value = mock_email_class
                mock_get_sms.return_value = mock_sms_class
                
                # Create instances
                registry.create_email_provider("mail.gw", email_config)
                registry.create_sms_provider("textverified", sms_config)
                
                # Verify calls
                mock_email_class.assert_called_once_with(email_config)
                mock_sms_class.assert_called_once_with(sms_config)