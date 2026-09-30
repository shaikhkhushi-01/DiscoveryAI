SCIENTIFIC_EXTRACTION_SYSTEM = """You are a scientific research extraction engine. Extract only information explicitly supported by the supplied paper text. Never invent entities or claims. Return valid JSON when requested."""

def scientific_extraction_prompt(text: str) -> str:
    return f"Extract topics, methods, datasets, problems, applications, metrics, limitations, and future_work from this scientific text. Return JSON with those keys.\n\nTEXT:\n{text}"
