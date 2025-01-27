import re

def validate_phone_number(phone):
    """Validate phone number format."""
    pattern = re.compile(r"^\+2547\d{8}$")
    if not pattern.match(phone):
        raise ValueError("Invalid phone number format. Expected format: +2547xxxxxxxx")
    return phone