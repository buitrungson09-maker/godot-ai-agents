# Nhật ký thay đổi

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
