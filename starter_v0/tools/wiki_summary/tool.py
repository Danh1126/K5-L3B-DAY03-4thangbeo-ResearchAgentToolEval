from __future__ import annotations

from typing import Any
from urllib.parse import quote

import requests

from tools._shared import TIMEOUT, err

VALID_LANGS = {"en", "vi"}


def get_wikipedia_summary(topic: str = "", lang: str = "en") -> dict[str, Any]:
    """Fetch a topic summary from the Wikipedia REST API."""
    try:
        if not isinstance(topic, str) or not topic.strip():
            raise ValueError("topic must be a non-empty string")
        clean_topic = topic.strip()

        if not isinstance(lang, str) or lang not in VALID_LANGS:
            raise ValueError("lang must be 'en' or 'vi'")

        slug = quote(clean_topic.replace(" ", "_"), safe="")
        url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{slug}"
        response = requests.get(
            url,
            headers={"User-Agent": "AI20k-Day03-Research-Agent/1.0"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        page_url = (data.get("content_urls") or {}).get("desktop", {}).get("page") or url
        item = {
            "title": data.get("title") or clean_topic,
            "url": page_url,
            "source": f"{lang}.wikipedia.org",
            "summary": data.get("extract") or "",
            "description": data.get("description") or "",
        }
        return {
            "tool": "wiki_summary",
            "topic": clean_topic,
            "lang": lang,
            "items": [item],
        }
    except Exception as exc:
        return err("wiki_summary", exc)

