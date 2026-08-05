from app.db import SessionLocal
from app.models import Topic

db = SessionLocal()

db.add(Topic(name="Energy & Climate"))
db.add(Topic(name="Health & Medicine"))
db.add(Topic(name="Technology & AI"))

db.commit()
db.close()

print("done")
