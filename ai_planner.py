"""AI Planner: đề xuất kế hoạch, không ghi file hoặc thực thi mã."""

from agents import Agent, RunConfig, Runner
from pydantic import BaseModel, Field

from llm_router import build_model_from_env


class AIPlannerError(RuntimeError):
    """Lỗi xảy ra khi SDK không thể hoàn thành yêu cầu lập kế hoạch."""


class GamePlan(BaseModel):
    """Cấu trúc kế hoạch để các thành phần khác đọc được."""

    summary: str = Field(description="Tóm tắt yêu cầu bằng tiếng Việt")
    features: list[str] = Field(description="Các chức năng cần xây dựng")
    gdscript_files: list[str] = Field(
        description="Đường dẫn tương đối của các file GDScript dự kiến"
    )
    scenes_and_nodes: list[str] = Field(
        description="Các scene và node Godot cần dùng, kèm vai trò"
    )
    implementation_steps: list[str] = Field(
        description="Các bước triển khai theo thứ tự"
    )
    test_cases: list[str] = Field(
        description="Các ca kiểm thử, mỗi ca có kết quả mong đợi"
    )
    assumptions: list[str] = Field(
        description="Các giả định hoặc thông tin cần người dùng xác nhận"
    )


PLANNER_INSTRUCTIONS = """
Bạn là Planner hỗ trợ sinh viên phát triển game tu tiên 2D
bằng Godot 4, hướng tới Android.

Hãy phân tích yêu cầu và trả về kế hoạch bằng tiếng Việt theo cấu trúc
được cung cấp.

Quy tắc:
- Giữ đúng các thông số người dùng yêu cầu, như sát thương và hồi chiêu.
- Đề xuất chức năng, file GDScript, scene, node và bước triển khai.
- Các file chỉ là đề xuất đường dẫn tương đối trong dự án.
- Mỗi ca kiểm thử phải mô tả cách kiểm tra và kết quả mong đợi.
- Nếu thiếu thông tin, ghi rõ giả định để người dùng duyệt.
- Ưu tiên giải pháp đơn giản, phù hợp người mới học Godot.
- Chỉ lập kế hoạch; không sinh toàn bộ mã nguồn.
- Không tuyên bố đã đọc, sửa hoặc chạy dự án Godot.
- Không tuyên bố các bài kiểm thử đã thành công.
"""


def plan_task_ai(task: str) -> GamePlan:
    """Gọi mô hình AI và trả về kế hoạch có cấu trúc."""

    if not isinstance(task, str) or not task.strip():
        raise ValueError("Yêu cầu không được rỗng.")

    model = build_model_from_env()

    planner = Agent(
        name="Godot AI Planner",
        instructions=PLANNER_INSTRUCTIONS,
        model=model,
        output_type=GamePlan,
        tools=[],
    )

    try:
        result = Runner.run_sync(
            planner,
            input=task.strip(),
            max_turns=1,
            run_config=RunConfig(tracing_disabled=True),
        )
    except Exception as error:
        # Chuyển lỗi SDK/API thành lỗi của tầng Planner để Coordinator sau này
        # không phải phụ thuộc vào từng loại exception nội bộ của SDK.
        raise AIPlannerError("Không thể nhận kế hoạch từ dịch vụ AI.") from error

    if not isinstance(result.final_output, GamePlan):
        raise ValueError("AI không trả về kế hoạch đúng cấu trúc.")

    return result.final_output


def main() -> None:
    """Nhận yêu cầu từ Terminal và in kế hoạch dưới dạng JSON."""

    task = input("Nhập yêu cầu phát triển game: ")

    try:
        plan = plan_task_ai(task)
    except (ValueError, AIPlannerError) as error:
        print(f"Lỗi: {error}")
        return

    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
