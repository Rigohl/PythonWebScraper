# src/scrapers/toscrape_scraper.py

from httpx import AsyncClient
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .base import BaseScraper
from ..models.results import ScrapeResult

class ToscrapeScraper(BaseScraper):
    """
    A scraper for books.toscrape.com.
    """
    def __init__(self):
        super().__init__(name="toscrape_books")

    async def scrape(self, client: AsyncClient, url: str) -> ScrapeResult:
        """
        Scrapes a single book page from books.toscrape.com.
        """
        response = await client.get(url)
        response.raise_for_status()
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        title = soup.find("h1").text
        price = soup.find("p", class_="price_color").text

        # Description is in a meta tag
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"].strip() if description_tag else "No description found."

        # Find all links on the page and make them absolute
        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]

        return ScrapeResult(
            status="SUCCESS",
            url=url,
            title=title,
            content_text=f"Title: {title}\nPrice: {price}\nDescription: {description}",
            content_html=html_content,
            links=links,
            extracted_data={
                "title": title,
                "price": price,
                "description": description,
            },
            http_status_code=response.status_code,
            content_type="PRODUCT",
        )

