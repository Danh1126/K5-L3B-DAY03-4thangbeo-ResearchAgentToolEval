# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: 4thangbeo
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Research Desk hỗ trợ tìm kiếm tin trên web và X/Twitter, tra cứu chính sách/paper, đọc URL hoặc tóm tắt Wikipedia, rồi tổng hợp kết quả 
thành bản tin. Agent cũng có thể tìm repository GitHub, lấy paper nổi bật từ Hugging Face và lưu ghi chú cục bộ; mọi thao tác gửi lên 
Telegram đều cần người dùng xác nhận trước.

**Cách chạy UI:**

Từ thư mục `starter_v0/`, chạy `python -m streamlit run app.py`. Dependency giao diện Streamlit được khai báo trong `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
(https://k5-l3b-day03-4thangbeo-m2o8.onrender.com/)

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
| timeline | lấy các bài đăng gần đây từ tài khoản X/Twitter cụ thể | không |
| social_search | tìm bài đăng X/Twitter theo từ khóa hoặc chủ đề | không |
| lookup | tìm thông tin và tin tức trên web | không |
| fetch | đọc và trích xuất nội dung từ URL cụ thể | không |
| format | tổng hợp dữ liệu đã thu thập thành digest Markdown | không |
| send | gửi nội dung lên Telegram sau khi người dùng xác nhận | không |
| policy | tra cứu chính sách và quy định nội bộ của công ty | không |
| papers | tìm bài báo khoa học trên arXiv | không |
| paper_text | tải PDF arXiv và trích xuất nội dung văn bản | không |
| github_search | tìm repository GitHub theo chủ đề, ngôn ngữ và mức độ phổ biến | đúng |
| wiki_summary | lấy tóm tắt chủ đề từ Wikipedia tiếng Anh hoặc tiếng Việt | đúng |
| hf_papers | tìm bài báo AI nổi bật trên Hugging Face Daily Papers | đúng |
| save_note | lưu ghi chú nghiên cứu thành file Markdown cục bộ | đúng |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. Tin tức AI hôm nay có gì nổi bật?
2. Tìm 3 repository GitHub về agent viết bằng Python, sắp xếp theo số sao.
3. Tóm tắt Wikipedia tiếng Việt về trí tuệ nhân tạo.
4. Có những paper AI nào nổi bật trên Hugging Face Daily Papers hôm nay?
5. Lưu ghi chú nghiên cứu với tiêu đề “Agent Eval Notes” và nội dung “Các kết quả cần xem lại”.


## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

- `system_prompt.md` quy định agent phải hỏi lại khi thiếu handle hoặc URL thay vì đoán; luôn xin xác nhận yes/no trước khi gửi/đăng và chỉ gọi `send` với `confirmed=true` sau khi người dùng đồng ý. Prompt cũng hướng dẫn gọi song song `lookup` và `social_search` khi cần cả nguồn web lẫn mạng xã hội, giữ `lookup.query` chỉ gồm từ khóa chủ đề, và trả lời trực tiếp các yêu cầu ngoài phạm vi tool.
- `tools.yaml` mô tả mục đích, trường hợp nên/không nên dùng và quy ước đối số của từng tool; bổ sung schema cho 4 tool mới, đồng thời làm rõ ranh giới xác nhận của `send` và cách phân biệt các nguồn tìm kiếm.
- Nhóm tự viết và đăng ký 4 tool mới trong `tools/__init__.py` và `tools.yaml`:
  - `github_search`: tìm repository GitHub theo chủ đề, lọc ngôn ngữ và sắp xếp theo sao/cập nhật; dùng khi người dùng cần tìm dự án hoặc thư viện mã nguồn mở.
  - `wiki_summary`: lấy tóm tắt một chủ đề từ Wikipedia tiếng Anh hoặc tiếng Việt; dùng khi người dùng yêu cầu nguồn Wikipedia, không dùng thay tìm tin mới.
  - `hf_papers`: lấy danh sách paper AI nổi bật từ Hugging Face Daily Papers, có thể lọc từ khóa; dùng cho yêu cầu paper trending, còn tìm học thuật tổng quát thì dùng `papers`.
  - `save_note`: lưu tiêu đề và nội dung thành file Markdown trong `notes/`; chỉ dùng khi người dùng yêu cầu lưu ghi chú, không dùng thay gửi Telegram hoặc chỉ trình bày câu trả lời.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | Baseline configuration | Initial baseline measurement for tool routing and argument accuracy on the core research agent benchmark. | - | Case Acc: 55.0% (11/20)<br>Routing Acc: 75.0%<br>Arg Acc: 55.0% | `v0_B_base_openai_20261110T175050488620.json` |
| v2 | `tools.yaml` | Optimizing tool definitions and parameter schemas reduces argument value errors and improves multi-turn context retention. | Case Acc: 70.0% (14/20) | Case Acc: 90.0% (18/20)<br>Routing Acc: 95.0%<br>Multi-turn Acc: 100.0% | `v2_B_base_openai_20261110T182303997939.json` |
| v3 | `system_prompt.md` & `tools.yaml` | Aligning system prompt rules with tool definition constraints fixes edge-case query formatting mismatches. | Case Acc: 90.0% (18/20) | Case Acc: 95.0% (19/20)<br>Routing Acc: 95.0%<br>Arg Acc: 95.0% | `v3_B_base_openai_20261110T184305315541.json` |
| v4 | `tools.yaml` & `eval_group.json` | Supporting new tools (`github_search`, `wiki_summary`, `hf_papers`, `save_note`) enables full pass rate on custom group evaluation cases. | Case Acc: 95.0% (19/20 base) | Case Acc: 100.0% (10/10)<br>Routing Acc: 100.0%<br>Arg Acc: 100.0% | `v4_B_group_openai_20261110T191704104430.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_tool | lookup(query="AI news", topic="news", max_results=5)  | Expected query="AI", got query="AI news" |  |
| R08_out_of_scope | out_of_scope | send(text="Nguyên hàm của x^2 là...")  |Expected no tool call, but model called send tool with calculus solution |  |
| R10_missing_handle | missing_info | timeline(screenname="sama") | Missing tool call clarify and extra tool call timeline. Guessed handle sama instead of asking user |  |
| R11_missing_url | wrong_tool | fetch(url="[https://example.com/article]")  | Missing tool call clarify and extra tool call fetch. Used placeholder URL |  |
| R12_confirm_before_send | wrong_boundary | send(text="Bản tin này")  | Missing tool call clarify and extra tool call send. Executed write/send action without user confirmation. |  |
| R13_parallel_web_and_tweets | wrong_tool | lookup(query="AI news", timeframe="day", max_results=5), social_search(query="AI", search_type="Latest", limit=5)  | Expected query="AI" and topic="news", but got query="AI news" and topic=None |  |
| R14_out_of_scope_coding | out_of_scope | send(text="Dưới đây là một hàm Python...") | Expected no tool call, but model called send tool with Python code | |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| `G01_github_search_routing` | Tìm repo GitHub theo ngôn ngữ và độ phổ biến. | `github_search(language="Python", sort_by="stars", limit=3)` | PASS — run group v4 |
| `G02_wiki_summary_routing` | Tóm tắt Wikipedia tiếng Việt, không dùng tìm kiếm web chung. | `wiki_summary(lang="vi")` | PASS — run group v4 |
| `G03_hf_papers_routing` | Tìm paper nổi bật trên Hugging Face Daily Papers, không nhầm với arXiv. | `hf_papers(limit=5)` | PASS — run group v4 |
| `G04_missing_github_query` | Thiếu chủ đề tìm repo thì hỏi lại, không tự bịa query. | `clarify(response_type="text")` | PASS — run group v4 |
| `G05_no_tool_translate` | Dịch thuật đơn thuần không cần nghiên cứu hay lưu file. | Trả lời trực tiếp; không gọi tool. | PASS — run group v4 |
| `GM01_github_clarify_then_fill` | Nhiều lượt bổ sung chủ đề, ngôn ngữ và cách sắp xếp; giữ giới hạn 5. | `github_search(language="TypeScript", sort_by="stars", limit=5)` | PASS — run group v4 |
| `GM02_save_note_research` | Nhiều lượt cung cấp tiêu đề/nội dung rồi yêu cầu lưu ghi chú cục bộ. | `save_note(title="Agent Eval Notes")` | PASS — run group v4 |
| `GM03_switch_arxiv_to_hf_papers` | Đổi yêu cầu từ arXiv sang Hugging Face Daily Papers và lấy 3 bài. | `hf_papers(limit=3)` | PASS — run group v4 |
| `GM04_switch_web_to_wiki` | Đổi từ tìm web sang tóm tắt Wikipedia tiếng Anh; không tiếp tục gọi tìm web. | `wiki_summary(lang="en")` | FAIL — gọi thêm `lookup`; run group v4 |
| `GM05_policy_carryover_area` | Nhiều lượt giữ lĩnh vực bảo mật dữ liệu và giới hạn số đoạn policy. | `policy(policy_area="data_privacy", top_k=2)` | PASS — run group v4 |


### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.
Số test đã viết: 12 tests (3 tests/tool × 4 tools: github_search, wiki_summary, hf_papers, save_note )
- Lỗi không xử lý ngoại lệ khi API trả về mã lỗi HTTP 429 (Too Many Requests) hoặc HTTP 500 (Server Error).
Chi tiết: Tập đánh giá eval_group.json tập trung vào luồng chạy chuẩn (happy path) để đo độ chính xác routing và argument của agent. Nếu API bên ngoài bị nghẽn mạng, eval chỉ ghi nhận agent thất bại chung chung. Trong khi đó, Unit Test sử dụng unittest.mock giả lập phản hồi HTTP status 429/500 sẽ bắt được ngay lỗi thiếu khối try-except trong file tool.py, ngăn chương trình bị crash đột ngột.   
### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
