"""Build a static Hub Space page from live engine runs."""

from __future__ import annotations

import html
from pathlib import Path

from engine import SCENARIO_CONTRADICTION, SCENARIO_EPISTEMIC, analyze_scenario

OUT = Path(__file__).resolve().parent / "index.html"


def _esc(value: object) -> str:
    return html.escape(str(value))


def _confidence_bar(value: str) -> str:
    try:
        pct = max(0, min(100, int(round(float(value) * 100))))
    except ValueError:
        pct = 0
    return (
        f'<div class="bar" title="{_esc(value)}">'
        f'<span style="width:{pct}%"></span>'
        f'<em>{_esc(value)}</em></div>'
    )


def _section(payload: dict, section_id: str, kicker: str, blurb: str) -> str:
    valid = payload["is_valid"]
    badge = "Valid" if valid else "Invalid"
    badge_class = "ok" if valid else "bad"
    findings = payload.get("findings") or payload.get("violations") or []
    finding_html = (
        "<ul class='findings'>"
        + "".join(f"<li>{_esc(item)}</li>" for item in findings)
        + "</ul>"
        if findings
        else "<p class='quiet'>No structural violations.</p>"
    )
    node_rows = []
    for concept, ntype, before, after in payload["nodes"]:
        changed = before != after
        delta = (
            f'<span class="delta">{"↑" if float(after) > float(before) else "↓"} '
            f"{_esc(before)} → {_esc(after)}</span>"
            if changed
            else f'<span class="quiet">{_esc(after)}</span>'
        )
        node_rows.append(
            "<tr>"
            f"<td>{_esc(concept)}</td>"
            f"<td><span class='chip'>{_esc(ntype)}</span></td>"
            f"<td>{_confidence_bar(after)}</td>"
            f"<td>{delta}</td>"
            "</tr>"
        )
    edge_rows = []
    for source, relation, target in payload["edges"]:
        cls = "rel-bad" if relation == "contradicts" else "rel"
        edge_rows.append(
            "<li>"
            f"<strong>{_esc(source)}</strong> "
            f"<span class='{cls}'>{_esc(relation)}</span> "
            f"<strong>{_esc(target)}</strong>"
            "</li>"
        )
    json_block = _esc(payload["json"])
    mermaid_src = _esc(payload["mermaid"])
    return f"""
<article class="panel" id="{_esc(section_id)}">
  <header class="panel-head">
    <div>
      <p class="kicker">{_esc(kicker)}</p>
      <h2>{_esc(payload['title'])}</h2>
      <p class="blurb">{_esc(blurb)}</p>
    </div>
    <span class="badge {badge_class}">{badge}</span>
  </header>
  <div class="metrics">
    <div><span>Contradictions</span><b>{_esc(payload['contradiction_count'])}</b></div>
    <div><span>Thoughts</span><b>{len(payload['nodes'])}</b></div>
    <div><span>Relations</span><b>{len(payload['edges'])}</b></div>
  </div>
  <div class="graph"><pre class="mermaid">{payload['mermaid']}</pre></div>
  <div class="split">
    <section>
      <h3>What the engine found</h3>
      {finding_html}
      <p class="note">{_esc(payload['recommendation'])}</p>
    </section>
    <section>
      <h3>Relations</h3>
      <ul class="rels">{''.join(edge_rows)}</ul>
    </section>
  </div>
  <h3>Confidence after propagation</h3>
  <table>
    <thead><tr><th>Thought</th><th>Type</th><th>Belief</th><th>Change</th></tr></thead>
    <tbody>{''.join(node_rows)}</tbody>
  </table>
  <details>
    <summary>Raw GraphDTO / Mermaid</summary>
    <pre><code>{json_block}</code></pre>
    <pre><code>{mermaid_src}</code></pre>
  </details>
</article>
"""


def build_html() -> str:
    contradiction = analyze_scenario(SCENARIO_CONTRADICTION, False)
    epistemic = analyze_scenario(SCENARIO_EPISTEMIC, False)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Graph-of-Thought</title>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{
      startOnLoad: true,
      theme: "base",
      themeVariables: {{
        fontFamily: "IBM Plex Sans, ui-sans-serif, system-ui, sans-serif",
        primaryColor: "#eef2ff",
        primaryTextColor: "#1c1917",
        primaryBorderColor: "#6366f1",
        lineColor: "#57534e",
        secondaryColor: "#fafaf9",
        tertiaryColor: "#fff1f2"
      }}
    }});
  </script>
  <style>
    :root {{
      --ink: #1c1917;
      --muted: #57534e;
      --paper: #f5f2ea;
      --panel: #fffcf6;
      --line: #e7e0d2;
      --accent: #4f46e5;
      --bad: #b91c1c;
      --ok: #047857;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font: 16px/1.55 "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
    }}
    .wrap {{ max-width: 880px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }}
    .hero h1 {{
      font-family: "Iowan Old Style", "Palatino Linotype", Palatino, serif;
      font-size: clamp(2.1rem, 5vw, 3.1rem);
      letter-spacing: -0.03em;
      margin: 0 0 0.6rem;
    }}
    .hero p {{ color: var(--muted); max-width: 42rem; margin: 0 0 1rem; }}
    .hero strong {{ color: var(--ink); }}
    .links {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1.25rem 0 2rem; }}
    .links a {{
      color: var(--ink);
      text-decoration: none;
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 999px;
      padding: 0.3rem 0.75rem;
      font-size: 0.85rem;
    }}
    .links a:hover {{ border-color: var(--accent); color: var(--accent); }}
    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 1.4rem 1.4rem 1.1rem;
      margin: 1.2rem 0;
      box-shadow: 0 12px 40px rgba(28, 25, 23, 0.04);
    }}
    .panel-head {{ display: flex; justify-content: space-between; gap: 1rem; align-items: flex-start; }}
    .kicker {{
      text-transform: uppercase;
      letter-spacing: 0.12em;
      font-size: 0.7rem;
      color: var(--muted);
      margin: 0 0 0.35rem;
    }}
    h2 {{ font-size: 1.35rem; margin: 0 0 0.35rem; }}
    h3 {{ font-size: 0.92rem; margin: 1.2rem 0 0.5rem; letter-spacing: 0.02em; }}
    .blurb {{ margin: 0; color: var(--muted); font-size: 0.95rem; }}
    .badge {{
      flex-shrink: 0;
      border-radius: 999px;
      padding: 0.35rem 0.7rem;
      font-size: 0.75rem;
      font-weight: 650;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    .badge.ok {{ background: #d1fae5; color: var(--ok); }}
    .badge.bad {{ background: #fee2e2; color: var(--bad); }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.6rem;
      margin: 1.1rem 0;
    }}
    .metrics div {{
      background: #f3efe4;
      border-radius: 12px;
      padding: 0.7rem 0.8rem;
    }}
    .metrics span {{ display: block; color: var(--muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; }}
    .metrics b {{ font-size: 1.35rem; }}
    .graph {{
      background: #fff;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 0.8rem;
      overflow-x: auto;
    }}
    .split {{ display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 1.2rem; }}
    @media (max-width: 720px) {{
      .split, .metrics, .panel-head {{ grid-template-columns: 1fr; display: grid; }}
      .panel-head {{ display: grid; }}
    }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.92rem; }}
    th {{ text-align: left; color: var(--muted); font-weight: 500; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.06em; }}
    th, td {{ padding: 0.55rem 0.4rem; border-bottom: 1px solid var(--line); vertical-align: middle; }}
    .chip {{
      display: inline-block;
      background: #eef2ff;
      color: var(--accent);
      border-radius: 999px;
      padding: 0.1rem 0.5rem;
      font-size: 0.75rem;
    }}
    .bar {{
      position: relative;
      height: 1.35rem;
      background: #efe9db;
      border-radius: 999px;
      overflow: hidden;
      min-width: 5.5rem;
    }}
    .bar span {{ display: block; height: 100%; background: #818cf8; }}
    .bar em {{
      position: absolute; inset: 0;
      display: flex; align-items: center; justify-content: center;
      font-style: normal; font-size: 0.75rem; font-variant-numeric: tabular-nums;
    }}
    .rels, .findings {{ list-style: none; padding: 0; margin: 0; }}
    .rels li, .findings li {{ margin: 0 0 0.55rem; }}
    .rel, .rel-bad {{
      display: inline-block;
      margin: 0 0.35rem;
      font-size: 0.75rem;
      padding: 0.05rem 0.45rem;
      border-radius: 999px;
    }}
    .rel {{ background: #eef2ff; color: var(--accent); }}
    .rel-bad {{ background: #fee2e2; color: var(--bad); }}
    .note, .quiet {{ color: var(--muted); font-size: 0.9rem; }}
    .delta {{ color: var(--ok); font-variant-numeric: tabular-nums; font-size: 0.85rem; }}
    details {{ margin-top: 1rem; color: var(--muted); }}
    summary {{ cursor: pointer; }}
    pre {{ overflow-x: auto; background: #1c1917; color: #f5f2ea; padding: 0.9rem; border-radius: 10px; font-size: 0.78rem; }}
    footer {{ margin-top: 2rem; color: var(--muted); font-size: 0.85rem; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <h1>Graph-of-Thought</h1>
      <p>A deterministic runtime for typed reasoning graphs. The engine validates structure, propagates confidence, and surfaces contradictions. The LLM, when used at all, only turns text into a graph — it does not reason here.</p>
      <p>These two snapshots were produced by the v0.1 Python engine, with <strong>no language model</strong>.</p>
      <nav class="links">
        <a href="#contradiction">Contradiction</a>
        <a href="#epistemic">Epistemic support</a>
        <a href="https://github.com/makenoodl/Graph-Of-Thought">GitHub</a>
        <a href="https://huggingface.co/papers/2308.09687">Besta 2023</a>
        <a href="https://huggingface.co/papers/2502.05078">AGoT</a>
      </nav>
    </header>
    {_section(
        contradiction,
        "contradiction",
        "Scenario 1",
        "A goal, a solution, and two constraints. One relation is CONTRADICTS — the graph is invalid.",
    )}
    {_section(
        epistemic,
        "epistemic",
        "Scenario 2",
        "Rain supports wet grass. Epistemic propagation raises belief in the supported node.",
    )}
    <footer>
      Complementary to Graph of Thoughts (Besta et al.): here the graph is inspectable system state, not a prompt-time thought topology.
      v0.1 is in-memory only; <code>blocked_paths</code> and <code>viable_paths</code> are always 0.
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    OUT.write_text(build_html(), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
