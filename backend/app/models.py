from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    trusted_domains: Mapped[list[str]] = mapped_column(JSON, default=list)


class Stance(Base):
    __tablename__ = "stances"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_text: Mapped[str] = mapped_column(Text)
    normalized_text: Mapped[str] = mapped_column(String(500), index=True)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    status: Mapped[str] = mapped_column(String(20), default="complete")
    out_of_scope_reason: Mapped[str | None] = mapped_column(Text, nullable=True)


class SubClaim(Base):
    __tablename__ = "sub_claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    stance_id: Mapped[int] = mapped_column(ForeignKey("stances.id"))
    text: Mapped[str] = mapped_column(Text)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048))
    domain: Mapped[str] = mapped_column(String(255), default="")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    sub_claim_id: Mapped[int] = mapped_column(ForeignKey("sub_claims.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    relation: Mapped[str] = mapped_column(String(20))
    summary: Mapped[str] = mapped_column(Text)
    credibility_score: Mapped[float] = mapped_column(Float, default=0.4)
    supporting_quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(20), default="journalism")
    retrieved_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
