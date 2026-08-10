import anthropic

client = anthropic.Anthropic()

def find_evidence(sub_claim_text):
    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
            messages=[
                {
                    "role": "user",
                    "content": f"""Search the web for evidence about this claim: "{sub_claim_text}"

Find 2-3 sources. For each one, reply on its own line in this exact format:
URL | supports or conflicts | one sentence summary""",
                }
            ],
        )
    except Exception:
        return []

    lines = []
    for block in response.content:
        if block.type == "text":
            lines.extend(block.text.strip().split("\n"))

    results = []
    for line in lines:
        parts = [p.strip() for p in line.split("|")]
        if len(parts) == 3:
            results.append({"url": parts[0], "relation": parts[1], "summary": parts[2]})
    return results
