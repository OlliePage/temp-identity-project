# TempIdentity

A powerful tool for generating temporary email addresses and phone numbers with an interactive terminal interface.

## Features

- **Temporary Email**: Create disposable email addresses and check for incoming messages
- **Temporary SMS**: Get temporary phone numbers for receiving SMS verification codes
- **Interactive Interface**: User-friendly terminal UI with colors and formatting
- **History Management**: Save and view history of created emails and phone numbers
- **Configuration System**: Easy-to-use settings management

## Installation

### From PyPI

```bash
pip install tempidentity
```

### From Source

```bash
git clone https://github.com/yourusername/tempidentity.git
cd tempidentity
pip install -e .
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

## Requirements

- Python 3.6+
- An API key for TextVerified (for SMS functionality)


Next Steps
To get started:

Copy the main script (tempidentity.py) into your project
Create the project structure with setup.py and package files
Install dependencies: requests, colorama, rich, and yaspin
Install the package with pip install -e .
Run tempidentity to start the interactive interface

The script is designed to be extended with additional email and SMS services in the future through the service factory pattern.


```bash
#
# tempidentity/
# ├── tempidentity/
# │   ├── __init__.py
# │   ├── tempidentity.py  # Main application
# │   ├── providers/       # Provider package
# │   │   ├── __init__.py
# │   │   ├── email/       # Email providers
# │   │   │   ├── __init__.py
# │   │   │   ├── base.py  # Base email provider class
# │   │   │   ├── mailgw.py
# │   │   │   └── temp_mail.py
# │   │   └── sms/         # SMS providers
# │   │       ├── __init__.py
# │   │       ├── base.py  # Base SMS provider class
# │   │       ├── textverified.py
# │   │       └── twilio.py
# │   └── utils/           # Utility functions
# │       ├── __init__.py
# │       └── ...
# ├── setup.py
# └── README.md
```
