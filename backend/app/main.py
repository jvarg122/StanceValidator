from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Topic

app = FastAPI()


@app.get("/status")
def health_check():
    return {"status": "ok"}


@app.get("/topics")
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()
    return [{"id": t.id, "name": t.name} for t in topics]
