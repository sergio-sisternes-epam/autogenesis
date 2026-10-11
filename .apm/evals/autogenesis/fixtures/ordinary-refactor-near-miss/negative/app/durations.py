def parse_duration(text):
    """Parse '5s', '2m' or '1h' into seconds."""
    if text.endswith("s"):
        value = int(text[:-1])
        return value
    if text.endswith("m"):
        value = int(text[:-1])
        return value * 60
    if text.endswith("h"):
        value = int(text[:-1])
        return value * 3600
    raise ValueError(f"unknown duration: {text}")
