# Godot AI Agents — Trợ lý 4 Agent phát triển game Godot 2D

Dự án Python hỗ trợ phát triển game tu tiên 2D trên **Godot 4**, kế thừa bài tập 3 Agent và phát triển thành bốn vai trò:

- **Coordinator**: Điều phối Planner → Developer → Reviewer, tổng hợp trạng thái.
- **Planner**: Phân tích yêu cầu và đề xuất các bước.
- **Developer**: Sinh mã nguồn Python mẫu (hướng tới GDScript cho Godot).
- **Reviewer**: Kiểm tra tĩnh cú pháp, lớp/hàm và từ khóa hướng di chuyển.

> **Trạng thái v2.0:** Coordinator hỗ trợ hai chế độ Planner: `offline`
> (mặc định, deterministic) và `ai` (OpenAI Agents SDK). Developer và
> Reviewer hiện vẫn là các thành phần mô phỏng/kiểm tra cục bộ. Dự án chưa
> thao tác trực tiếp với Godot và chưa tích hợp OmniRoute.

## Năng lực đã triển khai và giới hạn

| Thành phần | Hiện trạng v2.0 |
| --- | --- |
| Coordinator | Chọn Planner, điều phối pipeline và tổng hợp trạng thái `failed`, `planning_only`, `ready_for_manual_review` |
| Planner | Chạy luật offline hoặc OpenAI Agents SDK với structured output `GamePlan` |
| Developer | Ghi nhật ký mô phỏng và sinh mẫu Python `generated/player.py` |
| Reviewer | Kiểm tra báo cáo mô phỏng, cú pháp AST, class/phương thức `Player` và chuỗi 4 hướng di chuyển |
| Kiểm thử | **40 passed** trong lần xác minh v2.0; AI được mock, không gọi API thật |
| OpenAI Agents SDK | Đã nối vào AI Planner tùy chọn; chưa smoke-test bằng LLM thật |
| Godot Editor MCP | Có ghi nhận thử nghiệm thủ công trên bản sao game; chưa tích hợp vào pipeline và chưa xác nhận kết nối ổn định |

`ready_for_manual_review` **không đồng nghĩa** mã đã được triển khai hoặc game chạy đúng. Kiểm tra AST là kiểm tra tĩnh, không thay thế chạy thử game.

Xem [kiến trúc 4 Agent](docs/architecture.md), [lộ trình và trạng thái](ROADMAP.md), [nhật ký thay đổi](CHANGELOG.md).

## Chạy hai chế độ Planner

Môi trường `.venv-agents` dùng Python 3.11. Cài dependency:

```powershell
cd D:\godot-ai-agents
py -3.11 -m venv .venv-agents
.\.venv-agents\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv-agents\Scripts\python.exe -m pip install -r requirements-agents.txt
```

### Offline — chế độ mặc định

Không cần API key và không gọi dịch vụ AI:

```powershell
.\.venv-agents\Scripts\python.exe coordinator.py
# Tương đương:
.\.venv-agents\Scripts\python.exe coordinator.py --mode offline
```

### AI Planner

Chế độ này cần API key thật và có thể phát sinh chi phí. Chỉ đặt biến môi
trường trong Terminal; không ghi khóa vào file hoặc Git:

```powershell
$env:OPENAI_API_KEY = Read-Host "OPENAI_API_KEY"
$env:OPENAI_MODEL = "TEN_MODEL_DUOC_CAP_QUYEN"
.\.venv-agents\Scripts\python.exe coordinator.py --mode ai
```

AI Planner chỉ lập kế hoạch có cấu trúc. Developer và Reviewer tiếp tục xử lý
cục bộ; mọi file sinh ra vẫn cần được duyệt thủ công.

Ví dụ yêu cầu: `Tao nhan vat di chuyen trong game 2D`.

Lưu ý: file được sinh ra nằm trong `generated/`. **Không tự động chép hay ghi đè file trong game Godot thật.** Quy trình duyệt thủ công phải được duy trì.

## Hai dự án mã nguồn mở được chọn

| Dự án | GitHub upstream | Cách sử dụng |
| --- | --- | --- |
| **OpenAI Agents SDK** | https://github.com/openai/openai-agents-python | Thư viện Python chuẩn bị cho bước chuyển sang LLM |
| **Godot Editor MCP** | https://github.com/hybridindie/godot-mcp | MCP server + Godot addon để kết nối AI với editor |

Repository **khai báo dependency và ghi tài liệu tích hợp**, không sao chép
toàn bộ source của hai dự án upstream. OpenAI Agents SDK đã được nối vào nhánh
AI Planner; Godot Editor MCP chưa được nối vào pipeline.

Hướng dẫn chi tiết cho Windows, phiên bản, môi trường Python tách biệt, addon Godot và an toàn:

**[docs/OPEN_SOURCE_INTEGRATIONS.md](docs/OPEN_SOURCE_INTEGRATIONS.md)**.

### Cài tùy chọn

- OpenAI Agents SDK: `requirements-agents.txt` và demo `examples/sdk_smoke.py` (cần `OPENAI_API_KEY`; có thể phát sinh chi phí).
- Godot Editor MCP: `requirements-godot-mcp.txt` (cần addon trong Godot; nên dùng Python 3.11 riêng).

Godot Editor MCP không cần thiết để chạy pipeline hoặc bộ kiểm thử hiện tại.

## Cấu trúc

```text
godot-ai-agents/
├── coordinator.py
├── ai_planner.py
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

## Kiểm thử

Bộ kiểm thử dùng mock cho AI Planner, vì vậy không cần API key và không gọi API:

```powershell
.\.venv-agents\Scripts\python.exe -m pytest -q tests
.\.venv-agents\Scripts\python.exe -m pip check
```

Lần xác nhận gần nhất trên nhánh `feature/v2.0-ai-planner`: **40 passed**,
`pip check` không phát hiện dependency hỏng. Đây là kiểm thử Python; không đồng
nghĩa game đã được chạy hoặc kiểm thử trong Godot Engine.

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
