# TempIdentity Plugin Development Guide

This guide explains how to create custom provider plugins for the TempIdentity package. By following this structure, you can easily add new email or SMS providers that integrate seamlessly with the application.

## Plugin Architecture Overview

TempIdentity uses an abstract provider architecture with the following key components:

1. **Abstract Base Classes**: `EmailProvider` and `SMSProvider` define the interface that all providers must implement
2. **Provider Registry**: Central system that manages provider registration and discovery
3. **Provider Implementations**: Concrete classes that implement the provider interfaces

## Creating a New Email Provider

### 1. Create a new module file

Start by creating a new Python module in the `tempidentity/providers/email/` directory. For example, to create a provider for "ExampleMail", create a file named `examplemail.py`.

### 2. Implement the EmailProvider interface

```python
from tempidentity.providers.email.base import EmailProvider
from typing import Dict, List, Tuple
import requests
import json
import time

class ExampleMailProvider(EmailProvider):
    """Implementation for ExampleMail service."""
    
    name = "examplemail"  # Unique identifier for the provider
    display_name = "ExampleMail"  # Human-readable name
    description = "Example email service provider"  # Provider description
    requires_api_key = True  # Whether this provider requires an API key
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key', '')
        self.base_url = "https://api.examplemail.com/v1"
        self.email = None
        self.password = None
    
    def create_email(self) -> Tuple[bool, str, str]:
        """Create a temporary email address."""
        # Implementation code here
        # Must return: (success_bool, email_address, password)
        pass
    
    def check_messages(self) -> List[Dict]:
        """Check for messages in the inbox."""
        # Implementation code here
        # Must return: list of message objects
        pass
    
    def wait_for_messages(self, timeout: int = 60, check_interval: int = 5) -> List[Dict]:
        """Wait for new messages to arrive."""
        # Implementation code here
        # Must return: list of new message objects
        # Note: You can use the default implementation from the base class
        return super().wait_for_messages(timeout, check_interval)
    
    def get_message_content(self, message_id: str) -> Dict:
        """Get the content of a specific message."""
        # Implementation code here
        # Must return: message content object
        pass
    
    @classmethod
    def get_setup_fields(cls) -> List[Dict]:
        """Get fields needed for provider setup."""
        fields = super().get_setup_fields()
        # Add additional configuration fields if needed
        fields.append({
            "name": "custom_field",
            "display_name": "Custom Field",
            "type": "text",
            "required": False,
            "help_text": "An optional custom configuration field"
        })
        return fields
```

### 3. Register your provider

Import your provider in the `tempidentity/providers/email/__init__.py` file:

```python
from tempidentity.providers.email.base import EmailProvider
from tempidentity.providers.email.mailgw import MailGwProvider
from tempidentity.providers.email.examplemail import ExampleMailProvider

__all__ = ['EmailProvider', 'MailGwProvider', 'ExampleMailProvider']
```

## Creating a New SMS Provider

### 1. Create a new module file

Create a new Python module in the `tempidentity/providers/sms/` directory. For example, to create a provider for "ExampleSMS", create a file named `examplesms.py`.

### 2. Implement the SMSProvider interface

```python
from tempidentity.providers.sms.base import SMSProvider
from typing import Dict, List, Tuple, Optional
import requests
import json
import time

class ExampleSMSProvider(SMSProvider):
    """Implementation for ExampleSMS service."""
    
    name = "examplesms"  # Unique identifier for the provider
    display_name = "ExampleSMS"  # Human-readable name
    description = "Example SMS service provider"  # Provider description
    requires_api_key = True  # Whether this provider requires an API key
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key', '')
        self.base_url = "https://api.examplesms.com/v1"
        self.phone_number = None
        self.verification_id = None
    
    def get_available_services(self) -> List[Dict]:
        """Get available services for verification."""
        # Implementation code here
        # Must return: list of service objects 
        # (each with at least 'id', 'name', and 'price' fields)
        pass
    
    def create_number(self, service_name: str) -> Tuple[bool, str]:
        """Create a temporary phone number for a service."""
        # Implementation code here
        # Must return: (success_bool, phone_number)
        pass
    
    def check_sms(self) -> Optional[str]:
        """Check for received SMS."""
        # Implementation code here
        # Must return: SMS verification code if received, None otherwise
        pass
    
    def wait_for_sms(self, timeout: int = 300, check_interval: int = 10) -> Optional[str]:
        """Wait for an SMS to arrive."""
        # Implementation code here
        # Must return: SMS verification code if received, None otherwise
        # Note: You can use the default implementation from the base class
        return super().wait_for_sms(timeout, check_interval)
    
    def cancel_number(self) -> bool:
        """Cancel the current phone number."""
        # Implementation code here
        # Must return: success_bool
        pass
    
    @classmethod
    def get_setup_fields(cls) -> List[Dict]:
        """Get fields needed for provider setup."""
        fields = super().get_setup_fields()
        # Add additional configuration fields if needed
        fields.append({
            "name": "region",
            "display_name": "Region",
            "type": "select",
            "options": ["us", "eu", "asia"],
            "default": "us",
            "required": False,
            "help_text": "Select your preferred region"
        })
        return fields
```

### 3. Register your provider

Import your provider in the `tempidentity/providers/sms/__init__.py` file:

```python
from tempidentity.providers.sms.base import SMSProvider
from tempidentity.providers.sms.textverified import TextVerifiedProvider
from tempidentity.providers.sms.examplesms import ExampleSMSProvider

__all__ = ['SMSProvider', 'TextVerifiedProvider', 'ExampleSMSProvider']
```

## Creating a Provider Package

You can also distribute your providers as a separate package that can be installed alongside TempIdentity.

### 1. Create a package structure

```
tempidentity-myproviders/
├── tempidentity_myproviders/
│   ├── __init__.py
│   ├── email/
│   │   ├── __init__.py
│   │   └── custom_email_provider.py
│   └── sms/
│       ├── __init__.py
│       └── custom_sms_provider.py
├── setup.py
└── README.md
```

### 2. Create a setup.py file

```python
from setuptools import setup, find_packages

setup(
    name="tempidentity-myproviders",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Custom providers for TempIdentity",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tempidentity-myproviders",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "tempidentity>=0.1.0",
        # Add other dependencies needed by your providers
    ],
    entry_points={
        "tempidentity.providers": [
            "myproviders=tempidentity_myproviders",
        ],
    },
)
```

### 3. Register your providers in __init__.py

```python
# tempidentity_myproviders/__init__.py

def register_providers():
    """Register custom providers with TempIdentity."""
    try:
        from tempidentity.providers.registry import registry
        
        # Import and register email providers
        from tempidentity_myproviders.email.custom_email_provider import CustomEmailProvider
        registry.register_email_provider(CustomEmailProvider)
        
        # Import and register SMS providers
        from tempidentity_myproviders.sms.custom_sms_provider import CustomSMSProvider
        registry.register_sms_provider(CustomSMSProvider)
    except ImportError:
        # TempIdentity might not be installed
        pass

# Register providers when the package is imported
register_providers()
```

## Testing Your Provider

Here's a simple script to test your provider implementation:

```python
from tempidentity.providers.registry import registry

# Initialize the registry
registry.auto_discover_providers()

# Check if your provider is registered
email_providers = registry.get_all_email_providers()
sms_providers = registry.get_all_sms_providers()

print("Available Email Providers:")
for name, provider_class in email_providers.items():
    print(f"- {provider_class.display_name} ({name})")

print("\nAvailable SMS Providers:")
for name, provider_class in sms_providers.items():
    print(f"- {provider_class.display_name} ({name})")

# Test your provider
config = {"api_key": "test-api-key"}
my_provider = registry.create_email_provider("examplemail", config)

if my_provider:
    print("\nProvider initialized successfully")
    print(f"Provider type: {type(my_provider).__name__}")
    # Test other methods...
else:
    print("\nFailed to initialize provider")
```

## Best Practices

1. **Error Handling**: Always use try/except blocks when making API calls and handle errors gracefully
2. **Logging**: Add appropriate logging to help diagnose issues
3. **Documentation**: Document your provider with clear docstrings and README files
4. **Configuration**: Make sure all required configuration parameters are documented
5. **Testing**: Write tests for your provider implementation
6. **Rate Limiting**: Implement appropriate rate limiting for API calls
7. **Security**: Handle API keys and credentials securely

## Available Configuration Field Types

When defining `get_setup_fields()`, you can use the following field types:

- `text`: Regular text input
- `password`: Masked password input
- `select`: Selection from predefined options
- `checkbox`: Boolean checkbox
- `number`: Numeric input

Example:

```python
@classmethod
def get_setup_fields(cls) -> List[Dict]:
    return [
        {
            "name": "api_key",
            "display_name": "API Key",
            "type": "password",
            "required": True,
            "help_text": "Your API key from the provider"
        },
        {
            "name": "region",
            "display_name": "Region",
            "type": "select",
            "options": ["us", "eu", "asia"],
            "default": "us",
            "required": False,
            "help_text": "Select your preferred region"
        },
        {
            "name": "max_retries",
            "display_name": "Max Retries",
            "type": "number",
            "default": 3,
            "required": False,
            "help_text": "Maximum number of retry attempts"
        },
        {
            "name": "debug_mode",
            "display_name": "Debug Mode",
            "type": "checkbox",
            "default": False,
            "required": False,
            "help_text": "Enable debug logging"
        }
    ]
```