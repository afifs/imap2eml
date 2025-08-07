import os

def save_eml(email_obj, download_folder):
    """Save a single email as .eml using its raw MIME content."""
    eid = email_obj.get("id")
    raw_data = email_obj.get("raw")

    if not eid or not raw_data:
        return False

    os.makedirs(download_folder, exist_ok=True)
    filepath = os.path.join(download_folder, f"{eid}.eml")

    try:
        with open(filepath, "wb") as f:
            f.write(raw_data)
        return True
    except Exception:
        return False