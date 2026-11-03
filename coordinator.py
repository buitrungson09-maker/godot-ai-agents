
import argparse

from main import run_pipeline
from reviewer import review_player_behavior


def _run_ai_planner(task: str):
    """Goi Planner AI khi chon che do AI."""
    from ai_planner import plan_task_ai
    return plan_task_ai(task)


def _run_ai_developer(task: str):
    """Goi Developer AI, khong tu ghi file."""
    from ai_developer import develop_task_ai
    return develop_task_ai(task)


def coordinate(
    task: str,
    output_dir="generated",
    mode="offline",
    developer_mode="offline",
) -> dict:
    """Dieu phoi Planner, Developer va Reviewer."""

    if mode not in {"offline", "ai"}:
        raise ValueError(
            "Che do Planner phai la 'offline' hoac 'ai'."
        )

    if developer_mode not in {"offline", "ai"}:
        raise ValueError(
            "Che do Developer phai la 'offline' hoac 'ai'."
        )

    if developer_mode == "ai" and mode != "ai":
        raise ValueError(
            "Developer AI hien yeu cau Planner AI."
        )

    # 1. Chay Planner va pipeline hien tai
    if mode == "offline":
        result = run_pipeline(
            task,
            output_dir=output_dir,
        )
    else:
        ai_plan = _run_ai_planner(task)

        result = run_pipeline(
            task,
            output_dir=output_dir,
            planner_func=lambda _task: ai_plan.implementation_steps,
        )

        result["ai_plan"] = ai_plan.model_dump()

    result["planner_mode"] = mode
    result["developer_mode"] = developer_mode

    # 2. Kiem tra bao cao pipeline
    if not result["report"]["passed"]:
        result["status"] = "failed"
        return result

    # 3. Goi Developer AI neu duoc chon
    if developer_mode == "ai":
        developer_input = (
            f"Yeu cau: {task}\n"
            "Ke hoach tu Planner AI:\n"
            + "\n".join(
                f"- {step}" for step in result["plan"]
            )
            + "\n"
            "Hay tao mot file GDScript cho Godot 4 "
            "PC goc nhin top-down. "
            "Khong sua file hoac du an Godot."
        )

        generated = _run_ai_developer(developer_input)

        result["ai_developer"] = generated.model_dump()
        result["status"] = "generated_for_manual_review"

        return result

    # 4. Developer offline giu nguyen
    if "generated_file" not in result:
        result["status"] = "planning_only"
        return result

    # 5. Kiem tra ma nguon
    source_report = result["source_report"]

    if not source_report["passed"]:
        result["status"] = "failed"
        return result

    # 6. Kiem tra hanh vi di chuyen
    behavior_report = review_player_behavior(
        result["generated_file"]
    )

    result["behavior_report"] = behavior_report

    # 7. Tong hop trang thai
    if behavior_report["passed"]:
        result["status"] = "ready_for_manual_review"
    else:
        result["status"] = "failed"

    return result


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Dieu phoi he thong Godot AI Agents.",
    )

    parser.add_argument(
        "--mode",
        choices=("offline", "ai"),
        default="offline",
        help="Che do Planner, mac dinh offline.",
    )

    parser.add_argument(
        "--developer",
        choices=("offline", "ai"),
        default="offline",
        help="Che do Developer, mac dinh offline.",
    )

    args = parser.parse_args(argv)

    task = input("Nhap yeu cau phat trien game: ")

    try:
        # Giu tuong thich voi cac test CLI cu
        if args.developer == "offline":
            result = coordinate(
                task,
                mode=args.mode,
            )
        else:
            result = coordinate(
                task,
                mode=args.mode,
                developer_mode=args.developer,
            )

    except (ValueError, OSError, RuntimeError) as error:
        print("Loi:", error)
        return

    print("\n=== COORDINATOR ===")
    print("Yeu cau:", result["task"])
    print("Trang thai:", result["status"])
    print("Planner mode:", result["planner_mode"])
    print(
        "Developer mode:",
        result.get("developer_mode", "offline"),
    )

    print("\n=== PLANNER ===")
    for step in result["plan"]:
        print("-", step)

    print("\n=== DEVELOPER ===")

    if "ai_developer" in result:
        generated = result["ai_developer"]

        print("AI da sinh ma GDScript.")

        print("\n=== FILE DE XUAT ===")
        print(generated["file_name"])

        print("\n=== GDSCRIPT ===")
        print(generated["gdscript"])

        print("\n=== GIAI THICH ===")
        print(generated["explanation"])

    elif "generated_file" in result:
        print("Da tao:", result["generated_file"])
    else:
        print("Chua co ma nguon duoc tao.")

    print("\n=== REVIEWER ===")
    print("Pipeline:", result["report"])

    if "ai_developer" in result:
        print(
            "Chua kiem tra GDScript bang Reviewer AI "
            "hoac Godot Engine."
        )

    if "source_report" in result:
        print("Source:", result["source_report"])

    if "behavior_report" in result:
        print(
            "Movement checks:",
            result["behavior_report"],
        )

    print("\nCan duyet thu cong truoc khi dua vao game.")


if __name__ == "__main__":
    main()
