from app.db import SessionLocal
from app.models import Topic

TOPICS = {
    "Energy & Climate": ["iea.org", "eia.gov", "epa.gov", "nature.com", "sciencedirect.com"],
    "Health & Medicine": ["cdc.gov", "nih.gov", "who.int", "ncbi.nlm.nih.gov", "thelancet.com"],
    "Technology & AI": ["ieee.org", "acm.org", "arxiv.org", "nist.gov"],
    "Economics & Labor": ["bls.gov", "imf.org", "worldbank.org", "nber.org"],
    "Education": ["nces.ed.gov", "ed.gov", "brookings.edu"],
    "Public Policy": ["pewresearch.org", "brookings.edu", "rand.org", "cbo.gov"],
    "Psychology & Behavior": ["apa.org", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov"],
}

db = SessionLocal()

existing = {t.name: t for t in db.query(Topic).all()}
for name, domains in TOPICS.items():
    if name not in existing:
        db.add(Topic(name=name, trusted_domains=domains))
    elif not existing[name].trusted_domains:
        existing[name].trusted_domains = domains

db.commit()
db.close()

print("done")
