import json
from pathlib import Path


DEFAULT_SCHOOL_DETAILS = {
    'name': 'Shikshan',
    'address': '',
    'phone': '',
    'email': '',
    'website': '',
    'logo_filename': 'img/shikshan.png',
}


def get_school_details():
    details_path = Path(__file__).resolve().parent.parent / 'school_details.json'
    if not details_path.exists():
        return DEFAULT_SCHOOL_DETAILS.copy()

    try:
        loaded = json.loads(details_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return DEFAULT_SCHOOL_DETAILS.copy()

    details = DEFAULT_SCHOOL_DETAILS.copy()
    for key in details:
        value = loaded.get(key)
        if isinstance(value, str):
            details[key] = value.strip()
    return details
