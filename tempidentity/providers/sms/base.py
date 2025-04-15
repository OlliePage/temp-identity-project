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
    def wait_for_sms(
        self, timeout: int = 300, check_interval: int = 10
    ) -> Optional[str]:
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
            fields.append(
                {
                    "name": "api_key",
                    "display_name": "API Key",
                    "type": "password",
                    "required": True,
                    "help_text": f"API key for {cls.display_name}",
                }
            )
        return fields
