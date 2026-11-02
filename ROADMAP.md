# Lộ trình Godot AI Agents (4 Agent)

> Phân biệt rõ **đã có trong mã nguồn**, **đã thử nghiệm bên ngoài pipeline**, và **chưa hoàn thành**. Mốc kiểm thử baseline được trích từ README; không phải một lần chạy test mới.

| Giai đoạn | Nội dung | Trạng thái |
| --- | --- | --- |
| 1. MVP 3 Agent | Planner → Developer mô phỏng → Reviewer, chạy bằng CLI | Đã xây dựng |
| 2. Bổ sung Coordinator | Điều phối và tổng hợp trạng thái pipeline | Đã xây dựng trên `main` |
| 3. Sinh mã Python mẫu | Tạo `generated/player.py` với lớp Player và bốn hướng di chuyển | Đã có trong mã nguồn |
| 4. Reviewer tĩnh | Phân tích AST, kiểm tra phương thức và hướng di chuyển | Đã có trong mã nguồn |
| 5. Bộ kiểm thử offline | README ghi nhận baseline 22 bài pytest đạt | Đã ghi nhận trong README; cần chạy lại để xác nhận phiên bản mới |
| 6. Chuẩn bị nguồn mở | Khai báo dependency và tài liệu cho OpenAI Agents SDK, Godot Editor MCP | Đã chuẩn bị; chưa nối vào pipeline |
| 7. Kết nối MCP với Godot | Chạy trên bản sao dự án, đọc scene và node qua Codex | Đang thử nghiệm; Codex từng báo `connected: false` |
| 8. Agent dùng LLM | Planner/Developer/Reviewer sử dụng mô hình AI thực | Chưa hoàn thành |
| 9. GDScript và kiểm thử game | Đề xuất bản vá, chạy lint/test, đối chiếu gameplay Godot | Chưa hoàn thành |
| 10. Demo end-to-end | Yêu cầu → kế hoạch → code → review → người dùng duyệt → áp dụng bản sao | Mục tiêu tương lai |

## Ưu tiên gần nhất

1. Ổn định cầu nối Codex ↔ Godot Editor MCP trên bản sao `TuTien2D_MCP_Test` (cổng 9081), xác minh `connected: true`.
2. Ghi nhận log/bằng chứng đọc scene ở chế độ chỉ đọc trước khi cấp quyền sửa.
3. Tích hợp LLM Planner qua OpenAI Agents SDK trong nhánh thử nghiệm riêng.
4. Nâng cấp Developer từ mẫu Python cố định sang đề xuất GDScript, giới hạn đường dẫn ghi.
5. Bổ sung kiểm thử hành vi thực tế và cơ chế phê duyệt thủ công.

## Nguyên tắc an toàn

- Không đưa API key, token, `.env` hay thư mục venv lên Git.
- Không thao tác trên dự án Godot gốc khi chưa có phê duyệt; chỉ thử trên bản sao.
- Không coi `passed: true` của kiểm tra tĩnh là bằng chứng game chạy đúng.
- Kiểm tra diff và chạy test trước khi nhập kết quả vào dự án chính.
