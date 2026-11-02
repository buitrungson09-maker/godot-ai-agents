# Nhật ký thay đổi

## 2026-11-02 — Chuẩn bị Godot AI Agents v2.1

### Thêm mới

- Thêm `llm_router.py` với hai provider `direct` và `omniroute`.
- OmniRoute dùng `AsyncOpenAI` và `OpenAIChatCompletionsModel` của Agents SDK.
- Thêm `.env.example` chỉ chứa tên biến và giá trị mẫu không bí mật.
- Thêm kiểm thử cấu hình, custom client, bảo vệ API key và tích hợp Planner.

### Giới hạn đã xác nhận

- Không có fallback tự động giữa các provider.
- Offline vẫn là chế độ mặc định; direct giữ cấu hình OpenAI của v2.0.
- Chưa gọi API thật, chưa cài/chạy OmniRoute Server và chưa kiểm thử Godot.

### Xác minh

- Toàn bộ bộ test: **59 passed** bằng `.venv-agents` Python 3.11.
- `pip check`: không phát hiện dependency hỏng.

## 2026-11-02 — Chuẩn bị Godot AI Agents v2.0

### Thêm mới

- Thêm AI Planner dùng OpenAI Agents SDK và Pydantic `GamePlan`.
- Thêm hai chế độ Coordinator: `offline` mặc định và `ai` tùy chọn.
- Thêm CLI `--mode {offline,ai}`.
- Thêm kiểm thử AI Planner và chế độ Coordinator bằng mock, không gọi API thật.

### Cải thiện

- Cho phép truyền hàm Planner vào pipeline để giữ luồng offline độc lập.
- Xử lý đầu vào thiếu, cấu hình môi trường thiếu, output sai cấu trúc và lỗi Runner.
- Ghim `pywin32` tương thích Python 3.11 trên Windows.
- Bổ sung ignore cho môi trường ảo, secret, cache, coverage và thư mục test tạm.

### Xác minh

- Toàn bộ bộ test: **40 passed** bằng `.venv-agents` Python 3.11.
- `pip check`: không phát hiện dependency hỏng.
- Chưa gọi API thật, chưa chạy Godot và chưa tích hợp OmniRoute.

## 2026-11-02 — Đồng bộ tài liệu kiến trúc 4 Agent

- Cập nhật tài liệu kiến trúc theo `coordinator.py`, `planner.py`, `developer.py`, `reviewer.py` hiện có trên `main`.
- Phân biệt rõ: Developer sinh mẫu `player.py` nhưng chưa sinh GDScript; Reviewer kiểm tra AST, không chạy game.
- Cập nhật ROADMAP, đánh dấu phần OpenAI Agents SDK/LLM và Codex ↔ Godot MCP là hướng tích hợp đang phát triển.
- Ghi nhận kết nối MCP thủ công với bản sao Godot từng thành công; kết nối từ Codex chưa ổn định.
- Chỉ thay đổi **tài liệu**, không thay đổi mã nguồn hay chạy lại test khi cập nhật các tài liệu này.

## Giai đoạn v1.6 — Pipeline 4 vai trò offline

- Bổ sung Coordinator điều phối Planner → Developer → Reviewer, tổng hợp trạng thái.
- Developer có chức năng sinh file Python mẫu vào thư mục `generated/`.
- Reviewer có kiểm tra tĩnh cú pháp và cấu trúc mẫu `Player` bằng AST.
- README ghi nhận kết quả baseline **22 passed** trước khi bổ sung dependency; không suy ra kết quả các phiên bản về sau.

## 2026-10-28 — Bổ sung tài nguyên học tập

- Thêm mô tả kiến trúc và ghi chú thuật ngữ AI Agent.
- Thêm ví dụ đầu vào và dữ liệu thử minh họa.
- Thêm tài liệu tham khảo, lộ trình phát triển và liên kết từ README.
- Không thay đổi các hàm Planner/Developer/Reviewer trong lần cập nhật tài liệu đó.

## MVP Week 09 — Trước đó

- Triển khai pipeline Python offline gồm 3 vai trò mô phỏng.
- Có bộ 6 bài kiểm thử trong `tests/test_agents.py` ở giai đoạn ban đầu.
- Xem lịch sử commit GitHub để xác nhận thời điểm và nội dung từng lần thay đổi.
