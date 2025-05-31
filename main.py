from fastapi import FastAPI
from routes import talk, update, personal, summary, test


app = FastAPI()

app.include_router(talk.router, prefix="/api")
app.include_router(update.router, prefix="/api")
app.include_router(summary.router, prefix="/api")
app.include_router(personal.router, prefix="/api")
app.include_router(test.router, prefix="/api")
