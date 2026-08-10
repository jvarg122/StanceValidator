from app.db import SessionLocal
from app.models import Topic

TOPICS = [
    "Energy & Climate",
    "Health & Medicine",
    "Technology & AI",
    "Economics & Labor",
    "Education",
    "Public Policy",
    "Psychology & Behavior",
]

db = SessionLocal()

existing = {t.name for t in db.query(Topic).all()}
for name in TOPICS:
    if name not in existing:
        db.add(Topic(name=name))

db.commit()
db.close()

print("done")
