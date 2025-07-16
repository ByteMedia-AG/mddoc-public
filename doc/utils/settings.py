def flatten_settings(data, prefix=''):
    flat = {}
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            flat.update(flatten_settings(value, full_key))
    else:
        flat[prefix] = data
    return flat
