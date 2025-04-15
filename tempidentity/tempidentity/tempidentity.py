#!/usr/bin/env python3
"""
TempIdentity - A tool for generating temporary email addresses and phone numbers
"""

import os
import sys
import json
import time
import random
import string
import argparse
import requests
from typing import Dict, List, Any, Optional, Tuple
import subprocess
import pkg_resources
from pathlib import Path
import platform
from enum import Enum
import re

# Try to import colorama for cross-platform colored terminal output
try:
    from colorama import init, Fore, Style

    init()  # Initialize colorama
    HAS_COLORS = True
except ImportError:
    HAS_COLORS = False


    # Create dummy color classes if colorama isn't available
    class DummyFore:
        def __getattr__(self, name):
            return ""


    class DummyStyle:
        def __getattr__(self, name):
            return ""


    Fore = DummyFore()
    Style = DummyStyle()

# Try to import rich for enhanced terminal display
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.prompt import Prompt, Confirm

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False

# Try to import spinner for progress indication
try:
    from yaspin import yaspin
    from yaspin.spinners import Spinners

    HAS_SPINNER = True
except ImportError:
    HAS_SPINNER = False

# Define the version
__version__ = "0.1.0"

# Config file location
CONFIG_DIR = Path.home() / ".tempidentity"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Default configuration
DEFAULT_CONFIG = {
    "textverified_api_key": "",
    "preferred_email_service": "mail.gw",
    "preferred_sms_service": "textverified",
    "default_wait_time": 120,
    "save_history": True,
    "history_limit": 20,
    "theme": "default"
}


# ====== Utility Functions ======

def clear_screen():
    """Clear the terminal screen cross-platform."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def print_logo():
    """Print the TempIdentity logo."""
    logo = """
 _____                   ___     _            _   _ _         
|_   _|__ _ __ ___  _ __|_ _|__| | ___ _ __ | |_(_) |_ _   _ 
  | |/ _ \\ '_ ` _ \\| '_ \\| |/ _` |/ _ \\ '_ \\| __| | __| | | |
  | |  __/ | | | | | |_) | | (_| |  __/ | | | |_| | |_| |_| |
  |_|\\___|_| |_| |_| .__/___\\__,_|\\___|_| |_|\\__|_|\\__|\\__, |
                   |_|                                  |___/ 
    """
    if HAS_RICH:
        console.print(Panel(logo, style="bold blue"))
    else:
        print(f"{Fore.BLUE}{logo}{Style.RESET_ALL}")

    print(f"{Fore.CYAN}Temporary Email & SMS Tool v{__version__}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


def print_step(step: str, total: int, title: str):
    """Print a step in the wizard process."""
    if HAS_RICH:
        console.print(f"[bold cyan]Step {step}/{total}:[/bold cyan] [bold]{title}[/bold]")
    else:
        print(f"{Fore.CYAN}Step {step}/{total}:{Style.RESET_ALL} {Fore.BOLD}{title}{Style.RESET_ALL}")


def print_success(message: str):
    """Print a success message."""
    if HAS_RICH:
        console.print(f"[bold green]✓ {message}[/bold green]")
    else:
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print an error message."""
    if HAS_RICH:
        console.print(f"[bold red]✗ {message}[/bold red]")
    else:
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print a warning message."""
    if HAS_RICH:
        console.print(f"[bold yellow]! {message}[/bold yellow]")
    else:
        print(f"{Fore.YELLOW}! {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print an info message."""
    if HAS_RICH:
        console.print(f"[blue]ℹ {message}[/blue]")
    else:
        print(f"{Fore.BLUE}ℹ {message}{Style.RESET_ALL}")


def prompt(message: str, default=None, choices=None, password=False):
    """Prompt the user for input."""
    prompt_text = f"{message} "

    if default:
        prompt_text += f"[{default}] "

    if choices:
        prompt_text += f"({'/'.join(choices)}) "

    if HAS_RICH:
        if password:
            return Prompt.ask(prompt_text, password=True, default=default)
        else:
            return Prompt.ask(prompt_text, default=default, choices=choices)
    else:
        if password:
            import getpass
            result = getpass.getpass(prompt_text)
            return result if result else default
        else:
            result = input(prompt_text) or default

            # Validate choices if provided
            if choices and result not in choices:
                print_error(f"Invalid choice. Please select from: {', '.join(choices)}")
                return prompt(message, default, choices)

            return result


def confirm(message: str, default=True):
    """Ask for confirmation."""
    if HAS_RICH:
        return Confirm.ask(message, default=default)
    else:
        choice = input(f"{message} ({'Y/n' if default else 'y/N'}): ").lower()
        if choice == '':
            return default
        return choice in ['y', 'yes']


def spinner(message: str):
    """Return a spinner context manager if available, or a dummy one if not."""
    if HAS_SPINNER:
        return yaspin(Spinners.dots, text=message)
    else:
        # Create a dummy context manager
        class DummySpinner:
            def __init__(self, message):
                self.message = message

            def __enter__(self):
                print(f"{self.message}...")
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def ok(self, text=""):
                print_success(text if text else "Done!")

            def fail(self, text=""):
                print_error(text if text else "Failed!")

            def text(self, value):
                pass

        return DummySpinner(message)


def generate_random_string(length=12):
    """Generate a random string of letters and digits."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def validate_email(email: str) -> bool:
    """Validate an email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_api_key(api_key: str) -> bool:
    """Basic validation for API key format."""
    # This is a simple check - API keys vary in format
    return len(api_key) > 8 and ' ' not in api_key


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
            return config
    except Exception as e:
        print_error(f"Error loading config: {e}")
        print_warning("Using default configuration")
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
        print_error(f"Error saving config: {e}")
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
        print_error(f"Error saving history: {e}")


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


# ====== Temporary Email Implementation ======

class TempEmailService:
    """Base class for temporary email services."""

    def __init__(self):
        self.email = None
        self.password = None

    def create_email(self) -> Tuple[bool, str, str]:
        """Create a temporary email address."""
        pass

    def check_messages(self) -> List[Dict]:
        """Check for messages in the inbox."""
        pass

    def wait_for_messages(self, timeout: int = 60, check_interval: int = 5) -> List[Dict]:
        """Wait for new messages to arrive."""
        pass

    def get_message_content(self, message_id: str) -> Dict:
        """Get the content of a specific message."""
        pass


class MailGwService(TempEmailService):
    """Implementation for Mail.gw service."""

    def __init__(self):
        super().__init__()
        self.base_url = "https://api.mail.gw"
        self.token = None
        self.domain = None

    def _get_domains(self):
        """Get available domains from Mail.gw"""
        response = requests.get(f"{self.base_url}/domains")
        if response.status_code == 200:
            domains = response.json().get("hydra:member", [])
            if domains:
                return domains[0].get("domain")
        return None

    def create_email(self) -> Tuple[bool, str, str]:
        """Create a temporary email address."""
        # Get available domains
        with spinner("Getting available domains") as sp:
            self.domain = self._get_domains()
            if not self.domain:
                sp.fail("Failed to get domains")
                return False, "", ""

        # Generate random credentials
        username = generate_random_string()
        self.password = generate_random_string()
        self.email = f"{username}@{self.domain}"

        # Create the account
        with spinner(f"Creating email {self.email}") as sp:
            payload = {
                "address": self.email,
                "password": self.password
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{self.base_url}/accounts",
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 201:
                sp.ok(f"Created email {self.email}")
                # Login immediately
                if self._login():
                    return True, self.email, self.password
                else:
                    return False, self.email, self.password
            else:
                sp.fail(f"Failed to create account: {response.text}")
                return False, "", ""

    def _login(self) -> bool:
        """Login to the temporary email account and get token."""
        with spinner("Logging in to email account") as sp:
            payload = {
                "address": self.email,
                "password": self.password
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(
                f"{self.base_url}/token",
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                self.token = response.json().get("token")
                sp.ok("Logged in successfully")
                return True
            else:
                sp.fail(f"Failed to login: {response.text}")
                return False

    def check_messages(self) -> List[Dict]:
        """Check for messages in the inbox."""
        if not self.token:
            if not self._login():
                return []

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(
            f"{self.base_url}/messages",
            headers=headers
        )

        if response.status_code == 200:
            return response.json().get("hydra:member", [])
        else:
            print_error(f"Failed to get messages: {response.text}")
            return []

    def get_message_content(self, message_id: str) -> Dict:
        """Get the content of a specific message."""
        if not self.token:
            if not self._login():
                return {}

        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(
            f"{self.base_url}/messages/{message_id}",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            print_error(f"Failed to get message content: {response.text}")
            return {}

    def wait_for_messages(self, timeout: int = 60, check_interval: int = 5) -> List[Dict]:
        """Wait for new messages to arrive."""
        start_time = time.time()
        initial_messages = self.check_messages()
        initial_count = len(initial_messages)

        with spinner(f"Waiting for new messages (timeout: {timeout}s)") as sp:
            while time.time() - start_time < timeout:
                sp.text(f"Waiting for new messages ({int(timeout - (time.time() - start_time))}s remaining)")
                current_messages = self.check_messages()

                if len(current_messages) > initial_count:
                    new_messages = current_messages[:len(current_messages) - initial_count]
                    sp.ok(f"Received {len(new_messages)} new messages")
                    return new_messages

                time.sleep(check_interval)

            sp.fail("No new messages received within the timeout period")
            return []


class EmailServiceFactory:
    """Factory for creating email service instances."""

    @staticmethod
    def create_service(service_name: str) -> TempEmailService:
        """Create and return an email service instance."""
        if service_name.lower() == "mail.gw":
            return MailGwService()
        else:
            # Default to Mail.gw for now
            print_warning(f"Unknown email service '{service_name}', using Mail.gw")
            return MailGwService()


# ====== Temporary SMS Implementation ======

class TempSMSService:
    """Base class for temporary SMS services."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.phone_number = None

    def get_available_services(self) -> List[Dict]:
        """Get available services for verification."""
        pass

    def create_number(self, service_name: str) -> Tuple[bool, str]:
        """Create a temporary phone number for a service."""
        pass

    def check_sms(self) -> Optional[str]:
        """Check for received SMS."""
        pass

    def wait_for_sms(self, timeout: int = 300, check_interval: int = 10) -> Optional[str]:
        """Wait for an SMS to arrive."""
        pass

    def cancel_number(self) -> bool:
        """Cancel the current phone number."""
        pass


class TextVerifiedService(TempSMSService):
    """Implementation for TextVerified service."""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://www.textverified.com/api"
        self.verification_id = None
        self.service = None

    def get_available_services(self) -> List[Dict]:
        """Get available services for verification."""
        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key
        }

        with spinner("Getting available SMS services") as sp:
            response = requests.get(
                f"{self.base_url}/Services",
                headers=headers
            )

            if response.status_code == 200:
                sp.ok("Retrieved available services")
                return response.json()
            else:
                sp.fail(f"Failed to get services: {response.text}")
                return []

    def create_number(self, service_name: str) -> Tuple[bool, str]:
        """Create a temporary phone number for a service."""
        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "id": service_name
        }

        with spinner(f"Creating phone number for {service_name}") as sp:
            response = requests.post(
                f"{self.base_url}/Verifications",
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code == 200:
                data = response.json()
                self.verification_id = data.get("id")
                self.phone_number = data.get("number")
                self.service = service_name

                sp.ok(f"Created phone number: {self.phone_number}")
                return True, self.phone_number
            else:
                sp.fail(f"Failed to create verification: {response.text}")
                return False, ""

    def check_sms(self) -> Optional[str]:
        """Check for received SMS."""
        if not self.verification_id:
            print_error("No verification has been created yet.")
            return None

        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key
        }

        response = requests.get(
            f"{self.base_url}/Verifications/{self.verification_id}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("code")
        else:
            print_error(f"Failed to check SMS: {response.text}")
            return None

    def wait_for_sms(self, timeout: int = 300, check_interval: int = 10) -> Optional[str]:
        """Wait for an SMS to arrive."""
        if not self.verification_id:
            print_error("No verification has been created yet.")
            return None

        start_time = time.time()

        with spinner(f"Waiting for SMS (timeout: {timeout}s)") as sp:
            while time.time() - start_time < timeout:
                sp.text(f"Waiting for SMS ({int(timeout - (time.time() - start_time))}s remaining)")
                code = self.check_sms()

                if code:
                    sp.ok(f"Received SMS code: {code}")
                    return code

                time.sleep(check_interval)

            sp.fail("No SMS received within the timeout period")
            return None

    def cancel_number(self) -> bool:
        """Cancel the current phone number."""
        if not self.verification_id:
            print_warning("No verification to cancel.")
            return False

        headers = {
            "X-SIMPLE-API-ACCESS-TOKEN": self.api_key
        }

        with spinner("Canceling phone number") as sp:
            response = requests.delete(
                f"{self.base_url}/Verifications/{self.verification_id}",
                headers=headers
            )

            if response.status_code == 200:
                sp.ok(f"Canceled verification for number {self.phone_number}")
                self.verification_id = None
                self.phone_number = None
                self.service = None
                return True
            else:
                sp.fail(f"Failed to cancel verification: {response.text}")
                return False


class SMSServiceFactory:
    """Factory for creating SMS service instances."""

    @staticmethod
    def create_service(service_name: str, api_key: str) -> TempSMSService:
        """Create and return an SMS service instance."""
        if service_name.lower() == "textverified":
            return TextVerifiedService(api_key)
        else:
            # Default to TextVerified for now
            print_warning(f"Unknown SMS service '{service_name}', using TextVerified")
            return TextVerifiedService(api_key)


# ====== User Interface Components ======

def show_menu() -> str:
    """Show the main menu and return the selected option."""
    clear_screen()
    print_logo()

    if HAS_RICH:
        table = Table(title="Main Menu")
        table.add_column("Option", style="cyan")
        table.add_column("Description")

        table.add_row("1", "Create Temporary Email")
        table.add_row("2", "Create Temporary Phone Number (SMS)")
        table.add_row("3", "View Email History")
        table.add_row("4", "View SMS History")
        table.add_row("5", "Settings")
        table.add_row("0", "Exit")

        console.print(table)

        choice = Prompt.ask("Select an option", choices=["0", "1", "2", "3", "4", "5"], default="1")
    else:
        print(f"{Fore.CYAN}Main Menu:{Style.RESET_ALL}")
        print("1. Create Temporary Email")
        print("2. Create Temporary Phone Number (SMS)")
        print("3. View Email History")
        print("4. View SMS History")
        print("5. Settings")
        print("0. Exit")
        print()

        choice = input("Select an option [1]: ") or "1"

    return choice


def create_temp_email():
    """Create a temporary email and wait for messages."""
    clear_screen()
    print_logo()
    print_step("1", "3", "Create Temporary Email")

    config = load_config()
    service_name = config.get('preferred_email_service', 'mail.gw')
    wait_time = config.get('default_wait_time', 120)

    # Ask for confirmation
    print_info(f"Using email service: {service_name}")
    if not confirm("Continue with this service?"):
        service_name = prompt("Enter service name", default="mail.gw")

    # Create email service
    email_service = EmailServiceFactory.create_service(service_name)
    success, email, password = email_service.create_email()

    if not success:
        print_error("Failed to create temporary email.")
        input("Press Enter to continue...")
        return

    # Show email details
    clear_screen()
    print_logo()
    print_step("2", "3", "Email Created")

    if HAS_RICH:
        details_table = Table(title="Temporary Email Details")
        details_table.add_column("Property", style="cyan")
        details_table.add_column("Value")

        details_table.add_row("Email Address", email)
        details_table.add_row("Password", password)

        console.print(details_table)
    else:
        print(f"{Fore.CYAN}Temporary Email Details:{Style.RESET_ALL}")
        print(f"Email Address: {email}")
        print(f"Password: {password}")

    # Save to history
    save_history("email", {
        "email": email,
        "password": password,
        "service": service_name
    })

    # Ask if user wants to wait for messages
    wait_for_msgs = confirm("Wait for incoming messages?", default=True)

    if wait_for_msgs:
        wait_time = prompt("How long to wait for messages (seconds)?", default=str(wait_time))
        try:
            wait_time = int(wait_time)
        except:
            wait_time = 120

        # Wait for messages
        clear_screen()
        print_logo()
        print_step("3", "3", "Waiting for Messages")

        new_messages = email_service.wait_for_messages(timeout=wait_time)

        if new_messages:
            print_success(f"Received {len(new_messages)} new messages:")

            for idx, message in enumerate(new_messages):
                print()
                if HAS_RICH:
                    msg_table = Table(title=f"Message {idx + 1}")
                    msg_table.add_column("Property", style="cyan")
                    msg_table.add_column("Value")

                    msg_table.add_row("Subject", message.get('subject', 'No Subject'))
                    msg_table.add_row("From", message.get('from', {}).get('address', 'Unknown'))
                    msg_table.add_row("Date", message.get('createdAt', 'Unknown'))

                    console.print(msg_table)

                    # Get detailed message content if needed
                    if 'text' not in message and 'html' not in message and 'id' in message:
                        detailed_message = email_service.get_message_content(message['id'])
                        if detailed_message:
                            message = detailed_message

                    # Display content
                    if 'text' in message and message['text']:
                        console.print(Panel(message['text'], title="Content"))
                    elif 'html' in message and message['html']:
                        console.print(Panel(
                            message['html'].replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n'),
                            title="HTML Content"
                        ))
                    else:
                        console.print("[yellow]No message content available[/yellow]")
                else:
                    print(f"{Fore.CYAN}Message {idx + 1}:{Style.RESET_ALL}")
                    print(f"Subject: {message.get('subject', 'No Subject')}")
                    print(f"From: {message.get('from', {}).get('address', 'Unknown')}")
                    print(f"Date: {message.get('createdAt', 'Unknown')}")
                    print('-' * 40)

                    # Get detailed message content if needed
                    if 'text' not in message and 'html' not in message and 'id' in message:
                        detailed_message = email_service.get_message_content(message['id'])
                        if detailed_message:
                            message = detailed_message

                    # Display content
                    if 'text' in message and message['text']:
                        print(message['text'])
                    elif 'html' in message and message['html']:
                        print("Message is in HTML format. Here's a simplified version:")
                        print(message['html'].replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n'))
                    else:
                        print(f"{Fore.YELLOW}No message content available{Style.RESET_ALL}")
        else:
            print_warning("No new messages received.")

    input("\nPress Enter to continue...")


def create_temp_sms():
    """Create a temporary phone number and wait for SMS."""
    clear_screen()
    print_logo()
    print_step("1", "3", "Create Temporary Phone Number")

    config = load_config()
    api_key = config.get('textverified_api_key', '')

    # Check if API key is configured
    if not api_key:
        print_warning("TextVerified API key is not configured.")
        api_key = prompt("Enter your TextVerified API key", password=True)

        if not validate_api_key(api_key):
            print_error("Invalid API key format.")
            input("Press Enter to continue...")
            return

        # Ask to save the API key
        if confirm("Save this API key for future use?", default=True):
            config['textverified_api_key'] = api_key
            save_config(config)

    # Create SMS service
    sms_service = SMSServiceFactory.create_service("textverified", api_key)

    # Get available services
    services = sms_service.get_available_services()

    if not services:
        print_error("Failed to get available services.")
        input("Press Enter to continue...")
        return

    # Display available services
    clear_screen()
    print_logo()
    print_step("2", "3", "Select Service")

    if HAS_RICH:
        services_table = Table(title="Available Services")
        services_table.add_column("ID", style="cyan")
        services_table.add_column("Name")
        services_table.add_column("Price")

        for service in services:
            services_table.add_row(
                service.get('id', ''),
                service.get('name', ''),
                f"${service.get('price', '0.00')}"
            )

        console.print(services_table)
    else:
        print(f"{Fore.CYAN}Available Services:{Style.RESET_ALL}")
        for service in services:
            print(f"{service.get('id', '')}: {service.get('name', '')} (${service.get('price', '0.00')})")

    print()
    service_id = prompt("Select a service by ID")

    # Verify service exists
    service_exists = any(s.get('id') == service_id for s in services)
    if not service_exists:
        print_error(f"Invalid service ID: {service_id}")
        input("Press Enter to continue...")
        return

    # Create phone number
    clear_screen()
    print_logo()
    print_step("3", "3", "Creating Phone Number")

    success, phone_number = sms_service.create_number(service_id)

    if not success:
        print_error("Failed to create temporary phone number.")
        input("Press Enter to continue...")
        return

    # Show phone details
    if HAS_RICH:
        details_table = Table(title="Temporary Phone Number")
        details_table.add_column("Property", style="cyan")
        details_table.add_column("Value")

        details_table.add_row("Phone Number", phone_number)
        details_table.add_row("Service", service_id)

        console.print(details_table)
    else:
        print(f"{Fore.CYAN}Temporary Phone Number:{Style.RESET_ALL}")
        print(f"Phone Number: {phone_number}")
        print(f"Service: {service_id}")

    # Save to history
    save_history("sms", {
        "phone_number": phone_number,
        "service": service_id
    })

    # Wait for SMS
    wait_time = config.get('default_wait_time', 300)
    wait_time = prompt("How long to wait for SMS (seconds)?", default=str(wait_time))

    try:
        wait_time = int(wait_time)
    except:
        wait_time = 300

    code = sms_service.wait_for_sms(timeout=wait_time)

    if code:
        print_success(f"Received verification code: {code}")
    else:
        print_warning("No SMS received within the timeout period.")

    # Always try to cancel the number to avoid wasting credits
    sms_service.cancel_number()

    input("\nPress Enter to continue...")


def view_email_history():
    """View and manage email history."""
    clear_screen()
    print_logo()

    history = get_history("email")

    if not history:
        print_warning("No email history found.")
        input("Press Enter to continue...")
        return

    if HAS_RICH:
        history_table = Table(title="Email History")
        history_table.add_column("#", style="cyan")
        history_table.add_column("Email")
        history_table.add_column("Service")
        history_table.add_column("Date")

        for idx, item in enumerate(history):
            history_table.add_row(
                str(idx + 1),
                item.get('email', 'N/A'),
                item.get('service', 'N/A'),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))
            )

        console.print(history_table)
    else:
        print(f"{Fore.CYAN}Email History:{Style.RESET_ALL}")
        for idx, item in enumerate(history):
            print(f"{idx + 1}. {item.get('email', 'N/A')} ({item.get('service', 'N/A')}) - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))}")

    print()
    choice = prompt("Enter number to view details (or 0 to go back)", default="0")

    try:
        choice_idx = int(choice) - 1
        if choice_idx == -1:
            return

        if 0 <= choice_idx < len(history):
            item = history[choice_idx]

            clear_screen()
            print_logo()

            if HAS_RICH:
                details_table = Table(title=f"Email Details: {item.get('email', 'N/A')}")
                details_table.add_column("Property", style="cyan")
                details_table.add_column("Value")

                details_table.add_row("Email Address", item.get('email', 'N/A'))
                details_table.add_row("Password", item.get('password', 'N/A'))
                details_table.add_row("Service", item.get('service', 'N/A'))
                details_table.add_row("Created", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0))))

                console.print(details_table)
            else:
                print(f"{Fore.CYAN}Email Details:{Style.RESET_ALL}")
                print(f"Email Address: {item.get('email', 'N/A')}")
                print(f"Password: {item.get('password', 'N/A')}")
                print(f"Service: {item.get('service', 'N/A')}")
                print(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))}")
    except:
        print_error("Invalid selection.")

    input("\nPress Enter to continue...")


def view_sms_history():
    """View and manage SMS history."""
    clear_screen()
    print_logo()

    history = get_history("sms")

    if not history:
        print_warning("No SMS history found.")
        input("Press Enter to continue...")
        return

    if HAS_RICH:
        history_table = Table(title="SMS History")
        history_table.add_column("#", style="cyan")
        history_table.add_column("Phone Number")
        history_table.add_column("Service")
        history_table.add_column("Date")

        for idx, item in enumerate(history):
            history_table.add_row(
                str(idx + 1),
                item.get('phone_number', 'N/A'),
                item.get('service', 'N/A'),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))
            )

        console.print(history_table)
    else:
        print(f"{Fore.CYAN}SMS History:{Style.RESET_ALL}")
        for idx, item in enumerate(history):
            print(f"{idx + 1}. {item.get('phone_number', 'N/A')} ({item.get('service', 'N/A')}) - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))}")

    input("\nPress Enter to continue...")


def settings_menu():
    """Settings configuration menu."""
    config = load_config()

    while True:
        clear_screen()
        print_logo()

        if HAS_RICH:
            table = Table(title="Settings")
            table.add_column("Option", style="cyan")
            table.add_column("Value")

            table.add_row("1. TextVerified API Key", "*****" if config.get('textverified_api_key') else "Not set")
            table.add_row("2. Preferred Email Service", config.get('preferred_email_service', 'mail.gw'))
            table.add_row("3. Default Wait Time", str(config.get('default_wait_time', 120)) + " seconds")
            table.add_row("4. Save History", "Enabled" if config.get('save_history', True) else "Disabled")
            table.add_row("5. History Limit", str(config.get('history_limit', 20)) + " items")
            table.add_row("0. Back to Main Menu", "")

            console.print(table)

            choice = Prompt.ask("Select an option to change", choices=["0", "1", "2", "3", "4", "5"], default="0")
        else:
            print(f"{Fore.CYAN}Settings:{Style.RESET_ALL}")
            print(f"1. TextVerified API Key: {'*****' if config.get('textverified_api_key') else 'Not set'}")
            print(f"2. Preferred Email Service: {config.get('preferred_email_service', 'mail.gw')}")
            print(f"3. Default Wait Time: {config.get('default_wait_time', 120)} seconds")
            print(f"4. Save History: {'Enabled' if config.get('save_history', True) else 'Disabled'}")
            print(f"5. History Limit: {config.get('history_limit', 20)} items")
            print("0. Back to Main Menu")
            print()

            choice = input("Select an option to change [0]: ") or "0"

        if choice == "0":
            break
        elif choice == "1":
            # TextVerified API Key
            if config.get('textverified_api_key'):
                print_info("Current API key is set. Change it?")
                if not confirm("Change API key?"):
                    continue

            api_key = prompt("Enter your TextVerified API key", password=True)

            if api_key:
                if validate_api_key(api_key):
                    config['textverified_api_key'] = api_key
                    save_config(config)
                    print_success("API key updated.")
                else:
                    print_error("Invalid API key format.")

            input("Press Enter to continue...")
        elif choice == "2":
            # Preferred Email Service
            service = prompt("Enter preferred email service", default=config.get('preferred_email_service', 'mail.gw'))
            config['preferred_email_service'] = service
            save_config(config)
            print_success("Preferred email service updated.")
            input("Press Enter to continue...")
        elif choice == "3":
            # Default Wait Time
            wait_time = prompt("Enter default wait time (seconds)", default=str(config.get('default_wait_time', 120)))

            try:
                wait_time = int(wait_time)
                if wait_time > 0:
                    config['default_wait_time'] = wait_time
                    save_config(config)
                    print_success("Default wait time updated.")
                else:
                    print_error("Wait time must be greater than 0.")
            except:
                print_error("Invalid wait time. Please enter a number.")

            input("Press Enter to continue...")
        elif choice == "4":
            # Save History
            save_history = not config.get('save_history', True)
            config['save_history'] = save_history
            save_config(config)
            print_success(f"Save history {'enabled' if save_history else 'disabled'}.")
            input("Press Enter to continue...")
        elif choice == "5":
            # History Limit
            limit = prompt("Enter history limit", default=str(config.get('history_limit', 20)))

            try:
                limit = int(limit)
                if limit > 0:
                    config['history_limit'] = limit
                    save_config(config)
                    print_success("History limit updated.")
                else:
                    print_error("Limit must be greater than 0.")
            except:
                print_error("Invalid limit. Please enter a number.")

            input("Press Enter to continue...")


def run_setup_wizard():
    """Run the first-time setup wizard."""
    clear_screen()
    print_logo()

    print_info("Welcome to TempIdentity!")
    print("This wizard will help you set up the application.")
    print()

    if not confirm("Start setup wizard?", default=True):
        return

    config = load_config()

    # Step 1: TextVerified API Key
    clear_screen()
    print_logo()
    print_step("1", "3", "TextVerified API Key")

    print_info("TextVerified is a service that provides temporary phone numbers.")
    print_info("You'll need an API key to use this feature. If you don't have one,")
    print_info("you can still use the temporary email feature.")

    has_api_key = confirm("Do you have a TextVerified API key?", default=False)

    if has_api_key:
        api_key = prompt("Enter your TextVerified API key", password=True)

        if validate_api_key(api_key):
            config['textverified_api_key'] = api_key
            print_success("API key saved.")
        else:
            print_warning("Invalid API key format. You can set it later in Settings.")
    else:
        print_info("You can set up your API key later in Settings.")

    # Step 2: Email Service
    clear_screen()
    print_logo()
    print_step("2", "3", "Email Service")

    print_info("TempIdentity supports different email services.")
    print_info("Currently, 'mail.gw' is the recommended service.")

    email_service = prompt("Enter preferred email service", default="mail.gw")
    config['preferred_email_service'] = email_service

    # Step 3: Other Settings
    clear_screen()
    print_logo()
    print_step("3", "3", "Additional Settings")

    wait_time = prompt("Default wait time for messages/SMS (seconds)", default="120")
    try:
        wait_time = int(wait_time)
        if wait_time > 0:
            config['default_wait_time'] = wait_time
    except:
        print_warning("Invalid wait time. Using default (120 seconds).")

    save_history = confirm("Save history of created emails and phone numbers?", default=True)
    config['save_history'] = save_history

    if save_history:
        history_limit = prompt("Maximum number of history items to keep", default="20")
        try:
            history_limit = int(history_limit)
            if history_limit > 0:
                config['history_limit'] = history_limit
        except:
            print_warning("Invalid history limit. Using default (20 items).")

    # Save configuration
    save_config(config)

    clear_screen()
    print_logo()
    print_success("Setup completed successfully!")
    print_info("You can change these settings anytime from the Settings menu.")
    input("Press Enter to continue...")


# ====== Main Program ======

def main():
    """Main program entry point."""
    parser = argparse.ArgumentParser(description='TempIdentity - Temporary Email & SMS Tool')
    parser.add_argument('--version', action='version', version=f'TempIdentity v{__version__}')
    parser.add_argument('--email', action='store_true', help='Create a temporary email')
    parser.add_argument('--sms', action='store_true', help='Create a temporary phone number')
    parser.add_argument('--wait', type=int, help='Wait time in seconds')
    args = parser.parse_args()

    # Check if first run
    config_exists = CONFIG_FILE.exists()

    # Direct command line usage
    if args.email:
        # Load config
        load_config()
        create_temp_email()
        return
    elif args.sms:
        # Load config
        load_config()
        create_temp_sms()
        return

    # Interactive mode
    try:
        # First run wizard
        if not config_exists:
            run_setup_wizard()

        # Main loop
        while True:
            choice = show_menu()

            if choice == "0":
                clear_screen()
                print_logo()
                print_info("Thank you for using TempIdentity!")
                break
            elif choice == "1":
                create_temp_email()
            elif choice == "2":
                create_temp_sms()
            elif choice == "3":
                view_email_history()
            elif choice == "4":
                view_sms_history()
            elif choice == "5":
                settings_menu()
    except KeyboardInterrupt:
        clear_screen()
        print_logo()
        print_info("Exiting TempIdentity...")
    except Exception as e:
        print_error(f"An error occurred: {e}")
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()