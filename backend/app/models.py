from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))


class Stance(Base):
    __tablename__ = "stances"

    id: Mapped[int] = mapped_column(primary_key=True)
    raw_text: Mapped[str] = mapped_column(Text)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id"), nullable=True)


class SubClaim(Base):
    __tablename__ = "sub_claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    stance_id: Mapped[int] = mapped_column(ForeignKey("stances.id"))
    text: Mapped[str] = mapped_column(Text)


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048))


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    sub_claim_id: Mapped[int] = mapped_column(ForeignKey("sub_claims.id"))
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    relation: Mapped[str] = mapped_column(String(20))
    summary: Mapped[str] = mapped_column(Text)
    credibility_score: Mapped[float] = mapped_column(Float, default=0.4)
