# Nhật ký thay đổi

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

## 2026-10-28 — Bổ sung tài nguyên học tập
- Thêm mô tả kiến trúc và ghi chú thuật ngữ AI Agent.
- Thêm ví dụ đầu vào và dữ liệu thử minh họa.
- Thêm tài liệu tham khảo, lộ trình phát triển và liên kết từ README.
- Không thay đổi các hàm Planner/Developer/Reviewer; không tuyên bố đã kiểm thử phiên bản tài liệu này.

## MVP Week 09 — Trước đó
- Triển khai pipeline Python offline gồm 3 vai trò mô phỏng.
- Có bộ 6 bài kiểm thử trong `tests/test_agents.py`.
- Xem lịch sử commit GitHub để xác nhận thời điểm và nội dung từng lần thay đổi.
