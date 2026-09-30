import re

def normalize_concepts(values: list[str]) -> list[str]:
    seen=set(); result=[]
    for value in values:
        cleaned=re.sub(r"\s+", " ", value.strip()).strip(".,;:")
        key=cleaned.casefold()
        if cleaned and key not in seen: seen.add(key); result.append(cleaned)
    return result

def classify_limitation(text: str) -> str:
    t=text.casefold()
    if any(x in t for x in ("dataset", "data", "sample")): return "data"
    if any(x in t for x in ("comput", "memory", "runtime", "cost")): return "computational"
    if any(x in t for x in ("generaliz", "domain", "population")): return "generalization"
    if any(x in t for x in ("evaluation", "metric", "benchmark")): return "evaluation"
    return "other"

def classify_future_work(text: str) -> str:
    t=text.casefold()
    if any(x in t for x in ("dataset", "data collection", "benchmark")): return "data"
    if any(x in t for x in ("evaluate", "evaluation", "experiment")): return "evaluation"
    if any(x in t for x in ("extend", "scale", "larger")): return "extension"
    if any(x in t for x in ("apply", "application", "real-world")): return "application"
    return "research_direction"
