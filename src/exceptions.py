class ScraperException(Exception):
    """Base class for all custom scraper exceptions."""


class ScrapingError(ScraperException):
    """Exception for general errors during the scraping process."""


class NetworkError(ScraperException):
    """Exception for network errors like timeouts or failed connections."""


class ParsingError(ScraperException):
    """Exception for errors during content parsing or extraction."""


class ContentQualityError(ScraperException):
    """Exception for when the quality of scraped content is unacceptable."""


class LLMError(ScraperException):
    """Exception for errors during LLM processing (e.g., API calls)."""
