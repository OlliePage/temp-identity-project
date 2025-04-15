# TempIdentity Development Guide

This guide explains how to set up TempIdentity for development.

## Prerequisites

- Python 3.8 or higher
- Poetry package manager (see [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation))

## Setting Up Development Environment

1. Clone the repository:

```bash
git clone https://github.com/OlliePage/temp-identity-project.git
cd temp-identity-project
```

2. Install dependencies using Poetry:

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

3. Run the application:

```bash
# Using the CLI entry point
tempidentity

# Directly running the module
python -m tempidentity.cli
```

## Development Workflow

1. Make your changes to the codebase
2. Run tests:

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=tempidentity

# Run a specific test file
poetry run pytest tests/test_registry.py

# Run tests with verbose output
poetry run pytest -v
```

3. Format and check code style:

```bash
# Format code
poetry run black tempidentity

# Check style
poetry run flake8 tempidentity

# Sort imports
poetry run isort tempidentity
```

4. Build the package:

```bash
poetry build
```

## Project Architecture

TempIdentity is built around the concept of *providers* - pluggable components that implement specific services for creating temporary emails or phone numbers.

### Core Components

1. **Core Module (`core.py`)**: Contains the main business logic and functions for creating and managing temporary identities.

2. **Provider System**:
   - **Registry (`providers/registry.py`)**: Manages provider registration and discovery.
   - **Provider Base Classes**:
     - `EmailProvider`: Base class for email providers
     - `SMSProvider`: Base class for SMS providers
   - **Provider Implementations**:
     - `MailGwProvider`: Implementation for Mail.gw email service
     - `TextVerifiedProvider`: Implementation for TextVerified SMS service

3. **CLI (`cli.py`)**: Command-line interface implementation using argparse and interactive terminal components.

### Extension Points

The main extension points are the provider interfaces:

1. Create a new provider by extending `EmailProvider` or `SMSProvider`
2. Implement the required methods
3. Register the provider in the appropriate `__init__.py` file

See [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md) for detailed instructions.

## User Configuration

User configuration is stored in the `~/.tempidentity/` directory:

- `config.json`: Main configuration file
- `email_history.json`: History of email addresses created
- `sms_history.json`: History of phone numbers created

## Tests as Documentation

The test suite also serves as documentation for how to use the package. Key test files:

- `test_usage.py`: Examples of how to use the core functionality
- `test_cli.py`: Examples of how to use the command-line interface

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Commit Message Guidelines

Please use clear, descriptive commit messages that explain the "why" behind your changes.

Example:
```
Add Mail.gw provider for temporary email addresses

Implements a new provider for the Mail.gw service, supporting:
- Creating temporary email addresses
- Checking for incoming messages
- Retrieving message content
```

## Release Process

1. Update the version number in:
   - `pyproject.toml`
   - `tempidentity/__init__.py`

2. Update the CHANGELOG.md file with the changes

3. Create a new release on GitHub

4. Build and publish to PyPI:
   ```bash
   poetry build
   poetry publish
   ```