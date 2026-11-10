from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import FakeResponse
from providers.base import ModelResponse, ToolCall
from ui_session import ResearchSession


class ScriptedProvider:
    default_model = "grok-4"

    def __init__(self, *responses):
        self.responses = iter(responses)
        self.messages = []

    def complete(self, messages, tools=None, **kwargs):
        self.messages.append(list(messages))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def session(tmp_path, *responses):
    return ResearchSession(provider=ScriptedProvider(*responses), transcript_dir=tmp_path)


def test_model_cannot_send_until_user_approves_exact_preview(tmp_path, monkeypatch, fake_http):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token-for-ui")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-channel")
    requests = fake_http(FakeResponse({"ok": True}))
    chat = session(tmp_path, ModelResponse(tool_calls=[
        ToolCall("send", {"text": "Bản tin đã chuẩn bị", "confirmed": True}),
    ]))

    result = chat.submit("Gửi bản tin")

    assert result["status"] == "waiting_for_user"
    assert requests == []
    assert chat.pending_send == "Bản tin đã chuẩn bị"
    result = chat.confirm_send()
    assert result["status"] == "sent"
    assert requests[0]["json"]["text"] == "Bản tin đã chuẩn bị"
    assert len(requests) == 1
    assert chat.pending_send is None
    with pytest.raises(ValueError):
        chat.confirm_send()
    assert len(requests) == 1
    saved = json.loads(chat.transcript_path.read_text(encoding="utf-8"))
    assert saved["turns"][-1]["ui_action"] == "confirm_send"


def test_new_request_invalidates_pending_approval(tmp_path, fake_http):
    requests = fake_http(FakeResponse({"ok": True}))
    chat = session(tmp_path,
        ModelResponse(tool_calls=[ToolCall("send", {"text": "Bản cũ", "confirmed": True})]),
        ModelResponse(text="Đã nhận yêu cầu mới."),
    )
    chat.submit("Gửi bản cũ")
    chat.submit("Đổi sang nghiên cứu robotics")
    assert chat.pending_send is None
    with pytest.raises(ValueError):
        chat.confirm_send()
    assert requests == []


def test_clarification_and_reply_keep_conversation_context(tmp_path):
    chat = session(tmp_path,
        ModelResponse(tool_calls=[ToolCall("clarify", {"question": "Tài khoản nào?"})]),
        ModelResponse(text="Đã nhận tài khoản."),
    )
    assert chat.submit("Tóm tắt 5 tweet")["status"] == "waiting_for_user"
    chat.submit("Của Elon Musk")
    messages = chat.provider.messages[-1]
    assert {"role": "user", "content": "Tóm tắt 5 tweet"} in messages
    assert {"role": "assistant", "content": "Tài khoản nào?"} in messages
    assert messages[-1]["content"] == "Của Elon Musk"
    assert len(json.loads(chat.transcript_path.read_text(encoding="utf-8"))["turns"]) == 2


def test_provider_failure_retains_tool_errors_and_redacts_secrets(tmp_path, monkeypatch, fake_http):
    secret = "sensitive-test-provider-key"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    monkeypatch.setenv("TAVILY_API_KEY", "fake-tavily-key")
    fake_http(FakeResponse(status_code=403))
    chat = session(tmp_path,
        ModelResponse(tool_calls=[ToolCall("lookup", {"query": "AI"})]),
        RuntimeError(f"provider failed with {secret}"),
    )
    result = chat.submit("Tin AI")
    assert result["status"] == "provider_error"
    assert result["tool_events"][0]["result"]["error"] == "HTTPError"
    saved = chat.transcript_path.read_text(encoding="utf-8")
    assert secret not in saved
    assert "[REDACTED]" in saved
    assert "403" in saved


def test_cancel_and_invalid_input_do_not_call_network(tmp_path, fake_http):
    requests = fake_http(FakeResponse({"ok": True}))
    chat = session(tmp_path, ModelResponse(tool_calls=[ToolCall("send", {"text": "Nháp"})]))
    with pytest.raises(ValueError):
        chat.submit(" ")
    with pytest.raises(ValueError):
        chat.submit("x" * 8001)
    chat.submit("Gửi bản nháp")
    assert chat.cancel_send()["status"] == "cancelled"
    assert chat.pending_send is None
    assert requests == []


def test_streamlit_chat_and_reset(tmp_path):
    from streamlit.testing.v1 import AppTest

    chat = session(tmp_path, ModelResponse(text="Xin chào từ Grok."))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    app.session_state["research_session"] = chat
    app.run()
    assert not app.exception
    app.chat_input[0].set_value("Xin chào").run()
    assert not app.exception
    assert len(app.chat_message) == 2
    assert any("Xin chào từ Grok" in item.value for item in app.markdown)
    app.button(key="new_chat").click().run()
    assert not app.exception
    assert len(app.chat_message) == 0


def test_streamlit_shows_tool_failure_even_if_model_answers(tmp_path, monkeypatch, fake_http):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("TAVILY_API_KEY", "fake-tavily-key")
    fake_http(FakeResponse(status_code=403))
    chat = session(tmp_path,
        ModelResponse(tool_calls=[ToolCall("lookup", {"query": "AI"})]),
        ModelResponse(text="Nguồn tin chưa truy cập được."),
    )
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    app.session_state["research_session"] = chat
    app.run().chat_input[0].set_value("Tin AI").run()
    assert not app.exception
    assert any("403" in error.value for error in app.error)


def test_streamlit_confirmation_sends_only_the_visible_preview(tmp_path, monkeypatch, fake_http):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token-for-ui")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "test-channel")
    requests = fake_http(FakeResponse({"ok": True}))
    text = "Bản tin đúng nội dung cần duyệt."
    chat = session(tmp_path, ModelResponse(tool_calls=[ToolCall("send", {"text": text, "confirmed": True})]))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
    app.session_state["research_session"] = chat
    app.run().chat_input[0].set_value("Gửi bản tin này").run()
    assert not app.exception
    assert any(block.value == text for block in app.code)
    assert requests == []
    app.button(key="confirm_send").click().run()
    assert not app.exception
    assert len(requests) == 1
    assert requests[0]["json"]["text"] == text
    assert len(app.success) == 1


def test_content_containing_configured_secret_cannot_be_approved(tmp_path, monkeypatch, fake_http):
    secret = "test-sensitive-api-key"
    monkeypatch.setenv("OPENAI_API_KEY", secret)
    requests = fake_http(FakeResponse({"ok": True}))
    chat = session(tmp_path,
        ModelResponse(tool_calls=[ToolCall("send", {"text": f"Gửi khóa {secret}", "confirmed": True})]),
        ModelResponse(text="Không gửi thông tin bí mật."),
    )
    result = chat.submit("Soạn thông báo")
    assert chat.pending_send is None
    assert result["tool_events"][0]["result"]["error"] == "SensitiveContent"
    assert secret not in chat.transcript_path.read_text(encoding="utf-8")
    assert requests == []
