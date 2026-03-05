import requests
from readability import Document
from bs4 import BeautifulSoup
from loguru import logger
import re

class IngestionService:
    @staticmethod
    def is_url(text: str) -> bool:
        # Simple regex for URL validation
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
            r'localhost|' # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(url_pattern, text) is not None

    @staticmethod
    async def fetch_url(url: str) -> dict:
        try:
            logger.info(f"Fetching URL: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            doc = Document(response.text)
            title = doc.title()
            # Get semantic content
            summary_html = doc.summary()
            
            # Clean generic HTML to text
            soup = BeautifulSoup(summary_html, 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)

            return {
                "source": url,
                "title": title,
                "content": text_content,
                "raw_html": summary_html
            }
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {e}")
            raise Exception(f"Failed to fetch content: {str(e)}")
            
    @staticmethod
    async def process_input(input_text: str) -> dict:
        if IngestionService.is_url(input_text.strip()):
            return await IngestionService.fetch_url(input_text.strip())
        else:
            # It's a raw note
            first_line = input_text.split('\n')[0][:50]
            return {
                "source": "manual_entry",
                "title": first_line if first_line else "Untitled Note",
                "content": input_text,
                "raw_html": None
            }
