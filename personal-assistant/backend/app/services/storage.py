import aiofiles
from pathlib import Path
from datetime import datetime
from ..core.config import settings
from loguru import logger
import re

class StorageService:
    @staticmethod
    def _sanitize_filename(title: str) -> str:
        # Keep only valid chars, replace spaces with underscores
        return re.sub(r'[^a-zA-Z0-9_\-\u4e00-\u9fa5]', '', title.replace(' ', '_'))

    @staticmethod
    async def save_markdown(data: dict) -> str:
        """
        Saves content to a Markdown file with YAML frontmatter.
        Returns the absolute path of the saved file.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = StorageService._sanitize_filename(data.get("title", "Untitled"))
        filename = f"{date_str}_{safe_title}.md"
        file_path = settings.DATA_DIR / filename
        
        frontmatter = f"""---
title: "{data.get('title')}"
date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tags: {data.get('tags', [])}
category: "{data.get('category', 'Note')}"
source: "{data.get('source')}"
summary: "{data.get('summary')}"
---

# {data.get('title')}

{data.get('content')}
"""
        
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(frontmatter)
            
            logger.info(f"Saved note to {file_path}")
            return str(file_path)
        
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise e
