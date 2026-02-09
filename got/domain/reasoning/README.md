## Structural Reasoning Engine (Phase 2)

### 1. Purpose

The Structural Reasoning Engine is the second phase of the Graph-of-Thought (GoT) system.

Its primary goal is to transform a static reasoning graph into an **active cognitive object** by providing:

- **Deterministic validation** of structural and epistemic coherence
- **Propagation** of epistemic and causal information across the graph
- **Analysis** of contradictions, connectivity, and critical reasoning paths

This layer is **strictly non-LLM**. It operates solely on the graph structure and its metadata, ensuring reproducibility, testability, and auditability.

---

### 2. Conceptual Foundations

The engine assumes the following core model (defined in the domain foundation layer):

- **Nodes**: concepts, hypotheses, facts, constraints, states
- **Edges**: typed relations (e.g. causal, epistemic, support, contradiction, dependency, refinement)
- **Graph**: the current reasoning state

In this setting:

- Reasoning is **not** a sequence of tokens.
- Reasoning is a **persistent graph** that can be inspected, revised, and audited.
- Any change in “thinking” must correspond to a **graph mutation**.

The Structural Reasoning Engine is responsible for checking and transforming this graph in a principled way.

---

### 3. Design Constraints

The engine is designed under the following constraints:

- **Deterministic**: same input graph → same output and diagnostics.
- **Non-LLM**: no probabilistic or opaque model calls.
- **Fully testable**: all operations are unit-testable on small synthetic graphs.
- **Explainable**: every validation, propagation, and analysis step is grounded in explicit rules over the graph.

These constraints distinguish this layer from typical Chain-of-Thought (CoT) or Tree-of-Thought (ToT) approaches, which are often opaque and non-reproducible.

---

### 4. Module Overview

The Structural Reasoning Engine is organized into three main modules:

1. **Validation**
2. **Propagation**
3. **Analysis**

Each module exposes a clear interface and can be tested independently.

---

### 5. Validation

#### 5.1 Objective

The Validation module answers the question:

> “Is this reasoning structurally and epistemically coherent?”

It does so by checking **invariants** on the graph structure, such as the absence of forbidden cycles or epistemic conflicts.

#### 5.2 Components

- **CausalValidator**
  - Detects **causal cycles** (e.g. A causes B, B causes C, C causes A).
  - Validates **temporal coherence**, when temporal ordering is encoded.

- **EpistemicValidator**
  - Identifies **belief conflicts**, such as nodes asserting incompatible propositions within the same epistemic context.
  - Checks compatibility of confidence levels, sources, and perspectives.

- **StructuralValidator**
  - Verifies **hierarchical consistency** (e.g. refinement, part-of relations).
  - Checks **transitivity** and other structural properties where applicable.

- **Validator Orchestrator** (`validator.py`)
  - Coordinates all validators.
  - Provides a high-level interface, e.g.:
    - `validate(graph) -> ValidationReport`

#### 5.3 Output

The Validation module returns a **ValidationReport** containing:

- A list of **violations** (type, location in the graph, explanation).
- Optionally, suggestions for remediation or affected subgraphs.

This report is a key artefact for auditing reasoning quality.

---

### 6. Propagation

#### 6.1 Objective

The Propagation module answers the question:

> “What propagates from what in this reasoning state?”

It defines how information such as **confidence**, **activation**, or **effects** propagates along edges, according to their types.

#### 6.2 Components

- **EpistemicPropagator**
  - Propagates **epistemic attributes** (e.g. confidence, belief strength) across relations such as support, contradiction, or dependency.
  - Applies deterministic aggregation rules (e.g. combination of supporting/conflicting evidence).

- **CausalPropagator**
  - Propagates **causal influence** along causal edges.
  - Allows reasoning such as: “If A holds, and A causes B, then B should be updated accordingly.”

- **Propagation Orchestrator** (`propagation.py`)
  - Coordinates propagation processes.
  - Exposes operations such as:
    - `propagate_epistemic(graph, starting_nodes) -> graph'`
    - `propagate_causal(graph, starting_nodes) -> graph'`

#### 6.3 Design Considerations

- Propagation rules are **explicit** and **configurable**, not learned or implicit.
- The propagation process is **terminating** and **order-independent** (or explicitly ordered), to preserve determinism.

---

### 7. Analysis

#### 7.1 Objective

The Analysis module answers questions such as:

- “Where are the contradictions?”
- “How is this reasoning graph structurally organized?”
- “What are the critical paths supporting a given conclusion?”

It provides higher-level insights over the graph, beyond local validation.

#### 7.2 Components

- **ContradictionDetector**
  - Identifies **minimal conflicting subgraphs** where nodes and relations are jointly inconsistent.
  - Can reuse information from the EpistemicValidator or perform dedicated pattern detection.

- **Connectivity Analysis**
  - Examines the **connectivity structure** of the graph (components, clusters, articulation points).
  - Helps understand whether reasoning is fragmented or well-integrated.

- **Critical Reasoning Paths**
  - Extracts **key support paths** for a target node (e.g. a conclusion).
  - Useful for explainability: “Why does the system consider this claim justified?”

#### 7.3 Outputs

The Analysis module produces:

- Sets of **subgraphs** (e.g. contradiction clusters, main reasoning chains).
- **Metrics** characterizing the graph (e.g. degree distributions, central nodes).
- Artefacts that can be surfaced to users or downstream systems for transparency.

---

### 8. Relevance for Contributors

From an academic and engineering standpoint, this layer is critical because:

1. It enforces a **clear separation of concerns**:
   - Language interpretation (LLM) vs. structural reasoning (this engine).
2. It provides a **deterministic reasoning core**:
   - Essential for reproducibility, debugging, and scientific evaluation.
3. It grounds reasoning in **explicit, inspectable rules**:
   - Violations, propagations, and analyses can all be traced back to graph-level operations.
4. It treats the graph as a **persistent cognitive state**:
   - Reasoning is not an ephemeral log of tokens but an evolving, updatable structure.

Contributors should approach this module as the **logical backbone** of the system. Any extension or modification must preserve:

- Determinism
- Testability
- Explicitness of rules
- Independence from LLM behavior

---

### 9. Contribution Guidelines (for this layer)

- **Do**:
  - Add new validators, propagators, or analyzers as separate, composable components.
  - Write small, focused tests on synthetic graphs.
  - Document invariants and propagation rules explicitly.

- **Do NOT**:
  - Introduce LLM calls or non-deterministic behavior.
  - Encode hidden heuristics that cannot be explained in terms of graph operations.
  - Depend on textual prompts or token-level reasoning in this layer.

The Structural Reasoning Engine is the place where reasoning becomes **computationally precise**. All contributions should reinforce this property.