"""Test flow: build graph -> validate -> propagate -> assert."""
from got.domain.model.graph import Graph
from got.domain.model.value_objects import Confidence, NodeType, RelationType
from got.domain.ops import AddNode, AddEdge
from got.domain.reasoning.validation import Validator
from got.domain.reasoning.propagation import PropagationService


def test_validate_then_propagate_epistemic():
    graph = Graph()
    add_node = AddNode()
    add_edge = AddEdge()

    ev_a = add_node.execute(graph, "Rain", NodeType.FACT, Confidence(0.9))
    a_id = ev_a.node_id
    ev_b = add_node.execute(graph, "Wet grass", NodeType.CONCEPT, Confidence(0.5))
    b_id = ev_b.node_id

    add_edge.execute(graph, a_id, b_id, RelationType.SUPPORTS)

    validator = Validator()
    result = validator.validate(graph)
    assert result.is_valid or len(result.violations) == 0

    node_b_before = graph.get_node(b_id)
    assert node_b_before is not None
    conf_before = float(node_b_before.confidence)

    PropagationService().propagate_epistemic(graph, [a_id])

    node_b_after = graph.get_node(b_id)
    assert node_b_after is not None
    conf_after = float(node_b_after.confidence)
    assert conf_after >= conf_before
    assert conf_after > 0.5