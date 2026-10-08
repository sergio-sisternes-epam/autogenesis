UNITS = {"s": 1, "m": 60, "h": 3600}


def parse_duration(text):
    """Parse '5s', '2m' or '1h' into seconds."""
    unit = text[-1:]
    if unit not in UNITS:
        raise ValueError(f"unknown duration: {text}")
    return int(text[:-1]) * UNITS[unit]
