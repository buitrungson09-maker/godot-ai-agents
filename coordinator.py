
import argparse

from main import run_pipeline
from reviewer import review_player_behavior


def _run_ai_planner(task: str):
    """Nạp AI Planner khi cần để chế độ offline không phụ thuộc SDK."""

    from ai_planner import plan_task_ai

    return plan_task_ai(task)


def coordinate(task: str, output_dir="generated", mode="offline") -> dict:
    """Điều phối pipeline ở chế độ ``offline`` hoặc ``ai``."""

    if mode not in {"offline", "ai"}:
        raise ValueError("Chế độ Planner phải là 'offline' hoặc 'ai'.")

    # 1. Goi pipeline Planner -> Developer -> Reviewer
    if mode == "offline":
        result = run_pipeline(task, output_dir=output_dir)
    else:
        ai_plan = _run_ai_planner(task)
        result = run_pipeline(
            task,
            output_dir=output_dir,
            planner_func=lambda _task: ai_plan.implementation_steps,
        )
        result["ai_plan"] = ai_plan.model_dump()

    result["planner_mode"] = mode

    # 2. Kiem tra ket qua mo phong
    if not result["report"]["passed"]:
        result["status"] = "failed"
        return result

    # 3. Neu chua tao ma nguon, chi dung o buoc lap ke hoach
    if "generated_file" not in result:
        result["status"] = "planning_only"
        return result

    # 4. Kiem tra file ma nguon
    source_report = result["source_report"]
    if not source_report["passed"]:
        result["status"] = "failed"
        return result

    # 5. Kiem tra tinh cac huong di chuyen
    behavior_report = review_player_behavior(
        result["generated_file"]
    )
    result["behavior_report"] = behavior_report

    # 6. Tong hop ket qua
    if behavior_report["passed"]:
        result["status"] = "ready_for_manual_review"
    else:
        result["status"] = "failed"

    return result


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Dieu phoi pipeline phat trien game Godot.",
    )
    parser.add_argument(
        "--mode",
        choices=("offline", "ai"),
        default="offline",
        help="Chon Planner; mac dinh la offline.",
    )
    args = parser.parse_args(argv)

    task = input("Nhap yeu cau phat trien game: ")

    try:
        result = coordinate(task, mode=args.mode)
    except (ValueError, OSError, RuntimeError) as error:
        print("Loi:", error)
        return

    print("\n=== COORDINATOR ===")
    print("Yeu cau:", result["task"])
    print("Trang thai:", result["status"])
    print("Planner mode:", result["planner_mode"])

    print("\n=== PLANNER ===")
    for step in result["plan"]:
        print("-", step)

    print("\n=== DEVELOPER ===")
    if "generated_file" in result:
        print("Da tao:", result["generated_file"])
    else:
        print("Chua co ma nguon duoc tao")

    print("\n=== REVIEWER ===")
    print("Pipeline:", result["report"])

    if "source_report" in result:
        print("Source:", result["source_report"])

    if "behavior_report" in result:
        print("Movement checks:", result["behavior_report"])

    print("\nCan duyet thu cong truoc khi dua vao game.")


if __name__ == "__main__":
    main()
