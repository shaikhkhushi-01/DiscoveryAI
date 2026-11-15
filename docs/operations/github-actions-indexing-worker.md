# GitHub Actions indexing worker

DiscoveryAI's Render web service only persists indexing jobs in PostgreSQL. This
scheduled GitHub Actions workflow runs the existing worker on a GitHub-hosted
runner, so PDF embeddings and graph indexing do not consume the Render web
service's 512 MB memory budget. No Render Background Worker is required.

## Runtime model

- The workflow runs every 15 minutes and can also be started manually.
- Each run drains the PostgreSQL queue sequentially, one job at a time.
- PostgreSQL row locking remains the source of truth for claiming jobs.
- The existing worker recovers expired leases before claiming more work.
- A run stops after 5 hours 50 minutes; jobs not yet claimed remain queued for
  a later run. GitHub scheduled starts are best-effort, not exact timers.
- Workflow concurrency prevents two scheduled runs from indexing simultaneously.
- The repository is public. GitHub-hosted Actions usage for public repositories
  is generally free under GitHub's public-repository policy; check Actions
  usage/billing if GitHub displays a quota warning.

## Required repository Actions secrets

Open **Settings → Secrets and variables → Actions → New repository secret**
and add:

| Secret name | Value |
| --- | --- |
| `DATABASE_URL` | Supabase **Session Pooler** URI from Project → Connect → Session pooler (host must end in `.pooler.supabase.com`, port normally `5432`). Use the same Supabase project/database as Render. Do not use the direct database hostname or an old Neon URL: GitHub-hosted runners in this workflow need the IPv4-capable pooler. Keep the password private; URL-encode reserved characters such as `@` in the password. |
| `QDRANT_URL` | Reachable Qdrant endpoint URL. |
| `QDRANT_API_KEY` | Qdrant API key for the endpoint. |
| `NEO4J_URI` | Reachable Neo4j Bolt URI (the provider's public Bolt URI). |
| `NEO4J_USERNAME` | Neo4j username. |
| `NEO4J_PASSWORD` | Neo4j password. |
| `NEO4J_DATABASE` | Optional; defaults to `neo4j`. |

Use the same PostgreSQL database, Qdrant collection, and Neo4j database as the
web service. Never commit secrets or print them in workflow logs.

The workflow uses `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions),
matching the current backend defaults. It installs CPU-only PyTorch and caches
the model between runs. The worker does not need `GEMINI_API_KEY`: scientific
extraction is done at upload time; this worker embeds the stored text and writes
to Qdrant/Neo4j.

## First run

**Known blocker from the 15 November 2026 runs:** the stored `DATABASE_URL` resolved to an IPv6 address and failed on GitHub-hosted runners with `Network is unreachable`. This is a repository secret/configuration issue, not a worker-code exception. The updated workflow now fails early with a safe instruction if the secret is not the Supabase Session Pooler or has no IPv4 DNS answer. It cannot read or change repository secret values.

1. Merge this workflow into `main`.
2. Add/update the repository secrets above. In particular, replace any old Neon/direct-host `DATABASE_URL` with the Supabase Session Pooler URI. The workflow preflight checks the pooler hostname and IPv4 DNS without printing credentials.
3. Open **Actions → DiscoveryAI Scheduled Indexing Worker → Run workflow**.
4. Inspect logs for `durable indexing worker started`, `indexing job claimed`,
   `embedding batch completed`, `vector indexing completed`,
   `knowledge graph indexing completed`, and `indexing job finished`.
5. Confirm the Document Library reports completed vector and graph statuses.

GitHub-hosted runners are external infrastructure. During indexing, the runner
reads extracted paper text from PostgreSQL and sends embeddings to Qdrant. Do not
enable this workflow for confidential material unless that data flow is
acceptable for the project.
