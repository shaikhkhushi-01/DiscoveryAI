# Days 117–119 — Frontend and Dashboard Integration

## Implemented

### Day 117 — API client
Added a small typed-by-convention frontend API client supporting GET/POST requests and optional bearer authentication.

### Day 118 — Scientific intelligence integration
The dashboard now targets the implemented backend routes for:
- research gaps
- temporal trends
- GraphRAG search
- hypothesis and experiment planning

### Day 119 — Resilient UI
The dashboard keeps representative fallback data when the backend is unavailable and explicitly labels it as demo state. Live API state is shown separately.

## Environment

Set `NEXT_PUBLIC_API_URL` to the deployed FastAPI base URL in Vercel.

For local development:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Current scientific UI flow

Question → Evidence/GraphRAG → Research Gaps → Discovery Score → Trends → Hypothesis → Experiment Plan

## Runtime note

The dashboard integration code is committed to the repository. Live Vercel-to-FastAPI behavior requires a deployed backend URL and authentication configuration. No live deployment or runtime result is claimed by this milestone.
