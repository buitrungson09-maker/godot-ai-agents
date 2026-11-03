
import argparse

from main import run_pipeline
from reviewer import review_player_behavior


def _run_ai_planner(task: str):
    """Goi Planner AI khi can."""
    from ai_planner import plan_task_ai

    return plan_task_ai(task)


def _run_ai_developer(task: str):
    """Goi Developer AI, khong tu ghi file."""
    from ai_developer import develop_task_ai

    return develop_task_ai(task)


def _run_ai_reviewer(task: str, gdscript: str):
    """Goi Reviewer AI de danh gia GDScript."""
    from ai_reviewer import review_gdscript_ai

    return review_gdscript_ai(task, gdscript)


def coordinate(
    task: str,
    output_dir="generated",
    mode="offline",
    developer_mode="offline",
    reviewer_mode="offline",
) -> dict:
    """Dieu phoi Planner, Developer va Reviewer."""

    if not task.strip():
        raise ValueError("Yeu cau khong duoc rong.")

    if mode not in {"offline", "ai"}:
        raise ValueError(
            "Planner mode phai la offline hoac ai."
        )

    if developer_mode not in {"offline", "ai"}:
        raise ValueError(
            "Developer mode phai la offline hoac ai."
        )

    if reviewer_mode not in {"offline", "ai"}:
        raise ValueError(
            "Reviewer mode phai la offline hoac ai."
        )

    if developer_mode == "ai" and mode != "ai":
        raise ValueError(
            "Developer AI yeu cau Planner AI."
        )

    if reviewer_mode == "ai" and developer_mode != "ai":
        raise ValueError(
            "Reviewer AI yeu cau Developer AI."
        )

    # 1. Planner
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
    result["reviewer_mode"] = reviewer_mode

    # 2. Kiem tra pipeline mo phong
    if not result["report"]["passed"]:
        result["status"] = "failed"
        return result

    # 3. Developer AI
    if developer_mode == "ai":
        developer_input = (
            f"Yeu cau: {task}\n"
            "Ke hoach cua Planner AI:\n"
            + "\n".join(
                f"- {step}" for step in result["plan"]
            )
            + "\n"
            "Tao mot file GDScript cho Godot 4 "
            "PC goc nhin top-down. "
            "Khong tu sua du an Godot."
        )

        generated = _run_ai_developer(
            developer_input
        )

        if not generated.gdscript.strip():
            raise ValueError(
                "Developer AI tra ve GDScript rong."
            )

        result["ai_developer"] = generated.model_dump()

        # 4. Reviewer AI
        if reviewer_mode == "ai":
            review_input = (
                f"Yeu cau goc: {task}\n"
                f"Ten file: {generated.file_name}\n"
                "Kiem tra ma co dap ung yeu cau "
                "va tuong thich Godot 4 hay khong."
            )

            ai_review = _run_ai_reviewer(
                review_input,
                generated.gdscript,
            )

            result["ai_review"] = ai_review.model_dump()

            if ai_review.passed:
                result["status"] = (
                    "reviewed_for_manual_approval"
                )
            else:
                result["status"] = (
                    "review_changes_required"
                )

        else:
            result["status"] = (
                "generated_for_manual_review"
            )

        return result

    # 5. Developer offline
    if "generated_file" not in result:
        result["status"] = "planning_only"
        return result

    # 6. Reviewer offline: kiem tra Python
    source_report = result["source_report"]

    if not source_report["passed"]:
        result["status"] = "failed"
        return result

    behavior_report = review_player_behavior(
        result["generated_file"]
    )

    result["behavior_report"] = behavior_report

    if behavior_report["passed"]:
        result["status"] = (
            "ready_for_manual_review"
        )
    else:
        result["status"] = "failed"

    return result


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Godot AI Agents Coordinator.",
    )

    parser.add_argument(
        "--mode",
        choices=("offline", "ai"),
        default="offline",
        help="Planner mode.",
    )

    parser.add_argument(
        "--developer",
        choices=("offline", "ai"),
        default="offline",
        help="Developer mode.",
    )

    parser.add_argument(
        "--reviewer",
        choices=("offline", "ai"),
        default="offline",
        help="Reviewer mode.",
    )

    args = parser.parse_args(argv)

    task = input(
        "Nhap yeu cau phat trien game: "
    )

    try:
        # Khong truyen tham so moi khi o che do mac dinh.
        # Giu tuong thich voi cac test CLI cu.
        kwargs = {"mode": args.mode}

        if args.developer == "ai":
            kwargs["developer_mode"] = "ai"

        if args.reviewer == "ai":
            kwargs["reviewer_mode"] = "ai"

        result = coordinate(task, **kwargs)

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

    print(
        "Reviewer mode:",
        result.get("reviewer_mode", "offline"),
    )

    print("\n=== PLANNER ===")

    for step in result["plan"]:
        print("-", step)

    print("\n=== DEVELOPER ===")

    if "ai_developer" in result:
        generated = result["ai_developer"]

        print("AI da sinh GDScript.")

        print("\n=== FILE DE XUAT ===")
        print(generated["file_name"])

        print("\n=== GDSCRIPT ===")
        print(generated["gdscript"])

        print("\n=== GIAI THICH ===")
        print(generated["explanation"])

    elif "generated_file" in result:
        print(
            "Da tao:",
            result["generated_file"],
        )

    else:
        print("Chua co ma nguon duoc tao.")

    print("\n=== REVIEWER ===")
    print("Pipeline:", result["report"])

    if "ai_review" in result:
        review_result = result["ai_review"]

        print("\n=== AI REVIEWER ===")
        print(
            "Passed:",
            review_result["passed"],
        )
        print(
            "Score:",
            review_result["score"],
        )
        print(
            "Errors:",
            review_result["errors"],
        )
        print(
            "Warnings:",
            review_result["warnings"],
        )
        print(
            "Suggestions:",
            review_result["suggestions"],
        )
        print(
            "Explanation:",
            review_result["explanation"],
        )

    elif "ai_developer" in result:
        print(
            "Chua kiem tra GDScript "
            "bang Reviewer AI."
        )

    if "source_report" in result:
        print(
            "Source:",
            result["source_report"],
        )

    if "behavior_report" in result:
        print(
            "Movement checks:",
            result["behavior_report"],
        )

    print(
        "\nLuu y: Chua xac minh bang Godot Engine."
    )
    print(
        "Can duyet thu cong truoc khi dua vao game."
    )


if __name__ == "__main__":
    main()
