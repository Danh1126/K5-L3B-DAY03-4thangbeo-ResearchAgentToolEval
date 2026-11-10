from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err


def get_hf_daily_papers(query: str = "", limit: int = 5) -> dict[str, Any]:
    """Fetch trending AI papers from Hugging Face Daily Papers."""
    try:
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        clean_query = query.strip().lower()

        if isinstance(limit, bool):
            raise ValueError("limit must be an integer between 1 and 20")
        try:
            parsed_limit = int(limit)
        except (TypeError, ValueError) as exc:
            raise ValueError("limit must be an integer between 1 and 20") from exc
        if parsed_limit < 1 or parsed_limit > 20:
            raise ValueError("limit must be an integer between 1 and 20")

        response = requests.get(
            "https://huggingface.co/api/daily_papers",
            params={"limit": parsed_limit if not clean_query else 30},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        raw_items = response.json()
        if not isinstance(raw_items, list):
            raise ValueError("unexpected response format from Hugging Face Daily Papers")

        items: list[dict[str, Any]] = []
        for entry in raw_items:
            paper = entry.get("paper") or {}
            title = paper.get("title") or entry.get("title") or ""
            summary = paper.get("summary") or entry.get("summary") or ""
            paper_id = str(paper.get("id") or "").strip()
            if clean_query and clean_query not in title.lower() and clean_query not in summary.lower():
                continue
            items.append({
                "title": title,
                "url": f"https://huggingface.co/papers/{paper_id}" if paper_id else "",
                "source": "huggingface.co",
                "summary": summary[:400],
                "upvotes": paper.get("upvotes") or 0,
            })
            if len(items) >= parsed_limit:
                break

        return {
            "tool": "hf_papers",
            "query": query.strip(),
            "items": items,
        }
    except Exception as exc:
        return err("hf_papers", exc)

