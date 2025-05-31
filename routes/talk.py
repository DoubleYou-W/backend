from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from databases.embeddings import get_relevant_docs
from databases.storage_db import get_user_info

from routes import personal
from databases.llm_frame import invoke

router = APIRouter()

class TalkInput(BaseModel):
    prompt: str

@router.post("/talk")
async def talk(input: TalkInput):
    try:
        top_k_chunks = get_relevant_docs(input.prompt)
        context = ' '.join(doc.page_content for doc in top_k_chunks)
        
        personal_info = get_user_info()

        prompt = f"""
            You are {personal_info['name']}'s personal assistant, which is specialized in {personal_info['category']}.
            You are designed to answer questions based on the user's personal information and the context provided.
            Don't overthink and if the context is not relevant, just answer as best as you can, based on your knowledge.

            Personal Information: {personal_info['name']}, {personal_info['gender']}, {personal_info['age']} years old, {personal_info['about']}
            Context: {context}

            Question: {input.prompt}
            Answer:"""

        try:
            response = invoke(prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")
    
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error talking to the llm: {str(e)}")
