
from agents import Agent, Runner, RunConfig
from pydantic import BaseModel, Field

from llm_router import build_model_from_env


class ReviewResult(BaseModel):
    passed: bool = Field(
        description="AI danh gia ma co dat yeu cau hay khong"
    )
    score: int = Field(
        ge=0,
        le=10,
        description="Diem danh gia tu 0 den 10"
    )
    errors: list[str] = Field(
        description="Cac loi va van de can sua"
    )
    warnings: list[str] = Field(
        description="Cac canh bao, rui ro chua xac minh"
    )
    suggestions: list[str] = Field(
        description="De xuat cai thien"
    )
    explanation: str = Field(
        description="Nhan xet tong quan bang tieng Viet"
    )


REVIEWER_INSTRUCTIONS = """
Ban la AI Code Reviewer chuyen ve Godot 4 va GDScript.

Du an la game tu tien 2D tren PC, goc nhin top-down.

Nhiem vu:
1. Kiem tra ma GDScript co dap ung yeu cau hay khong.
2. Phat hien loi logic, cooldown, damage va signal.
3. Kiem tra cach su dung node, Area2D va physics.
4. Kiem tra nguy co gay damage nhieu lan.
5. Tim cac gia dinh khong dung voi Godot 4.
6. De xuat huong sua cu the.

Quy tac:
- Khong sua file.
- Khong thuc thi ma.
- Khong goi tool.
- Khong tu nhan da chay Godot Engine.
- Neu khong the xac minh, phai ghi vao warnings.
- Khong coi ma AI sinh ra la an toan mac dinh.
- Tra ve danh gia trung thuc bang tieng Viet.
"""


def review_gdscript_ai(
    task: str,
    gdscript: str,
) -> ReviewResult:
    """Danh gia GDScript bang AI, khong ghi file."""

    if not task.strip():
        raise ValueError("Yeu cau khong duoc rong")

    if not gdscript.strip():
        raise ValueError("Ma GDScript khong duoc rong")

    reviewer = Agent(
        name="Godot AI Reviewer",
        instructions=REVIEWER_INSTRUCTIONS,
        model=build_model_from_env(),
        output_type=ReviewResult,
        tools=[],
    )

    reviewer_input = (
        f"YEU CAU:\n{task}\n\n"
        f"MA GDSCRIPT CAN KIEM TRA:\n"
        f"```gdscript\n{gdscript}\n```\n"
    )

    result = Runner.run_sync(
        reviewer,
        input=reviewer_input,
        max_turns=1,
        run_config=RunConfig(tracing_disabled=True),
    )

    if not isinstance(result.final_output, ReviewResult):
        raise ValueError(
            "AI khong tra ve ket qua ReviewResult"
        )

    return result.final_output


def main():
    print("=== GODOT AI REVIEWER ===")

    task = input("Nhap yeu cau can kiem tra: ")

    file_path = input(
        "Nhap duong dan file GDScript: "
    ).strip()

    try:
        from pathlib import Path

        path = Path(file_path)

        if path.suffix.lower() != ".gd":
            raise ValueError("Chi chap nhan file .gd")

        if not path.is_file():
            raise ValueError("File khong ton tai")

        # Chi doc file, khong chinh sua.
        gdscript = path.read_text(
            encoding="utf-8"
        )

        result = review_gdscript_ai(
            task,
            gdscript,
        )

    except (ValueError, OSError, RuntimeError) as error:
        print("Loi:", error)
        return

    print("\n=== KET QUA REVIEW ===")
    print(
        result.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":
    main()
