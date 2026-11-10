"""Run from starter_v0: python -m streamlit run app.py."""
from __future__ import annotations

import json
import os

import streamlit as st

from ui_session import ResearchSession

TOOL_LABELS = {
    "clarify": "Hỏi lại & xác nhận", "timeline": "Bài đăng theo tài khoản",
    "social_search": "Thảo luận trên X", "lookup": "Tìm kiếm trên web",
    "fetch": "Đọc một đường dẫn", "format": "Biên soạn bản tin",
    "send": "Gửi bản tin Telegram", "policy": "Chính sách nội bộ",
    "papers": "Tìm paper arXiv", "paper_text": "Đọc PDF arXiv",
}
EXAMPLES = [
    ("Tin AI hôm nay", "Tin tức AI hôm nay có gì nổi bật?"),
    ("Theo dõi tài khoản", "Lấy 5 tweet mới nhất của Elon Musk"),
    ("Tra chính sách", "Chính sách nội bộ về trích dẫn nguồn nghiên cứu là gì?"),
]


def prefill(text: str) -> None:
    st.session_state["research_input"] = text


def render_turn(turn: dict) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        if turn["status"] == "provider_error":
            st.error(turn["assistant_text"])
            st.caption(turn.get("error", ""))
        elif turn["status"] == "sent":
            st.success(turn["assistant_text"])
        else:
            st.markdown(turn.get("assistant_text") or "Chưa có câu trả lời bằng văn bản.")
        if turn["status"] == "waiting_for_user":
            st.caption("Đang chờ bạn bổ sung thông tin hoặc xác nhận.")
        if turn["status"] == "max_tool_rounds":
            st.warning("Đã đạt giới hạn 4 vòng tool. Bạn có thể thu hẹp yêu cầu và thử lại.")
        events = turn.get("tool_events", [])
        for event in events:
            result = event.get("result", {})
            if isinstance(result, dict) and result.get("error"):
                st.error(f"{event['tool']} · {result['error']}: {result.get('message', '')}")
        if events:
            with st.expander(f"Công cụ & nguồn dữ liệu · {len(events)} lời gọi"):
                for event in events:
                    st.caption(TOOL_LABELS.get(event["tool"], event["tool"]))
                    st.json(event, expanded=False)


def main() -> None:
    st.set_page_config(page_title="Research Desk · Grok", page_icon="🔎", layout="wide")
    st.markdown("""<style>
    .stApp {background:#f6f8fa;}
    .block-container {max-width:1060px;padding-top:2.4rem;padding-bottom:3rem;}
    [data-testid="stSidebar"] {background:#fff;border-right:1px solid #e0e7ed;}
    [data-testid="stChatMessage"] {border:1px solid #e0e7ed;border-radius:10px;background:#fff;}
    h1 {letter-spacing:-0.045em;font-weight:700;font-size:clamp(1.8rem,2.5vw,2.5rem)!important;}
    .desk-mark {font-size:13px;font-weight:700;letter-spacing:.14em;color:#176b56;margin-bottom:10px;}
    button:focus-visible,textarea:focus-visible {outline:3px solid #176b56!important;outline-offset:3px;}
    @media(max-width:640px) {.block-container {padding-top:3.2rem;padding-left:1rem;padding-right:1rem;}}
    </style>""", unsafe_allow_html=True)
    if "research_session" not in st.session_state:
        st.session_state["research_session"] = ResearchSession()
    chat = st.session_state["research_session"]

    with st.sidebar:
        st.markdown('<div class="desk-mark">RESEARCH DESK</div>', unsafe_allow_html=True)
        st.caption("Không gian nghiên cứu của bạn")
        if st.button("Cuộc trò chuyện mới", key="new_chat", icon=":material/add:", width="stretch"):
            st.session_state["research_session"] = ResearchSession()
            st.session_state.pop("research_input", None)
            st.rerun()
        st.divider()
        st.caption("MODEL ĐANG DÙNG")
        st.markdown(f"**{chat.model}**")
        st.caption("Grok API · Đã cấu hình" if os.getenv("OPENAI_API_KEY") else "Grok API · Chưa có API key trong .env")
        st.caption(f"{chat.transcript['version']} · {len(chat.tools)} công cụ · {len(chat.transcript['turns'])} lượt")
        with st.expander("Khám phá công cụ"):
            for tool in chat.tools:
                name = tool["function"]["name"]
                st.write(TOOL_LABELS.get(name, name))
        st.divider()
        st.markdown("**Lưu lại nghiên cứu**")
        st.caption("Hội thoại và kết quả tool được lưu sau mỗi lượt.")
        st.download_button(
            "Tải hội thoại JSON",
            data=json.dumps(chat.transcript, ensure_ascii=False, indent=2),
            file_name=chat.transcript_path.name,
            mime="application/json",
            disabled=not chat.transcript["turns"],
            width="stretch",
        )

    st.markdown('<div class="desk-mark">TÌM HIỂU SÂU HƠN, TỪ NHỮNG NGUỒN THẬT</div>', unsafe_allow_html=True)
    st.title("Câu hỏi của bạn. Bàn nghiên cứu của bạn.")
    st.markdown("Tìm tin trên web, theo dõi thảo luận, đọc tài liệu và tổng hợp thành bản tin trong một cuộc trò chuyện.")
    st.divider()
    if "storage_error" in st.session_state:
        st.error(st.session_state.pop("storage_error"))
    if not chat.transcript["turns"]:
        st.subheader("Bạn muốn bắt đầu từ đâu?")
        for column, (label, question) in zip(st.columns(3), EXAMPLES):
            with column:
                st.button(label, on_click=prefill, args=(question,), width="stretch")
        st.caption("Chọn một gợi ý để điền câu hỏi, hoặc viết yêu cầu của bạn ở bên dưới.")
    for turn in chat.transcript["turns"]:
        render_turn(turn)

    if chat.pending_send is not None:
        with st.container(border=True):
            st.subheader("Xem trước bản gửi Telegram")
            st.caption("Chỉ nội dung dưới đây sẽ được gửi lên channel đã cấu hình khi bạn xác nhận.")
            st.code(chat.pending_send, language=None, wrap_lines=True)
            confirm, cancel = st.columns(2)
            action = None
            if confirm.button("Xác nhận gửi", key="confirm_send", type="primary", width="stretch"):
                action = chat.confirm_send
            if cancel.button("Hủy gửi", key="cancel_send", width="stretch"):
                action = chat.cancel_send
            if action:
                try:
                    with st.spinner("Đang xử lý lựa chọn của bạn…"):
                        action()
                except OSError:
                    st.session_state["storage_error"] = "Không lưu được tệp transcript. Bạn vẫn có thể tải hội thoại JSON."
                st.rerun()
            st.caption("Gửi yêu cầu mới sẽ hủy bản đang chờ xác nhận.")

    if prompt := st.chat_input("Bạn muốn nghiên cứu điều gì?", key="research_input", max_chars=8000):
        with st.chat_message("user"):
            st.markdown(prompt)
        try:
            with st.spinner("Đang tìm hiểu yêu cầu và kiểm tra nguồn…"):
                chat.submit(prompt)
        except ValueError as exc:
            st.session_state["storage_error"] = str(exc)
        except OSError:
            st.session_state["storage_error"] = "Không lưu được tệp transcript. Bạn vẫn có thể tải hội thoại JSON."
        st.rerun()


if __name__ == "__main__":
    main()
