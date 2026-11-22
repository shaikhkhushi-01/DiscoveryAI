# DiscoveryAI — Phase 1 related-work review

**Search date:** 2026-11-22  
**Scope:** NLP research discovery, scientific QA, retrieval, GraphRAG, and automated RAG evaluation.  
**Status:** Focused initial review completed for project scoping; not an exhaustive systematic review or a novelty proof.

## 1. Search log

Searches run on 2026-11-22 using scholarly, publisher and maintainer sources:
- literature based discovery systematic review Swanson ABC model scientific discovery literature mining review NLP
- QASPER paper 5049 questions 1585 NLP papers ACL Anthology NAACL 2021
- GraphRAG paper official arxiv retrieval augmented generation knowledge graphs
- RAGAS automated evaluation RAG paper faithfulness answer relevancy context precision recall
- ARES automated evaluation framework retrieval augmented generation
- BEIR benchmark official repository license dataset retrieval evaluation
- SciFact dataset official repository license benchmark paper evidence retrieval

Primary source pages reviewed:
- Dasigi et al. (2021), QASPER, NAACL: https://aclanthology.org/2021.naacl-main.365/
- QASPER official dataset card: https://huggingface.co/datasets/allenai/qasper
- Thilakaratne et al. (2019), A systematic review on literature-based discovery workflow: https://doi.org/10.7717/peerj-cs.235
- Han et al. (2024; revised 2025), Retrieval-Augmented Generation with Graphs: https://arxiv.org/abs/2501.00309
- Peng et al. (2024; journal version 2025), Graph Retrieval-Augmented Generation: A Survey: https://arxiv.org/abs/2408.08921
- Es et al. (2024), RAGAs: https://aclanthology.org/2024.eacl-demo.16/
- Saad-Falcon et al. (2023), ARES: https://arxiv.org/abs/2311.09476
- Thakur et al. (2021), BEIR: https://github.com/beir-cellar/beir

## 2. Closest-work comparison

| Work | Main task/contribution | Evaluation/data | Relevance to DiscoveryAI | Boundary / implication |
|---|---|---|---|---|
| Thilakaratne et al. (2019), LBD systematic review | Reviews literature-based discovery workflows: inputs, filtering/ranking, outputs and evaluation | Survey of LBD approaches and evaluation practices | Establishes that automated literature discovery and hypothesis generation predate current LLM/RAG systems | DiscoveryAI cannot claim invention of literature-based discovery; position its exact workflow and evidence controls narrowly |
| Dasigi et al. (2021), QASPER | Question answering over research papers; 5,049 questions across 1,585 NLP papers, with answers and supporting evidence | QA and evidence-selection tasks; official card reports F1-based tasks and Longformer baselines | Strong fit for scientific-paper QA and evidence extraction in NLP | Measures paper comprehension/QA, not research-gap novelty or quality |
| Thakur et al. (2021), BEIR | Heterogeneous zero-shot IR benchmark and common evaluation framework | Multiple datasets and retrieval metrics; each underlying dataset has its own terms | Useful framework for testing retrieval baselines and generalization | BEIR toolkit license does not grant a blanket license to every wrapped dataset; select per-dataset only after rights review |
| Peng et al. (2024; journal version 2025), Graph Retrieval-Augmented Generation: A Survey | Organizes graph-based RAG into graph-based indexing, graph-guided retrieval and graph-enhanced generation | Survey of GraphRAG methods, tasks and evaluation | Supports rationale for comparing vector-only, graph, and hybrid paths | Graph use is established; measure when graph context helps rather than assume it always helps |
| Han et al. (2024; revised 2025), Retrieval-Augmented Generation with Graphs (GraphRAG) | Survey of graph-enhanced RAG components, query processing, retrieval, organization, generation and data sources | Survey and taxonomy | Provides a broad architecture view of GraphRAG design choices | Not an empirical validation of DiscoveryAI's implementation |
| Es et al. (2024), RAGAs: Automated Evaluation of Retrieval Augmented Generation | Reference-free evaluation of retrieval relevance, faithfulness and answer quality | LLM-based metrics without requiring gold answer labels for common metrics | Useful inspiration for automated proxy checks in a no-new-annotator student project | Automated judge scores are proxies and can be biased; they do not replace ground truth or expert assessment |
| Saad-Falcon et al. (2023), ARES | Automated RAG evaluation for context relevance, answer faithfulness and answer relevance | Synthetic training data plus a small human-annotated calibration set | Helps distinguish automated evaluation from human-calibrated evaluation | ARES's published approach still uses some human labels; DiscoveryAI will not claim equivalent calibrated reliability without them |

## 3. What is and is not novel

### Established prior art
The following are established ideas and must not be claimed as inventions by this project:
- literature-based discovery and candidate hypothesis generation;
- semantic/vector retrieval and RAG;
- graph-based retrieval and GraphRAG;
- automated RAG evaluation metrics;
- scientific paper QA and evidence selection;
- corpus-bounded trend analysis and ranking.

### Defensible student-project contribution
The defensible contribution is an integrated, reproducible software workflow that:
1. is scoped specifically to NLP/language-model literature;
2. combines vector, graph and hybrid retrieval in comparable configurations;
3. preserves paper/document/chunk provenance through candidate opportunity generation;
4. adds explicit uncertainty, contradiction handling and critic/ablation paths;
5. packages the process in a usable dashboard with reproducible run metadata;
6. evaluates established component tasks on compatible public benchmarks and separately reports workflow-level proxy checks.

This is an engineering and evaluation contribution, not a claim of a new general-purpose discovery algorithm. Whether the integration yields a measurable improvement is an open empirical question.

## 4. Limitations of this review

- This is a targeted initial review, not a PRISMA-compliant exhaustive systematic review.
- Search coverage is limited to the queries and sources above.
- The GraphRAG literature evolves quickly; this review does not cover every recent method.
- A full novelty claim requires a later, broader, dated search and direct comparison with the closest implementations.
- No paper was treated as fully read solely from its abstract. The table summarizes the cited works' stated scope and official dataset/project documentation.

## 5. Project implications

- Use QASPER for scientific paper QA/evidence-selection task evaluation, subject to the dataset restrictions in the benchmark register.
- Keep research-gap generation quality as an exploratory capability with automated structural/traceability proxies only.
- Compare component configurations under matched settings; do not assume graph/hybrid methods outperform simpler retrieval.
- Include RAGAS-inspired metrics only as explicitly labelled automated proxies, and report the judge model/prompt and its limitations.
- Report all negative results and failure cases.
