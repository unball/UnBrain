def valueOrDefault(dict, key, default):
    try:
        return dict[key]
    except Exception as e:
        return default