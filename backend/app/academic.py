import anthropic
import requests

from app.config import get_settings

client = anthropic.Anthropic()
settings = get_settings()


def search_semantic_scholar(sub_claim_text, limit=2):
    try:
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": sub_claim_text, "fields": "title,abstract,url", "limit": limit},
            timeout=10,
        )
        papers = resp.json().get("data", [])
    except Exception:
        return []

    results = []
    for paper in papers:
        if not paper.get("abstract") or not paper.get("url"):
            continue

        prompt = f"""Sub-claim: {sub_claim_text}

Paper title: {paper['title']}
Abstract: {paper['abstract']}

Does this paper support or conflict with the sub-claim? Reply with just "supports" or "conflicts"."""

        try:
            response = client.messages.create(
                model=settings.model_name,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            relation = response.content[0].text.strip().lower()
        except Exception:
            continue

        if relation not in ("supports", "conflicts"):
            continue

        abstract = paper["abstract"]
        quote = abstract[:300] + "..." if len(abstract) > 300 else abstract

        results.append(
            {
                "url": paper["url"],
                "relation": relation,
                "summary": paper["title"],
                "supporting_quote": quote,
            }
        )

    return results
