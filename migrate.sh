#!/bin/bash
# This script migrates from the old pip-based structure to the new poetry-based structure

echo "TempIdentity Migration Script"
echo "============================"
echo "This script will migrate the package from the old pip-based structure to the new poetry-based structure."
echo ""

# Check if poetry is installed
if ! command -v poetry &> /dev/null
then
    echo "Error: Poetry is not installed."
    echo "Please install Poetry by following the instructions at https://python-poetry.org/docs/#installation"
    exit 1
fi

# Check if old directory exists
if [ ! -d "tempidentity" ]; then
    echo "Error: Old 'tempidentity' directory not found."
    echo "Please run this script from the root of the TempIdentity repository."
    exit 1
fi

# Check if new directory already exists
if [ -d "tempidentity_new" ]; then
    echo "Using existing tempidentity_new directory."
else
    echo "Error: New 'tempidentity_new' directory not found."
    echo "Please ensure you have the new structure in the 'tempidentity_new' directory."
    exit 1
fi

# Backup the old directory
echo "Creating backup of old structure..."
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="tempidentity_backup_${timestamp}"
cp -r tempidentity "$backup_dir"
echo "Backup created at '${backup_dir}'."

# Move the new structure to replace the old one
echo "Setting up new structure..."
rm -rf tempidentity
mv tempidentity_new/* .
rm -rf tempidentity_new

# Initialize poetry
echo "Initializing poetry environment..."
poetry install

echo ""
echo "Migration completed successfully!"
echo "You can now use the package with poetry."
echo ""
echo "To run the application, use:"
echo "  poetry run tempidentity"
echo ""
echo "To activate the virtual environment, use:"
echo "  poetry shell"
echo ""
echo "For more information, see README.md and DEVELOPMENT.md."