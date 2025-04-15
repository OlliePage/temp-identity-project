#!/usr/bin/env python3
"""
Example code showing how to integrate the provider system into the main application.
"""

import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

# Import provider registry
from tempidentity.providers.registry import registry


# For UI components (simplified for this example)
def print_success(message: str):
    print(f"✅ {message}")


def print_error(message: str):
    print(f"❌ {message}")


def print_info(message: str):
    print(f"ℹ️ {message}")


def spinner(message: str):
    print(f"{message}...")
    return type('obj', (object,), {
        '__enter__': lambda self: self,
        '__exit__': lambda *args: None,
        'ok': lambda text="": print_success(text if text else "Done!"),
        'fail': lambda text="": print_error(text if text else "Failed!"),
        'text': lambda value: None
    })()


# Configuration management
CONFIG_DIR = Path.home() / ".tempidentity"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> Dict:
    """Load configuration from file or create default."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    if not CONFIG_FILE.exists():
        default_config = {
            "preferred_email_service": "mail.gw",
            "preferred_sms_service": "textverified",
            "providers": {
                "mail.gw": {},
                "textverified": {
                    "api_key": ""
                }
            },
            "default_wait_time": 120,
            "save_history": True,
            "history_limit": 20
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config.copy()

    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print_error(f"Error loading config: {e}")
        return {}


def save_config(config: Dict):
    """Save configuration to file."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print_error(f"Error saving config: {e}")
        return False


# Functions that use the provider system
def create_temp_email():
    """Create a temporary email and wait for messages."""
    # Load configuration
    config = load_config()

    # Get preferred email service
    service_name = config.get('preferred_email_service', 'mail.gw')
    provider_config = config.get('providers', {}).get(service_name, {})

    # Create email provider
    with spinner(f"Creating {service_name} provider") as sp:
        email_provider = registry.create_email_provider(service_name, provider_config)
        if not email_provider:
            sp.fail(f"Provider {service_name} not found or could not be initialized")
            return
        sp.ok()

    # Create email
    with spinner("Creating temporary email") as sp:
        success, email, password = email_provider.create_email()
        if not success:
            sp.fail("Failed to create email")
            return
        sp.ok(f"Created email: {email}")

    # Display email details
    print_info(f"Email: {email}")
    print_info(f"Password: {password}")

    # Save email to history
    save_history("email", {
        "email": email,
        "password": password,
        "service": service_name
    })

    # Ask if user wants to wait for messages
    wait_time = config.get('default_wait_time', 120)
    wait_for_msgs = input(f"Wait for incoming messages? [Y/n]: ").lower() != 'n'

    if wait_for_msgs:
        wait_time_input = input(f"How long to wait for messages (seconds) [{wait_time}]: ")
        if wait_time_input.strip():
            try:
                wait_time = int(wait_time_input)
            except ValueError:
                print_error("Invalid time, using default")

        # Wait for messages
        with spinner(f"Waiting for messages (timeout: {wait_time}s)") as sp:
            new_messages = email_provider.wait_for_messages(timeout=wait_time)
            if new_messages:
                sp.ok(f"Received {len(new_messages)} messages")
            else:
                sp.fail("No messages received")

        # Display messages
        if new_messages:
            for i, message in enumerate(new_messages):
                print(f"\nMessage {i + 1}:")
                print(f"Subject: {message.get('subject', 'No Subject')}")
                print(f"From: {message.get('from', {}).get('address', 'Unknown')}")
                print(f"Date: {message.get('createdAt', 'Unknown')}")
                print("-" * 40)

                # Get detailed message content if needed
                if 'text' not in message and 'html' not in message and 'id' in message:
                    detailed_message = email_provider.get_message_content(message['id'])
                    if detailed_message:
                        message = detailed_message

                # Display content
                if 'text' in message and message['text']:
                    print(message['text'])
                elif 'html' in message and message['html']:
                    print("Message is in HTML format. Here's a simplified version:")
                    print(message['html'].replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n'))
                else:
                    print("No message content available")


def create_temp_sms():
    """Create a temporary phone number and wait for SMS."""
    # Load configuration
    config = load_config()

    # Get preferred SMS service
    service_name = config.get('preferred_sms_service', 'textverified')
    provider_config = config.get('providers', {}).get(service_name, {})

    # Check if API key is configured
    if not provider_config.get('api_key'):
        print_error(f"API key for {service_name} is not configured")
        api_key = input("Enter API key: ")
        if not api_key:
            return

        # Update configuration
        if not config.get('providers'):
            config['providers'] = {}
        if not config['providers'].get(service_name):
            config['providers'][service_name] = {}
        config['providers'][service_name]['api_key'] = api_key
        save_config(config)
        provider_config = config['providers'][service_name]

    # Create SMS provider
    with spinner(f"Creating {service_name} provider") as sp:
        sms_provider = registry.create_sms_provider(service_name, provider_config)
        if not sms_provider:
            sp.fail(f"Provider {service_name} not found or could not be initialized")
            return
        sp.ok()

    # Get available services
    with spinner("Getting available services") as sp:
        services = sms_provider.get_available_services()
        if not services:
            sp.fail("Failed to get services")
            return
        sp.ok(f"Found {len(services)} services")

    # Display services
    print("\nAvailable services:")
    for i, service in enumerate(services):
        print(f"{i + 1}. {service.get('name', 'Unknown')} ({service.get('id', 'Unknown')}) - ${service.get('price', '0.00')}")

    # Select a service
    service_idx = input("\nSelect service (number): ")
    try:
        service_idx = int(service_idx) - 1
        if service_idx < 0 or service_idx >= len(services):
            print_error("Invalid selection")
            return
        selected_service = services[service_idx]
    except ValueError:
        print_error("Invalid selection")
        return

    # Create phone number
    with spinner(f"Creating phone number for {selected_service.get('name')}") as sp:
        success, phone_number = sms_provider.create_number(selected_service.get('id'))
        if not success:
            sp.fail("Failed to create phone number")
            return
        sp.ok(f"Created phone number: {phone_number}")

    # Display phone details
    print_info(f"Phone Number: {phone_number}")
    print_info(f"Service: {selected_service.get('name')}")

    # Save to history
    save_history("sms", {
        "phone_number": phone_number,
        "service": selected_service.get('name')
    })

    try:
        # Wait for SMS
        wait_time = config.get('default_wait_time', 300)
        wait_time_input = input(f"How long to wait for SMS (seconds) [{wait_time}]: ")
        if wait_time_input.strip():
            try:
                wait_time = int(wait_time_input)
            except ValueError:
                print_error("Invalid time, using default")

        # Wait for SMS
        with spinner(f"Waiting for SMS (timeout: {wait_time}s)") as sp:
            code = sms_provider.wait_for_sms(timeout=wait_time)
            if code:
                sp.ok(f"Received code: {code}")
            else:
                sp.fail("No SMS received")
    finally:
        # Always try to cancel the number
        with spinner("Canceling phone number") as sp:
            if sms_provider.cancel_number():
                sp.ok()
            else:
                sp.fail("Failed to cancel number")


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
        print_error(f"Error saving history: {e}")


def settings_menu():
    """Settings configuration menu for providers."""
    config = load_config()

    while True:
        print("\n==== Provider Settings ====")
        print("1. Configure Email Providers")
        print("2. Configure SMS Providers")
        print("0. Back")

        choice = input("\nSelect an option [0]: ") or "0"

        if choice == "0":
            break
        elif choice == "1":
            configure_provider_type("email", config)
        elif choice == "2":
            configure_provider_type("sms", config)


def configure_provider_type(provider_type, config):
    """Configure a specific provider type."""
    if provider_type == "email":
        providers = registry.get_all_email_providers()
        current = config.get('preferred_email_service', 'mail.gw')
    else:
        providers = registry.get_all_sms_providers()
        current = config.get('preferred_sms_service', 'textverified')

    # Display available providers
    print(f"\n==== Available {provider_type.title()} Providers ====")
    for i, (name, provider_class) in enumerate(providers.items()):
        print(f"{i + 1}. {provider_class.display_name} ({name}) - {provider_class.description}")
        if name == current:
            print("   ↳ Current provider")

    # Select a provider to configure
    provider_idx = input("\nSelect provider to configure (number) [1]: ") or "1"
    try:
        provider_idx = int(provider_idx) - 1
        if provider_idx < 0 or provider_idx >= len(providers):
            print_error("Invalid selection")
            return

        # Get the selected provider
        provider_name = list(providers.keys())[provider_idx]
        provider_class = list(providers.values())[provider_idx]
    except ValueError:
        print_error("Invalid selection")
        return

    # Set as preferred provider
    if provider_type == "email":
        config['preferred_email_service'] = provider_name
    else:
        config['preferred_sms_service'] = provider_name

    # Get provider configuration
    if not config.get('providers'):
        config['providers'] = {}
    if not config['providers'].get(provider_name):
        config['providers'][provider_name] = {}

    provider_config = config['providers'][provider_name]

    # Get setup fields
    setup_fields = provider_class.get_setup_fields()

    if not setup_fields:
        print_info(f"No configuration needed for {provider_class.display_name}")
    else:
        print(f"\nConfiguring {provider_class.display_name}:")

        for field in setup_fields:
            name = field.get('name')
            display_name = field.get('display_name')
            field_type = field.get('type', 'text')
            required = field.get('required', False)
            help_text = field.get('help_text', '')

            # Display current value if it exists
            current_value = provider_config.get(name, '')
            display_value = '*****' if field_type == 'password' and current_value else current_value

            print(f"\n{display_name} ({name}):")
            if help_text:
                print(f"  {help_text}")
            if current_value:
                print(f"  Current value: {display_value}")

            # Get new value
            if field_type == 'password':
                prompt = f"Enter new {display_name} (leave empty to keep current): "
            else:
                prompt = f"Enter {display_name} (leave empty to keep current): "

            value = input(prompt)

            # Update configuration if value is provided
            if value:
                provider_config[name] = value
            elif not current_value and required:
                print_error(f"{display_name} is required")
                return

    # Save configuration
    save_config(config)
    print_success("Configuration saved")


def main():
    """Main function."""
    # Initialize the provider registry
    registry.auto_discover_providers()

    # Example usage
    print("TempIdentity Provider System Example")
    print("1. Create Temporary Email")
    print("2. Create Temporary SMS")
    print("3. Settings")
    print("0. Exit")

    choice = input("\nSelect an option [0]: ") or "0"

    if choice == "1":
        create_temp_email()
    elif choice == "2":
        create_temp_sms()
    elif choice == "3":
        settings_menu()


if __name__ == "__main__":
    main()