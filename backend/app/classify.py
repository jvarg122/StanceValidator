import anthropic

client = anthropic.Anthropic()


def classify_topic(text, topic_names):
    prompt = f"""Which of these topics best fits this stance? Reply with just the topic name, nothing else.

Topics: {", ".join(topic_names)}

Stance: {text}"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()
    except Exception:
        return ""
