"""
Base email provider implementation.
"""

import abc
from typing import Dict, List, Tuple, Optional
import time

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