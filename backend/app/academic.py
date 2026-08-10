import anthropic
import requests

client = anthropic.Anthropic()


def search_semantic_scholar(sub_claim_text, limit=2):
    resp = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query": sub_claim_text, "fields": "title,abstract,url", "limit": limit},
    )
    papers = resp.json().get("data", [])

    results = []
    for paper in papers:
        if not paper.get("abstract") or not paper.get("url"):
            continue

        prompt = f"""Sub-claim: {sub_claim_text}

Paper title: {paper['title']}
Abstract: {paper['abstract']}

Does this paper support or conflict with the sub-claim? Reply with just "supports" or "conflicts"."""

        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}],
        )
        relation = response.content[0].text.strip().lower()
        if relation not in ("supports", "conflicts"):
            continue

        results.append({"url": paper["url"], "relation": relation, "summary": paper["title"]})

    return results
