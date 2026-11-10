from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

VALID_SORT_BY = {"stars", "updated"}


def search_github_repos(
    query: str = "",
    language: str = "",
    sort_by: str = "stars",
    limit: int = 5,
) -> dict[str, Any]:
    """Search public GitHub repositories by keyword and optional language."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        clean_query = query.strip()

        if not isinstance(language, str):
            raise ValueError("language must be a string")
        clean_lang = language.strip()

        if not isinstance(sort_by, str) or sort_by not in VALID_SORT_BY:
            raise ValueError("sort_by must be 'stars' or 'updated'")

        if isinstance(limit, bool):
            raise ValueError("limit must be an integer between 1 and 20")
        try:
            parsed_limit = int(limit)
        except (TypeError, ValueError) as exc:
            raise ValueError("limit must be an integer between 1 and 20") from exc
        if parsed_limit < 1 or parsed_limit > 20:
            raise ValueError("limit must be an integer between 1 and 20")

        q = f"{clean_query} language:{clean_lang}" if clean_lang else clean_query
        response = requests.get(
            "https://api.github.com/search/repositories",
            params={"q": q, "sort": sort_by, "order": "desc", "per_page": parsed_limit},
            headers={"Accept": "application/vnd.github+json"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        items = [
            {
                "title": repo.get("full_name") or repo.get("name") or "",
                "url": repo.get("html_url") or "",
                "source": "github.com",
                "summary": repo.get("description") or "",
                "stars": repo.get("stargazers_count") or 0,
                "language": repo.get("language") or "",
            }
            for repo in data.get("items", [])
        ]
        return {
            "tool": "github_search",
            "query": clean_query,
            "language": clean_lang,
            "sort_by": sort_by,
            "items": items,
        }
    except Exception as exc:
        return err("github_search", exc)

