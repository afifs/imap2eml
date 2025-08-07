#settings_handler

from cryptography.fernet import Fernet
import json
import os

from src.utils.helpers import resource_path

SETTINGS_FILE = resource_path("settings.dat")
FERNET_KEY_FILE = resource_path("key.key")

def get_fernet():
    if not os.path.exists(FERNET_KEY_FILE):
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(Fernet.generate_key())
    with open(FERNET_KEY_FILE, "rb") as f:
        return Fernet(f.read())

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return None
    try:
        fernet = get_fernet()
        with open(SETTINGS_FILE, "rb") as f:
            decrypted = fernet.decrypt(f.read()).decode()
            return json.loads(decrypted)
    except Exception:
        return None