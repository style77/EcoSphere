import uuid


def generate_id(name: str):
    return f"{name}_{uuid.uuid4()}"
