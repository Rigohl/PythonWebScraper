import re
import json
import os

# Load autonomy settings

def load_autonomy_settings():
    settings_file = os.path.join(os.path.dirname(__file__), '../../config/autonomy_settings.json')
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"use_emojis": True}

SETTINGS = load_autonomy_settings()


def sanitize_text(text: str) -> str:
    """If use_emojis is disabled, remove emojis from the input text."""
    if SETTINGS.get("use_emojis", True):
        return text
    # Simple regex to remove emoji (unicode range)
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


# Example usage:
if __name__ == '__main__':
    sample = "Hello 😃!"
    print(sanitize_text(sample))
