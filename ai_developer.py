
from agents import Agent, Runner, RunConfig
from pydantic import BaseModel, Field

from llm_router import build_model_from_env


class GeneratedScript(BaseModel):
    file_name: str = Field(
        description="Ten file GDScript duoc de xuat"
    )
    gdscript: str = Field(
        description="Ma nguon GDScript Godot 4"
    )
    explanation: str = Field(
        description="Giai thich ngan gon chuc nang"
    )


DEVELOPER_INSTRUCTIONS = """
Ban la lap trinh vien Godot 4 GDScript.

Du an la game tu tien 2D tren PC, goc nhin top-down.

QUY TAC:
1. Chi tao mot file GDScript cho moi yeu cau.
2. Ma nguon phai tuong thich Godot 4.
3. Khong gia dinh cac node da ton tai
   neu nguoi dung chua cung cap scene tree.
4. Neu can node, giai thich trong explanation.
5. Neu ky nang co damage, signal skill_activated
   phai truyen tham so damage: int.
6. Ham use_skill() nen tra ve bool.
7. Truong explanation phai mo ta cac node
   can thiet va cach su dung.
8. Neu duoc yeu cau sua loi, phai tra ve
   toan bo GDScript da sua.
9. Giu nguyen cac chuc nang da dung.
10. Khong su dung tool, khong ghi file,
    khong truy cap du an Godot.
"""


def develop_task_ai(task: str) -> GeneratedScript:
    """Sinh GDScript bang Developer AI."""

    if not task.strip():
        raise ValueError("Yeu cau khong duoc rong")

    developer = Agent(
        name="Godot AI Developer",
        instructions=DEVELOPER_INSTRUCTIONS,
        model=build_model_from_env(),
        output_type=GeneratedScript,
        tools=[],
    )

    result = Runner.run_sync(
        developer,
        input=task.strip(),
        max_turns=1,
        run_config=RunConfig(tracing_disabled=True),
    )

    if not isinstance(result.final_output, GeneratedScript):
        raise ValueError(
            "AI khong tra ve GeneratedScript"
        )

    if not result.final_output.gdscript.strip():
        raise ValueError(
            "Developer AI tra ve ma GDScript rong"
        )

    return result.final_output


def revise_task_ai(
    task: str,
    original_code: str,
    review_errors: list[str],
) -> GeneratedScript:
    """Sua GDScript dua tren loi Reviewer AI."""

    if not task.strip():
        raise ValueError("Yeu cau goc khong duoc rong")

    if not original_code.strip():
        raise ValueError("Ma GDScript ban dau rong")

    if not review_errors:
        raise ValueError("Khong co loi can sua")

    repair_prompt = (
        f"YEU CAU GOC:\n{task}\n\n"
        "MA GDSCRIPT CAN SUA:\n"
        f"```gdscript\n{original_code}\n```\n\n"
        "CAC LOI REVIEWER PHAT HIEN:\n"
        + "\n".join(
            f"- {error}"
            for error in review_errors
        )
        + "\n\n"
        "Hay sua tat ca loi bat buoc o tren. "
        "Tra ve TOAN BO file GDScript da sua. "
        "Khong chi tra ve doan code thay doi. "
        "Giu nguyen chuc nang da hoat dong dung. "
        "Giai thich nhung thay doi trong explanation. "
        "Khong tu ghi file hoac sua du an Godot."
    )

    return develop_task_ai(repair_prompt)


def main():
    task = input("Nhap yeu cau lap trinh: ")

    try:
        result = develop_task_ai(task)

    except (ValueError, RuntimeError) as error:
        print("Loi:", error)
        return

    print("\n=== FILE DE XUAT ===")
    print(result.file_name)

    print("\n=== GDSCRIPT ===")
    print(result.gdscript)

    print("\n=== GIAI THICH ===")
    print(result.explanation)


if __name__ == "__main__":
    main()
