import anthropic

from app.config import get_settings

client = anthropic.Anthropic()
settings = get_settings()

def find_evidence(sub_claim_text, allowed_domains=None):
    web_search_tool = {"type": "web_search_20250305", "name": "web_search", "max_uses": 3}
    if allowed_domains:
        web_search_tool["allowed_domains"] = allowed_domains

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=1000,
            tools=[web_search_tool],
            messages=[
                {
                    "role": "user",
                    "content": f"""Search the web for evidence about this claim: "{sub_claim_text}"

Find 2-3 sources. For each one, reply on its own line in this exact format:
URL | supports or conflicts | one sentence summary | a short direct quote from the source backing the summary""",
                }
            ],
        )
    except Exception:
        return []

    full_text = "".join(block.text for block in response.content if block.type == "text")
    return parse_evidence_lines(full_text)


def parse_evidence_lines(full_text):
    lines = full_text.strip().split("\n")

    results = []
    for line in lines:
        parts = [p.strip() for p in line.split("|", 3)]
        if len(parts) != 4 or not parts[3]:
            continue

        relation_raw = parts[1].strip("* ").lower()
        if "conflict" in relation_raw:
            relation = "conflicts"
        elif "support" in relation_raw:
            relation = "supports"
        else:
            continue

        results.append(
            {
                "url": parts[0],
                "relation": relation,
                "summary": parts[2],
                "supporting_quote": parts[3],
            }
        )
    return results
