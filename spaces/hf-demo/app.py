"""Hugging Face Space UI: optional local Gradio (Pro required to host on the Hub)."""

from __future__ import annotations

import gradio as gr

from engine import SCENARIO_CONTRADICTION, SCENARIO_EPISTEMIC, run_scenario


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Graph-of-Thought") as demo:
        gr.Markdown(
            """
# Graph-of-Thought — deterministic engine

This UI runs an **in-memory** graph: validation, confidence propagation,
contradiction analysis. **No LLM is called.**

Complementary to [Graph of Thoughts (Besta et al.)](https://huggingface.co/papers/2308.09687)
(prompt-time thought graphs): here the graph is **inspectable state**,
not a prompting topology.

Code: [makenoodl/Graph-Of-Thought](https://github.com/makenoodl/Graph-Of-Thought)
"""
        )
        with gr.Row():
            scenario = gr.Dropdown(
                choices=[SCENARIO_CONTRADICTION, SCENARIO_EPISTEMIC],
                value=SCENARIO_CONTRADICTION,
                label="Scenario",
            )
            propagate_causal = gr.Checkbox(
                value=False,
                label="Causal propagation (in addition to epistemic)",
            )
        run_btn = gr.Button("Run engine", variant="primary")
        status = gr.Markdown()
        with gr.Row():
            nodes = gr.Dataframe(
                headers=["concept", "type", "before", "after"],
                label="Nodes (confidence before → after)",
            )
            edges = gr.Dataframe(
                headers=["from", "relation", "to"],
                label="Relations",
            )
        mermaid = gr.Code(language="markdown", label="Mermaid")
        graph_json = gr.Code(language="json", label="GraphDTO JSON")
        run_btn.click(
            fn=run_scenario,
            inputs=[scenario, propagate_causal],
            outputs=[status, nodes, edges, mermaid, graph_json],
        )
        demo.load(
            fn=run_scenario,
            inputs=[scenario, propagate_causal],
            outputs=[status, nodes, edges, mermaid, graph_json],
        )
    return demo


demo = build_ui()

if __name__ == "__main__":
    demo.launch()
