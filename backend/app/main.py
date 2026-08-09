from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.classify import classify_topic
from app.db import get_db
from app.decompose import decompose_claim
from app.models import Evidence, Source, Stance, SubClaim, Topic
from app.retrieve import find_evidence

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    sub_claim_texts = decompose_claim(stance.text)
    sub_claims = [SubClaim(stance_id=new_stance.id, text=text) for text in sub_claim_texts]
    db.add_all(sub_claims)
    db.commit()

    result = []
    for sub_claim in sub_claims:
        evidence_list = []
        for item in find_evidence(sub_claim.text):
            source = db.query(Source).filter(Source.url == item["url"]).first()
            if not source:
                source = Source(url=item["url"])
                db.add(source)
                db.commit()
                db.refresh(source)

            db.add(
                Evidence(
                    sub_claim_id=sub_claim.id,
                    source_id=source.id,
                    relation=item["relation"],
                    summary=item["summary"],
                )
            )
            evidence_list.append(item)
        db.commit()
        result.append({"text": sub_claim.text, "evidence": evidence_list})

    return {
        "id": new_stance.id,
        "text": new_stance.raw_text,
        "topic_id": new_stance.topic_id,
        "sub_claims": result,
    }


@app.get("/stances")
def get_stances(db: Session = Depends(get_db)):
    stances = db.query(Stance).all()
    return [{"id": s.id, "text": s.raw_text} for s in stances]


@app.get("/stances/{stance_id}")
def get_stance(stance_id: int, db: Session = Depends(get_db)):
    stance = db.query(Stance).filter(Stance.id == stance_id).first()

    sub_claims = db.query(SubClaim).filter(SubClaim.stance_id == stance_id).all()
    result = []
    for sc in sub_claims:
        evidence = db.query(Evidence).filter(Evidence.sub_claim_id == sc.id).all()
        evidence_list = []
        for e in evidence:
            source = db.query(Source).filter(Source.id == e.source_id).first()
            evidence_list.append(
                {"url": source.url, "relation": e.relation, "summary": e.summary}
            )
        result.append({"text": sc.text, "evidence": evidence_list})

    return {
        "id": stance.id,
        "text": stance.raw_text,
        "topic_id": stance.topic_id,
        "sub_claims": result,
    }
