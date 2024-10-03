import re


def remove_non_printable(input_string):
    # Use a regex to replace non-printable characters with an empty string
    return re.sub(r'[^\x20-\x7E]', '', input_string)


def clean_object(obj):
    if isinstance(obj, dict):
        return {k: clean_object(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_object(v) for v in obj]
    elif isinstance(obj, str):
        return remove_non_printable(obj)  # Remove non-printable characters
    else:
        return obj
