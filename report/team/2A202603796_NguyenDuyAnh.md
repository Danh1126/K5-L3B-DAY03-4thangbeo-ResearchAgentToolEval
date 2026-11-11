# Báo cáo cá nhân — HoVaTen-MSSV

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên:Nguyễn Duy Anh
- MSSV: 2A202603796
- Email: duy021101@gmail.com

## 2. Phần việc phụ trách

- Thiết lập môi trường (`starter_v0/.venv` Python 3.12, `.env`, cấu hình `starter_v0/providers/openai_provider.py` chạy Groq `openai/gpt-oss-20b`).
- Chạy baseline `v0` (CP1) và test lại `v1` → `v2` → `v3` của các thành vien
- Hỗ trợ xây dựng 4 tool mới và bộ unit test offline (CP3 + Bonus ≥ 4 tool mới).
- Hỗ trợ và góp ý trong việc thiết kế bộ 10 eval case của nhóm.
- Phối hợp hoàn thiện báo cáo nhóm (`report/team/group_report.md`).

## 3. Đóng góp cụ thể

  - Chạy baseline `v0` 
  - Hỗ trợ viết 4 tool mới không cần API key trả phí: `github_search`, `wiki_summary`, `hf_papers`, `save_note` 
  - Hỗ trợ kiểm tra routing cho cả 4 tool mới của nhóm 
  - Hoàn thành các đầu mục B trong (`report/team/group_report.md`)
## 4. Bằng chứng

- File/commit/PR: https://github.com/Danh1126/K5-L3B-DAY03-4thangbeo-ResearchAgentToolEval/commit/8754e8a5eacf25d9ac34797212d540fad663b9fc, https://github.com/Danh1126/K5-L3B-DAY03-4thangbeo-ResearchAgentToolEval/commit/b8f06ef8e8d7652c1178ba7980b73c9ec3d6c7ad, ...
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: 
Trợ lý lập trình AI  (Gemini) hỗ trợ phân tích log FAIL, hỗ trợ kiểm thử CP2 / CP3 / CP4 với đồng đội.

cách tự kiểm tra:
    1. Chạy `run_eval.py --provider openai` cho `v0` rồi check lại qua các v1-v4 , tự đối chiếu từng file JSON trong `runs/` xác nhận `provider_error_cases == 0` và hash `prompt_hash`/`tools_hash` khớp với `version_log.csv`.
    2. Chạy `pytest` offline .

## 5. Tự đánh giá

...
