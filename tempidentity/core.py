"""
Core functionality for TempIdentity.
"""

import os
import json
import time
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

from tempidentity.providers.registry import registry

# Configuration
CONFIG_DIR = Path.home() / ".tempidentity"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "log.txt"

# Default configuration
DEFAULT_CONFIG = {
    "preferred_email_service": "mail.gw",
    "preferred_sms_service": "textverified",
    "providers": {"textverified": {"api_key": ""}, "mail.gw": {}},
    "default_wait_time": 120,
    "save_history": True,
    "history_limit": 20,
    "theme": "default",
    "logging": True,
    "log_retention_days": 3,
    "log_max_size_mb": 10,
}


# Setup logging
def setup_logging():
    """Configure logging with timestamps and output to both console and file."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    # Check if log file needs to be rotated
    rotate_logs()

    # Configure logging format and handlers
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Clear existing handlers if any
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.info("Logging initialized")


def rotate_logs():
    """Check if logs need to be rotated based on age or size."""
    config = load_config(skip_logging=True)

    if not LOG_FILE.exists():
        return

    # Check file age
    file_time = datetime.datetime.fromtimestamp(LOG_FILE.stat().st_mtime)
    now = datetime.datetime.now()
    age_days = (now - file_time).days

    # Check file size
    size_mb = LOG_FILE.stat().st_size / (1024 * 1024)  # Convert bytes to MB

    # Rotate if either condition is met
    if age_days >= config.get("log_retention_days", 3) or size_mb >= config.get(
        "log_max_size_mb", 10
    ):
        try:
            # Create backup of old log
            backup_file = LOG_FILE.with_suffix(f".bak.{int(time.time())}")
            LOG_FILE.rename(backup_file)

            # Limit number of backups to keep
            backup_files = sorted(
                CONFIG_DIR.glob("log.txt.bak.*"), key=lambda x: x.stat().st_mtime
            )

            # Keep only the 3 most recent backups
            for old_file in backup_files[:-3]:
                old_file.unlink()

        except Exception as e:
            # If failed to rotate, just continue with current log
            pass


# ====== Configuration Management ======


def load_config(skip_logging=False) -> Dict:
    """Load configuration from file or create default."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Ensure all default keys exist
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            # Ensure providers dict exists
            if "providers" not in config:
                config["providers"] = {}
            return config
    except Exception as e:
        if not skip_logging:
            if logging.getLogger().handlers:
                logging.error(f"Error loading config: {e}")
            else:
                print(f"Error loading config: {e}")
                print("Using default configuration")
        return DEFAULT_CONFIG.copy()


def save_config(config: Dict):
    """Save configuration to file."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        logging.info("Configuration saved successfully")
        return True
    except Exception as e:
        logging.error(f"Error saving config: {e}")
        return False


def save_history(history_type: str, data: Dict):
    """Save history item to file."""
    config = load_config()
    if not config.get("save_history", True):
        return

    history_file = CONFIG_DIR / f"{history_type}_history.json"
    history = []

    # Load existing history
    if history_file.exists():
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except Exception as e:
            logging.error(f"Error loading history file: {e}")
            history = []

    # Add new item with timestamp
    data["timestamp"] = time.time()
    history.insert(0, data)

    # Limit history size
    limit = config.get("history_limit", 20)
    history = history[:limit]

    # Save history
    try:
        with open(history_file, "w") as f:
            json.dump(history, f, indent=4)
        logging.info(f"Added new item to {history_type} history")
    except Exception as e:
        logging.error(f"Error saving history: {e}")


def get_history(history_type: str) -> List[Dict]:
    """Get history items from file."""
    history_file = CONFIG_DIR / f"{history_type}_history.json"

    if not history_file.exists():
        logging.info(f"No {history_type} history file found")
        return []

    try:
        with open(history_file, "r") as f:
            history = json.load(f)
            logging.info(f"Loaded {len(history)} {history_type} history items")
            return history
    except Exception as e:
        logging.error(f"Error reading history file: {e}")
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
    service_name = config.get("preferred_email_service", "mail.gw")
    provider_config = config.get("providers", {}).get(service_name, {})

    logging.info(f"Creating temporary email using {service_name} provider")

    # Create email provider
    email_provider = registry.create_email_provider(service_name, provider_config)
    if not email_provider:
        logging.error(f"Failed to instantiate email provider: {service_name}")
        return False, "", "", []

    # Create email
    try:
        logging.info("Attempting to create email address...")
        success, email, password = email_provider.create_email()
        if not success:
            logging.error("Failed to create temporary email")
            return False, "", "", []

        logging.info(f"Successfully created email: {email}")

        # Save email to history
        save_history(
            "email", {"email": email, "password": password, "service": service_name}
        )

        return True, email, password, []
    except Exception as e:
        logging.error(f"Exception while creating email: {str(e)}")
        return False, "", "", []


def check_email_messages(
    service_name: str,
    email: str,
    password: str,
    wait: bool = False,
    wait_time: int = 120,
) -> List[Dict]:
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
    provider_config = config.get("providers", {}).get(service_name, {})

    logging.info(f"Checking messages for {email} using {service_name} provider")

    # Create email provider
    email_provider = registry.create_email_provider(service_name, provider_config)
    if not email_provider:
        logging.error(f"Failed to instantiate email provider: {service_name}")
        return []

    # Set credentials
    email_provider.email = email
    email_provider.password = password

    # Check for messages
    try:
        if wait:
            logging.info(f"Waiting for new messages for {wait_time} seconds")
            messages = email_provider.wait_for_messages(timeout=wait_time)
            logging.info(f"Received {len(messages)} message(s) after waiting")
            return messages
        else:
            logging.info("Checking for messages (no wait)")
            messages = email_provider.check_messages()
            logging.info(f"Found {len(messages)} message(s)")
            return messages
    except Exception as e:
        logging.error(f"Error checking messages: {str(e)}")
        return []


def get_email_message_content(
    service_name: str, email: str, password: str, message_id: str
) -> Dict:
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
    provider_config = config.get("providers", {}).get(service_name, {})

    logging.info(f"Getting message content for message ID: {message_id}")

    # Create email provider
    email_provider = registry.create_email_provider(service_name, provider_config)
    if not email_provider:
        logging.error(f"Failed to instantiate email provider: {service_name}")
        return {}

    # Set credentials
    email_provider.email = email
    email_provider.password = password

    # Get message content
    try:
        message = email_provider.get_message_content(message_id)
        if message:
            logging.info(f"Successfully retrieved message content")
        else:
            logging.warning(f"Message content is empty")
        return message
    except Exception as e:
        logging.error(f"Error getting message content: {str(e)}")
        return {}


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
    service_name = config.get("preferred_sms_service", "textverified")
    provider_config = config.get("providers", {}).get(service_name, {})

    # Check if API key is configured
    if not provider_config.get("api_key"):
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
    service_name = config.get("preferred_sms_service", "textverified")
    provider_config = config.get("providers", {}).get(service_name, {})

    # Check if API key is configured
    if not provider_config.get("api_key"):
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
    save_history(
        "sms",
        {"phone_number": phone_number, "service": service_id, "provider": service_name},
    )

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
    provider_config = config.get("providers", {}).get(service_name, {})

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
    provider_config = config.get("providers", {}).get(service_name, {})

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


def configure_provider(
    provider_type: str, provider_name: str, config_data: Dict
) -> bool:
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
    if "providers" not in app_config:
        app_config["providers"] = {}
    if provider_name not in app_config["providers"]:
        app_config["providers"][provider_name] = {}

    # Update provider configuration
    for key, value in config_data.items():
        app_config["providers"][provider_name][key] = value

    # Set as preferred provider if requested
    if provider_type == "email":
        app_config["preferred_email_service"] = provider_name
    elif provider_type == "sms":
        app_config["preferred_sms_service"] = provider_name

    # Save configuration
    return save_config(app_config)
