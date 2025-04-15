# TempIdentity

[![CI](https://github.com/OlliePage/temp-identity-project/actions/workflows/ci.yml/badge.svg)](https://github.com/OlliePage/temp-identity-project/actions/workflows/ci.yml)

A powerful tool for generating temporary email addresses and phone numbers with an interactive terminal interface.

## Features

- **Temporary Email**: Create disposable email addresses and check for incoming messages
- **Temporary SMS**: Get temporary phone numbers for receiving SMS verification codes
- **Interactive Interface**: User-friendly terminal UI with colors and formatting
- **History Management**: Save and view history of created emails and phone numbers
- **Configuration System**: Easy-to-use settings management
- **Plugin Architecture**: Extensible provider system for adding new email and SMS services

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone https://github.com/OlliePage/temp-identity-project.git
cd temp-identity-project

# Install with Poetry
poetry install

# Activate the virtual environment
poetry shell

# Run the application
tempidentity
```

### Using Pip

```bash
pip install tempidentity
```

## Usage

### Interactive Mode

Simply run:

```bash
tempidentity
```

This will start the interactive terminal interface where you can create temporary emails and phone numbers.

### Command Line Mode

```bash
# Create a temporary email
tempidentity --email

# Create a temporary phone number
tempidentity --sms

# Show version
tempidentity --version

# Show help
tempidentity --help
```

## Project Structure

```
tempidentity/
├── tempidentity/                # Main package
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # Command-line interface implementation
│   ├── core.py                  # Core functionality and business logic
│   ├── providers/               # Provider system for extensibility
│   │   ├── __init__.py          # Provider package initialization
│   │   ├── registry.py          # Registry for provider discovery
│   │   ├── email/               # Email provider implementations
│   │   │   ├── __init__.py      # Email provider initialization
│   │   │   ├── base.py          # Base email provider abstract class
│   │   │   └── mailgw.py        # Mail.gw provider implementation
│   │   └── sms/                 # SMS provider implementations
│   │       ├── __init__.py      # SMS provider initialization
│   │       ├── base.py          # Base SMS provider abstract class
│   │       └── textverified.py  # TextVerified provider implementation
├── tests/                       # Test suite
│   ├── __init__.py              # Test package initialization
│   ├── conftest.py              # Pytest configuration and fixtures
│   ├── test_core.py             # Tests for core functionality
│   ├── test_registry.py         # Tests for provider registry
│   ├── test_usage.py            # Usage examples as tests
│   └── test_cli.py              # Tests for CLI functionality
├── pyproject.toml               # Poetry package configuration
├── README.md                    # Project documentation (this file)
├── LICENSE                      # License information
├── DEVELOPMENT.md               # Development guide
├── PLUGIN_DEVELOPMENT_GUIDE.md  # Guide for creating custom providers
└── .github/workflows/           # GitHub Actions CI/CD configuration
    └── ci.yml                   # Continuous integration workflow
```

## Key Components

- **CLI Module**: The entry point for the command-line interface, handling user input and displaying output.
- **Core Module**: Contains the main business logic for creating temporary emails and SMS numbers.
- **Provider System**: An extensible architecture for integrating different email and SMS services.
  - **Registry**: Manages provider registration and discovery.
  - **Email Providers**: Implementations for different temporary email services.
  - **SMS Providers**: Implementations for different temporary phone number services.
- **Tests**: Comprehensive test suite that also serves as documentation.

## Adding Custom Providers

TempIdentity uses an extensible provider system, allowing you to add custom email and SMS services. 
See [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md) for detailed instructions.

## Development

For detailed development instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

### Quick Start for Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=tempidentity

# Format code
poetry run black tempidentity

# Check style
poetry run flake8 tempidentity
```

## Configuration

TempIdentity stores configuration in `~/.tempidentity/config.json`. The configuration includes:

- Preferred email and SMS providers
- API keys for providers
- Default wait times
- History settings

## Requirements

- Python 3.8+
- An API key for TextVerified (for SMS functionality)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.