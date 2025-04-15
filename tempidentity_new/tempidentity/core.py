"""
Core functionality for TempIdentity.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from tempidentity.providers.registry import registry

# Configuration
CONFIG_DIR = Path.home() / ".tempidentity"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "preferred_email_service": "mail.gw",
    "preferred_sms_service": "textverified", 
    "providers": {
        "textverified": {
            "api_key": ""
        },
        "mail.gw": {}
    },
    "default_wait_time": 120,
    "save_history": True,
    "history_limit": 20,
    "theme": "default"
}

# ====== Configuration Management ======

def load_config() -> Dict:
    """Load configuration from file or create default."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Ensure all default keys exist
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            # Ensure providers dict exists
            if 'providers' not in config:
                config['providers'] = {}
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        print("Using default configuration")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict):
    """Save configuration to file."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def save_history(history_type: str, data: Dict):
    """Save history item to file."""
    config = load_config()
    if not config.get('save_history', True):
        return

    history_file = CONFIG_DIR / f"{history_type}_history.json"
    history = []

    # Load existing history
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                history = json.load(f)
        except:
            history = []

    # Add new item with timestamp
    data['timestamp'] = time.time()
    history.insert(0, data)

    # Limit history size
    limit = config.get('history_limit', 20)
    history = history[:limit]

    # Save history
    try:
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        print(f"Error saving history: {e}")


def get_history(history_type: str) -> List[Dict]:
    """Get history items from file."""
    history_file = CONFIG_DIR / f"{history_type}_history.json"

    if not history_file.exists():
        return []

    try:
        with open(history_file, 'r') as f:
            return json.load(f)
    except:
        return []


# ====== Email Functionality ======

def create_temp_email() -> Tuple[bool, str, str, List[Dict]]:
    """
    Create a temporary email and optionally wait for messages.
    
    Returns:
        Tuple[bool, str, str, List[Dict]]: 
            Success status, email address, password, and messages (if any)
    """
    # Load configuration
    config = load_config()
    
    # Get preferred email service
    service_name = config.get('preferred_email_service', 'mail.gw')
    provider_config = config.get('providers', {}).get(service_name, {})
    
    # Create email provider
    email_provider = registry.create_email_provider(service_name, provider_config)
    if not email_provider:
        return False, "", "", []
    
    # Create email
    success, email, password = email_provider.create_email()
    if not success:
        return False, "", "", []
    
    # Save email to history
    save_history("email", {
        "email": email,
        "password": password,
        "service": service_name
    })
    
    return True, email, password, []


def check_email_messages(service_name: str, email: str, password: str, wait: bool = False, wait_time: int = 120) -> List[Dict]:
    """
    Check for messages in the given email account.
    
    Args:
        service_name: Name of the email service
        email: Email address
        password: Password for the email
        wait: Whether to wait for new messages
        wait_time: How long to wait for new messages (in seconds)
        
    Returns:
        List[Dict]: List of messages
    """
    # Load configuration
    config = load_config()
    provider_config = config.get('providers', {}).get(service_name, {})
    
    # Create email provider
    email_provider = registry.create_email_provider(service_name, provider_config)
    if not email_provider:
        return []
    
    # Set credentials
    email_provider.email = email
    email_provider.password = password
    
    # Check for messages
    if wait:
        return email_provider.wait_for_messages(timeout=wait_time)
    else:
        return email_provider.check_messages()


def get_email_message_content(service_name: str, email: str, password: str, message_id: str) -> Dict:
    """
    Get the content of a specific email message.
    
    Args:
        service_name: Name of the email service
        email: Email address
        password: Password for the email
        message_id: ID of the message to retrieve
        
    Returns:
        Dict: Message content
    """
    # Load configuration
    config = load_config()
    provider_config = config.get('providers', {}).get(service_name, {})
    
    # Create email provider
    email_provider = registry.create_email_provider(service_name, provider_config)
    if not email_provider:
        return {}
    
    # Set credentials
    email_provider.email = email
    email_provider.password = password
    
    # Get message content
    return email_provider.get_message_content(message_id)


# ====== SMS Functionality ======

def get_sms_services() -> List[Dict]:
    """
    Get available SMS services.
    
    Returns:
        List[Dict]: List of available services
    """
    # Load configuration
    config = load_config()
    
    # Get preferred SMS service
    service_name = config.get('preferred_sms_service', 'textverified')
    provider_config = config.get('providers', {}).get(service_name, {})
    
    # Check if API key is configured
    if not provider_config.get('api_key'):
        return []
    
    # Create SMS provider
    sms_provider = registry.create_sms_provider(service_name, provider_config)
    if not sms_provider:
        return []
    
    # Get available services
    return sms_provider.get_available_services()


def create_temp_sms(service_id: str) -> Tuple[bool, str, str]:
    """
    Create a temporary phone number for a service.
    
    Args:
        service_id: ID of the service to create a number for
        
    Returns:
        Tuple[bool, str, str]: Success status, phone number, and service name
    """
    # Load configuration
    config = load_config()
    
    # Get preferred SMS service
    service_name = config.get('preferred_sms_service', 'textverified')
    provider_config = config.get('providers', {}).get(service_name, {})
    
    # Check if API key is configured
    if not provider_config.get('api_key'):
        return False, "", ""
    
    # Create SMS provider
    sms_provider = registry.create_sms_provider(service_name, provider_config)
    if not sms_provider:
        return False, "", ""
    
    # Create phone number
    success, phone_number = sms_provider.create_number(service_id)
    if not success:
        return False, "", ""
    
    # Save to history
    save_history("sms", {
        "phone_number": phone_number,
        "service": service_id,
        "provider": service_name
    })
    
    return True, phone_number, service_name


def wait_for_sms_code(service_name: str, wait_time: int = 300) -> Optional[str]:
    """
    Wait for an SMS to arrive.
    
    Args:
        service_name: Name of the SMS service
        wait_time: How long to wait for the SMS (in seconds)
        
    Returns:
        Optional[str]: SMS verification code if received, None otherwise
    """
    # Load configuration
    config = load_config()
    provider_config = config.get('providers', {}).get(service_name, {})
    
    # Create SMS provider
    sms_provider = registry.create_sms_provider(service_name, provider_config)
    if not sms_provider:
        return None
    
    # Wait for SMS
    code = sms_provider.wait_for_sms(timeout=wait_time)
    
    # Always try to cancel the number to avoid wasting credits
    sms_provider.cancel_number()
    
    return code


def cancel_sms_number(service_name: str) -> bool:
    """
    Cancel a temporary phone number.
    
    Args:
        service_name: Name of the SMS service
        
    Returns:
        bool: Success status
    """
    # Load configuration
    config = load_config()
    provider_config = config.get('providers', {}).get(service_name, {})
    
    # Create SMS provider
    sms_provider = registry.create_sms_provider(service_name, provider_config)
    if not sms_provider:
        return False
    
    # Cancel the number
    return sms_provider.cancel_number()


# ====== Provider Management ======

def get_available_providers():
    """
    Get all available providers.
    
    Returns:
        Tuple[Dict, Dict]: Email providers and SMS providers
    """
    # Initialize the registry
    registry.auto_discover_providers()
    
    # Get all providers
    email_providers = registry.get_all_email_providers()
    sms_providers = registry.get_all_sms_providers()
    
    return email_providers, sms_providers


def configure_provider(provider_type: str, provider_name: str, config_data: Dict) -> bool:
    """
    Configure a provider with the given data.
    
    Args:
        provider_type: Type of provider ('email' or 'sms')
        provider_name: Name of the provider
        config_data: Configuration data
        
    Returns:
        bool: Success status
    """
    # Load current configuration
    app_config = load_config()
    
    # Ensure providers dict exists
    if 'providers' not in app_config:
        app_config['providers'] = {}
    if provider_name not in app_config['providers']:
        app_config['providers'][provider_name] = {}
    
    # Update provider configuration
    for key, value in config_data.items():
        app_config['providers'][provider_name][key] = value
    
    # Set as preferred provider if requested
    if provider_type == 'email':
        app_config['preferred_email_service'] = provider_name
    elif provider_type == 'sms':
        app_config['preferred_sms_service'] = provider_name
    
    # Save configuration
    return save_config(app_config)