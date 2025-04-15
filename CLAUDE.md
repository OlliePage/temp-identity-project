# TempIdentity Project Guide

This guide helps Claude understand the TempIdentity project structure, conventions, and common commands.

## Project Overview

TempIdentity is a Python tool for generating temporary email addresses and phone numbers with an interactive terminal interface. It features:

- Temporary email creation via Mail.gw
- Temporary SMS numbers via TextVerified
- Interactive CLI with color support
- History management for created identities
- Plugin architecture for extensible providers

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
│   │   └── sms/                 # SMS provider implementations
├── tests/                       # Test suite
│   ├── test_core.py             # Tests for core functionality
│   ├── test_registry.py         # Tests for provider registry
│   ├── test_usage.py            # Usage examples as tests
│   └── test_cli.py              # Tests for CLI functionality
```

## Key Components

1. **Provider Architecture**: Uses abstract base classes (`EmailProvider`, `SMSProvider`) and a registry system for extensibility.

2. **Core Functions**: Centralized in `core.py` with functions for email/SMS creation and configuration management.

3. **CLI**: Interactive interface in `cli.py` with both command-line arguments and menu-based operation.

4. **Tests**: Comprehensive test suite includes documentation-as-code examples in `test_usage.py`.

## Common Commands

### Development

```bash
# Install dependencies
poetry install

# Run the application 
poetry run tempidentity

# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=tempidentity

# Format code
poetry run black tempidentity

# Check style
poetry run flake8 tempidentity
```

### Build & Package

```bash
# Build the package
poetry build

# Publish to PyPI (if you have credentials)
poetry publish
```

## Coding Style & Conventions

1. **Black**: Code is formatted using Black with a line length of 100.

2. **Typing**: Use type hints for function parameters and return values.

3. **Docstrings**: Use Google-style docstrings for all public functions and classes.

4. **Provider Convention**: New providers must extend the appropriate base class and implement all abstract methods.

## Adding New Providers

1. Create a new file in `providers/email/` or `providers/sms/`
2. Extend the appropriate base class
3. Implement required methods
4. Set class attributes: `name`, `display_name`, `description`, and `requires_api_key`

Example provider class structure:
```python
class NewEmailProvider(EmailProvider):
    name = "provider_name"
    display_name = "Provider Display Name"
    description = "Description of the provider"
    requires_api_key = True
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        # Provider-specific initialization
    
    def create_email(self) -> Tuple[bool, str, str]:
        # Implementation
        pass
    
    def check_messages(self) -> List[Dict]:
        # Implementation
        pass
    
    def get_message_content(self, message_id: str) -> Dict:
        # Implementation
        pass
```