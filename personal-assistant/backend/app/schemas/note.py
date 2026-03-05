from pydantic import BaseModel
from typing import List, Optional

class IngestRequest(BaseModel):
    text: str  # Can be a URL or raw text

class IngestResponse(BaseModel):
    file_path: str
    title: str
    summary: str
    tags: List[str]
    category: str
