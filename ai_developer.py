
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


def develop_task_ai(task: str) -> GeneratedScript:
    if not task.strip():
        raise ValueError("Yeu cau khong duoc rong")

    developer = Agent(
        name="Godot AI Developer",
        instructions=(
            "Ban la lap trinh vien Godot 4 GDScript. "
            "Du an la game 2D PC goc nhin top-down. "
            "Chi tao mot script GDScript cho moi yeu cau. "
            "Ma nguon phai tuong thich Godot 4. "
            "Khong gia dinh rang cac node da ton tai "
            "neu nguoi dung chua cung cap scene tree. "
            "Neu can node, hay giai thich trong explanation. "
            "Khong su dung tool, khong sua file, "
            "khong truy cap du an Godot."
            "Neu skill co damage, signal skill_activated "
            "phai truyen tham so damage: int. "
            "Phuong thuc use_skill() nen tra ve bool "
            "de thong bao kich hoat thanh cong. "
            "Truong explanation phai co noi dung, "
            "mo ta cac node can thiet va cach su dung. "
            "Khong tu ghi file vao du an Godot. "
        ),
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
        raise ValueError("AI khong tra ve GeneratedScript")

    return result.final_output


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
