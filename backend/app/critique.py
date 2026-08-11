import anthropic

from app.config import get_settings

client = anthropic.Anthropic()
settings = get_settings()


def needs_more_evidence(sub_claim_text, evidence_list):
    if not evidence_list:
        return True

    summary_lines = "\n".join(
        f"- ({e['relation']}) {e['summary']}" for e in evidence_list
    )

    prompt = f"""Sub-claim: {sub_claim_text}

Evidence found so far:
{summary_lines}

Is this evidence one-sided (all supporting or all conflicting, no opposing view) or too thin (only 1 source)? Reply with just "yes" or "no"."""

    try:
        response = client.messages.create(
            model=settings.model_name,
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip().lower().startswith("yes")
    except Exception:
        return False
