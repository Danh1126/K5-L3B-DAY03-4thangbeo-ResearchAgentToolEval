"""Per-browser chat state, real transcripts, and explicit approval for sending."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from chat import execute_tool_call, now_iso, run_model_tool_loop, trim_history, write_transcript
from providers import make_provider
from providers.base import ToolCall
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).resolve().parent


class ResearchSession:
    def __init__(self, *, provider=None, transcript_dir: Path | None = None):
        self.provider = provider if provider is not None else make_provider("openai")
        self.model = getattr(self.provider, "default_model", "grok-4")
        self.system_prompt = (ROOT / "artifacts/system_prompt.md").read_text(encoding="utf-8")
        declarations = load_tool_declarations(ROOT / "artifacts/tools.yaml")
        self.tools = to_openai_tools(declarations)
        self.history: list[dict[str, str]] = []
        self.pending_send: str | None = None
        self._events: list[dict[str, Any]] = []
        self._secrets = sorted({
            value for name, value in os.environ.items()
            if ("KEY" in name or "TOKEN" in name) and len(value) >= 8
        }, key=len, reverse=True)
        version = os.getenv("AGENT_VERSION", "v0")
        artifact = build_artifact_version(version, ROOT / "artifacts/system_prompt.md", ROOT / "artifacts/tools.yaml")
        session_id = f"ui_{uuid4().hex}"
        self.transcript_path = (transcript_dir if transcript_dir is not None else ROOT / "transcripts") / f"{session_id}.transcript.json"
        self.transcript = {
            "transcript_id": session_id,
            **artifact_version_dict(artifact),
            "provider": "openai",
            "model": self.model,
            "source": "streamlit",
            "created_at": now_iso(),
            "turns": [],
        }

    def _clean(self, value: Any) -> Any:
        if isinstance(value, str):
            for secret in self._secrets:
                value = value.replace(secret, "[REDACTED]")
            return value
        if isinstance(value, dict):
            return {key: self._clean(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._clean(item) for item in value]
        return value

    def _execute(self, call: ToolCall) -> dict[str, Any]:
        if call.name == "send":
            text = call.args.get("text")
            if not isinstance(text, str) or not text.strip():
                result = {"error": "InvalidContent", "message": "Cần có nội dung cụ thể trước khi gửi."}
            elif self._clean(text) != text:
                result = {"error": "SensitiveContent", "message": "Nội dung chứa thông tin bí mật đã cấu hình; không tạo bản gửi."}
            else:
                self.pending_send = text
                result = {
                    "status": "needs_confirmation",
                    "awaiting_user": True,
                    "question": "Hãy kiểm tra nội dung bên dưới, rồi chọn Xác nhận gửi hoặc Hủy gửi.",
                }
            event = {"tool": "send", "args": call.args, "result": result}
        else:
            event = execute_tool_call(call)
        event = self._clean(event)
        self._events.append(event)
        return event

    def _record(self, user: str, result: dict[str, Any], started_at: str, **extra) -> dict[str, Any]:
        record = self._clean({
            "turn_index": len(self.transcript["turns"]) + 1,
            "started_at": started_at,
            "ended_at": now_iso(),
            "user": user,
            "rounds": [],
            "tool_events": [],
            **result,
            **extra,
        })
        self.transcript["turns"].append(record)
        if record["status"] != "provider_error":
            self.history.extend([
                {"role": "user", "content": record["user"]},
                {"role": "assistant", "content": record["assistant_text"]},
            ])
        write_transcript(self.transcript_path, self.transcript)
        return record

    def submit(self, text: str) -> dict[str, Any]:
        if not isinstance(text, str) or not text.strip() or len(text) > 8000:
            raise ValueError("Nhập yêu cầu từ 1 đến 8.000 ký tự.")
        self.pending_send = None
        self._events = []
        started = now_iso()
        try:
            result = run_model_tool_loop(
                provider=self.provider,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *trim_history(self.history, 5),
                    {"role": "user", "content": text.strip()},
                ],
                tools=self.tools,
                model=self.model,
                max_tool_rounds=4,
                tool_executor=self._execute,
            )
        except Exception as exc:
            result = {
                "status": "provider_error",
                "assistant_text": "Không nhận được phản hồi từ model. Kiểm tra kết nối hoặc cấu hình API rồi thử lại.",
                "error": f"{type(exc).__name__}: {exc}",
                "tool_events": self._events,
            }
        return self._record(text.strip(), result, started)

    def confirm_send(self) -> dict[str, Any]:
        if self.pending_send is None:
            raise ValueError("Không có nội dung đang chờ xác nhận.")
        text, self.pending_send = self.pending_send, None
        started = now_iso()
        event = self._clean(execute_tool_call(ToolCall("send", {"text": text, "confirmed": True})))
        sent = event.get("result", {}).get("status") == "sent"
        return self._record("Xác nhận gửi đúng nội dung đã xem.", {
            "status": "sent" if sent else "tool_error",
            "assistant_text": "Đã gửi nội dung lên Telegram." if sent else "Chưa gửi được nội dung. Xem lỗi tool bên dưới.",
            "tool_events": [event],
        }, started, ui_action="confirm_send")

    def cancel_send(self) -> dict[str, Any]:
        if self.pending_send is None:
            raise ValueError("Không có nội dung đang chờ xác nhận.")
        self.pending_send = None
        return self._record("Hủy gửi.", {
            "status": "cancelled", "assistant_text": "Đã hủy bản chờ gửi. Chưa gửi nội dung lên Telegram.",
        }, now_iso(), ui_action="cancel_send")
