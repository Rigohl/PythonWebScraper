class ScraperException(Exception):
    """Base class for all custom scraper exceptions."""

    pass


class ScrapingError(ScraperException):
    """Exception for general errors during the scraping process."""

    pass


class NetworkError(ScraperException):
    """Exception for network errors like timeouts or failed connections."""

    pass


class ParsingError(ScraperException):
    """Exception for errors during content parsing or extraction."""

    pass


class ContentQualityError(ScraperException):
    """Exception for when the quality of scraped content is unacceptable."""

    pass


class LLMError(ScraperException):
    """Exception for errors during LLM processing (e.g., API calls)."""

    pass
