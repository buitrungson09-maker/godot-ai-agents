# Godot AI Agents — Trợ lý 4 Agent phát triển game Godot 2D

Dự án Python hỗ trợ phát triển game tu tiên 2D trên **Godot 4**, kế thừa bài tập 3 Agent và phát triển thành bốn vai trò:

- **Coordinator**: Điều phối Planner → Developer → Reviewer, tổng hợp trạng thái.
- **Planner**: Phân tích yêu cầu và đề xuất các bước.
- **Developer**: Sinh mã nguồn Python mẫu (hướng tới GDScript cho Godot).
- **Reviewer**: Kiểm tra tĩnh cú pháp, lớp/hàm và từ khóa hướng di chuyển.

> **Trạng thái:** v1.6 là hệ thống Python **offline/deterministic**, chưa phải bốn AI Agent chạy bằng LLM, chưa thao tác trực tiếp với Godot. Kết quả kiểm thử baseline đã được xác nhận là **22 passed** trước khi thêm dependency. Kiểm tra tĩnh không đồng nghĩa đã kiểm tra hành vi khi chạy game.

## Bắt đầu với pipeline hiện có

Cần Python 3.12+ và VS Code/PowerShell (người phát triển đang sử dụng Python 3.14).

```powershell
cd D:\godot-ai-agents
python -m pip install -r requirements-dev.txt
python coordinator.py
python -m pytest -v tests
```

Ví dụ yêu cầu: `Tao nhan vat di chuyen trong game 2D`.

Lưu ý: file được sinh ra nằm trong `generated/`. **Không tự động chép hay ghi đè file trong game Godot thật.** Quy trình duyệt thủ công phải được duy trì.

## Hai dự án mã nguồn mở được chọn

| Dự án | GitHub upstream | Cách sử dụng |
| --- | --- | --- |
| **OpenAI Agents SDK** | https://github.com/openai/openai-agents-python | Thư viện Python chuẩn bị cho bước chuyển sang LLM |
| **Godot Editor MCP** | https://github.com/hybridindie/godot-mcp | MCP server + Godot addon để kết nối AI với editor |

Repository **khai báo dependency và ghi tài liệu tích hợp**, không sao chép toàn bộ source của hai dự án upstream và **chưa kết nối chúng vào pipeline đang chạy**.

Hướng dẫn chi tiết cho Windows, phiên bản, môi trường Python tách biệt, addon Godot và an toàn:

**[docs/OPEN_SOURCE_INTEGRATIONS.md](docs/OPEN_SOURCE_INTEGRATIONS.md)**.

### Cài tùy chọn

- OpenAI Agents SDK: `requirements-agents.txt` và demo `examples/sdk_smoke.py` (cần `OPENAI_API_KEY`; có thể phát sinh chi phí).
- Godot Editor MCP: `requirements-godot-mcp.txt` (cần addon trong Godot; nên dùng Python 3.11 riêng).

Không cần hai dependency này để chạy 22 bài kiểm thử offline đang có.

## Cấu trúc

```text
godot-ai-agents/
├── coordinator.py
├── planner.py
├── developer.py
├── reviewer.py
├── main.py
├── tests/
├── generated/
├── examples/sdk_smoke.py
├── requirements-dev.txt
├── requirements-agents.txt
├── requirements-godot-mcp.txt
└── docs/OPEN_SOURCE_INTEGRATIONS.md
```

## Quy tắc an toàn

- Không commit API key, token, `.env` hoặc thư mục môi trường ảo.
- Thử Agent và Godot MCP trên **bản sao dự án game**, đọc dữ liệu trước khi cấp quyền sửa.
- Xem diff, duyệt thủ công và chạy test trước khi chép kết quả vào game chính.
- Chỉ ghi nhận PASS nếu đã chạy kiểm thử và có bằng chứng.

## Nguồn học tập và tiến độ

- [Tài liệu kiến trúc](docs/architecture.md)
- [Ghi chú AI Agent](docs/ai-agent-notes.md)
- [ROADMAP.md](ROADMAP.md) · [CHANGELOG.md](CHANGELOG.md) · [RESOURCES.md](RESOURCES.md)
- [Tài liệu OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Tài liệu Godot Editor MCP](https://hybridindie.github.io/godot-mcp/)

Lịch sử phát triển từ dự án Python giữa kỳ được bảo toàn khi tách repository. Hai dự án upstream đều phát hành dưới giấy phép **MIT**; khi phân phối bản sao mã upstream phải giữ các thông báo giấy phép liên quan.
