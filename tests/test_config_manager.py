import os
import json
import pytest
import config_manager

def test_get_default_config():
    """
    Tests if get_default_config returns the correct default dictionary.
    """
    assert config_manager.get_default_config() == {'theme': 'Escuro'}

def test_load_config_creates_default_when_missing(monkeypatch, tmp_path):
    """
    Tests if load_config creates and returns a default config if none exists.
    """
    temp_config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_manager, 'CONFIG_FILE', str(temp_config_file))

    # Ensure the file doesn't exist
    assert not os.path.exists(temp_config_file)

    # Load config
    config = config_manager.load_config()

    # Check if default config is returned and file is created
    assert config == {'theme': 'Escuro'}
    assert os.path.exists(temp_config_file)
    with open(temp_config_file, 'r') as f:
        assert json.load(f) == {'theme': 'Escuro'}

def test_load_config_loads_existing_file(monkeypatch, tmp_path):
    """
    Tests if load_config correctly loads an existing configuration file.
    """
    temp_config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_manager, 'CONFIG_FILE', str(temp_config_file))

    # Create a custom config file
    custom_config = {'theme': 'Claro'}
    with open(temp_config_file, 'w') as f:
        json.dump(custom_config, f)

    # Load config
    config = config_manager.load_config()

    # Check if the custom config is loaded
    assert config == custom_config

def test_load_config_handles_corrupted_file(monkeypatch, tmp_path):
    """
    Tests if load_config returns a default config if the file is corrupted.
    """
    temp_config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_manager, 'CONFIG_FILE', str(temp_config_file))

    # Create a corrupted config file
    with open(temp_config_file, 'w') as f:
        f.write("{'theme': 'Claro',") # Invalid JSON

    # Load config
    config = config_manager.load_config()

    # Check if the default config is returned
    assert config == {'theme': 'Escuro'}

def test_save_config(monkeypatch, tmp_path):
    """
    Tests if save_config correctly saves the configuration data to a file.
    """
    temp_config_file = tmp_path / "config.json"
    monkeypatch.setattr(config_manager, 'CONFIG_FILE', str(temp_config_file))

    new_config = {'theme': 'Azul'}
    config_manager.save_config(new_config)

    # Check if the file was saved correctly
    with open(temp_config_file, 'r') as f:
        saved_config = json.load(f)
    assert saved_config == new_config
