# src/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # General settings
    APP_NAME: str = "Web Scraper PRO"
    
    # Scraper settings
    START_URLS: List[str] = ["http://books.toscrape.com/"]
    CONCURRENCY: int = 4
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/scraper_run.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
