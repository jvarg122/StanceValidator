import logging
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.academic import search_semantic_scholar
from app.classify import classify_topic
from app.config import get_settings
from app.credibility import classify_source_type, score_source
from app.critique import needs_more_evidence
from app.db import get_db
from app.decompose import decompose_claim
from app.models import Evidence, Source, Stance, SubClaim, Topic
from app.retrieve import find_evidence
from app.reuse import find_similar_subclaim

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stance_tool")

settings = get_settings()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class StanceIn(BaseModel):
    text: str = Field(min_length=5, max_length=500)


def compute_strength(evidence_list):
    supports = sum(1 for e in evidence_list if e["relation"] == "supports")
    conflicts = sum(1 for e in evidence_list if e["relation"] == "conflicts")

    if supports == 0 and conflicts == 0:
        return "insufficient evidence"
    if supports > conflicts:
        return "supported"
    if conflicts > supports:
        return "disputed"
    return "mixed"


def match_topic(raw_name, topics):
    normalized = raw_name.strip().rstrip(".").lower()
    return next((t for t in topics if t.name.lower() == normalized), None)


def normalize_text(text):
    return " ".join(text.strip().lower().split())


def evidence_row_to_dict(db, evidence_row):
    source = db.query(Source).filter(Source.id == evidence_row.source_id).first()
    return {
        "url": source.url,
        "relation": evidence_row.relation,
        "summary": evidence_row.summary,
        "credibility_score": evidence_row.credibility_score,
        "supporting_quote": evidence_row.supporting_quote,
        "source_type": evidence_row.source_type,
    }


def compute_overall_lean(strengths):
    if all(s == "insufficient evidence" for s in strengths):
        return "insufficient_evidence"
    if all(s == "supported" for s in strengths):
        return "well_supported"
    if "disputed" in strengths and "supported" in strengths:
        return "contested"
    return "weakly_supported"


def build_digest(db, stance):
    if stance.status == "out_of_scope":
        return {
            "id": stance.id,
            "text": stance.raw_text,
            "status": "out_of_scope",
            "out_of_scope_reason": stance.out_of_scope_reason,
            "topic_id": None,
            "topic_name": None,
            "sub_claims": [],
            "overall_lean": None,
        }

    topic = db.query(Topic).filter(Topic.id == stance.topic_id).first() if stance.topic_id else None

    sub_claims = db.query(SubClaim).filter(SubClaim.stance_id == stance.id).all()
    result = []
    for sc in sub_claims:
        evidence = db.query(Evidence).filter(Evidence.sub_claim_id == sc.id).all()
        evidence_list = [evidence_row_to_dict(db, e) for e in evidence]
        result.append(
            {
                "text": sc.text,
                "evidence": evidence_list,
                "strength": compute_strength(evidence_list),
            }
        )

    overall_lean = compute_overall_lean([sc["strength"] for sc in result])

    return {
        "id": stance.id,
        "text": stance.raw_text,
        "status": "complete",
        "topic_id": stance.topic_id,
        "topic_name": topic.name if topic else None,
        "sub_claims": result,
        "overall_lean": overall_lean,
    }


@app.get("/status")
def health_check():
    return {"status": "ok"}


@app.get("/topics")
def get_topics(db: Session = Depends(get_db)):
    topics = db.query(Topic).all()
    return [{"id": t.id, "name": t.name} for t in topics]


@app.post("/stances")
@limiter.limit(settings.rate_limit)
def create_stance(request: Request, stance: StanceIn, db: Session = Depends(get_db)):
    normalized = normalize_text(stance.text)
    duplicate = db.query(Stance).filter(Stance.normalized_text == normalized).first()
    if duplicate:
        logger.info("duplicate stance -> reusing stance %d", duplicate.id)
        return build_digest(db, duplicate)

    topics = db.query(Topic).all()
    topic_names = [t.name for t in topics]
    raw_name = classify_topic(stance.text, topic_names)
    matched_topic = match_topic(raw_name, topics)
    logger.info("classify_topic -> %r matched %s", raw_name, matched_topic.name if matched_topic else None)

    if not matched_topic:
        new_stance = Stance(
            raw_text=stance.text,
            normalized_text=normalized,
            topic_id=None,
            status="out_of_scope",
            out_of_scope_reason=(
                f"This stance doesn't clearly fit any topic we cover yet. "
                f"Topics we cover: {', '.join(topic_names)}."
            ),
        )
        db.add(new_stance)
        db.commit()
        db.refresh(new_stance)
        logger.info("stance %d out of scope, skipping pipeline", new_stance.id)
        return build_digest(db, new_stance)

    new_stance = Stance(
        raw_text=stance.text,
        normalized_text=normalized,
        topic_id=matched_topic.id,
    )
    db.add(new_stance)
    db.commit()
    db.refresh(new_stance)

    sub_claim_texts = decompose_claim(stance.text)
    logger.info("decompose_claim -> %d sub-claims", len(sub_claim_texts))
    sub_claims = [SubClaim(stance_id=new_stance.id, text=text) for text in sub_claim_texts]
    db.add_all(sub_claims)
    db.commit()

    result = []
    for sub_claim in sub_claims:
        similar = None
        if new_stance.topic_id:
            similar = find_similar_subclaim(
                db, new_stance.topic_id, sub_claim.text, exclude_stance_id=new_stance.id
            )

        if similar:
            existing = db.query(Evidence).filter(Evidence.sub_claim_id == similar.id).all()
            found = [evidence_row_to_dict(db, e) for e in existing]
        else:
            domains = matched_topic.trusted_domains
            found = find_evidence(sub_claim.text, domains) + search_semantic_scholar(sub_claim.text)
            iterations = 0
            while (
                needs_more_evidence(sub_claim.text, found)
                and iterations < settings.max_critique_iterations
            ):
                more = find_evidence(sub_claim.text, domains) + search_semantic_scholar(sub_claim.text)
                new_items = [item for item in more if item not in found]
                if not new_items:
                    break
                found = found + new_items
                iterations += 1
            logger.info(
                "evidence for %r -> %d items after %d critique iterations",
                sub_claim.text[:50],
                len(found),
                iterations,
            )

        evidence_list = []
        for item in found:
            source = db.query(Source).filter(Source.url == item["url"]).first()
            if not source:
                source = Source(url=item["url"], domain=urlparse(item["url"]).netloc.lower())
                db.add(source)
                db.commit()
                db.refresh(source)

            credibility_score = item.get("credibility_score", score_source(item["url"]))
            source_type = item.get("source_type", classify_source_type(item["url"]))

            db.add(
                Evidence(
                    sub_claim_id=sub_claim.id,
                    source_id=source.id,
                    relation=item["relation"],
                    summary=item["summary"],
                    credibility_score=credibility_score,
                    supporting_quote=item.get("supporting_quote"),
                    source_type=source_type,
                )
            )
            evidence_list.append(
                {**item, "credibility_score": credibility_score, "source_type": source_type}
            )
        db.commit()
        result.append(
            {
                "text": sub_claim.text,
                "evidence": evidence_list,
                "strength": compute_strength(evidence_list),
                "reused": similar is not None,
            }
        )

    overall_lean = compute_overall_lean([sc["strength"] for sc in result])

    return {
        "id": new_stance.id,
        "text": new_stance.raw_text,
        "topic_id": new_stance.topic_id,
        "topic_name": matched_topic.name if matched_topic else None,
        "sub_claims": result,
        "overall_lean": overall_lean,
    }


@app.get("/stances")
def get_stances(db: Session = Depends(get_db)):
    stances = db.query(Stance).all()
    return [{"id": s.id, "text": s.raw_text} for s in stances]


@app.get("/stances/{stance_id}")
def get_stance(stance_id: int, db: Session = Depends(get_db)):
    stance = db.query(Stance).filter(Stance.id == stance_id).first()
    return build_digest(db, stance)
