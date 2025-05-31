from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from databases import embeddings
from databases.llm_frame import invoke
from databases.storage_db import get_summary, save_summary
from datetime import datetime

router = APIRouter()

@router.post("/summary")
def generate_summary(timestamp: Optional[str] = Query(default=None)):
    if timestamp:
        try:
            date = datetime.fromtimestamp(float(timestamp))
        except (ValueError, OSError):
            raise HTTPException(status_code=400, detail="Invalid Unix timestamp format.")
    else:
        date = datetime.today()

    cached_summary = get_summary(date)

    if cached_summary:
        return {
            "status": "ok",
            "summary": cached_summary,
        }

    results = embeddings.vectordb.get(include=["metadatas", "documents"])

    day_docs = [
        doc for doc, meta in zip(results["documents"], results["metadatas"])
        if meta.get("timestamp", "").startswith(date.strftime("%m-%d-%Y"))
    ]

    if not day_docs:
        return {"summary": f"No data found for {date.strftime('%m-%d-%Y')}"}

    context = "\n".join(day_docs)
    prompt = f"""
    You are a personal assistant. Please consider all the following context to generate a daily summary for your user. The context may have emails or messages the user received, things the user decided to share or anything in between. Your can start it with: 'Hello! Your daily summary is...".
        Date: {date.strftime('%m-%d-%Y')}
        Context:{context}
    """

    response = invoke(prompt)

    save_summary(response, date)

    return {"status": "ok", "summary": response}


@router.get("/summary")
def get_summary_of_date(timestamp: Optional[str] = Query(default=None)):
    if timestamp:
        try:
            date = datetime.fromtimestamp(float(timestamp))
        except (ValueError, OSError):
            raise HTTPException(status_code=400, detail="Invalid Unix timestamp format.")
    else:
        date = datetime.today()

    summary = get_summary(date)

    if summary:
        return {
            "status": "ok",
            "summary": summary,
            "source": "cached"
        }

    return generate_summary(f"{date.timestamp()}")
