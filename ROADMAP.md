# Lộ trình Godot AI Agents (4 Agent)

> Phân biệt rõ **đã có trong mã nguồn**, **đã thử nghiệm bên ngoài pipeline**,
> và **chưa hoàn thành**. Kết quả 40 test là lần xác minh Python v2.0; không
> phải bằng chứng game đã chạy đúng trong Godot.

| Giai đoạn | Trạng thái | Mục tiêu / tiêu chí |
| --- | --- | --- |
| 1 — MVP offline | Hoàn thành | Pipeline Planner → Developer → Reviewer và Coordinator chạy deterministic. |
| 2 — Tăng độ tin cậy | Hoàn thành | Kiểm thử đầu vào, source Python sinh ra, AST, hành vi và điều phối; 40 test pass. |
| 3 — AI Planner v2.0 | Đang hoàn thiện | SDK, `GamePlan`, xử lý lỗi, hai mode và test mock đã có; chưa smoke-test API thật. |
| 4 — Godot Editor MCP | Chưa tích hợp | Có thử nghiệm thủ công được ghi nhận trên bản sao game; kết nối chưa được xác nhận ổn định trong pipeline. |
| 5 — Developer có tool | Chưa bắt đầu | Đề xuất GDScript/patch trong whitelist; không tự sửa dự án game gốc. |
| 6 — Reviewer thực tế | Chưa bắt đầu | Chạy lint/test Godot và phân biệt test pass với chất lượng nghiệp vụ. |
| 7 — Demo end-to-end | Mục tiêu tương lai | Yêu cầu → kế hoạch → patch → review → người dùng duyệt → áp dụng trên bản sao. |
| 8 — OmniRoute | Hoãn sau v2.0 | Chỉ đánh giá và tích hợp sau khi v2.0 ổn định. |

## Năng lực offline đã có

- Coordinator tổng hợp các trạng thái `failed`, `planning_only` và
  `ready_for_manual_review`.
- Planner offline phân loại yêu cầu và tạo kế hoạch deterministic.
- Developer mô phỏng công việc, sinh mẫu Python `generated/player.py` và một
  mẫu GDScript kỹ năng; chưa phải Developer LLM tổng quát.
- Reviewer kiểm tra báo cáo, AST, class/phương thức và bốn hướng di chuyển;
  không chạy game Godot.

## Ưu tiên gần nhất

1. Hoàn tất review và phát hành nhánh AI Planner v2.0.
2. Chọn model được cấp quyền trước khi chạy smoke test API có kiểm soát chi phí.
3. Xác nhận chính sách lỗi/fallback giữa `ai` và `offline`.
4. Chỉ sau v2.0 mới đánh giá lại cầu nối Godot MCP trên bản sao dự án, ưu tiên
   thao tác chỉ đọc và bằng chứng `connected: true`.
5. Nâng cấp Developer/Reviewer theo whitelist và phê duyệt thủ công.

## Nguyên tắc an toàn

- Không đưa API key, token, `.env` hay thư mục venv lên Git.
- Không thao tác trên dự án Godot gốc khi chưa có phê duyệt; chỉ thử trên bản sao.
- Không coi `passed: true` của kiểm tra tĩnh là bằng chứng game chạy đúng.
- Kiểm tra diff và chạy test trước khi nhập kết quả vào dự án chính.
- Giữ MVP offline để đối chiếu với bản tích hợp AI.
