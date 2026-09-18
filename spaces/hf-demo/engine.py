"""Deterministic demo graphs for the Hub Space (no LLM)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
for _candidate in (_HERE, _HERE.parent.parent):
    if (_candidate / "got" / "domain").is_dir():
        sys.path.insert(0, str(_candidate))
        break

from got.application.schemas.graph import GraphDTO  # noqa: E402
from got.application.use_cases.analyze_reasoning import AnalyzeReasoningUseCase  # noqa: E402
from got.domain.model.graph import Graph  # noqa: E402
from got.domain.model.value_objects import Confidence, NodeType, RelationType  # noqa: E402
from got.domain.ops import AddEdge, AddNode  # noqa: E402

SCENARIO_CONTRADICTION = "Contradiction (basketball sandbox)"
SCENARIO_EPISTEMIC = "Epistemic propagation (rain → wet grass)"


def build_contradiction_graph() -> tuple[Graph, str]:
    """Same topology as examples/simple_sandbox.py."""
    graph = Graph()
    add_node = AddNode()
    add_edge = AddEdge()

    goal_id = add_node.execute(
        graph, "I want to play basketball", NodeType.GOAL, Confidence(0.3)
    ).node_id
    sol_id = add_node.execute(
        graph, "I have a basketball", NodeType.SOLUTION, Confidence(0.2)
    ).node_id
    c1_id = add_node.execute(
        graph, "I love basketball", NodeType.CONSTRAINT, Confidence(0.8)
    ).node_id
    c2_id = add_node.execute(
        graph, "I love sports", NodeType.CONSTRAINT, Confidence(0.8)
    ).node_id

    add_edge.execute(graph, goal_id, sol_id, RelationType.REQUIRES)
    add_edge.execute(graph, sol_id, c1_id, RelationType.DEPENDS_ON)
    add_edge.execute(graph, c1_id, c2_id, RelationType.CONTRADICTS)
    return graph, goal_id


def build_epistemic_graph() -> tuple[Graph, str]:
    """Same topology as got/tests/test_validation_propagation_flow.py."""
    graph = Graph()
    add_node = AddNode()
    add_edge = AddEdge()

    rain_id = add_node.execute(graph, "Rain", NodeType.FACT, Confidence(0.9)).node_id
    grass_id = add_node.execute(
        graph, "Wet grass", NodeType.CONCEPT, Confidence(0.5)
    ).node_id
    add_edge.execute(graph, rain_id, grass_id, RelationType.SUPPORTS)
    return graph, rain_id


def _concept(graph: Graph, node_id: str) -> str:
    node = graph.get_node(node_id)
    return node.concept if node is not None else node_id


def _humanize(text: str, graph: Graph) -> str:
    for node_id, node in graph.nodes.items():
        text = text.replace(node_id, node.concept)
    return text


def graph_to_mermaid(graph: Graph) -> str:
    aliases: dict[str, str] = {}
    lines = ["flowchart LR"]
    for index, node in enumerate(graph.nodes.values()):
        alias = f"n{index}"
        aliases[node.id] = alias
        label = f"{node.concept}<br/>{node.node_type.value} · {float(node.confidence):.2f}"
        safe = label.replace('"', "'")
        lines.append(f'    {alias}["{safe}"]')
    for edge in graph.edges:
        src = aliases[edge.source_id]
        dst = aliases[edge.target_id]
        rel = edge.relation_type.value
        if edge.relation_type == RelationType.CONTRADICTS:
            lines.append(f"    {src} -.->|{rel}| {dst}")
        else:
            lines.append(f"    {src} -->|{rel}| {dst}")
    return "\n".join(lines)


def run_scenario(scenario: str, propagate_causal: bool) -> tuple[str, list, list, str, str]:
    payload = analyze_scenario(scenario, propagate_causal)
    return (
        payload["status_markdown"],
        payload["nodes"],
        payload["edges"],
        payload["mermaid"],
        payload["json"],
    )


def analyze_scenario(scenario: str, propagate_causal: bool = False) -> dict:
    if scenario == SCENARIO_EPISTEMIC:
        graph, start_id = build_epistemic_graph()
    else:
        graph, start_id = build_contradiction_graph()

    before = {
        node.id: float(node.confidence) for node in graph.nodes.values()
    }
    result = AnalyzeReasoningUseCase().execute(
        graph,
        starting_node_ids=[start_id],
        propagate_causal=propagate_causal,
    )

    clusters: list[str] = []
    component_count = 0
    if result.analysis is not None:
        clusters = [
            _humanize(cluster.description, result.graph)
            for cluster in result.analysis.contradiction_clusters
        ]
        if result.analysis.connectivity is not None:
            component_count = result.analysis.connectivity.component_count

    findings = [
        _humanize(message, result.graph) for message in result.validation.violations
    ]
    for cluster in clusters:
        if cluster not in findings:
            findings.append(cluster)

    status_markdown = "\n".join(
        [
            f"**is_valid:** {result.validation.is_valid}",
            f"**findings:** {findings or 'none'}",
            f"**contradiction_count:** {result.summary.contradiction_count}",
            f"**blocked_paths / viable_paths:** {result.summary.blocked_paths} / {result.summary.viable_paths} (always 0 in v0.1)",
            f"**recommendation:** {result.summary.recommendation}",
        ]
    )
    nodes_rows = [
        [
            node.concept,
            node.node_type.value,
            f"{before.get(node.id, float(node.confidence)):.2f}",
            f"{float(node.confidence):.2f}",
        ]
        for node in result.graph.nodes.values()
    ]
    edges_rows = [
        [
            _concept(result.graph, edge.source_id),
            edge.relation_type.value,
            _concept(result.graph, edge.target_id),
        ]
        for edge in result.graph.edges
    ]
    graph_json = GraphDTO.from_domain(result.graph).model_dump(mode="json")
    return {
        "title": scenario,
        "is_valid": result.validation.is_valid,
        "violations": findings,
        "warnings": [
            _humanize(message, result.graph) for message in result.validation.warnings
        ],
        "findings": findings,
        "contradiction_count": result.summary.contradiction_count,
        "clusters": clusters,
        "component_count": component_count,
        "blocked_paths": result.summary.blocked_paths,
        "viable_paths": result.summary.viable_paths,
        "recommendation": result.summary.recommendation,
        "status_markdown": status_markdown,
        "nodes": nodes_rows,
        "edges": edges_rows,
        "mermaid": graph_to_mermaid(result.graph),
        "json": json.dumps(graph_json, indent=2, ensure_ascii=False),
    }
