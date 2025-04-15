# TempIdentity

[![CI](https://github.com/OlliePage/TempIdentity/actions/workflows/ci.yml/badge.svg)](https://github.com/OlliePage/TempIdentity/actions/workflows/ci.yml)

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
git clone https://github.com/OlliePage/TempIdentity.git
cd TempIdentity

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

## Adding Custom Providers

TempIdentity uses an extensible provider system, allowing you to add custom email and SMS services. 
See [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md) for more information.

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

## Requirements

- Python 3.6+
- An API key for TextVerified (for SMS functionality)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.