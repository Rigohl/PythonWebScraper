````markdown
# Gemini Code Assist - PRO Configuration

## 1. Project Overview

This project is a sophisticated Python-based web scraping application. Its primary function is to extract structured data from various websites. The architecture is designed to be modular, allowing for easy extension to new sites and data types.

**Core Functionality:**
- Asynchronous fetching of web pages using `httpx` and `playwright`.
- Parsing of HTML content with `BeautifulSoup` and `readability-lxml`.
- Data validation and structuring using `pydantic`.
- Storing extracted data in a structured format using `dataset`.

## 2. Dependencies

### Production Dependencies:
- `dataset`: For database operations.
- `html2text`: To convert HTML to Markdown.
- `playwright`: For browser automation and JavaScript rendering.
- `readability-lxml`: To extract the main content of a page.
- `pydantic`: For data validation.
- `httpx`: For asynchronous HTTP requests.
- `imagehash`: For hashing and comparing images.
- `robotexclusionrulesparser`: To respect `robots.txt`.
- `playwright-stealth`: To avoid bot detection.
- `pydantic-settings`: For managing settings.

### Development Dependencies:
- `pre-commit`: To run hooks before committing.
- `black`: For code formatting.
- `isort`: For sorting imports.
- `flake8`: For linting.

## 3. Coding Style and Conventions

The project enforces a strict coding style to maintain readability and consistency. All code must adhere to the following standards, which are automatically checked and enforced by pre-commit hooks.

- **Formatter:** `black` with a line length of **120 characters**.
- **Import Sorting:** `isort` with the `black` profile.
- **Linter:** `flake8` for identifying potential errors and style issues.

**Golden Rule:** Always run `pre-commit run --all-files` before committing changes.

## 4. Testing

The project uses `pytest` for unit and integration testing.

- **Test Location:** All tests are located in the `tests/` directory.
- **Execution:** Run tests using the `pytest` command.
- **Configuration:** `pytest.ini` is configured to automatically discover and run tests in the `tests` directory.

## 5. Advanced Configuration: MCP Servers

This section is intended for configuring connections to custom Model Control Plane (MCP) servers. These could be private or fine-tuned AI models that provide specialized capabilities for data extraction, classification, or other tasks.

**Gemini, when you need to use a specialized model for a task, refer to the configuration below. If a model is not listed, use your default capabilities.**

### Example Configuration (To be filled in by the user)

```yaml
# This is an example of how you might configure MCP servers.
# Replace with your actual configuration.
mcp_servers:
  - name: "document_summarizer"
    url: "https://api.example.com/summarize"
    api_key: "YOUR_API_KEY_HERE"
    description: "A specialized model for summarizing long documents."
  - name: "product_classifier"
    url: "https://api.example.com/classify"
    api_key: "YOUR_API_KEY_HERE"
    description: "A model for classifying e-commerce products into categories."
```

## 6. Instructions for Gemini

As a PRO AI assistant for this project, you are expected to:

1.  **Adhere to Conventions:** Strictly follow the coding style and conventions defined in section 3.
2.  **Write Tests:** For any new feature or bug fix, you must write corresponding tests in the `tests/` directory.
3.  **Use Dependencies:** Leverage the existing dependencies to their full potential. Do not introduce new dependencies without explicit permission.
4.  **Be Proactive:** When asked to perform a task, consider the full scope of the request. For example, if asked to add a new scraper, you should also create a test file for it.
5.  **Stay Modular:** Keep the code modular and easy to maintain. Create new files and classes where appropriate.

## 7. Boilerplate: New Scraper

When creating a new scraper, use the following boilerplate as a starting point.

```python
# src/scrapers/new_site_scraper.py

from httpx import AsyncClient
from .base_scraper import BaseScraper, ScrapeResult

class NewSiteScraper(BaseScraper):
    """
    A scraper for new-site.com.
    """
    def __init__(self):
        super().__init__(name="new_site")

    async def scrape(self, client: AsyncClient, url: str) -> ScrapeResult:
        """
        Scrapes a single URL from new-site.com.
        """
        response = await client.get(url)
        response.raise_for_status()

        # ... parsing logic here ...

        return ScrapeResult(
            url=url,
            content="...",
            data={...}
        )
```
