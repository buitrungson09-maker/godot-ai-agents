# Lộ trình Godot AI Agents

> Đây là kế hoạch **dự kiến**, không phải các tính năng đã hoàn thành.

| Giai đoạn | Trạng thái | Mục tiêu / tiêu chí |
|---|---|---|
| 1 — MVP offline | Hoàn thành | Pipeline Planner → Developer → Reviewer và Coordinator chạy deterministic. |
| 2 — Tăng độ tin cậy | Hoàn thành | Kiểm thử đầu vào, source sinh ra, hành vi và điều phối; 40 test pass. |
| 3 — AI Planner v2.0 | Đang hoàn thiện | SDK, structured output, xử lý lỗi, hai mode và test mock đã có; còn smoke test API có kiểm soát khi được cho phép. |
| 4 — Godot Editor MCP | Chưa bắt đầu | Kết nối trên bản sao dự án, ưu tiên tool chỉ đọc và phê duyệt thủ công. |
| 5 — Developer có tool | Chưa bắt đầu | Đề xuất patch trong whitelist; không tự sửa dự án game gốc. |
| 6 — Reviewer thực tế | Chưa bắt đầu | Chạy lint/test Godot và phân biệt test pass với chất lượng nghiệp vụ. |
| 7 — OmniRoute | Hoãn sau v2.0 | Chỉ thiết kế/tích hợp sau khi v2.0 ổn định và dependency được đánh giá. |

## Nguyên tắc
- Không ghi khóa API vào Git.
- Các thao tác ghi, xóa, chạy lệnh cần giới hạn quyền và xác nhận.
- Chỉ đánh dấu hoàn thành khi có commit, bài kiểm thử hoặc minh chứng thực tế.
- Giữ MVP cũ để đối chiếu với bản tích hợp AI.

## Việc còn lại trước khi phát hành v2.0

- Duyệt diff và commit riêng mã nguồn, kiểm thử, tài liệu và dependency pin.
- Chọn model được cấp quyền trước khi chạy smoke test AI có phát sinh chi phí.
- Xác nhận thông báo lỗi CLI và chính sách fallback giữa `ai`/`offline`.
- Chưa đưa Godot MCP hoặc OmniRoute vào tiêu chí phát hành v2.0 này.
