from openai import OpenAI
from ..core.config import settings
from loguru import logger
import json

class ProcessorService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning("OPENAI_API_KEY not found. Using Mock Processor.")

    async def process_content(self, title: str, content: str) -> dict:
        """
        Generates tags, summary, and refined title using LLM.
        """
        if not self.client:
            return self._mock_process(title, content)
        
        try:
            prompt = f"""
            Analyze the following content and extract structured metadata.
            
            Content Title: {title}
            Content Body:
            {content[:4000]}  # Truncate for safety
            
            Return ONLY a valid JSON object with these fields:
            - "title": A clean, descriptive title (string).
            - "summary": A 2-sentence summary (string).
            - "tags": A list of 5 relevant tags (lowercase, no hash) (list of strings).
            - "category": One of [Note, Article, Todo, Technical] (string).
            """
            
            response = self.client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful knowledge assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"LLM Processing failed: {e}")
            return self._mock_process(title, content)

    def _mock_process(self, title: str, content: str) -> dict:
        """Fallback if no API key or error"""
        return {
            "title": title,
            "summary": content[:200].replace("\n", " ") + "...",
            "tags": ["uncategorized", "mock"],
            "category": "Note"
        }
