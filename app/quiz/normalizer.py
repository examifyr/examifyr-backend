def normalize_topic(raw_topic: str) -> str:
    cleaned = " ".join(raw_topic.split())
    normalized = cleaned.lower()
    aliases = {
        "lists": "python lists",
        "list": "python lists",
        "python list": "python lists",
        "python lists": "python lists",
        "dict": "python dicts",
        "dicts": "python dicts",
        "dictionary": "python dicts",
        "dictionaries": "python dicts",
        "python dict": "python dicts",
        "python dicts": "python dicts",
        "function": "python functions",
        "functions": "python functions",
        "python function": "python functions",
        "python functions": "python functions",
        "sql": "sql basics",
        "sql basics": "sql basics",
    }
    return aliases.get(normalized, cleaned)
