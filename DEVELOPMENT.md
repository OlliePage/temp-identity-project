# TempIdentity Development Guide

This guide explains how to set up TempIdentity for development.

## Prerequisites

- Python 3.6 or higher
- Poetry package manager (see [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation))

## Setting Up Development Environment

1. Clone the repository:

```bash
git clone https://github.com/yourusername/tempidentity.git
cd tempidentity
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

## Project Structure

```
tempidentity/
├── tempidentity/          # Main package
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── core.py            # Core functionality
│   ├── providers/         # Provider implementations
│   │   ├── __init__.py    # Provider package initialization
│   │   ├── registry.py    # Provider registry
│   │   ├── email/         # Email providers
│   │   │   ├── __init__.py
│   │   │   ├── base.py    # Base email provider class
│   │   │   └── mailgw.py  # Mail.gw provider implementation
│   │   └── sms/           # SMS providers
│   │       ├── __init__.py
│   │       ├── base.py    # Base SMS provider class
│   │       └── textverified.py  # TextVerified provider implementation
├── pyproject.toml         # Poetry configuration
├── README.md              # Project documentation
├── LICENSE                # License information
└── PLUGIN_DEVELOPMENT_GUIDE.md  # Guide for creating custom providers
```

## Adding a New Provider

See [PLUGIN_DEVELOPMENT_GUIDE.md](PLUGIN_DEVELOPMENT_GUIDE.md) for detailed instructions on how to create new email and SMS providers.

## Development Workflow

1. Make your changes to the codebase
2. Run tests:

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=tempidentity
```

3. Format and check code style:

```bash
# Format code
poetry run black tempidentity

# Check style
poetry run flake8 tempidentity
```

4. Build the package:

```bash
poetry build
```

## User Configuration

User configuration is stored in the `~/.tempidentity/` directory:

- `config.json`: Main configuration file
- `email_history.json`: History of email addresses created
- `sms_history.json`: History of phone numbers created

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request