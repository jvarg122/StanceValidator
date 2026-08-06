import anthropic

client = anthropic.Anthropic()


def decompose_claim(text):
    prompt = f"""Break this stance down into 2-4 separate, checkable sub-claims. Reply with one sub-claim per line, nothing else.

Stance: {text}"""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )

    lines = response.content[0].text.strip().split("\n")
    return [line.strip("- ").strip() for line in lines if line.strip()]
