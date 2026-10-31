# Tích hợp mã nguồn mở cho Godot AI Agents

Tài liệu này ghi nhận **hai dự án mã nguồn mở được chọn** để nâng cấp hệ thống Coordinator → Planner → Developer → Reviewer. Chúng được khai báo dưới dạng **dependency ngoài**, không sao chép toàn bộ mã upstream vào repository.

| Thành phần | Repository upstream | Vai trò | Giấy phép |
| --- | --- | --- | --- |
| OpenAI Agents SDK | https://github.com/openai/openai-agents-python | Agent, Runner, tools, MCP, handoffs | MIT |
| Godot Editor MCP | https://github.com/hybridindie/godot-mcp | MCP server điều khiển Godot Editor qua addon | MIT |

## Trạng thái hiện tại

- Pipeline Python offline và **22 bài kiểm thử** là baseline đã xác nhận trước khi thêm hai dependency.
- Hai file `requirements-*.txt` chỉ khai báo thư viện để người dùng **tự cài**; push lên GitHub **không tự cài** vào máy.
- `examples/sdk_smoke.py` là demo **một** AI Agent dùng LLM (chỉ chạy khi có khóa API); không thay thế bốn vai trò của pipeline hiện tại.
- **Chưa kết nối** OpenAI Agents SDK với `coordinator.py`; **chưa kết nối** MCP với Godot; **chưa chạy Godot hay thực thi game thật**. Không xem việc thêm dependency là tích hợp hoàn chỉnh.

## 1. OpenAI Agents SDK — cài trên Windows/VS Code

Ở `D:\godot-ai-agents` trong PowerShell:

```powershell
python -m venv .venv-agents
.\.venv-agents\Scripts\python.exe -m pip install -r requirements-agents.txt
.\.venv-agents\Scripts\python.exe -c "from agents import Agent, Runner; print('Agents SDK import OK')"
```

Chạy demo LLM **chỉ nếu bạn muốn gọi API** (có thể phát sinh chi phí). Thiết lập khóa trong phiên Terminal của bạn, **không ghi khóa vào file Git**:

```powershell
$env:OPENAI_API_KEY = Read-Host "OPENAI_API_KEY"
.\.venv-agents\Scripts\python.exe examples\sdk_smoke.py
```

**Không đưa `OPENAI_API_KEY` vào README, file nguồn, commit hoặc ảnh chụp màn hình.** Nếu chưa có khóa, vẫn chạy pipeline offline và pytest bình thường.

## 2. Godot Editor MCP — cài riêng

Upstream hiện công bố phiên bản `2026.10.24`, yêu cầu **Godot 4.4+**, **Python 3.11+**; README upstream khuyến nghị Python 3.13, nhưng CI tại thời điểm tham khảo chỉ kiểm thử 3.11. Vì vậy nên **dùng Python 3.11 cho MCP** thay vì môi trường Python 3.14 hiện tại.

Kiểm tra Python 3.11 trên Windows:

```powershell
py -3.11 --version
```

Nếu chưa có, cài Python 3.11 rồi tạo venv riêng:

```powershell
py -3.11 -m venv .venv-godot-mcp
.\.venv-godot-mcp\Scripts\python.exe -m pip install -r requirements-godot-mcp.txt
.\.venv-godot-mcp\Scripts\godot-editor-mcp.exe --help
```

Cài **Godot Editor MCP - Addon** từ https://github.com/hybridindie/godot-mcp/releases hoặc Godot Asset Store **vào một bản sao dự án Godot**. Mở Godot → Project → Project Settings → Plugins → bật `Godot Editor MCP - Addon`.

Chạy lệnh chẩn đoán (đổi đường dẫn thành thư mục dự án Godot của bạn, nơi chứa `project.godot`):

```powershell
.\.venv-godot-mcp\Scripts\godot-editor-mcp.exe doctor --project "D:\DUONG_DAN_GAME_GODOT"
```

Godot Editor MCP sử dụng MCP server và addon kết nối với Godot editor đang chạy. Cần cấu hình MCP client hoặc dùng MCP client trong Agents SDK trước khi Agent có thể gọi các công cụ Godot. Chưa cấu hình tự động trong dự án này.

Tài liệu upstream: https://hybridindie.github.io/godot-mcp/

## 3. Kiểm thử hệ thống cũ

Không thay đổi logic baseline. Cài pytest vào Python đang dùng và kiểm tra:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -v tests
```

Số lượng test có thể tăng khi các tính năng mới được thêm; không coi kết quả dự kiến là bằng chứng đã chạy.

## 4. Hướng tích hợp theo giai đoạn

1. Giữ Coordinator, Planner, Developer, Reviewer offline làm baseline; không để Agent sửa dự án game gốc.
2. Tạo adapter SDK riêng cho Planner/Developer/Reviewer dùng LLM và kiểm soát chi phí.
3. Kết nối MCP trên **bản sao dự án Godot**, ưu tiên công cụ chỉ đọc (scene tree, project settings).
4. Thêm phê duyệt thủ công trước khi Agent viết GDScript, sửa scene, chạy lệnh hoặc xuất APK.
5. Kiểm tra diff, chạy test Godot, rồi mới đưa thay đổi sang game chính.

## Nguồn và bản quyền

Hai repository upstream sử dụng giấy phép **MIT**. Khi phân phối lại mã nguồn upstream (nếu có), phải giữ thông báo bản quyền/giấy phép tương ứng. Hiện dự án chỉ sử dụng dependency và ghi công bằng đường dẫn upstream, không vendor mã nguồn.

- SDK: https://github.com/openai/openai-agents-python/blob/main/LICENSE
- Godot MCP: https://github.com/hybridindie/godot-mcp/blob/main/LICENSE
