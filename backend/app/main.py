from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Stance, Topic

app = FastAPI()


class StanceIn(BaseModel):
    text: str


@app.get("/status")
def health_check():
    return {"status": "ok"}


@app.get("/topics")
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()
    return [{"id": t.id, "name": t.name} for t in topics]


@app.post("/stances")
def create_stance(stance: StanceIn, db: Session = Depends(get_db)):
    new_stance = Stance(raw_text=stance.text)
    db.add(new_stance)
    db.commit()
    db.refresh(new_stance)
    return {"id": new_stance.id, "text": new_stance.raw_text}
