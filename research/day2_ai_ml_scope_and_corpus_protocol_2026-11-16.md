# DiscoveryAI — Phase 1, Day 2: AI/ML Study Scope and Corpus Protocol

**Protocol status:** proposed and versioned for review; not yet a populated corpus or a preregistered experiment.  
**Protocol version:** 1.0  
**Prepared:** 2026-11-16  
**Repository baseline:** main at `7c45799f9d49a8aa030bd9650481330d0cf97a6d`

## 1. Day 2 decision

The first empirical study will use **Natural Language Processing (NLP) and language-model research** as a bounded subdomain within AI/ML. Healthcare, robotics, climate science, general computer vision, and unrelated AI subfields are out of scope for this first study. They may be considered in later external-validity studies, not mixed into this benchmark.

This is a proposed scope decision for the project owner to review. It must not be described as a completed corpus freeze: no paper list, full-text archive, candidate benchmark, or expert labels are created by this document.

## 2. Study objective and research questions

### Objective

Evaluate whether DiscoveryAI's evidence-grounded hybrid retrieval and research-gap workflow identifies **corpus-bounded research opportunities** more reliably than simpler retrieval/generation baselines on a frozen NLP/language-model literature collection.

### Primary research question

**RQ1:** On the same frozen NLP/language-model corpus and candidate questions, does the full DiscoveryAI system achieve better expert-adjudicated gap-status classification and evidence support quality than (a) LLM-only, (b) Vector RAG, (c) GraphRAG, and (d) Hybrid Retrieval without the full discovery reasoning layer?

The primary outcome definitions, metrics, hypotheses, and statistical tests must be locked in the later statistical protocol before test-set evaluation. This document does not claim that any system is better.

### Secondary questions (exploratory until separately locked)

- **RQ2:** How often can a system provide traceable, relevant supporting *and* contradictory evidence for a proposed gap?
- **RQ3:** How does performance vary by gap type (method, dataset, evaluation, application, or evidence gap)?
- **RQ4:** What are the main error modes when evidence is sparse, contradictory, or outside the frozen corpus?

### Unit of analysis

One benchmark record consists of a bounded research question, one candidate gap claim, one immutable corpus snapshot identifier, and a set of resolvable evidence passages. A gap is judged only relative to the stated corpus and cutoff. It is not a claim of global novelty or proof that no work exists elsewhere.

## 3. Domain boundaries

### Included topical areas

- Natural language processing and computational linguistics.
- Language models, pretraining, fine-tuning, instruction tuning, and adaptation.
- Information retrieval, semantic search, question answering, and retrieval-augmented generation.
- NLP evaluation, robustness, factuality, efficiency, and reproducibility.
- NLP datasets, benchmarks, and evaluation methodology.
- Methods directly applied to language tasks, where the paper reports a clear NLP contribution.

### Excluded topical areas

- Medical/clinical NLP when the research question depends on patient-level or clinical claims; may be considered only as a clearly tagged subtopic in a later study.
- Robotics, climate science, general healthcare, and unrelated scientific domains.
- Purely theoretical ML papers with no identifiable NLP/language task.
- General-purpose software/tool announcements without a research contribution.
- Opinion pieces, editorials, news, tutorials, slides, posters without a full paper, and non-scholarly marketing material.
- Papers for which the relevant full text cannot be lawfully accessed or processed under the applicable terms.

## 4. Time window and snapshot policy

- **Publication window:** 2018-01-01 through 2025-12-31 inclusive.
- **Search/snapshot date:** record the actual retrieval timestamp in UTC at collection time; this protocol's preparation date is not the corpus snapshot date.
- **Why close the publication window:** allow a stable retrospective corpus and avoid mixing in an incomplete current publication year.
- Preserve publication date, version date, venue date, and preprint date separately when available.
- Freeze query strings, API parameters, source versions, retrieval timestamps, raw metadata responses, and checksums before generating benchmark candidates.
- Any later additions create a new corpus version; never silently modify an existing frozen snapshot.

## 5. Candidate source strategy

Use sources for distinct roles. A metadata record, an accessible PDF, and permission to reuse full text are three separate things.

| Source | Role in study | Use rule | Official reference |
|---|---|---|---|
| OpenAlex | Primary discovery and bibliographic metadata; DOI/venue/year/author crosswalk; OA-location and license fields | Use CC0 metadata. Treat full-text rights separately and inspect the specific location license before downloading or processing | https://help.openalex.org/api/ |
| ACL Anthology | Curated computational-linguistics/NLP venue coverage and venue/ID cross-check | Use its bibliographic metadata and stable Anthology IDs; check rights for each full-text item rather than assuming PDF availability grants reuse | https://aclanthology.org/faq/ |
| arXiv | Recent NLP preprints and version history, particularly `cs.CL`; supplementary discovery source, not a substitute for peer-reviewed venue labels | Follow arXiv API/bulk terms and each paper's own license. Store preprint status separately from peer-reviewed status | https://info.arxiv.org/help/bulk_data.html |
| Semantic Scholar | Optional citation/reference cross-check and candidate discovery | Use only if needed; record API/dataset version and access conditions. It is not the sole source of truth for inclusion | https://www.semanticscholar.org/product/api |

### Source precedence and deduplication

1. DOI is the preferred cross-source identity where available.
2. Otherwise use normalized title + first author + year, followed by manual review for ambiguous matches.
3. Link preprint and published versions as one intellectual work when they are materially the same paper; preserve all source/version identifiers.
4. Do not count a preprint and its proceedings version as two independent papers.
5. Preserve source-specific metadata and do not overwrite conflicts silently; record resolution notes.
6. Keep peer-reviewed venue status distinct from preprint-only status.

## 6. Search strategy (to be executed and logged during corpus collection)

### OpenAlex concept/keyword discovery

Use OpenAlex works search/filter with publication years 2018–2025 and NLP/language-related concepts or venue filters. Store the exact API URL/parameters and response timestamp in the retrieval log. Start with terms such as:

- "natural language processing"
- "computational linguistics"
- "language model"
- "large language model"
- "information retrieval"
- "question answering"
- "retrieval augmented generation"
- "text generation"
- "NLP evaluation"

The query should be piloted for precision/recall on a manually inspected sample before finalizing. Do not treat keyword matches as proof of topical eligibility.

### ACL Anthology discovery

Use the official Anthology metadata repository/package to enumerate relevant venues and years. Record the exact repository commit or package version, venue list, and extraction script version.

### arXiv discovery

Use the official arXiv API/bulk access for `cs.CL` records in the time window, with relevant title/abstract terms. Record query syntax, API parameters, version identifiers, and retrieval time. Respect rate limits and terms of use.

### Search log fields

For every source query, record: source, exact query/filters, API or repository version, retrieval timestamp (UTC), result count, page/cursor, raw-response checksum, and collector code commit.

## 7. Inclusion and exclusion rules

### Include a work only when all apply

1. Publication/preprint date falls within 2018–2025.
2. The primary contribution is directly relevant to NLP, computational linguistics, language models, or NLP-oriented information retrieval/evaluation.
3. It is a full research paper or full conference/journal article with enough method/results context for evidence extraction.
4. It has a stable source identifier (DOI, ACL Anthology ID, arXiv ID, or OpenAlex ID).
5. Bibliographic provenance can be verified from at least one authoritative source.
6. Full-text processing is permitted by an explicit applicable license, public-domain status, or documented permission. If only metadata/abstract use is permitted, keep it in the discovery index but exclude it from the full-text evidence corpus.
7. The work is not a duplicate version of another included work.

### Exclude a work when any apply

- Out of scope by domain or contribution.
- Not a full research paper (unless a separately predeclared track explicitly includes it).
- Duplicate, retracted, withdrawn, or superseded without a retained version relationship and rationale.
- Metadata is too incomplete to resolve identity and provenance.
- No lawful basis to retrieve/process the full text for the evidence corpus.
- Full text is corrupt, inaccessible, or too incomplete for reliable extraction.

### Screening process

- Stage A: automated metadata filtering (date, source, terms, identifiers).
- Stage B: title/abstract screening with a recorded reason code.
- Stage C: full-text eligibility and license review.
- Stage D: duplicate/version resolution.
- Keep counts at every stage and preserve excluded-record IDs and reasons. Do not discard screening decisions after the final corpus is frozen.

## 8. Corpus size and composition target (operational, not a power calculation)

Initial operational target: **200–300 eligible full-text papers**, with a discovery pool larger than the final sample. This is a feasibility target only; it is not a statistical power claim. The final size may be lower if rights-clear full text or screening quality is insufficient. Do not lower eligibility standards merely to hit a number.

Seek coverage across:
- publication years (2018–2025);
- core topics (language models, NLP methods/tasks, retrieval/QA/RAG, evaluation/robustness);
- publication types (peer-reviewed venue papers and preprint-only works, reported separately).

Report actual counts and imbalance. Do not force equal quotas where the source population does not support them. Any sampling method and random seed must be recorded before selecting the final subset.

## 9. Licensing, privacy, and data handling

- OpenAlex metadata is CC0; this does **not** relicense the underlying papers.
- arXiv metadata terms and each paper's full-text license are separate; follow both.
- ACL Anthology metadata availability and PDF availability do not, by themselves, establish permission to redistribute or process every paper.
- Store license identifier, license URL, source URL, access date, and decision for each full-text item.
- Do not commit copyrighted PDFs or private reviewer materials to the public GitHub repository unless redistribution rights are explicit.
- Public manifests may contain bibliographic metadata and permitted identifiers; private/local storage may hold files where terms allow.
- Escape/sanitize all externally sourced titles, abstracts, and author strings before rendering or using them in SQL/HTML contexts.
- Keep reviewer identities separate from benchmark records and use pseudonymous annotator IDs.

## 10. Required corpus manifest schema

Each included work must have, at minimum:

- `paper_id` (DiscoveryAI stable internal ID)
- `doi`, `openalex_id`, `arxiv_id`, `acl_anthology_id` (nullable source identifiers)
- `title`, `authors`, `abstract`
- `publication_year`, `publication_date`, `venue`, `peer_review_status`
- `primary_topic`, `secondary_topics`
- `source_name`, `source_record_url`, `fulltext_url`
- `fulltext_access_status`, `license_id`, `license_url`, `license_reviewed_at`
- `version_ids`, `duplicate_group_id`
- `retrieved_at_utc`, `raw_metadata_sha256`, `fulltext_sha256` (when a file is lawfully retained)
- `screening_stage`, `inclusion_status`, `exclusion_reason`, `review_notes`

Never use a mutable URL as the only identity or provenance field.

## 11. Leakage and benchmark separation

- Corpus inclusion and benchmark candidate generation are separate operations.
- Freeze corpus membership and compute its manifest checksum before candidate generation.
- Split by research question and related-paper/version groups, not random chunks. Keep near-duplicate versions and closely related records in the same split where feasible.
- The final test set must not be used for prompt/threshold tuning.
- Candidate-generation outputs must retain their source-paper and evidence provenance.
- Only adjudicated benchmark records may enter official scoring, consistent with the existing annotation rubric.

## 12. Day 2 completion checklist

- [x] Read Day 1 audit and confirm the documented blocker: no frozen populated corpus.
- [x] Define a single bounded primary AI/ML subdomain.
- [x] Define the study objective, primary RQ, exploratory RQs, and unit of analysis.
- [x] Define time window and snapshot/version policy.
- [x] Identify source roles and distinguish metadata access from full-text reuse rights.
- [x] Define search terms, screening stages, inclusion/exclusion rules, and deduplication.
- [x] Define an operational corpus target without presenting it as a power calculation.
- [x] Define manifest, provenance, licensing, privacy, and leakage requirements.
- [ ] Review and accept the proposed NLP/language-model scope.
- [ ] Execute source queries, screen real records, and freeze the actual corpus (planned follow-on collection work; not claimed complete by this scope document).

## 13. Day 2 decision and limitations

**Scope/protocol drafting: complete.**  
**Owner acceptance: pending.**  
**Corpus collection and freeze: not performed.**  
**Scientific validation: not performed.**

This protocol narrows the first study to NLP/language-model literature because it is a coherent AI/ML subdomain with identifiable scholarly sources and venue metadata. The choice should be accepted before corpus collection. Search recall, source coverage, licensing, final corpus size, and screening reliability remain empirical questions to be measured during collection.

## 14. Official source references

- OpenAlex API reference: https://help.openalex.org/api/
- OpenAlex license vocabulary: https://help.openalex.org/data/licenses/
- OpenAlex full-text licensing note: https://help.openalex.org/access/fulltext/
- ACL Anthology FAQ and data access: https://aclanthology.org/faq/
- arXiv bulk access overview and terms reminder: https://info.arxiv.org/help/bulk_data.html
- Semantic Scholar API: https://www.semanticscholar.org/product/api/
