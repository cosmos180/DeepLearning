from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..schemas.note import IngestRequest, IngestResponse
from ..services.ingestion import IngestionService
from ..services.processor import ProcessorService
from ..services.storage import StorageService
from loguru import logger

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
async def ingest_note(request: IngestRequest):
    """
    Ingest a note or URL.
    1. Fetch content (if URL) or use raw text.
    2. Process with LLM (Summary, Tags).
    3. Save to Markdown.
    """
    try:
        # Step 1: Ingestion
        data = await IngestionService.process_input(request.text)
        
        # Step 2: Processing (Assessment)
        processor = ProcessorService()
        processed_data = await processor.process_content(
            title=data['title'],
            content=data['content']
        )
        
        # Merge raw source info with processed info
        final_data = {**data, **processed_data}
        
        # Step 3: Storage
        file_path = await StorageService.save_markdown(final_data)
        
        return IngestResponse(
            file_path=file_path,
            title=final_data['title'],
            summary=final_data['summary'],
            tags=final_data['tags'],
            category=final_data['category']
        )
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
