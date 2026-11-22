# DiscoveryAI Phase 2 — QASPER benchmark data card

**Dataset:** QASPER v0.3.0  
**Use:** Scientific-paper question answering and evidence-selection component evaluation.  
**Official dataset card:** https://huggingface.co/datasets/allenai/qasper  
**Paper:** https://aclanthology.org/2021.naacl-main.365/  
**License stated by the dataset card:** CC BY 4.0; attribution required.  
**License text:** https://creativecommons.org/licenses/by/4.0/

## Version and immutable source inputs

The preparation script uses the official v0.3.0 archive URLs and checksums published in the official dataset metadata at revision `fdc9d8214fbab5dd782958601db4d678e6934a54`:
- Train + development archive: `qasper-train-dev-v0.3.tgz`; SHA-256 `a28fdf966db827bcee3d873107d6b6669864fb7ca8fbf73a192f5e39191bdb5a`.
- Test + evaluator archive: `qasper-test-and-evaluator-v0.3.tgz`; SHA-256 `72a52a41193e2838b8074f80ac074b94f956b84886c36a61c58a7df4171bdd72`.

Expected paper counts from the official metadata:
- Train: 888 papers.
- Validation: 281 papers.
- Test: 416 papers.

The preparation script verifies archive hashes before parsing and rejects changed archives, unexpected split counts, malformed question arrays, and duplicate paper IDs across splits.

## Content and schema

QASPER contains NLP research papers with title, abstract, section names, paragraphs, question IDs, questions, answer annotations, and evidence strings. The source card says full text was extracted from S2ORC. The local pipeline creates:
- `normalized/papers/<split>.jsonl`: paper metadata;
- `normalized/chunks/<split>.jsonl`: abstract and paragraph chunks with stable IDs;
- `normalized/queries/<split>.jsonl`: question inputs only;
- `normalized/references/<split>.jsonl`: gold answer/evidence annotations, separate from model inputs;
- `normalized/manifest.json`: version, checksums, counts, and limitations.

Question records never include gold answers/evidence. Paper IDs remain in a single split; cross-split duplicate paper IDs cause failure.

## Rights and handling

The official dataset card declares CC BY 4.0 for QASPER. DiscoveryAI will retain attribution and version provenance. The paper text is documented as extracted from S2ORC, so this project does not treat the dataset card as an automatic license grant to independently obtain, redistribute, or republish original source-paper PDFs. Local benchmark processing is distinct from public redistribution. Raw archives, normalized full text, and generated benchmark data are gitignored and must not be uploaded as public workflow artifacts.

If source-paper content is independently republished or merged into the general DiscoveryAI literature corpus, perform a separate source-version permission review first.

## Evaluation boundaries

- QASPER supports scientific-paper QA and evidence-selection evaluation, not research-gap novelty or hypothesis quality.
- Report actual split counts, answer-label availability, scoring procedure, and any hidden/withheld test labels observed after acquisition.
- Train is for training/development; validation for model selection; test is locked for final evaluation.
- Do not put reference answers, evidence strings, or hidden test labels into prompts or retrieval indexes used to generate predictions.
- Published Longformer baseline scores in the dataset card are reference points, not DiscoveryAI results.

## Attribution

Dasigi, P., Lo, K., Beltagy, I., Cohan, A., Smith, N. A., & Gardner, M. (2021). A Dataset of Information-Seeking Questions and Answers Anchored in Research Papers. Proceedings of NAACL-HLT 2021.
