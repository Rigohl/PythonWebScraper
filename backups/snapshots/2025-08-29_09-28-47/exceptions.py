class ScraperException(Exception):
    """Clase base para todas las excepciones personalizadas del scraper."""
    pass

class ScrapingError(ScraperException):
    """Excepción para errores generales durante el proceso de scraping."""
    pass

class NetworkError(ScraperException):
    """Excepción para errores relacionados con la red (ej. timeouts, conexiones fallidas)."""
    pass

class ParsingError(ScraperException):
    """Excepción para errores durante el parseo o extracción de contenido."""
    pass

class ContentQualityError(ScraperException):
    """Excepción para cuando la calidad del contenido scrapeado es inaceptable."""
    pass
