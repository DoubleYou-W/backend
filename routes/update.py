from datetime import datetime
from typing import Optional

from fastapi import APIRouter ,HTTPException
from pydantic import BaseModel

from databases.embeddings import add_to_vector_db

router = APIRouter()

class UpdateRequest(BaseModel):
    content: str
    source: Optional[str] = None
    timestamp: Optional[str] = None

@router.post("/update")
def update_data(request: UpdateRequest):
    parsed_timestamp = None

    if request.timestamp:
        try:
            parsed_timestamp = datetime.fromtimestamp(float(request.timestamp))
        except (ValueError, OSError):
            raise HTTPException(status_code=400, detail="Invalid Unix timestamp format.")

    if not parsed_timestamp:
        parsed_timestamp = datetime.now()

    metadata = {
        "source": request.source,
        "timestamp": parsed_timestamp.strftime("%m-%d-%Y")
    }

    try:
        add_to_vector_db(request.content, metadata)

        return {
            "status": "ok",
            "message": "Data added to vector DB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
