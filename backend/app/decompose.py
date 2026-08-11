import anthropic

from app.config import get_settings

client = anthropic.Anthropic()
settings = get_settings()


def decompose_claim(text):
    prompt = f"""Break this stance down into 2-4 separate, checkable sub-claims. Reply with one sub-claim per line, nothing else.

Stance: {text}"""

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )
        lines = response.content[0].text.strip().split("\n")
        return [line.strip("- ").strip() for line in lines if line.strip()]
    except Exception:
        return []
