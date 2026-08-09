from app.db import SessionLocal
from app.models import Topic

db = SessionLocal()

db.add(Topic(name="Energy & Climate"))
db.add(Topic(name="Health & Medicine"))
db.add(Topic(name="Technology & AI"))
db.add(Topic(name="Economics & Labor"))
db.add(Topic(name="Education"))
db.add(Topic(name="Public Policy"))
db.add(Topic(name="Psychology & Behavior"))

db.commit()
db.close()

print("done")
