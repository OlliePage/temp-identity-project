"""
Command-line interface for TempIdentity.
"""

import os
import sys
import argparse
import platform
import time
from typing import Dict, List, Optional

from tempidentity import __version__
from tempidentity.core import (
    load_config,
    save_config,
    get_history,
    CONFIG_FILE,
    create_temp_email,
    check_email_messages,
    get_email_message_content,
    get_sms_services,
    create_temp_sms,
    wait_for_sms_code,
    cancel_sms_number,
    get_available_providers,
    configure_provider,
    setup_logging,
    LOG_FILE,
)

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


# ====== Utility Functions ======


def clear_screen():
    """Clear the terminal screen cross-platform."""
    os.system("cls" if platform.system() == "Windows" else "clear")


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


def print_step(step: str, total: str, title: str):
    """Print a step in the wizard process."""
    if HAS_RICH:
        console.print(
            f"[bold cyan]Step {step}/{total}:[/bold cyan] [bold]{title}[/bold]"
        )
    else:
        print(
            f"{Fore.CYAN}Step {step}/{total}:{Style.RESET_ALL} {Fore.BOLD}{title}{Style.RESET_ALL}"
        )


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
        if choice == "":
            return default
        return choice in ["y", "yes"]


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

        choice = Prompt.ask(
            "Select an option", choices=["0", "1", "2", "3", "4", "5"], default="1"
        )
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


def create_temp_email_ui():
    """Create a temporary email and wait for messages."""
    clear_screen()
    print_logo()
    print_step("1", "3", "Create Temporary Email")

    config = load_config()
    service_name = config.get("preferred_email_service", "mail.gw")
    wait_time = config.get("default_wait_time", 120)

    # Ask for confirmation
    print_info(f"Using email service: {service_name}")
    if not confirm("Continue with this service?"):
        service_name = prompt("Enter service name", default="mail.gw")

    # Create email
    with spinner("Creating temporary email") as sp:
        success, email, password, _ = create_temp_email()
        if not success:
            sp.fail("Failed to create temporary email")
            input("Press Enter to continue...")
            return
        sp.ok(f"Created email: {email}")

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

    # Ask if user wants to wait for messages
    wait_for_msgs = confirm("Wait for incoming messages?", default=True)

    if wait_for_msgs:
        wait_time = prompt(
            "How long to wait for messages (seconds)?", default=str(wait_time)
        )
        try:
            wait_time = int(wait_time)
        except:
            wait_time = 120

        # Wait for messages
        clear_screen()
        print_logo()
        print_step("3", "3", "Waiting for Messages")

        with spinner(f"Waiting for messages (timeout: {wait_time}s)") as sp:
            new_messages = check_email_messages(
                service_name, email, password, True, wait_time
            )
            if new_messages:
                sp.ok(f"Received {len(new_messages)} messages")
            else:
                sp.fail("No messages received within the timeout period")

        if new_messages:
            print_success(f"Received {len(new_messages)} new messages:")

            for idx, message in enumerate(new_messages):
                print()
                if HAS_RICH:
                    msg_table = Table(title=f"Message {idx + 1}")
                    msg_table.add_column("Property", style="cyan")
                    msg_table.add_column("Value")

                    msg_table.add_row("Subject", message.get("subject", "No Subject"))
                    msg_table.add_row(
                        "From", message.get("from", {}).get("address", "Unknown")
                    )
                    msg_table.add_row("Date", message.get("createdAt", "Unknown"))

                    console.print(msg_table)

                    # Get detailed message content if needed
                    if (
                        "text" not in message
                        and "html" not in message
                        and "id" in message
                    ):
                        detailed_message = get_email_message_content(
                            service_name, email, password, message["id"]
                        )
                        if detailed_message:
                            message = detailed_message

                    # Display content
                    if "text" in message and message["text"]:
                        console.print(Panel(message["text"], title="Content"))
                    elif "html" in message and message["html"]:
                        console.print(
                            Panel(
                                message["html"]
                                .replace("<br>", "\n")
                                .replace("<p>", "\n")
                                .replace("</p>", "\n"),
                                title="HTML Content",
                            )
                        )
                    else:
                        console.print("[yellow]No message content available[/yellow]")
                else:
                    print(f"{Fore.CYAN}Message {idx + 1}:{Style.RESET_ALL}")
                    print(f"Subject: {message.get('subject', 'No Subject')}")
                    print(f"From: {message.get('from', {}).get('address', 'Unknown')}")
                    print(f"Date: {message.get('createdAt', 'Unknown')}")
                    print("-" * 40)

                    # Get detailed message content if needed
                    if (
                        "text" not in message
                        and "html" not in message
                        and "id" in message
                    ):
                        detailed_message = get_email_message_content(
                            service_name, email, password, message["id"]
                        )
                        if detailed_message:
                            message = detailed_message

                    # Display content
                    if "text" in message and message["text"]:
                        print(message["text"])
                    elif "html" in message and message["html"]:
                        print("Message is in HTML format. Here's a simplified version:")
                        print(
                            message["html"]
                            .replace("<br>", "\n")
                            .replace("<p>", "\n")
                            .replace("</p>", "\n")
                        )
                    else:
                        print(
                            f"{Fore.YELLOW}No message content available{Style.RESET_ALL}"
                        )
        else:
            print_warning("No new messages received.")

    input("\nPress Enter to continue...")


def create_temp_sms_ui():
    """Create a temporary phone number and wait for SMS."""
    clear_screen()
    print_logo()
    print_step("1", "3", "Create Temporary Phone Number")

    config = load_config()
    service_name = config.get("preferred_sms_service", "textverified")
    provider_config = config.get("providers", {}).get(service_name, {})
    api_key = provider_config.get("api_key", "")

    # Check if API key is configured
    if not api_key:
        print_warning(f"API key for {service_name} is not configured.")
        api_key = prompt("Enter your API key", password=True)

        if not api_key:
            print_error("API key is required.")
            input("Press Enter to continue...")
            return

        # Ask to save the API key
        if confirm("Save this API key for future use?", default=True):
            if "providers" not in config:
                config["providers"] = {}
            if service_name not in config["providers"]:
                config["providers"][service_name] = {}
            config["providers"][service_name]["api_key"] = api_key
            save_config(config)

    # Get available services
    with spinner("Getting available SMS services") as sp:
        services = get_sms_services()
        if not services:
            sp.fail("Failed to get available services")
            input("Press Enter to continue...")
            return
        sp.ok(f"Found {len(services)} services")

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
                service.get("id", ""),
                service.get("name", ""),
                f"${service.get('price', '0.00')}",
            )

        console.print(services_table)
    else:
        print(f"{Fore.CYAN}Available Services:{Style.RESET_ALL}")
        for service in services:
            print(
                f"{service.get('id', '')}: {service.get('name', '')} (${service.get('price', '0.00')})"
            )

    print()
    service_id = prompt("Select a service by ID")

    # Verify service exists
    service_exists = any(s.get("id") == service_id for s in services)
    if not service_exists:
        print_error(f"Invalid service ID: {service_id}")
        input("Press Enter to continue...")
        return

    # Create phone number
    clear_screen()
    print_logo()
    print_step("3", "3", "Creating Phone Number")

    with spinner(f"Creating phone number for {service_id}") as sp:
        success, phone_number, service_name = create_temp_sms(service_id)
        if not success:
            sp.fail("Failed to create temporary phone number")
            input("Press Enter to continue...")
            return
        sp.ok(f"Created phone number: {phone_number}")

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

    # Wait for SMS
    wait_time = config.get("default_wait_time", 300)
    wait_time = prompt("How long to wait for SMS (seconds)?", default=str(wait_time))

    try:
        wait_time = int(wait_time)
    except:
        wait_time = 300

    with spinner(f"Waiting for SMS (timeout: {wait_time}s)") as sp:
        code = wait_for_sms_code(service_name, wait_time)
        if code:
            sp.ok(f"Received verification code: {code}")
        else:
            sp.fail("No SMS received within the timeout period")

    if code:
        print_success(f"Received verification code: {code}")
    else:
        print_warning("No SMS received within the timeout period.")

        # Try to cancel the number manually
        with spinner("Canceling phone number") as sp:
            if cancel_sms_number(service_name):
                sp.ok("Phone number canceled successfully")
            else:
                sp.fail("Failed to cancel phone number")

    input("\nPress Enter to continue...")


def view_email_history_ui():
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
                item.get("email", "N/A"),
                item.get("service", "N/A"),
                time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(item.get("timestamp", 0))
                ),
            )

        console.print(history_table)
    else:
        print(f"{Fore.CYAN}Email History:{Style.RESET_ALL}")
        for idx, item in enumerate(history):
            print(
                f"{idx + 1}. {item.get('email', 'N/A')} ({item.get('service', 'N/A')}) - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))}"
            )

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
                details_table = Table(
                    title=f"Email Details: {item.get('email', 'N/A')}"
                )
                details_table.add_column("Property", style="cyan")
                details_table.add_column("Value")

                details_table.add_row("Email Address", item.get("email", "N/A"))
                details_table.add_row("Password", item.get("password", "N/A"))
                details_table.add_row("Service", item.get("service", "N/A"))
                details_table.add_row(
                    "Created",
                    time.strftime(
                        "%Y-%m-%d %H:%M:%S", time.localtime(item.get("timestamp", 0))
                    ),
                )

                console.print(details_table)
            else:
                print(f"{Fore.CYAN}Email Details:{Style.RESET_ALL}")
                print(f"Email Address: {item.get('email', 'N/A')}")
                print(f"Password: {item.get('password', 'N/A')}")
                print(f"Service: {item.get('service', 'N/A')}")
                print(
                    f"Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))}"
                )

            # Option to check for messages
            if confirm("\nCheck for new messages?", default=False):
                service_name = item.get("service", "mail.gw")
                email = item.get("email", "")
                password = item.get("password", "")

                wait_time = prompt(
                    "How long to wait for messages (seconds)?", default="60"
                )
                try:
                    wait_time = int(wait_time)
                except:
                    wait_time = 60

                wait = confirm("Wait for new messages?", default=True)

                with spinner("Checking for messages") as sp:
                    messages = check_email_messages(
                        service_name, email, password, wait, wait_time
                    )
                    if messages:
                        sp.ok(f"Found {len(messages)} messages")
                    else:
                        sp.fail("No messages found")

                if messages:
                    if HAS_RICH:
                        msg_table = Table(title="Messages")
                        msg_table.add_column("#", style="cyan")
                        msg_table.add_column("Subject")
                        msg_table.add_column("From")
                        msg_table.add_column("Date")

                        for idx, message in enumerate(messages):
                            msg_table.add_row(
                                str(idx + 1),
                                message.get("subject", "No Subject"),
                                message.get("from", {}).get("address", "Unknown"),
                                message.get("createdAt", "Unknown"),
                            )

                        console.print(msg_table)
                    else:
                        print(f"{Fore.CYAN}Messages:{Style.RESET_ALL}")
                        for idx, message in enumerate(messages):
                            print(
                                f"{idx + 1}. {message.get('subject', 'No Subject')} - From: {message.get('from', {}).get('address', 'Unknown')}"
                            )

                    # Select a message to view
                    msg_choice = prompt(
                        "\nEnter number to view message (or 0 to go back)", default="0"
                    )
                    try:
                        msg_idx = int(msg_choice) - 1
                        if msg_idx >= 0 and msg_idx < len(messages):
                            message = messages[msg_idx]

                            # Get detailed message content if needed
                            if (
                                "text" not in message
                                and "html" not in message
                                and "id" in message
                            ):
                                detailed_message = get_email_message_content(
                                    service_name, email, password, message["id"]
                                )
                                if detailed_message:
                                    message = detailed_message

                            # Display message content
                            if HAS_RICH:
                                console.print(
                                    Panel(
                                        f"Subject: {message.get('subject', 'No Subject')}",
                                        title="Message Details",
                                    )
                                )
                                console.print(
                                    f"From: {message.get('from', {}).get('address', 'Unknown')}"
                                )
                                console.print(
                                    f"Date: {message.get('createdAt', 'Unknown')}"
                                )

                                if "text" in message and message["text"]:
                                    console.print(
                                        Panel(message["text"], title="Content")
                                    )
                                elif "html" in message and message["html"]:
                                    console.print(
                                        Panel(
                                            message["html"]
                                            .replace("<br>", "\n")
                                            .replace("<p>", "\n")
                                            .replace("</p>", "\n"),
                                            title="HTML Content",
                                        )
                                    )
                                else:
                                    console.print(
                                        "[yellow]No message content available[/yellow]"
                                    )
                            else:
                                print(f"{Fore.CYAN}Message Details:{Style.RESET_ALL}")
                                print(
                                    f"Subject: {message.get('subject', 'No Subject')}"
                                )
                                print(
                                    f"From: {message.get('from', {}).get('address', 'Unknown')}"
                                )
                                print(f"Date: {message.get('createdAt', 'Unknown')}")
                                print("-" * 40)

                                if "text" in message and message["text"]:
                                    print(message["text"])
                                elif "html" in message and message["html"]:
                                    print(
                                        "Message is in HTML format. Here's a simplified version:"
                                    )
                                    print(
                                        message["html"]
                                        .replace("<br>", "\n")
                                        .replace("<p>", "\n")
                                        .replace("</p>", "\n")
                                    )
                                else:
                                    print(
                                        f"{Fore.YELLOW}No message content available{Style.RESET_ALL}"
                                    )
                    except:
                        pass

    except:
        print_error("Invalid selection.")

    input("\nPress Enter to continue...")


def view_sms_history_ui():
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
                item.get("phone_number", "N/A"),
                item.get("service", "N/A"),
                time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(item.get("timestamp", 0))
                ),
            )

        console.print(history_table)
    else:
        print(f"{Fore.CYAN}SMS History:{Style.RESET_ALL}")
        for idx, item in enumerate(history):
            print(
                f"{idx + 1}. {item.get('phone_number', 'N/A')} ({item.get('service', 'N/A')}) - {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item.get('timestamp', 0)))}"
            )

    input("\nPress Enter to continue...")


def settings_menu_ui():
    """Settings configuration menu."""
    # Load configuration for use in the settings menu
    load_config()

    while True:
        clear_screen()
        print_logo()

        if HAS_RICH:
            table = Table(title="Settings")
            table.add_column("Option", style="cyan")
            table.add_column("Description")

            table.add_row("1", "Configure Email Providers")
            table.add_row("2", "Configure SMS Providers")
            table.add_row("3", "General Settings")
            table.add_row("0", "Back to Main Menu")

            console.print(table)

            choice = Prompt.ask(
                "Select an option", choices=["0", "1", "2", "3"], default="0"
            )
        else:
            print(f"{Fore.CYAN}Settings:{Style.RESET_ALL}")
            print("1. Configure Email Providers")
            print("2. Configure SMS Providers")
            print("3. General Settings")
            print("0. Back to Main Menu")
            print()

            choice = input("Select an option [0]: ") or "0"

        if choice == "0":
            break
        elif choice == "1":
            # Configure Email Providers
            configure_providers_ui("email")
        elif choice == "2":
            # Configure SMS Providers
            configure_providers_ui("sms")
        elif choice == "3":
            # General Settings
            general_settings_ui()


def configure_providers_ui(provider_type: str):
    """Configure providers of a specific type."""
    # Initialize the registry
    email_providers, sms_providers = get_available_providers()

    # Get providers based on type
    if provider_type == "email":
        providers = email_providers
        title = "Email Providers"
        config_key = "preferred_email_service"
    else:
        providers = sms_providers
        title = "SMS Providers"
        config_key = "preferred_sms_service"

    # Load configuration
    config = load_config()
    current_provider = config.get(config_key, "")

    # Display available providers
    clear_screen()
    print_logo()

    if HAS_RICH:
        table = Table(title=title)
        table.add_column("#", style="cyan")
        table.add_column("Name")
        table.add_column("ID")
        table.add_column("Description")
        table.add_column("Status")

        for idx, (name, provider_class) in enumerate(providers.items()):
            status = "Current" if name == current_provider else ""
            table.add_row(
                str(idx + 1),
                provider_class.display_name,
                name,
                provider_class.description,
                status,
            )

        console.print(table)
    else:
        print(f"{Fore.CYAN}{title}:{Style.RESET_ALL}")
        for idx, (name, provider_class) in enumerate(providers.items()):
            status = (
                f" {Fore.GREEN}(Current){Style.RESET_ALL}"
                if name == current_provider
                else ""
            )
            print(
                f"{idx + 1}. {provider_class.display_name} ({name}): {provider_class.description}{status}"
            )

    print()
    choice = prompt("Select a provider to configure (or 0 to go back)", default="0")

    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(providers):
            print_error("Invalid selection.")
            input("Press Enter to continue...")
            return

        # Get selected provider
        provider_name = list(providers.keys())[idx]
        provider_class = list(providers.values())[idx]

        # Display provider details
        clear_screen()
        print_logo()

        if HAS_RICH:
            console.print(
                f"[bold cyan]Configuring {provider_class.display_name}[/bold cyan]"
            )
        else:
            print(
                f"{Fore.CYAN}Configuring {provider_class.display_name}{Style.RESET_ALL}"
            )

        print(f"ID: {provider_name}")
        print(f"Description: {provider_class.description}")
        print()

        # Set as preferred provider
        make_preferred = confirm(
            f"Set as preferred {provider_type} provider?", default=True
        )

        # Get setup fields
        setup_fields = provider_class.get_setup_fields()
        config_data = {}

        if setup_fields:
            print(f"\nProvider configuration:")

            for field in setup_fields:
                name = field.get("name")
                display_name = field.get("display_name")
                field_type = field.get("type", "text")
                required = field.get("required", False)
                help_text = field.get("help_text", "")

                # Get current value if exists
                current_value = (
                    config.get("providers", {}).get(provider_name, {}).get(name, "")
                )

                print(f"\n{display_name}:")
                if help_text:
                    print(f"  {help_text}")

                if current_value and field_type == "password":
                    print(f"  Current value: *****")
                elif current_value:
                    print(f"  Current value: {current_value}")

                # Get new value
                value = prompt(
                    f"Enter value (leave empty to keep current)",
                    password=(field_type == "password"),
                )

                if value:
                    config_data[name] = value
                elif current_value:
                    config_data[name] = current_value
                elif required:
                    print_error(f"{display_name} is required.")
                    input("Press Enter to continue...")
                    return

        # Save configuration
        with spinner("Saving configuration") as sp:
            if configure_provider(provider_type, provider_name, config_data):
                if make_preferred:
                    config = load_config()
                    config[config_key] = provider_name
                    save_config(config)
                sp.ok("Configuration saved successfully")
            else:
                sp.fail("Failed to save configuration")

        input("Press Enter to continue...")
    except ValueError:
        print_error("Invalid selection.")
        input("Press Enter to continue...")


def general_settings_ui():
    """Configure general settings."""
    config = load_config()

    clear_screen()
    print_logo()

    if HAS_RICH:
        table = Table(title="General Settings")
        table.add_column("Option", style="cyan")
        table.add_column("Current Value")

        table.add_row(
            "1. Default Wait Time", f"{config.get('default_wait_time', 120)} seconds"
        )
        table.add_row(
            "2. Save History",
            "Enabled" if config.get("save_history", True) else "Disabled",
        )
        table.add_row("3. History Limit", f"{config.get('history_limit', 20)} items")
        table.add_row(
            "4. Logging",
            "Enabled" if config.get("logging", True) else "Disabled",
        )
        table.add_row("5. Log Retention", f"{config.get('log_retention_days', 3)} days")
        table.add_row("6. Log Size Limit", f"{config.get('log_max_size_mb', 10)} MB")
        table.add_row("7. View Log File", "")
        table.add_row("0. Back", "")

        console.print(table)

        choice = Prompt.ask(
            "Select an option to change", 
            choices=["0", "1", "2", "3", "4", "5", "6", "7"], 
            default="0"
        )
    else:
        print(f"{Fore.CYAN}General Settings:{Style.RESET_ALL}")
        print(f"1. Default Wait Time: {config.get('default_wait_time', 120)} seconds")
        print(
            f"2. Save History: {'Enabled' if config.get('save_history', True) else 'Disabled'}"
        )
        print(f"3. History Limit: {config.get('history_limit', 20)} items")
        print(
            f"4. Logging: {'Enabled' if config.get('logging', True) else 'Disabled'}"
        )
        print(f"5. Log Retention: {config.get('log_retention_days', 3)} days")
        print(f"6. Log Size Limit: {config.get('log_max_size_mb', 10)} MB")
        print(f"7. View Log File")
        print("0. Back")
        print()

        choice = input("Select an option to change [0]: ") or "0"

    if choice == "0":
        return
    elif choice == "1":
        # Default Wait Time
        wait_time = prompt(
            "Enter default wait time (seconds)",
            default=str(config.get("default_wait_time", 120)),
        )

        try:
            wait_time = int(wait_time)
            if wait_time > 0:
                config["default_wait_time"] = wait_time
                save_config(config)
                print_success("Default wait time updated.")
            else:
                print_error("Wait time must be greater than 0.")
        except:
            print_error("Invalid wait time. Please enter a number.")
    elif choice == "2":
        # Save History
        save_history = not config.get("save_history", True)
        config["save_history"] = save_history
        save_config(config)
        print_success(f"Save history {'enabled' if save_history else 'disabled'}.")
    elif choice == "3":
        # History Limit
        limit = prompt(
            "Enter history limit", default=str(config.get("history_limit", 20))
        )

        try:
            limit = int(limit)
            if limit > 0:
                config["history_limit"] = limit
                save_config(config)
                print_success("History limit updated.")
            else:
                print_error("Limit must be greater than 0.")
        except:
            print_error("Invalid limit. Please enter a number.")
    elif choice == "4":
        # Logging setting
        logging_enabled = not config.get("logging", True)
        config["logging"] = logging_enabled
        save_config(config)
        print_success(f"Logging {'enabled' if logging_enabled else 'disabled'}.")
    elif choice == "5":
        # Log retention days
        days = prompt(
            "Enter log retention in days", default=str(config.get("log_retention_days", 3))
        )

        try:
            days = int(days)
            if days > 0:
                config["log_retention_days"] = days
                save_config(config)
                print_success("Log retention days updated.")
            else:
                print_error("Days must be greater than 0.")
        except:
            print_error("Invalid value. Please enter a number.")
    elif choice == "6":
        # Log size limit
        size = prompt(
            "Enter log size limit in MB", default=str(config.get("log_max_size_mb", 10))
        )

        try:
            size = int(size)
            if size > 0:
                config["log_max_size_mb"] = size
                save_config(config)
                print_success("Log size limit updated.")
            else:
                print_error("Size must be greater than 0.")
        except:
            print_error("Invalid value. Please enter a number.")
    elif choice == "7":
        # View log file
        clear_screen()
        print_logo()
        print_step("1", "1", "Log File")
        
        if not os.path.exists(LOG_FILE):
            print_warning("Log file does not exist yet")
        else:
            import logging
            logging.info("User viewed log file from settings")
            
            if HAS_RICH:
                try:
                    with open(LOG_FILE, 'r') as f:
                        console.print(Panel(f.read(), title="TempIdentity Log File"))
                except Exception as e:
                    print_error(f"Error reading log file: {e}")
            else:
                try:
                    with open(LOG_FILE, 'r') as f:
                        print(f.read())
                except Exception as e:
                    print_error(f"Error reading log file: {e}")

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

    # Step 1: Email Provider
    clear_screen()
    print_logo()
    print_step("1", "3", "Email Provider")

    print_info("TempIdentity supports different email services.")
    print_info("Currently, 'mail.gw' is the recommended service.")

    email_service = prompt("Enter preferred email service", default="mail.gw")
    config["preferred_email_service"] = email_service

    # Step 2: SMS Provider
    clear_screen()
    print_logo()
    print_step("2", "3", "SMS Provider")

    print_info("TextVerified is a service that provides temporary phone numbers.")
    print_info("You'll need an API key to use this feature. If you don't have one,")
    print_info("you can still use the temporary email feature.")

    has_api_key = confirm("Do you have a TextVerified API key?", default=False)

    if has_api_key:
        api_key = prompt("Enter your TextVerified API key", password=True)

        if api_key:
            if not config.get("providers"):
                config["providers"] = {}
            if not config["providers"].get("textverified"):
                config["providers"]["textverified"] = {}
            config["providers"]["textverified"]["api_key"] = api_key
            print_success("API key saved.")
        else:
            print_warning("No API key provided. You can set it later in Settings.")
    else:
        print_info("You can set up your API key later in Settings.")

    # Step 3: Other Settings
    clear_screen()
    print_logo()
    print_step("3", "3", "Additional Settings")

    wait_time = prompt("Default wait time for messages/SMS (seconds)", default="120")
    try:
        wait_time = int(wait_time)
        if wait_time > 0:
            config["default_wait_time"] = wait_time
    except:
        print_warning("Invalid wait time. Using default (120 seconds).")

    save_history = confirm(
        "Save history of created emails and phone numbers?", default=True
    )
    config["save_history"] = save_history

    if save_history:
        history_limit = prompt("Maximum number of history items to keep", default="20")
        try:
            history_limit = int(history_limit)
            if history_limit > 0:
                config["history_limit"] = history_limit
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
    try:
        # Initialize logging
        setup_logging()
        
        # Get command-line arguments before logging for privacy
        parser = argparse.ArgumentParser(
            description="TempIdentity - Temporary Email & SMS Tool"
        )
        parser.add_argument(
            "--version", action="version", version=f"TempIdentity v{__version__}"
        )
        parser.add_argument(
            "--email", action="store_true", help="Create a temporary email"
        )
        parser.add_argument(
            "--sms", action="store_true", help="Create a temporary phone number"
        )
        parser.add_argument("--wait", type=int, help="Wait time in seconds")
        parser.add_argument(
            "--log-view", action="store_true", help="View the log file"
        )
        args = parser.parse_args()
        
        # Log start of program
        import logging
        logging.info(f"TempIdentity v{__version__} starting")
        
        # Initialize the registry
        get_available_providers()

        # Check if first run
        config_exists = os.path.exists(CONFIG_FILE)
        if not config_exists:
            logging.info("First run detected, configuration file does not exist")

        # View logs if requested
        if args.log_view:
            if os.path.exists(LOG_FILE):
                if HAS_RICH:
                    with open(LOG_FILE, 'r') as f:
                        console.print(Panel(f.read(), title="TempIdentity Log File"))
                else:
                    os.system(f"cat {LOG_FILE}")
            else:
                print_error("Log file does not exist yet")
            return

        # Direct command line usage
        if args.email:
            logging.info("Command-line mode: creating temporary email")
            create_temp_email_ui()
            return
        elif args.sms:
            logging.info("Command-line mode: creating temporary SMS")
            create_temp_sms_ui()
            return

        # Interactive mode
        logging.info("Starting interactive mode")
        
        # First run wizard
        if not config_exists:
            run_setup_wizard()

        # Main loop
        while True:
            choice = show_menu()

            if choice == "0":
                logging.info("User selected to exit the application")
                clear_screen()
                print_logo()
                print_info("Thank you for using TempIdentity!")
                break
            elif choice == "1":
                logging.info("User selected to create temporary email")
                create_temp_email_ui()
            elif choice == "2":
                logging.info("User selected to create temporary SMS")
                create_temp_sms_ui()
            elif choice == "3":
                logging.info("User selected to view email history")
                view_email_history_ui()
            elif choice == "4":
                logging.info("User selected to view SMS history")
                view_sms_history_ui()
            elif choice == "5":
                logging.info("User selected to access settings")
                settings_menu_ui()
    except KeyboardInterrupt:
        import logging
        logging.info("Program interrupted by user (KeyboardInterrupt)")
        clear_screen()
        print_logo()
        print_info("Exiting TempIdentity...")
    except Exception as e:
        import logging
        logging.exception(f"Unhandled exception: {str(e)}")
        print_error(f"An error occurred: {e}")
        print_info(f"Check the log file for details: {LOG_FILE}")
        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
