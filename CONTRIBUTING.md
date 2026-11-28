# Contributing

Thanks for your interest in DiscoveryAI. The project is a research prototype focused on evidence-grounded scientific discovery.

## Before opening a change

1. Open an issue describing the problem or proposed change.
2. Keep changes focused and preserve source provenance for scientific claims.
3. Do not add private papers, API credentials, local databases, or benchmark gold labels.
4. Add or update tests for behavior changes.
5. Update documentation when setup, API behavior, data flow, or evaluation assumptions change.

## Local checks

Backend (from `backend/`):
```bash
pip install -r requirements.txt pytest pytest-asyncio
PYTHONPATH=. pytest app/tests tests ../tests -q
python -m compileall app
```

Frontend (from `frontend/`):
```bash
npm install
npm run typecheck
npm run build
npm audit --audit-level=moderate
```

Repository checks (from the root):
```bash
python scripts/setup/foundation_check.py
python scripts/evaluation/release_check.py
docker compose config
```

## Research integrity requirements

- Cite papers and exact evidence passages behind generated claims.
- Treat research gaps as corpus-bounded candidate opportunities, not proof of global novelty.
- Keep gold labels separate from model inputs and tuning.
- Do not invent evaluation results, expert annotations, or baseline comparisons.
- Record model/provider, prompt, corpus snapshot, retrieval configuration, code revision, split, and random seed for benchmark runs.
- Report limitations, missing predictions, and negative results.

All contributions are subject to review; passing automated checks does not constitute scientific validation.