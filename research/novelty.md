# DiscoveryAI — Research Novelty and Contributions

## 1. Purpose

The purpose of this document is to define the proposed research novelty, candidate scientific contributions, and research hypotheses for DiscoveryAI.

The objective is not to claim that the individual technologies used by DiscoveryAI are new. Retrieval-Augmented Generation, knowledge graphs, GraphRAG, scientific trend analysis, and LLM-based hypothesis generation are already active research areas.

Instead, this document defines the specific research problem and proposed integration that DiscoveryAI will investigate experimentally.

---

# 2. Novelty Principle

DiscoveryAI does not claim novelty merely from combining popular technologies.

The proposed research novelty is centered on:

> Evidence-grounded research opportunity discovery from scientific literature through the integration of scientific knowledge representation, hybrid retrieval, structured gap detection, temporal analysis, contradictory evidence validation, and opportunity assessment.

The novelty claim should remain a research hypothesis until validated through a broader literature review and experimental comparison.

---

# 3. Limitations Identified from Existing Research

The Day 2 literature review identified several limitations relevant to research opportunity discovery.

## 3.1 Retrieval Limitation

RAG systems can retrieve relevant evidence, but retrieval alone does not establish whether a research opportunity exists.

## 3.2 Structural Reasoning Limitation

Text retrieval does not explicitly represent relationships among methods, datasets, problems, experiments, metrics, and applications.

## 3.3 Research Gap Limitation

Existing retrieval and recommendation systems do not inherently classify and validate different types of research gaps.

## 3.4 Evidence Validation Limitation

A generated research gap can be incorrect if contradictory or more recent evidence is not considered.

## 3.5 Temporal Limitation

Static literature analysis can miss changes in research activity, emerging topics, and evolving research directions.

## 3.6 Hypothesis Validation Limitation

LLM-generated research ideas may be unsupported, non-novel, difficult to test, or already investigated.

---

# 4. Proposed DiscoveryAI Novelty

DiscoveryAI proposes an evidence-grounded research opportunity discovery pipeline:

```text
Scientific Documents
        ↓
Scientific Information Extraction
        ↓
Knowledge Graph + Vector Index
        ↓
Hybrid Retrieval
        ↓
Research Landscape Analysis
        ↓
Candidate Gap Detection
        ↓
Supporting Evidence
        ↓
Contradictory Evidence
        ↓
Temporal Validation
        ↓
Opportunity Assessment
        ↓
Hypothesis Generation
        ↓
Experiment Proposal
```

The central research question is whether this integrated pipeline can identify useful and evidence-supported research opportunities more reliably than simpler baselines.

---

# 5. Proposed Research Contributions

## Contribution 1 — Scientific Research Opportunity Graph

DiscoveryAI proposes extending scientific knowledge representation beyond papers, authors, methods, and datasets to include:

```text
Paper
Author
Institution
Topic
Method
Dataset
Problem
Application
Metric
Experiment
Domain
ResearchGap
Evidence
Hypothesis
ResearchOpportunity
```

The graph will represent relationships such as:

```text
Paper ──USES──> Method
Paper ──EVALUATED_ON──> Dataset
Paper ──ADDRESSES──> Problem
Paper ──USES_METRIC──> Metric
Paper ──APPLIED_TO──> Application
Paper ──CITES──> Paper
Paper ──MENTIONS_LIMITATION──> ResearchGap
Paper ──PROPOSES_FUTURE_WORK──> ResearchGap
ResearchGap ──SUPPORTED_BY──> Evidence
ResearchGap ──CHALLENGED_BY──> Evidence
ResearchGap ──GENERATES──> Hypothesis
```

The purpose is to provide a structured representation that can support reasoning over research opportunities.

---

# 6. Evidence-Grounded Research Gap Detection

DiscoveryAI will treat research-gap detection as an evidence-analysis problem rather than simple text generation.

Candidate workflow:

```text
Candidate Gap
      ↓
Retrieve Supporting Evidence
      ↓
Retrieve Contradictory Evidence
      ↓
Check Temporal Evidence
      ↓
Assess Corpus Coverage
      ↓
Estimate Confidence
```

The system must not convert absence of retrieved evidence into a universal statement.

Incorrect:

> Nobody has researched this.

Preferred:

> No relevant evidence was identified within the indexed corpus and search scope.

---

# 7. Multi-Type Research Gap Taxonomy

DiscoveryAI will investigate multiple gap types:

```text
Research Gap
├── Topic Gap
├── Dataset Gap
├── Benchmark Gap
├── Experiment Gap
├── Evaluation Gap
├── Application Gap
└── Interdisciplinary Gap
```

This allows the system to distinguish between different forms of underexplored research.

---

# 8. Temporal Research Opportunity Analysis

Research opportunities will be analyzed using temporal information.

Potential signals include:

* Publication frequency
* Topic growth
* Method adoption
* Dataset usage
* Citation trends
* Research concentration
* Research stagnation
* Emerging topics

The system will not assume:

```text
Low publication count = Research Gap
```

or:

```text
High publication growth = Research Opportunity
```

Temporal signals will instead be combined with structural and evidence-based analysis.

---

# 9. Explainable Research Opportunity Assessment

Each candidate opportunity should have an evidence chain:

```text
Research Opportunity
        ↓
Reason for Identification
        ↓
Supporting Evidence
        ↓
Contradictory Evidence
        ↓
Research Density
        ↓
Temporal Evidence
        ↓
Missing Experiment / Dataset / Evaluation
        ↓
Confidence
        ↓
Potential Hypothesis
        ↓
Experiment Proposal
```

This is intended to make the system auditable and allow researchers to challenge individual reasoning steps.

---

# 10. Candidate Research Hypotheses

## H1 — Hybrid Retrieval

Hybrid vector and graph retrieval can improve evidence retrieval for research-gap questions compared with vector-only retrieval.

Potential evaluation:

* Recall@K
* Precision@K
* MRR
* nDCG

---

## H2 — Scientific Structural Reasoning

Explicit representation of method-dataset-problem-experiment relationships can improve identification of candidate research gaps compared with text-only retrieval.

Potential comparison:

```text
LLM-only
Vector RAG
GraphRAG
Hybrid DiscoveryAI
```

---

## H3 — Contradictory Evidence Validation

Explicit retrieval and analysis of contradictory evidence can reduce unsupported research-gap claims compared with systems that do not perform contradiction checking.

Potential evaluation:

* Unsupported claim rate
* Evidence coverage
* Contradiction detection accuracy
* Expert assessment

---

## H4 — Temporal Reasoning

Incorporating temporal research activity can improve identification of emerging research opportunities compared with static literature analysis.

Potential evaluation:

* Emerging-topic detection
* Opportunity relevance
* Temporal prediction error
* Expert evaluation

---

## H5 — End-to-End Opportunity Discovery

An integrated evidence-grounded research opportunity discovery pipeline can produce opportunities that experts rate as more evidence-supported, relevant, novel, and feasible than an LLM-only baseline.

This hypothesis must be tested experimentally and should not be treated as an established result.

---

# 11. Baseline Systems

DiscoveryAI should be evaluated against progressively stronger baselines:

```text
Baseline 1
LLM-only

Baseline 2
Vector RAG

Baseline 3
GraphRAG

Baseline 4
Hybrid RAG

Proposed System
DiscoveryAI
```

The exact implementation and evaluation protocol will be defined in later phases.

---

# 12. Ablation Studies

The full DiscoveryAI pipeline will eventually be compared against reduced versions:

```text
Full DiscoveryAI

DiscoveryAI - Knowledge Graph

DiscoveryAI - Vector Retrieval

DiscoveryAI - Temporal Analysis

DiscoveryAI - Evidence Validation

DiscoveryAI - Research Critic
```

The objective is to determine which components contribute materially to research-opportunity discovery performance.

---

# 13. Proposed Contribution Summary

| Contribution                          | Research Purpose                                                                                      |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Scientific Research Opportunity Graph | Represent scientific knowledge and opportunity-related structure                                      |
| Evidence-Grounded Gap Detection       | Identify candidate gaps with supporting evidence                                                      |
| Multi-Type Gap Taxonomy               | Distinguish topic, dataset, benchmark, experiment, evaluation, application and interdisciplinary gaps |
| Temporal Opportunity Analysis         | Incorporate evolution of scientific activity                                                          |
| Explainable Opportunity Assessment    | Provide evidence chains and confidence for candidate opportunities                                    |

---

# 14. What DiscoveryAI Does NOT Claim

DiscoveryAI does not claim:

* That RAG is a new technology.
* That knowledge graphs are a new technology.
* That GraphRAG is a new technology.
* That LLM hypothesis generation is a new technology.
* That research-gap detection has never been attempted.
* That the system can prove that nobody has researched a topic.
* That every low-density research area represents a valuable opportunity.
* That generated hypotheses are automatically scientifically valid.

The project instead investigates whether the proposed integrated framework can provide measurable improvements in evidence-grounded research opportunity discovery.

---

# 15. Research Position

The current research position is:

> Existing research provides many of the individual components required for AI-assisted scientific discovery, but DiscoveryAI investigates whether these components can be integrated into an evidence-grounded framework that detects, validates, explains, and evaluates research opportunities across scientific literature.

This position remains subject to further literature review and experimental validation.

---

# 16. Day 3 Completion Criteria

Day 3 is complete when:

* [ ] Existing limitations are explicitly documented.
* [ ] DiscoveryAI's proposed novelty is clearly stated.
* [ ] 3–5 candidate research contributions are defined.
* [ ] Research hypotheses H1–H5 are defined.
* [ ] Baselines are identified.
* [ ] Ablation strategy is identified.
* [ ] Novelty claims are separated from hypotheses.
* [ ] `research/novelty.md` is created.
* [ ] The document is committed to GitHub.

---

# 17. Final Research Question for Day 3

The key question is no longer:

> Can we build an AI system that finds papers?

It is:

> Can an evidence-grounded combination of scientific knowledge representation, hybrid retrieval, gap detection, temporal reasoning, and evidence validation reliably identify research opportunities that are useful, explainable, and experimentally supported?
