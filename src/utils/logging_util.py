import json
import logging
import logging.config
import os
import re
from pathlib import Path


def load_autonomy_settings():
    settings_file = os.path.join(
        os.path.dirname(__file__), "../../config/autonomy_settings.json"
    )
    try:
        with open(settings_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"use_emojis": True}


def setup_logging(default_path="config/logging.json", default_level=logging.INFO):
    """Initialize logging configuration"""
    path = Path(default_path)
    if path.exists():
        with open(path, "rt") as f:
            config = json.load(f)
            # Ensure log directories exist
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logging.warning(
            f"Logging config file {default_path} not found. Using basic configuration."
        )


def sanitize_text(text: str) -> str:
    """If use_emojis is disabled, remove emojis from the input text."""
    settings = load_autonomy_settings()
    if settings.get("use_emojis", True):
        return text
    # Simple regex to remove emoji (unicode range)
    emoji_pattern = re.compile(
        "[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff\U0001f1e0-\U0001f1ff]",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", text)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


def rotate_logs(max_size_mb=10, max_backups=5):
    """Rotate log files if they exceed the maximum size"""
    log_dir = Path("logs")
    for log_file in log_dir.glob("*.log"):
        if log_file.stat().st_size > max_size_mb * 1024 * 1024:
            # Implement log rotation
            for i in range(max_backups - 1, 0, -1):
                old = log_file.with_suffix(f".log.{i}")
                new = log_file.with_suffix(f".log.{i + 1}")
                if old.exists():
                    old.rename(new)
            if log_file.exists():
                log_file.rename(log_file.with_suffix(".log.1"))


# Example usage:
if __name__ == "__main__":
    setup_logging()
    logger = get_logger(__name__)
    logger.info("Logging test message")
    sample = "Hello 😃!"
    logger.info(sanitize_text(sample))
