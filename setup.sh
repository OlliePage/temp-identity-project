#!/bin/bash
# This script shows how to set up the TempIdentity project

# Create project structure
mkdir -p tempidentity/tempidentity

# Create the main script
cat > tempidentity/tempidentity/tempidentity.py << 'ENDFILE'
#!/usr/bin/env python3
"""
TempIdentity - A tool for generating temporary email addresses and phone numbers
"""

# Paste the full tempidentity.py script contents here
ENDFILE

# Create the __init__.py file
cat > tempidentity/tempidentity/__init__.py << 'ENDFILE'
from .tempidentity import main

__version__ = "0.1.0"
ENDFILE

# Create setup.py
cat > tempidentity/setup.py << 'ENDFILE'
#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tempidentity",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for generating temporary email addresses and phone numbers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tempidentity",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "colorama>=0.4.4",
        "rich>=10.0.0",
        "yaspin>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "tempidentity=tempidentity.tempidentity:main",
        ],
    },
)
ENDFILE

# Create README.md
cat > tempidentity/README.md << 'ENDFILE'
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
ENDFILE

# Create LICENSE file
cat > tempidentity/LICENSE << 'ENDFILE'
MIT License

Copyright (c) 2025 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
ENDFILE

# Installation instructions
echo "
Project structure created in ./tempidentity/ directory

To install the package:

cd tempidentity
pip install -e .

Then run:
tempidentity
"
