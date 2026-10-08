SCIENTIFIC_EXTRACTION_SYSTEM = """You are a scientific research extraction engine. Extract only information explicitly supported by the supplied paper text. Never invent entities or claims. Return valid JSON when requested."""


def scientific_extraction_prompt(
    text: str,
    *,
    chunk_number: int = 1,
    total_chunks: int = 1,
) -> str:
    return (
        "Extract topics, keywords, methods, algorithms, datasets, problems, "
        "applications, domains, metrics, baselines, limitations, and future_work "
        "from this scientific text. Return JSON with exactly those keys. "
        f"This is chunk {chunk_number} of {total_chunks}; extract only evidence "
        "present in this chunk. Do not invent missing information.\n\n"
        f"TEXT:\n{text}"
    )
