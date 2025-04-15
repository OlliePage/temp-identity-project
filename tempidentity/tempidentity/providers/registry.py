#!/usr/bin/env python3
"""
This demonstrates how to set up the provider package structure for TempIdentity
"""

# Example directory structure:
#
# tempidentity/
# ├── tempidentity/
# │   ├── __init__.py
# │   ├── tempidentity.py  # Main application
# │   ├── providers/       # Provider package
# │   │   ├── __init__.py
# │   │   ├── email/       # Email providers
# │   │   │   ├── __init__.py
# │   │   │   ├── base.py  # Base email provider class
# │   │   │   ├── mailgw.py
# │   │   │   └── temp_mail.py
# │   │   └── sms/         # SMS providers
# │   │       ├── __init__.py
# │   │       ├── base.py  # Base SMS provider class
# │   │       ├── textverified.py
# │   │       └── twilio.py
# │   └── utils/           # Utility functions
# │       ├── __init__.py
# │       └── ...
# ├── setup.py
# └── README.md

# Example provider package initialization:

# tempidentity/providers/__init__.py
"""
Provider package for TempIdentity.
This package contains email and SMS provider implementations.
"""


def get_registry():
    """
    Get the provider registry.

    Returns:
        ProviderRegistry: The provider registry instance.
    """
    from tempidentity.tempidentity.providers.registry import registry
    return registry


# tempidentity/providers/email/__init__.py
"""
Email provider implementations for TempIdentity.
"""

# Import other email providers here
# from tempidentity.providers.email.temp_mail import TempMailProvider

__all__ = ['EmailProvider', 'MailGwProvider']

# tempidentity/providers/sms/__init__.py
"""
SMS provider implementations for TempIdentity.
"""

# Import other SMS providers here
# from tempidentity.providers.sms.twilio import TwilioProvider

__all__ = ['SMSProvider', 'TextVerifiedProvider']

# tempidentity/providers/registry.py
"""
Provider registry for TempIdentity.
"""

from typing import Dict, Type, Optional
import inspect

from tempidentity.providers.email.base import EmailProvider
from tempidentity.providers.sms.base import SMSProvider


class ProviderRegistry:
    """Registry for email and SMS providers."""

    def __init__(self):
        """Initialize empty provider registries."""
        self.email_providers = {}  # name -> class mapping
        self.sms_providers = {}  # name -> class mapping
        self._initialized = False

    def register_email_provider(self, provider_class: Type[EmailProvider]):
        """Register an email provider class."""
        self.email_providers[provider_class.name] = provider_class

    def register_sms_provider(self, provider_class: Type[SMSProvider]):
        """Register an SMS provider class."""
        self.sms_providers[provider_class.name] = provider_class

    def get_email_provider(self, name: str) -> Optional[Type[EmailProvider]]:
        """Get an email provider class by name."""
        self._ensure_initialized()
        return self.email_providers.get(name)

    def get_sms_provider(self, name: str) -> Optional[Type[SMSProvider]]:
        """Get an SMS provider class by name."""
        self._ensure_initialized()
        return self.sms_providers.get(name)

    def get_all_email_providers(self) -> Dict[str, Type[EmailProvider]]:
        """Get all registered email providers."""
        self._ensure_initialized()
        return self.email_providers.copy()

    def get_all_sms_providers(self) -> Dict[str, Type[SMSProvider]]:
        """Get all registered SMS providers."""
        self._ensure_initialized()
        return self.sms_providers.copy()

    def create_email_provider(self, name: str, config: Dict = None) -> Optional[EmailProvider]:
        """Create an instance of an email provider by name."""
        self._ensure_initialized()
        provider_class = self.get_email_provider(name)
        if provider_class:
            return provider_class(config)
        return None

    def create_sms_provider(self, name: str, config: Dict = None) -> Optional[SMSProvider]:
        """Create an instance of an SMS provider by name."""
        self._ensure_initialized()
        provider_class = self.get_sms_provider(name)
        if provider_class:
            return provider_class(config)
        return None

    def _ensure_initialized(self):
        """Ensure the registry is initialized."""
        if not self._initialized:
            self._discover_builtin_providers()
            self._initialized = True

    def _discover_builtin_providers(self):
        """Discover built-in providers."""
        try:
            # Import email providers
            import tempidentity.providers.email as email_module
            for name in dir(email_module):
                obj = getattr(email_module, name)
                if (inspect.isclass(obj) and issubclass(obj, EmailProvider) and
                        obj != EmailProvider and hasattr(obj, 'name')):
                    self.register_email_provider(obj)

            # Import SMS providers
            import tempidentity.providers.sms as sms_module
            for name in dir(sms_module):
                obj = getattr(sms_module, name)
                if (inspect.isclass(obj) and issubclass(obj, SMSProvider) and
                        obj != SMSProvider and hasattr(obj, 'name')):
                    self.register_sms_provider(obj)
        except ImportError:
            # Handle import errors
            pass


# Create a singleton instance
registry = ProviderRegistry()

# tempidentity/providers/email/base.py
"""
Base email provider implementation.
"""

import abc
from typing import Dict, List, Tuple


class EmailProvider(abc.ABC):
    """Abstract base class for all email service providers."""

    # Class attributes for provider registration
    name = "base"  # Provider name for configuration
    display_name = "Base Provider"  # Human-readable name
    description = "Base email provider class"  # Provider description
    requires_api_key = False  # Whether this provider requires an API key

    def __init__(self, config: Dict = None):
        """Initialize the email provider with configuration."""
        self.config = config or {}
        self.email = None
        self.password = None

    @abc.abstractmethod
    def create_email(self) -> Tuple[bool, str, str]:
        """
        Create a temporary email address.

        Returns:
            Tuple[bool, str, str]: Success status, email address, and password
        """
        pass

    @abc.abstractmethod
    def check_messages(self) -> List[Dict]:
        """
        Check for messages in the inbox.

        Returns:
            List[Dict]: List of message objects
        """
        pass

    @abc.abstractmethod
    def wait_for_messages(self, timeout: int = 60, check_interval: int = 5) -> List[Dict]:
        """
        Wait for new messages to arrive.

        Args:
            timeout: Maximum time to wait in seconds
            check_interval: How often to check for new messages in seconds

        Returns:
            List[Dict]: List of new message objects
        """
        # Default implementation that can be overridden
        start_time = time.time()
        initial_messages = self.check_messages()
        initial_count = len(initial_messages)

        while time.time() - start_time < timeout:
            current_messages = self.check_messages()

            if len(current_messages) > initial_count:
                new_messages = current_messages[:len(current_messages) - initial_count]
                return new_messages

            time.sleep(check_interval)

        return []

    @abc.abstractmethod
    def get_message_content(self, message_id: str) -> Dict:
        """
        Get the content of a specific message.

        Args:
            message_id: ID of the message to retrieve

        Returns:
            Dict: Message content object
        """
        pass

    @classmethod
    def get_setup_fields(cls) -> List[Dict]:
        """
        Get fields needed for provider setup.

        Returns:
            List[Dict]: List of field definitions with name, type, required, etc.
        """
        fields = []
        if cls.requires_api_key:
            fields.append({
                "name": "api_key",
                "display_name": "API Key",
                "type": "password",
                "required": True,
                "help_text": f"API key for {cls.display_name}"
            })
        return fields


# tempidentity/providers/sms/base.py
"""
Base SMS provider implementation.
"""

import abc
from typing import Dict, List, Tuple, Optional
import time


class SMSProvider(abc.ABC):
    """Abstract base class for all SMS service providers."""

    # Class attributes for provider registration
    name = "base"  # Provider name for configuration
    display_name = "Base Provider"  # Human-readable name
    description = "Base SMS provider class"  # Provider description
    requires_api_key = True  # Whether this provider requires an API key

    def __init__(self, config: Dict = None):
        """Initialize the SMS provider with configuration."""
        self.config = config or {}
        self.phone_number = None
        self.verification_id = None

    @abc.abstractmethod
    def get_available_services(self) -> List[Dict]:
        """
        Get available services for verification.

        Returns:
            List[Dict]: List of service objects
        """
        pass

    @abc.abstractmethod
    def create_number(self, service_name: str) -> Tuple[bool, str]:
        """
        Create a temporary phone number for a service.

        Args:
            service_name: Name or ID of the service to create a number for

        Returns:
            Tuple[bool, str]: Success status and phone number
        """
        pass

    @abc.abstractmethod
    def check_sms(self) -> Optional[str]:
        """
        Check for received SMS.

        Returns:
            Optional[str]: SMS verification code if received, None otherwise
        """
        pass

    @abc.abstractmethod
    def wait_for_sms(self, timeout: int = 300, check_interval: int = 10) -> Optional[str]:
        """
        Wait for an SMS to arrive.

        Args:
            timeout: Maximum time to wait in seconds
            check_interval: How often to check for new SMS in seconds

        Returns:
            Optional[str]: SMS verification code if received, None otherwise
        """
        # Default implementation that can be overridden
        start_time = time.time()

        while time.time() - start_time < timeout:
            code = self.check_sms()

            if code:
                return code

            time.sleep(check_interval)

        return None

    @abc.abstractmethod
    def cancel_number(self) -> bool:
        """
        Cancel the current phone number.

        Returns:
            bool: Success status
        """
        pass

    @classmethod
    def get_setup_fields(cls) -> List[Dict]:
        """
        Get fields needed for provider setup.

        Returns:
            List[Dict]: List of field definitions with name, type, required, etc.
        """
        fields = []
        if cls.requires_api_key:
            fields.append({
                "name": "api_key",
                "display_name": "API Key",
                "type": "password",
                "required": True,
                "help_text": f"API key for {cls.display_name}"
            })
        return fields