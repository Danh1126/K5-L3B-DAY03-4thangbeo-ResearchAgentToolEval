"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    result = TOOL_FUNCTIONS["clarify"](
        question="Bạn muốn tìm trên nguồn nào?",
        response_type="choice",
        options=["Web", "Twitter"],
    )

    assert result["tool"] == "ask_user"
    assert result["question"] == "Bạn muốn tìm trên nguồn nào?"
    assert result["response_type"] == "choice"
    assert result["options"] == ["Web", "Twitter"]
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "Item 1", "url": "https://example.com/1", "section": "A"},
        {"title": "Item 2", "url": "https://example.com/2", "section": "B"},
        {"title": "Item 3", "url": "https://example.com/3", "section": "A"},
    ]
    result = TOOL_FUNCTIONS["format"](items=items, template="sections", headline="Digest")

    assert result["tool"] == "render_digest"
    assert result["item_count"] == 3
    assert result["markdown"].count("## A") == 1
    assert result["markdown"].count("## B") == 1
    assert result["markdown"].index("## A") < result["markdown"].index("Item 3") < result["markdown"].index("## B")


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "bot-secret-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100123456")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin AI hôm nay", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "bot-secret-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100123456"
    assert calls[0]["json"]["text"] == "Bản tin AI hôm nay"
    assert result == {"tool": "send_telegram", "status": "sent"}


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")
    calls = fake_http(FakeResponse({"results": [
        {"title": "Result 1", "url": "https://example.com/r1", "content": "Summary", "score": 0.8},
    ]}))

    result = TOOL_FUNCTIONS["lookup"](query="AI agents", topic="general", timeframe=None, max_results=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.tavily.com/search"
    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "AI agents"
    assert result["items"][0]["title"] == "Result 1"


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


# ---------------- YOUR NEW TOOL(S): 4 new tools (>= 3 tests each) ----------------

# 1. github_search -----------------------------------------------------------

def test_github_search_happy_path_sends_query_and_maps_repos(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "items": [
            {
                "full_name": "modelcontextprotocol/python-sdk",
                "html_url": "https://github.com/modelcontextprotocol/python-sdk",
                "description": "Official Python SDK for MCP",
                "stargazers_count": 12500,
                "language": "Python",
            }
        ]
    }))

    result = TOOL_FUNCTIONS["github_search"](query="MCP server", language="Python", sort_by="stars", limit=3)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/search/repositories"
    assert calls[0]["params"]["q"] == "MCP server language:Python"
    assert calls[0]["params"]["sort"] == "stars"
    assert calls[0]["params"]["per_page"] == 3
    assert result["tool"] == "github_search"
    assert result["items"][0] == {
        "title": "modelcontextprotocol/python-sdk",
        "url": "https://github.com/modelcontextprotocol/python-sdk",
        "source": "github.com",
        "summary": "Official Python SDK for MCP",
        "stars": 12500,
        "language": "Python",
    }


@pytest.mark.parametrize("kwargs", [
    {"query": ""},
    {"query": "   "},
    {"query": "agent", "sort_by": "forks"},
    {"query": "agent", "limit": 0},
    {"query": "agent", "limit": True},
    {"query": "agent", "limit": "bad"},
])
def test_github_search_bad_input_returns_error_dict(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({"items": []}))
    result = TOOL_FUNCTIONS["github_search"](**kwargs)

    assert result["tool"] == "github_search"
    assert result["error"] == "ValueError"
    assert calls == []


def test_github_search_http_429_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=429))
    result = TOOL_FUNCTIONS["github_search"](query="MCP")

    assert result["tool"] == "github_search"
    assert result["error"] == "HTTPError"


# 2. wiki_summary ------------------------------------------------------------

def test_wiki_summary_happy_path_requests_lang_endpoint_and_maps_item(fake_http) -> None:
    calls = fake_http(FakeResponse({
        "title": "Trí tuệ nhân tạo",
        "extract": "Trí tuệ nhân tạo là trí tuệ do con người lập trình...",
        "description": "Ngành khoa học máy tính",
        "content_urls": {"desktop": {"page": "https://vi.wikipedia.org/wiki/Tr%C3%AD_tu%E1%BB%87_nh%C3%A2n_t%E1%BA%A1o"}},
    }))

    result = TOOL_FUNCTIONS["wiki_summary"](topic="Trí tuệ nhân tạo", lang="vi")

    assert len(calls) == 1
    assert calls[0]["url"].startswith("https://vi.wikipedia.org/api/rest_v1/page/summary/")
    assert "User-Agent" in calls[0]["headers"]
    assert result["tool"] == "wiki_summary"
    assert result["items"][0]["source"] == "vi.wikipedia.org"
    assert result["items"][0]["title"] == "Trí tuệ nhân tạo"


@pytest.mark.parametrize("kwargs", [
    {"topic": ""},
    {"topic": "   "},
    {"topic": 123},
    {"topic": "AI", "lang": "fr"},
])
def test_wiki_summary_bad_input_returns_error_dict(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse({}))
    result = TOOL_FUNCTIONS["wiki_summary"](**kwargs)

    assert result["tool"] == "wiki_summary"
    assert result["error"] == "ValueError"
    assert calls == []


def test_wiki_summary_http_404_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=404))
    result = TOOL_FUNCTIONS["wiki_summary"](topic="NonexistentTopicXYZ", lang="en")

    assert result["tool"] == "wiki_summary"
    assert result["error"] == "HTTPError"


# 3. hf_papers ---------------------------------------------------------------

def test_hf_papers_happy_path_filters_query_and_maps_items(fake_http) -> None:
    calls = fake_http(FakeResponse([
        {"paper": {"id": "2501.00001", "title": "Multimodal Agent Benchmarks", "summary": "New benchmark", "upvotes": 42}},
        {"paper": {"id": "2501.00002", "title": "Protein Folding Fast", "summary": "Biology model", "upvotes": 15}},
    ]))

    result = TOOL_FUNCTIONS["hf_papers"](query="multimodal", limit=2)

    assert len(calls) == 1
    assert calls[0]["url"] == "https://huggingface.co/api/daily_papers"
    assert result["tool"] == "hf_papers"
    assert len(result["items"]) == 1
    assert result["items"][0] == {
        "title": "Multimodal Agent Benchmarks",
        "url": "https://huggingface.co/papers/2501.00001",
        "source": "huggingface.co",
        "summary": "New benchmark",
        "upvotes": 42,
    }


@pytest.mark.parametrize("kwargs", [
    {"query": 123},
    {"limit": 0},
    {"limit": 25},
    {"limit": True},
    {"limit": "abc"},
])
def test_hf_papers_bad_input_returns_error_dict(fake_http, kwargs) -> None:
    calls = fake_http(FakeResponse([]))
    result = TOOL_FUNCTIONS["hf_papers"](**kwargs)

    assert result["tool"] == "hf_papers"
    assert result["error"] == "ValueError"
    assert calls == []


def test_hf_papers_timeout_returns_error_dict(monkeypatch) -> None:
    import requests as req_lib

    def raise_timeout(*args, **kwargs):
        raise req_lib.Timeout("HF API timed out")

    monkeypatch.setattr(req_lib, "get", raise_timeout)
    result = TOOL_FUNCTIONS["hf_papers"](query="agent", limit=3)

    assert result["tool"] == "hf_papers"
    assert result["error"] == "Timeout"


# 4. save_note ---------------------------------------------------------------

def test_save_note_happy_path_writes_markdown_file(monkeypatch, tmp_path) -> None:
    import tools.save_note.tool as save_note_mod

    monkeypatch.setattr(save_note_mod, "NOTES_DIR", tmp_path)
    result = TOOL_FUNCTIONS["save_note"](
        title="Agent Eval Notes",
        content="Check routing and args.",
        filename="agent_eval",
    )

    saved_file = tmp_path / "agent_eval.md"
    assert result["tool"] == "save_note"
    assert result["status"] == "saved"
    assert result["filename"] == "agent_eval.md"
    assert saved_file.exists()
    assert saved_file.read_text(encoding="utf-8") == "# Agent Eval Notes\n\nCheck routing and args.\n"


@pytest.mark.parametrize("kwargs", [
    {"title": "", "content": "abc"},
    {"title": "Valid", "content": "   "},
    {"title": "Valid", "content": "abc", "filename": "../../etc/passwd"},
    {"title": "Valid", "content": "abc", "filename": "dir/sub.md"},
    {"title": 123, "content": "abc"},
])
def test_save_note_bad_input_and_path_traversal_return_error_dict(monkeypatch, tmp_path, kwargs) -> None:
    import tools.save_note.tool as save_note_mod

    monkeypatch.setattr(save_note_mod, "NOTES_DIR", tmp_path)
    result = TOOL_FUNCTIONS["save_note"](**kwargs)

    assert result["tool"] == "save_note"
    assert result["error"] == "ValueError"
    assert list(tmp_path.iterdir()) == []


def test_save_note_os_error_returns_error_dict(monkeypatch, tmp_path) -> None:
    import tools.save_note.tool as save_note_mod
    from pathlib import Path

    monkeypatch.setattr(save_note_mod, "NOTES_DIR", tmp_path)

    def raise_oserror(*args, **kwargs):
        raise PermissionError("disk read-only")

    monkeypatch.setattr(Path, "write_text", raise_oserror)
    result = TOOL_FUNCTIONS["save_note"](title="Test", content="Body")

    assert result["tool"] == "save_note"
    assert result["error"] == "PermissionError"
