import uuid


def generate_id(name: str):
    return f"{name}_{uuid.uuid4()}"


def clamp(value, min_value, max_value):
    """Ensure value stays within the specified range."""
    return max(min_value, min(value, max_value))
