# Báo cáo cá nhân — Nguyen Thanh Tung - 2A202603807

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Thanh Tùng
- MSSV: 2A202603807
- Email: 26ai.tungnt7@vinuni.edu.vn

## 2. Phần việc phụ trách

- Thiết lập môi trường (`starter_v0/.venv` Python 3.12, `.env`, cấu hình `starter_v0/providers/openai_provider.py` chạy Groq `openai/gpt-oss-20b`).
- Chạy baseline `v0` (CP1) và thực hiện vòng lặp tối ưu `v1` → `v2` → `v3` (CP2) dựa trên bằng chứng run JSON.
- Hỗ trợ xây dựng 4 tool mới và bộ unit test offline (CP3 + Bonus ≥ 4 tool mới).
- Hỗ trợ và góp ý trong việc thiết kế bộ 10 eval case của nhóm.
- Phối hợp hoàn thiện báo cáo nhóm (`report/team/group_report.md`). 

## 3. Đóng góp cụ thể

- **CP1 & CP2 :**
  - Chạy baseline `v0` (`case_accuracy = 0.55`, 11/20 pass) và phân loại lỗi (`R10`–`R14` do rule đoán bừa / tự gửi / ép 1 tool trong prompt starter; `R01`, `R03`, `M02`, `M06` do thiếu quy ước args).
  - `v1` : Gỡ bỏ 3 chỉ dẫn xấu của starter, bổ sung rule gọi `clarify`, xác nhận trước `send`, cho phép gọi nhiều tool và trả lời trực tiếp với câu ngoài phạm vi.
  - `v2` : Viết lại `description`  và chuẩn hóa quy ước `lookup.query`, `clarify.response_type`, `timeline.screenname`, boundary `send(confirmed=true)` 
  - `v3` : Tách rõ `clarify(response_type="yes_no")` cho bước xác nhận `send` và `clarify(response_type="text")` cho thông tin thiếu, giữ `lookup.query` sạch 
- **CP3 (4 tool mới + unit test offline):**
  - Hỗ trợ viết 4 tool mới không cần API key trả phí: `github_search`, `wiki_summary`, `hf_papers`, `save_note` 
- **CP4 (10 eval case nhóm):**
  - Hỗ trợ kiểm tra routing cho cả 4 tool mới của nhóm 

## 4. Bằng chứng

- **File / commit / run:**
  - Commit CP2: `a005646` (`first commit : cp2`) — cập nhật `starter_v0/artifacts/system_prompt.md`, `tools.yaml`, `version_log.csv` và các run `v0`–`v3`.
  - Run baseline & tối ưu (`starter_v0/runs/`):
    - `v0_B_base_openai_20261110T175050488620.json` (`0.55`, 11/20)
    - `v1_B_base_openai_20261110T180452641851.json` (`0.70`, 14/20)
    - `v2_B_base_openai_20261110T182303997939.json` (`0.90`, 18/20)
    - `v3_B_base_openai_20261110T184305315541.json` (`0.95`, 19/20)

- **AI / công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Công cụ AI: Trợ lý lập trình AI (Antigravity / Gemini) hỗ trợ phân tích log FAIL từ run JSON `v0`–`v3`, đề xuất giả thuyết sửa prompt/`tools.yaml`, hỗ trợ kiểm thử CP3/ CP4 với đồng đội.
  - Cách tự kiểm tra độc lập:
    1. Chạy `run_eval.py --provider openai` cho `v0`–`v3` (`eval_base.json`) , tự đối chiếu từng file JSON trong `runs/` xác nhận `provider_error_cases == 0` và hash `prompt_hash`/`tools_hash` khớp với `version_log.csv`.
    2. Chạy `pytest` offline .

## 5. Tự đánh giá

- **Điểm làm tốt:** Tuân thủ quy trình evidence-driven từ `v0` (0.55) lên `v3` (0.95) với giả thuyết rõ ràng và hash khớp log; hỗ trợ thiết kế 4 tool mới độc lập, có validate input an toàn và test offline đầy đủ; kiểm thử  đạt 10/10 trên bộ `eval_group.json` của thành viên nhóm.
- **Hạn chế & hướng cải thiện:** Model `openai/gpt-oss-20b` vẫn chưa phát 2 tool call song song ở case `R13_parallel_web_and_tweets`; py chưa mở hết nếu muốn lấy thêm Bonus Test Challenge.
