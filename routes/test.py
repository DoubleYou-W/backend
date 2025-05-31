from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from databases.embeddings import get_relevant_docs, vectordb
from databases import llm_frame
from databases.storage_db import get_user_info

router = APIRouter()

@router.get("/test_vectordb")
async def test():
    res = vectordb.get()

    return {
        "status": "ok",
        "data": {
            "documents": res["documents"],
            "metadatas": res["metadatas"]
        }
    }
