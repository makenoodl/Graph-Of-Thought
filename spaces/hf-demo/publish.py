"""Publish a static Hub Space (free) plus a paper collection.

Gradio Spaces need Hugging Face Pro. This script uploads `index.html`.

    hf auth login
    uv run --with huggingface_hub python spaces/hf-demo/publish.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import requests
from huggingface_hub import HfApi, get_token
from huggingface_hub.utils import build_hf_headers

ROOT = Path(__file__).resolve().parents[2]
DEMO = Path(__file__).resolve().parent
STAGING = ROOT / ".hf-space-staging"
sys.path.insert(0, str(DEMO))
REPO_ID = "MSBIG/graph-of-thought"
COLLECTION_TITLE = "Graph of Thought — deterministic runtime"

PAPER_COMMENT = """Open-source **deterministic runtime** for typed reasoning graphs (validation, confidence propagation, contradiction analysis). The LLM is used only as an interpreter, not as the reasoner.

This is complementary to the prompting formulation in this paper: we treat the graph as inspectable system state rather than a prompt-time thought topology.

- Demo (no LLM): https://huggingface.co/spaces/MSBIG/graph-of-thought
- Code: https://github.com/makenoodl/Graph-Of-Thought
"""

PAPER_IDS = ("2308.09687", "2502.05078")


def stage() -> Path:
    from build_static import main as build_index

    build_index()
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir()
    for name in ("index.html", "README.md"):
        shutil.copy2(DEMO / name, STAGING / name)
    return STAGING


def publish_space(api: HfApi) -> str:
    staging = stage()
    api.create_repo(
        repo_id=REPO_ID,
        repo_type="space",
        space_sdk="static",
        private=False,
        exist_ok=True,
    )
    api.upload_folder(
        repo_id=REPO_ID,
        repo_type="space",
        folder_path=str(staging),
        commit_message="Refresh static demo in English (no LLM)",
    )
    return f"https://huggingface.co/spaces/{REPO_ID}"


def publish_collection(api: HfApi) -> str:
    collection = api.create_collection(
        title=COLLECTION_TITLE,
        description=(
            "Typed in-memory reasoning graphs. LLM interprets; the engine is deterministic."
        ),
        namespace="MSBIG",
        exists_ok=True,
    )
    items = [
        (REPO_ID, "space"),
        ("2308.09687", "paper"),
        ("2502.05078", "paper"),
        ("2504.02670", "paper"),
    ]
    for item_id, item_type in items:
        try:
            api.add_collection_item(
                collection.slug,
                item_id=item_id,
                item_type=item_type,
                exists_ok=True,
            )
        except Exception as exc:  # noqa: BLE001 — Hub item APIs vary by type
            print(f"collection item skipped {item_type}:{item_id}: {exc}")
    return f"https://huggingface.co/collections/{collection.slug}"


def comment_on_papers() -> None:
    token = get_token()
    if not token:
        print("no Hub token; skip paper comments")
        return
    headers = build_hf_headers(token=token, is_write_action=True)
    for paper_id in PAPER_IDS:
        urls = (
            f"https://huggingface.co/api/papers/{paper_id}/comment",
            f"https://huggingface.co/api/papers/{paper_id}/comments",
        )
        for url in urls:
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json={"comment": PAPER_COMMENT},
                    timeout=30.0,
                )
            except requests.RequestException as exc:
                print(f"paper {paper_id} comment failed: {exc}")
                continue
            print(f"paper {paper_id} POST {url} -> {response.status_code}")
            if response.status_code < 400:
                break
            print(response.text[:500])


def main() -> int:
    if not get_token():
        print("No Hugging Face token. Run `hf auth login` with a Write token, then retry.")
        return 1
    api = HfApi()
    try:
        space_url = publish_space(api)
    except Exception as exc:  # noqa: BLE001
        print(f"Space create/upload failed.\n{exc}")
        return 1
    print("space", space_url)
    try:
        print("collection", publish_collection(api))
    except Exception as exc:  # noqa: BLE001
        print("collection failed:", exc)
    comment_on_papers()
    return 0


if __name__ == "__main__":
    sys.exit(main())
