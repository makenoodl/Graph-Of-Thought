from got.domain.model.graph import Graph
from got.domain.model.value_objects import NodeType, RelationType, Confidence
from got.domain.ops import AddNode, AddEdge
from got.application.use_cases.analyze_reasoning import AnalyzeReasoningUseCase

def build_demo_graph() -> tuple[Graph, str]:
    graph = Graph()
    add_node = AddNode()
    add_edge = AddEdge()

    ev_goal = add_node.execute(graph, "I want to play basketball", NodeType.GOAL, Confidence(0.3))
    goal_id = ev_goal.node_id

    ev_sol = add_node.execute(graph, "I have a basketball", NodeType.SOLUTION, Confidence(0.2))
    sol_id = ev_sol.node_id

    ev_c1 = add_node.execute(graph, "I love basketball", NodeType.CONSTRAINT, Confidence(0.8))
    c1_id = ev_c1.node_id

    ev_c2 = add_node.execute(graph, "I love sports", NodeType.CONSTRAINT, Confidence(0.8))
    c2_id = ev_c2.node_id

    add_edge.execute(graph, goal_id, sol_id, RelationType.REQUIRES)
    add_edge.execute(graph, sol_id, c1_id, RelationType.DEPENDS_ON)
    add_edge.execute(graph, c1_id, c2_id, RelationType.CONTRADICTS)

    return graph, goal_id

def main() -> None:
    graph, goal_id = build_demo_graph()

    uc = AnalyzeReasoningUseCase()
    result = uc.execute(graph, starting_node_ids=[goal_id], propagate_causal=False)

    print("=== VALIDATION ===")
    print("is_valid:", result.validation.is_valid)
    print("violations:", result.validation.violations)
    print("warnings:", result.validation.warnings)

    print("\n=== ANALYSIS SUMMARY ===")
    print("contradiction_count:", result.summary.contradiction_count)
    print("blocked_paths:", result.summary.blocked_paths)
    print("viable_paths:", result.summary.viable_paths)
    print("recommendation:", result.summary.recommendation)

if __name__ == "__main__":
    main()