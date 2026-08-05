from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.classify import classify_topic
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
    topics = db.query(Topic).all()
    topic_names = [t.name for t in topics]
    matched_name = classify_topic(stance.text, topic_names)
    matched_topic = next((t for t in topics if t.name == matched_name), None)

    new_stance = Stance(
        raw_text=stance.text,
        topic_id=matched_topic.id if matched_topic else None,
    )
    db.add(new_stance)
    db.commit()
    db.refresh(new_stance)
    return {"id": new_stance.id, "text": new_stance.raw_text, "topic_id": new_stance.topic_id}


@app.get("/stances")
def get_stances(db: Session = Depends(get_db)):
    stances = db.query(Stance).all()
    return [{"id": s.id, "text": s.raw_text} for s in stances]
