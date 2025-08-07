# test_settings_handler.py

import os
import json
import pytest
from src.utils.settings_handler import load_settings, get_fernet

def test_valid_settings_load(tmp_path):
    test_data = {
        "email": "test@example.com",
        "password": "123",
        "server": "imap.test.com"
    }
    encrypted = get_fernet().encrypt(json.dumps(test_data).encode())
    settings_file = tmp_path / "settings.bin"
    settings_file.write_bytes(encrypted)

    result = load_settings(str(settings_file), get_fernet())
    assert result == test_data