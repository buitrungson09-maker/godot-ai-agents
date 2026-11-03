
from pathlib import Path

from agents import Agent, Runner, RunConfig
from pydantic import BaseModel, Field

from llm_router import build_model_from_env


class ReviewResult(BaseModel):
    passed: bool = Field(
        description="Ma co dap ung yeu cau bat buoc hay khong"
    )

    score: int = Field(
        ge=0,
        le=10,
        description="Diem danh gia tu 0 den 10"
    )

    errors: list[str] = Field(
        description="Loi bat buoc phai sua"
    )

    warnings: list[str] = Field(
        description="Rui ro hoac van de chua xac minh"
    )

    suggestions: list[str] = Field(
        description="De xuat cai thien khong bat buoc"
    )

    explanation: str = Field(
        description="Nhan xet tong quan bang tieng Viet"
    )


REVIEWER_INSTRUCTIONS = """
Ban la AI Code Reviewer chuyen ve Godot 4 va GDScript.

Du an la game tu tien 2D tren PC, goc nhin top-down.

NHIEM VU:

1. Doi chieu GDScript voi yeu cau cua nguoi dung.
2. Kiem tra cau truc, kieu du lieu va API Godot 4.
3. Kiem tra logic damage, cooldown va signal.
4. Kiem tra Area2D, collision va physics neu can.
5. Kiem tra nguy co gay damage lap.
6. Phat hien cac loi logic va de xuat huong sua.
7. Co the danh gia lai ma da duoc Developer sua.

QUY TAC DANH GIA:

1. errors:
   Chi chua loi thuc su anh huong den yeu cau bat buoc
   hoac loi ma nguon co nguy co khong hoat dong.

2. warnings:
   Chua cac rui ro, gia dinh hoac van de
   chua the xac minh bang doc ma.

3. suggestions:
   Chua cac cai tien khong bat buoc.

4. passed:
   True khi ma dap ung cac yeu cau bat buoc
   theo danh gia tinh cua AI.
   False khi con loi bat buoc can sua.

5. Neu passed la False:
   Phai liet ke loi cu the trong errors.
   Moi loi can mo ta van de va huong sua.

6. Neu passed la True:
   errors phai rong.
   Co the van co warnings va suggestions.

7. Khong danh truot ma chi vi thieu
   mot tinh nang khong nam trong yeu cau.

8. Neu nguoi dung chi yeu cau bo dieu khien
   kich hoat ky nang, khong bat buoc co hitbox.

9. Neu nguoi dung yeu cau ky nang chien dau
   hoan chinh, phai kiem tra damage, hitbox,
   pham vi tan cong va muc tieu bi trung.

10. Neu duoc cung cap ma da sua:
    Danh gia lai ma moi doc lap.
    Khong mac dinh ma da sua la dung.

QUY TAC AN TOAN:

- Khong sua file.
- Khong thuc thi ma nguon.
- Khong su dung tool.
- Khong truy cap du an Godot.
- Khong tu nhan da chay Godot Engine.
- Khong tu dong chap thuan dua ma vao game.
- Neu khong the xac minh, ghi trong warnings.
- Tra ve nhan xet bang tieng Viet.
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
        f"YEU CAU GOC:\n{task.strip()}\n\n"
        "MA GDSCRIPT CAN DANH GIA:\n"
        f"```gdscript\n{gdscript}\n```\n\n"
        "Hay kiem tra theo dung pham vi yeu cau. "
        "Neu FAIL, liet ke loi bat buoc va "
        "cach sua cu the trong errors. "
        "Khong danh dong canh bao voi loi bat buoc."
    )

    result = Runner.run_sync(
        reviewer,
        input=reviewer_input,
        max_turns=1,
        run_config=RunConfig(
            tracing_disabled=True
        ),
    )

    if not isinstance(result.final_output, ReviewResult):
        raise ValueError(
            "AI khong tra ve ReviewResult"
        )

    review_result = result.final_output

    # Bao dam ket qua co du lieu de Developer sua.
    if not review_result.passed and not review_result.errors:
        raise ValueError(
            "Reviewer bao FAIL nhung khong neu loi can sua."
        )

    if review_result.passed and review_result.errors:
        raise ValueError(
            "Reviewer bao PASS nhung van co loi bat buoc."
        )

    return review_result


def main():
    print("=== GODOT AI REVIEWER V2.4 ===")

    task = input(
        "Nhap yeu cau can kiem tra: "
    )

    file_path = input(
        "Nhap duong dan file GDScript: "
    ).strip()

    try:
        path = Path(file_path)

        if path.suffix.lower() != ".gd":
            raise ValueError(
                "Chi chap nhan file GDScript .gd"
            )

        if not path.is_file():
            raise ValueError(
                "File GDScript khong ton tai"
            )

        # Chi doc file, khong sua.
        gdscript = path.read_text(
            encoding="utf-8"
        )

        review_result = review_gdscript_ai(
            task,
            gdscript,
        )

    except (ValueError, OSError, RuntimeError) as error:
        print("Loi:", error)
        return

    print("\n=== KET QUA REVIEW ===")

    print(
        review_result.model_dump_json(
            indent=2
        )
    )

    print("\n=== KET LUAN ===")

    if review_result.passed:
        print(
            "AI danh gia dat yeu cau. "
            "Can kiem thu Godot truoc khi su dung."
        )
    else:
        print(
            "Can sua cac loi trong errors "
            "va kiem tra lai."
        )


if __name__ == "__main__":
    main()
