# Research Desk

UI Streamlit cho research agent Python hiện có, mặc định dùng adapter `openai`
đã được cấu hình sang xAI/Grok. UI không thay đổi prompt, tool declaration,
eval case hoặc cấu hình Grok của bài lab.

## Chạy local

Từ thư mục gốc của repo:

```powershell
cd starter_v0
python -m pip install -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1
```

Mở http://localhost:8501. Key được đọc từ `.env` theo `env_loader.py` của starter;
adapter hiện tại dùng `OPENAI_API_KEY` cho Grok. Không nhập key vào ô chat.
Khi đổi nhãn thử nghiệm, đặt `AGENT_VERSION` trước khi chạy UI; mặc định là `v0`.
Transcript luôn có hash prompt/tools thực tế, không chỉ có nhãn version.
Nếu sửa prompt hoặc `tools.yaml` trong lúc UI chạy, chọn **Cuộc trò chuyện mới**
để nạp lại chúng; mỗi phiên giữ snapshot và hash của lúc bắt đầu. Nếu đổi key
trong `.env`, khởi động lại server.

## Dùng giao diện

- Chọn gợi ý để điền câu hỏi, sau đó bấm gửi hoặc Enter.
- Chat nhiều lượt; agent nhận tối đa 5 cặp user/assistant trước đó làm ngữ cảnh.
- Mỗi yêu cầu có tối đa 4 vòng model/tool, dùng lại vòng lặp trong `chat.py`.
- Lỗi model hiện trên giao diện; lỗi tool hiện kể cả khi model vẫn trả lời.
  Mục **Công cụ & nguồn dữ liệu** chứa arguments và kết quả JSON đã che key/token
  được cấu hình trong môi trường của phiên.
- **Tải hội thoại JSON** tải transcript hiện tại. Sau mỗi lượt, bản thật được lưu
  trong `starter_v0/transcripts/ui_<id>.transcript.json` theo format của lab.
- **Cuộc trò chuyện mới** tạo phiên riêng và bỏ bản chờ gửi; các file hội thoại cũ
  vẫn được giữ.

## Xác nhận gửi Telegram

UI chặn mọi lời gọi `send` từ model và chỉ tạo bản xem trước, kể cả khi model
trả `confirmed=true`. Xem đúng nội dung rồi chọn **Xác nhận gửi** hoặc **Hủy gửi**.
Xác nhận thực thi đúng nội dung đã xem, không gọi lại model để viết lại bản tin.
Gửi yêu cầu chat mới làm mất hiệu lực bản xác nhận đang chờ.

Gửi thật dùng `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID` hiện có. UI chỉ báo
**Đã gửi** khi tool trả `status=sent`; lỗi gửi vẫn được hiển thị và lưu transcript.
UI không tạo tool Telegram mới và không thay đổi implementation tool có sẵn.

## Link dùng thử cho nhóm

Sau khi UI chạy local, nếu đã cài `cloudflared`, mở terminal khác:

```powershell
cloudflared tunnel --url http://localhost:8501
```

URL public được in trong terminal; cập nhật URL thật đó vào mục A1 của báo cáo.
Không commit `.env`, API key hoặc token. Chỉ chia sẻ cho người được phép dùng
quota API và các tool đã cấu hình. UI local chưa có lớp đăng nhập.

## Kiểm tra

```powershell
python -m pytest -q
```

`tests/test_ui.py` dùng fake provider và HTTP mock: không gọi Grok/Telegram thật,
không tạo transcript giả trong repo. Test bao phủ ngữ cảnh, lỗi tool/provider,
che bí mật, xác nhận đúng nội dung, hủy xác nhận cũ và các tương tác Streamlit.

## Ghi chú thiết kế và tích hợp

Giao diện ưu tiên việc đặt câu hỏi, đọc kết quả và kiểm tra nguồn. Repo chưa có
UI hoặc bộ nhận diện trước đó; chọn nền sáng, màu xanh lá đậm, font hệ thống,
sidebar gọn và các điều khiển Streamlit có nhãn rõ ràng. Trạng thái cần thể hiện:
chưa có hội thoại, đang xử lý, hỏi lại, lỗi, bản chờ duyệt, gửi thành công và hủy.
Trên màn hình hẹp, sidebar thu gọn và các cột dùng bố cục responsive của Streamlit.

`ResearchSession` là trạng thái riêng từng browser session; không cache dùng chung
lịch sử hay bản chờ gửi. `run_model_tool_loop` nhận callback `tool_executor` tùy
chọn; khi không truyền callback, CLI giữ cách thực thi trước đó. Các lần gửi được
duyệt có `ui_action=confirm_send` trong transcript để phân biệt với câu trả lời model.

Tham khảo yêu cầu lab trong [slide giảng viên](https://sagitakdx.github.io/k5-day03-instructor-slides/)
và API [chat](https://docs.streamlit.io/develop/api-reference/chat),
[AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
của Streamlit.
