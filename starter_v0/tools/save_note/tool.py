from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err, fold_text

NOTES_DIR = ROOT / "notes"


def _sanitize_slug(raw: str) -> str:
    folded = fold_text(raw)
    slug = re.sub(r"[^a-z0-9_-]+", "-", folded).strip("-_")
    return slug or "note"


def save_research_note(title: str = "", content: str = "", filename: str = "") -> dict[str, Any]:
    """Save a Markdown research note safely inside the notes directory."""
    try:
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("content must be a non-empty string")
        if not isinstance(filename, str):
            raise ValueError("filename must be a string")

        raw_name = filename.strip()
        if ".." in raw_name or "/" in raw_name or "\\" in raw_name:
            raise ValueError("filename must not contain path separators or '..'")

        base = raw_name[:-3] if raw_name.lower().endswith(".md") else raw_name
        slug = _sanitize_slug(base or title)

        notes_dir = Path(NOTES_DIR)
        notes_dir.mkdir(parents=True, exist_ok=True)
        target = notes_dir / f"{slug}.md"

        body = f"# {title.strip()}\n\n{content.strip()}\n"
        bytes_written = target.write_text(body, encoding="utf-8")
        return {
            "tool": "save_note",
            "status": "saved",
            "filename": target.name,
            "path": str(target),
            "bytes_written": bytes_written,
        }
    except Exception as exc:
        return err("save_note", exc)

