from app.services.extraction import ScientificExtractor
from app.services.normalization import classify_future_work, classify_limitation, normalize_concepts

class PaperUnderstandingPipeline:
    def __init__(self, extractor: ScientificExtractor): self.extractor=extractor
    async def run(self, parsed: dict) -> dict:
        raw=await self.extractor.extract(parsed.get("text", ""))
        for key in ("topics","keywords","methods","algorithms","datasets","problems","applications","domains","metrics","baselines"):
            raw[key]=normalize_concepts(raw.get(key, []))
        raw["limitations"]=[{"text":x,"category":classify_limitation(x)} for x in raw.get("limitations", [])]
        raw["future_work"]=[{"text":x,"category":classify_future_work(x)} for x in raw.get("future_work", [])]
        raw["document_id"]=parsed.get("document_id")
        return raw
