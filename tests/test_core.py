"""
Tests for the core functionality.
"""

import os
import tempfile
from pathlib import Path
import json
import pytest

from tempidentity.core import load_config, save_config, DEFAULT_CONFIG


@pytest.fixture
def temp_config_dir():
    """
    Fixture that creates a temporary configuration directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the original config directory path
        original_config_dir = Path.home() / ".tempidentity"
        
        # Set the CONFIG_DIR to the temporary directory
        import tempidentity.core
        tempidentity.core.CONFIG_DIR = Path(temp_dir) / ".tempidentity"
        tempidentity.core.CONFIG_FILE = tempidentity.core.CONFIG_DIR / "config.json"
        
        yield tempidentity.core.CONFIG_DIR
        
        # Restore the original config directory path
        tempidentity.core.CONFIG_DIR = original_config_dir
        tempidentity.core.CONFIG_FILE = original_config_dir / "config.json"


def test_load_config_creates_default_config(temp_config_dir):
    """Test that load_config creates a default config if one doesn't exist."""
    # Load config which should create the default config
    config = load_config()
    
    # Check that the config directory was created
    assert temp_config_dir.exists()
    
    # Check that the config file was created
    config_file = temp_config_dir / "config.json"
    assert config_file.exists()
    
    # Check that the config matches the default
    for key, value in DEFAULT_CONFIG.items():
        assert key in config
        assert config[key] == value


def test_save_config(temp_config_dir):
    """Test that save_config properly saves the configuration."""
    # Create a test config
    test_config = {
        "preferred_email_service": "test_email",
        "preferred_sms_service": "test_sms",
        "providers": {
            "test_email": {"api_key": "test_email_key"},
            "test_sms": {"api_key": "test_sms_key"}
        },
        "default_wait_time": 300,
        "save_history": False,
        "history_limit": 10
    }
    
    # Save the config
    assert save_config(test_config) is True
    
    # Check that the config file was created
    config_file = temp_config_dir / "config.json"
    assert config_file.exists()
    
    # Load the saved config and check it matches
    with open(config_file, 'r') as f:
        loaded_config = json.load(f)
    
    for key, value in test_config.items():
        assert key in loaded_config
        assert loaded_config[key] == value


def test_load_config_adds_missing_defaults(temp_config_dir):
    """Test that load_config adds missing defaults to an existing config."""
    # Create a partial config
    partial_config = {
        "preferred_email_service": "test_email",
        "save_history": False
    }
    
    # Ensure config directory exists
    temp_config_dir.mkdir(parents=True, exist_ok=True)
    
    # Save the partial config
    with open(temp_config_dir / "config.json", 'w') as f:
        json.dump(partial_config, f)
    
    # Load the config which should add missing defaults
    config = load_config()
    
    # Check that the config has all default keys
    for key in DEFAULT_CONFIG:
        assert key in config
    
    # Check that the specified values are preserved
    assert config["preferred_email_service"] == "test_email"
    assert config["save_history"] is False
    
    # Check that missing values are filled with defaults
    assert config["preferred_sms_service"] == DEFAULT_CONFIG["preferred_sms_service"]
    assert config["default_wait_time"] == DEFAULT_CONFIG["default_wait_time"]
    assert config["history_limit"] == DEFAULT_CONFIG["history_limit"]