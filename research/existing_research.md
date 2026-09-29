# DiscoveryAI — Existing Research Review

## 1. Purpose

The purpose of this review is to understand existing approaches related to DiscoveryAI and identify the capabilities and limitations that motivate the proposed research direction.

The review focuses on:

1. Retrieval-Augmented Generation (RAG)
2. GraphRAG
3. Scientific Knowledge Graphs
4. Scientific Paper Recommendation Systems
5. Scientific Research Trend Detection
6. Automated Hypothesis Generation

The objective is not to claim that existing approaches are ineffective. Instead, the goal is to identify which research capabilities are already addressed and which capabilities remain insufficiently integrated for evidence-grounded research opportunity discovery.

---

# 2. Retrieval-Augmented Generation

## 2.1 Core Idea

Retrieval-Augmented Generation combines:

```text
User Query
    ↓
Retriever
    ↓
Relevant Documents / Passages
    ↓
Language Model
    ↓
Generated Answer
```

The original RAG work by Lewis et al. introduced a framework combining parametric language-model memory with non-parametric external memory accessed through a dense retriever. The work demonstrated benefits on knowledge-intensive NLP tasks and emphasized issues such as updating knowledge and providing provenance.

Source:
Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", 2020.

## 2.2 Strengths

RAG provides:

* External knowledge retrieval
* Better access to information not stored in model parameters
* Ability to work with private or newly indexed corpora
* Source-oriented generation
* Knowledge updating without retraining the entire model

## 2.3 Limitations Relevant to DiscoveryAI

Standard RAG primarily operates over retrieved textual passages.

This creates several challenges for scientific opportunity discovery:

* It may retrieve relevant passages without understanding the larger research structure.
* Relationships between methods, datasets, problems and experiments are not explicitly represented.
* Global corpus-level questions are difficult.
* Missing relationships are not directly represented.
* Retrieval relevance does not automatically imply research novelty.
* A retrieved paper collection does not itself identify a research gap.
* Contradictory evidence requires explicit analysis.
* Temporal evolution requires additional processing.

Therefore:

```text
RAG
=
Evidence Retrieval + Generation
```

but DiscoveryAI requires:

```text
Evidence Retrieval
        +
Scientific Structure
        +
Temporal Reasoning
        +
Gap Detection
        +
Evidence Validation
        +
Opportunity Analysis
```

---

# 3. GraphRAG

## 3.1 Core Idea

GraphRAG extends retrieval by representing information from documents through graph structures.

Microsoft Research's GraphRAG work constructs an entity knowledge graph and community summaries from source documents. It targets questions requiring corpus-level or global understanding, where conventional retrieval may not be sufficient.

Source:

Edge et al., "From Local to Global: A Graph RAG Approach to Query-Focused Summarization", 2024.

## 3.2 Basic Architecture

```text
Scientific Documents
        ↓
Entity Extraction
        ↓
Relationship Extraction
        ↓
Knowledge Graph
        ↓
Graph Communities
        ↓
Community Summaries
        ↓
Query
        ↓
Graph Retrieval
        ↓
LLM
        ↓
Answer
```

## 3.3 Strengths

GraphRAG provides:

* Structured relationships
* Multi-entity reasoning
* Multi-hop retrieval
* Better corpus-level understanding
* Community-level organization
* More explicit connections between pieces of information

The GraphRAG paper reports improvements over naive RAG for certain global sensemaking questions, particularly in comprehensiveness and diversity.

## 3.4 Limitations Relevant to DiscoveryAI

GraphRAG itself is primarily a retrieval and reasoning architecture.

It does not automatically solve:

* Research gap taxonomy
* Missing dataset detection
* Missing experiment detection
* Missing evaluation detection
* Contradictory research evidence analysis
* Research opportunity validation
* Scientific novelty estimation
* Research opportunity scoring
* Testable hypothesis generation
* Experimental planning

Therefore DiscoveryAI should use GraphRAG as an infrastructure component rather than treating GraphRAG itself as the final research-discovery solution.

---

# 4. Scientific Knowledge Graphs

## 4.1 Core Idea

A scientific knowledge graph represents scientific information as entities and relationships.

Example:

```text
Paper
  │
  ├── USES → Method
  │
  ├── EVALUATED_ON → Dataset
  │
  ├── ADDRESSES → Problem
  │
  ├── USES_METRIC → Metric
  │
  ├── APPLIED_TO → Application
  │
  ├── AUTHORED_BY → Author
  │
  └── CITES → Paper
```

Scientific information extraction research has demonstrated extraction of entities, relations and coreference information from scientific articles, including work such as SciERC/SciIE.

Source:

Luan et al., "Multi-Task Identification of Entities, Relations, and Coreference for Scientific Knowledge Graph Construction", 2018.

## 4.2 Strengths

Scientific knowledge graphs can support:

* Entity-level representation
* Relationship reasoning
* Citation analysis
* Method-dataset relationships
* Research landscape analysis
* Multi-hop reasoning
* Structured scientific search

## 4.3 Limitations

A knowledge graph is primarily a representation.

A graph containing:

```text
Method A → Dataset A
Method B → Dataset B
```

does not automatically prove:

```text
Method A → Dataset B
```

is a meaningful research opportunity.

The system still needs:

* Evidence validation
* Domain understanding
* Temporal analysis
* Research-density analysis
* Contradiction detection
* Opportunity classification
* Human/expert evaluation

This distinction is central to DiscoveryAI.

---

# 5. Scientific Paper Recommendation Systems

## 5.1 Core Idea

Scientific paper recommendation systems recommend papers relevant to a researcher's interests.

A survey by Bai et al. categorizes scientific paper recommendation approaches into content-based, collaborative filtering, graph-based and hybrid approaches. The survey also identifies issues including cold start, sparsity, scalability, privacy, serendipity and unified scholarly-data standards.

Source:

Bai et al., "Scientific Paper Recommendation: A Survey", 2020.

## 5.2 Typical Pipeline

```text
Researcher Profile / Query
        ↓
Candidate Papers
        ↓
Similarity / Recommendation Model
        ↓
Ranked Papers
```

## 5.3 Strengths

Recommendation systems can help researchers:

* Find relevant papers
* Discover related work
* Navigate large literature collections
* Personalize literature discovery

## 5.4 Limitation for DiscoveryAI

The main output is generally:

```text
"What papers should I read?"
```

DiscoveryAI asks a different question:

```text
"What scientifically meaningful opportunities appear insufficiently explored?"
```

Therefore:

```text
Paper Recommendation
        ≠
Research Opportunity Discovery
```

Recommendation can become one input to DiscoveryAI, but it is not the final objective.

---

# 6. Scientific Research Trend Detection

## 6.1 Core Idea

Research trend analysis studies how topics, keywords, methods or publication patterns evolve over time.

Recent work such as BERTrend investigates emerging trends and weak signals in evolving text collections using neural topic modeling and temporal topic-popularity measurements.

Source:

Boutaleb et al., "BERTrend: Neural Topic Modeling for Emerging Trends Detection", 2024.

## 6.2 Typical Representation

```text
Year
 ↓
Topic Frequency
 ↓
Growth Rate
 ↓
Topic Momentum
 ↓
Emerging / Stable / Declining
```

## 6.3 Strengths

Trend analysis can identify:

* Fast-growing topics
* Emerging research areas
* Declining topics
* Weak signals
* Topic evolution

## 6.4 Limitations

A rapidly growing topic is not necessarily a research gap.

For example:

```text
High publication growth
        ≠
Missing research opportunity
```

Similarly:

```text
Low publication count
        ≠
Important research gap
```

Low research density could be caused by:

* Low scientific importance
* High technical difficulty
* Lack of data
* Lack of funding
* Immature technology
* Already-solved problems
* Limited applicability

Therefore temporal analysis needs to be combined with scientific evidence and contextual reasoning.

---

# 7. Automated Hypothesis Generation

## 7.1 Core Idea

Automated hypothesis generation attempts to assist researchers in proposing potentially testable scientific hypotheses from existing knowledge.

Recent surveys of LLM-based hypothesis generation cover approaches ranging from prompting-based methods to structured frameworks and discuss evaluation, novelty, reasoning, multimodal systems and human-AI collaboration.

Source:

Alkan et al., "A Survey on Hypothesis Generation for Scientific Discovery in the Era of Large Language Models", 2025.

## 7.2 Basic Pipeline

```text
Existing Knowledge
        ↓
Knowledge Combination
        ↓
Potential Relationship
        ↓
Hypothesis
        ↓
Validation / Experiment
```

## 7.3 Strengths

LLM-based approaches can assist with:

* Knowledge synthesis
* Cross-domain combinations
* Hypothesis drafting
* Structured reasoning
* Scientific idea generation

## 7.4 Limitations

Generated hypotheses can be:

* Unsupported
* Non-novel
* Difficult to test
* Too broad
* Scientifically implausible
* Already investigated
* Missing appropriate datasets or baselines

Therefore hypothesis generation should happen **after evidence and gap analysis**, rather than being treated as unconstrained idea generation.

---

# 8. Comparative Analysis

| Approach              | Main Purpose                                    | Strong Capability               | Important Limitation for DiscoveryAI                |
| --------------------- | ----------------------------------------------- | ------------------------------- | --------------------------------------------------- |
| RAG                   | Retrieve knowledge and generate answers         | Evidence retrieval              | Does not inherently detect research gaps            |
| GraphRAG              | Graph-based retrieval and corpus reasoning      | Multi-hop/global reasoning      | Not a complete opportunity-discovery framework      |
| Scientific KG         | Represent scientific entities and relationships | Structured scientific knowledge | Representation alone does not establish opportunity |
| Paper Recommendation  | Recommend relevant literature                   | Literature discovery            | Optimizes paper relevance, not research opportunity |
| Trend Detection       | Detect temporal patterns                        | Emerging-topic detection        | Growth does not necessarily indicate a gap          |
| Hypothesis Generation | Generate potential scientific hypotheses        | Idea synthesis                  | Hypotheses require evidence and validation          |

---

# 9. Research Gap Identified from Existing Approaches

The reviewed approaches address different parts of the scientific discovery workflow.

```text
RAG
 ↓
Retrieve Evidence

GraphRAG
 ↓
Reason Over Structured Relationships

Scientific Knowledge Graph
 ↓
Represent Scientific Structure

Paper Recommendation
 ↓
Find Relevant Literature

Trend Detection
 ↓
Analyze Temporal Evolution

Hypothesis Generation
 ↓
Generate Potential Scientific Ideas
```

However, DiscoveryAI proposes integrating these capabilities into a research-opportunity workflow:

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
Gap Candidate Detection
        ↓
Supporting Evidence
        ↓
Contradictory Evidence
        ↓
Temporal Validation
        ↓
Research Opportunity Assessment
        ↓
Hypothesis
        ↓
Experiment Proposal
```

The important research question is therefore not simply whether each individual technology works.

The question is whether their combination can produce **evidence-grounded and experimentally validated research opportunity discovery**.

---

# 10. Initial Limitations to Investigate Experimentally

The following should be treated as research questions rather than predetermined conclusions:

### L1 — Retrieval limitation

Can hybrid vector + graph retrieval improve evidence retrieval for research-gap questions compared with vector-only retrieval?

### L2 — Structural reasoning limitation

Can explicit scientific relationships improve reasoning over method-dataset-problem combinations?

### L3 — Gap detection limitation

Can a structured gap detector identify missing experiments, datasets and evaluations more reliably than an LLM-only baseline?

### L4 — False-gap limitation

Can contradictory-evidence retrieval reduce false research-gap claims?

### L5 — Temporal limitation

Can temporal research analysis improve identification of emerging opportunities compared with static corpus analysis?

### L6 — Hypothesis limitation

Can evidence-grounded hypothesis generation produce more scientifically useful hypotheses than unconstrained LLM generation?

### L7 — End-to-end limitation

Can the complete DiscoveryAI pipeline produce research opportunities that expert researchers consider novel, relevant, feasible and evidence-supported?

---

# 11. Key Insight for DiscoveryAI

The existing literature suggests that the individual components required for DiscoveryAI already exist in different research areas.

The potential research contribution is therefore unlikely to be simply:

> "Build another RAG system."

or:

> "Build another knowledge graph."

Instead, the research direction is the integration and evaluation of:

```text
Retrieval
+
Scientific Knowledge Representation
+
Graph Reasoning
+
Temporal Analysis
+
Gap Detection
+
Evidence Validation
+
Opportunity Assessment
+
Hypothesis Generation
+
Experiment Planning
```

The scientific validity of this integration must be established experimentally.

---

# 12. Important Research Principle

DiscoveryAI must not convert absence of retrieved evidence into a universal claim.

Incorrect:

> "Nobody has researched this."

Preferred:

> "No relevant evidence was identified within the indexed corpus and search scope."

This distinction is essential because incomplete indexing, retrieval failures, terminology differences and inaccessible literature can create false gaps.

---

# 13. Day 2 Conclusion

Existing research provides strong foundations for the major components of DiscoveryAI:

* RAG provides external evidence retrieval.
* GraphRAG provides graph-based and corpus-level reasoning.
* Scientific knowledge graphs provide structured scientific relationships.
* Paper recommendation systems provide literature discovery.
* Trend analysis provides temporal research intelligence.
* Automated hypothesis generation provides scientific idea synthesis.

The remaining challenge for DiscoveryAI is to investigate whether these capabilities can be combined into a reliable, evidence-grounded system for identifying and validating research opportunities.

This motivates the next research phase:

```text
Existing Research
        ↓
Identify Limitations
        ↓
Define Novelty
        ↓
Formulate Research Contributions
        ↓
Test Experimentally
```
