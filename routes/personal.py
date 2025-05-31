from fastapi import APIRouter ,HTTPException
from pydantic import BaseModel

from databases.storage_db import save_user_info, get_user_info, delete_all
from databases.embeddings import delete_vector_db

router = APIRouter()

class PersonalInfo(BaseModel):
    name: str
    age: int
    gender: str
    about: str
    category :str

@router.post("/personal")
def store_personal_info(info: PersonalInfo):
    if not info.name or not info.age or not info.gender or not info.about or  not info.category:
        raise HTTPException(status_code=400, detail="Some fields are missing")

    try:
        save_user_info(info.name, info.age, info.gender, info.about, info.category)

        return {"status": "ok", "message": "Personal info added to mongo DB"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving user info: {str(e)}")

@router.get("/personal")
def get_personal_info():
    try:
        user_info = get_user_info()

        return {
            "status": "ok",
            "data": {
                "name": user_info['name'],
                "age": user_info['age'],
                "gender": user_info['gender'],
                "about": user_info['about'],
                "category": user_info['category']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user info: {str(e)}")

@router.delete("/personal")
def delete_personal_info():
    try:
        delete_all()
        delete_vector_db()

        return {"status": "ok", "message": "All personal info deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user info: {str(e)}")
