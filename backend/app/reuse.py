def word_overlap(a, b):
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())
    if not words_a or not words_b:
        return 0
    return len(words_a & words_b) / len(words_a | words_b)


def find_similar_subclaim(db, topic_id, text, exclude_stance_id=None, threshold=0.5):
    from app.models import Stance, SubClaim

    query = (
        db.query(SubClaim)
        .join(Stance, SubClaim.stance_id == Stance.id)
        .filter(Stance.topic_id == topic_id)
    )
    if exclude_stance_id is not None:
        query = query.filter(Stance.id != exclude_stance_id)
    candidates = query.all()

    best = None
    best_score = threshold
    for candidate in candidates:
        score = word_overlap(text, candidate.text)
        if score > best_score:
            best = candidate
            best_score = score

    return best
