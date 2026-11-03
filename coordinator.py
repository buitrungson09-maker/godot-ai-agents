
import argparse

from main import run_pipeline
from reviewer import review_player_behavior


# ==================================================
# 1. CAC HAM GOI AI AGENT
# ==================================================

def _run_ai_planner(task: str):
    """Goi Planner AI de lap ke hoach."""
    from ai_planner import plan_task_ai

    return plan_task_ai(task)


def _run_ai_developer(task: str):
    """Goi Developer AI de sinh GDScript."""
    from ai_developer import develop_task_ai

    return develop_task_ai(task)


def _run_ai_reviewer(task: str, gdscript: str):
    """Goi Reviewer AI de danh gia ma GDScript."""
    from ai_reviewer import review_gdscript_ai

    return review_gdscript_ai(task, gdscript)


def _run_ai_repair(
    task: str,
    original_code: str,
    errors: list[str],
):
    """Yeu cau Developer AI sua ma theo loi Reviewer."""
    from ai_developer import revise_task_ai

    return revise_task_ai(
        task,
        original_code,
        errors,
    )


# ==================================================
# 2. COORDINATOR
# ==================================================

def coordinate(
    task: str,
    output_dir="generated",
    mode="offline",
    developer_mode="offline",
    reviewer_mode="offline",
    auto_repair=False,
) -> dict:
    """Dieu phoi cac AI Agent va sua loi toi da mot lan."""

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

    if auto_repair and not (
        mode == "ai"
        and developer_mode == "ai"
        and reviewer_mode == "ai"
    ):
        raise ValueError(
            "Auto repair yeu cau ca 3 AI Agent."
        )

    # --------------------------------------------------
    # BUOC 1: PLANNER
    # --------------------------------------------------

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
            planner_func=lambda _task: (
                ai_plan.implementation_steps
            ),
        )

        result["ai_plan"] = ai_plan.model_dump()

    result["planner_mode"] = mode
    result["developer_mode"] = developer_mode
    result["reviewer_mode"] = reviewer_mode
    result["repair_attempts"] = 0

    # --------------------------------------------------
    # BUOC 2: KIEM TRA PIPELINE HIEN TAI
    # --------------------------------------------------

    if not result["report"]["passed"]:
        result["status"] = "failed"
        return result

    # --------------------------------------------------
    # BUOC 3: DEVELOPER AI
    # --------------------------------------------------

    if developer_mode == "ai":
        developer_input = (
            f"Yeu cau goc:\n{task}\n\n"
            "Ke hoach cua Planner AI:\n"
            + "\n".join(
                f"- {step}"
                for step in result["plan"]
            )
            + "\n\n"
            "Hay tao mot file GDScript cho Godot 4 "
            "PC goc nhin top-down. "
            "Khong tu sua file hay du an Godot."
        )

        generated = _run_ai_developer(
            developer_input
        )

        if not generated.gdscript.strip():
            raise ValueError(
                "Developer AI tra ve GDScript rong."
            )

        result["ai_developer"] = generated.model_dump()

        # Khong bat Reviewer AI
        if reviewer_mode == "offline":
            result["status"] = (
                "generated_for_manual_review"
            )
            return result

        # --------------------------------------------------
        # BUOC 4: REVIEWER AI LAN 1
        # --------------------------------------------------

        review_input = (
            f"Yeu cau goc: {task}\n"
            f"Ten file: {generated.file_name}\n"
            "Kiem tra GDScript theo yeu cau goc. "
            "Phan biet loi bat buoc va de xuat mo rong. "
            "Khong tu nhan da chay Godot Engine."
        )

        first_review = _run_ai_reviewer(
            review_input,
            generated.gdscript,
        )

        result["ai_review"] = (
            first_review.model_dump()
        )

        # Truong hop Reviewer PASS ngay
        if first_review.passed:
            result["status"] = (
                "reviewed_for_manual_approval"
            )
            return result

        # Truong hop Reviewer FAIL nhung khong bat auto repair
        if not auto_repair:
            result["status"] = (
                "review_changes_required"
            )
            return result

        # Khong co loi cu the de Developer sua
        if not first_review.errors:
            result["status"] = (
                "review_changes_required"
            )
            return result

        # --------------------------------------------------
        # BUOC 5: DEVELOPER AI SUA MA MOT LAN
        # --------------------------------------------------

        revised = _run_ai_repair(
            task,
            generated.gdscript,
            first_review.errors,
        )

        if not revised.gdscript.strip():
            raise ValueError(
                "Developer AI tra ve ma sua rong."
            )

        if not revised.file_name.lower().endswith(".gd"):
            raise ValueError(
                "Developer AI phai tra ve file .gd."
            )

        result["ai_revised_developer"] = (
            revised.model_dump()
        )

        result["repair_attempts"] = 1

        # --------------------------------------------------
        # BUOC 6: REVIEWER AI KIEM TRA LAI
        # --------------------------------------------------

        second_review_input = (
            f"Yeu cau goc: {task}\n"
            f"Ten file: {revised.file_name}\n"
            "Day la GDScript da duoc Developer sua. "
            "Hay danh gia lai doc lap theo yeu cau goc. "
            "Khong mac dinh ma da sua la dung."
        )

        second_review = _run_ai_reviewer(
            second_review_input,
            revised.gdscript,
        )

        result["ai_second_review"] = (
            second_review.model_dump()
        )

        # Dung tai day, khong sua lan thu hai
        if second_review.passed:
            result["status"] = (
                "reviewed_for_manual_approval"
            )
        else:
            result["status"] = (
                "review_changes_required"
            )

        return result

    # --------------------------------------------------
    # BUOC 7: DEVELOPER OFFLINE
    # --------------------------------------------------

    if "generated_file" not in result:
        result["status"] = "planning_only"
        return result

    source_report = result["source_report"]

    if not source_report["passed"]:
        result["status"] = "failed"
        return result

    # Reviewer offline kiem tra Python Player
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


# ==================================================
# 3. GIAO DIEN DONG LENH
# ==================================================

def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="Godot AI Agents Coordinator v2.4",
    )

    parser.add_argument(
        "--mode",
        choices=("offline", "ai"),
        default="offline",
        help="Chon Planner mode.",
    )

    parser.add_argument(
        "--developer",
        choices=("offline", "ai"),
        default="offline",
        help="Chon Developer mode.",
    )

    parser.add_argument(
        "--reviewer",
        choices=("offline", "ai"),
        default="offline",
        help="Chon Reviewer mode.",
    )

    parser.add_argument(
        "--auto-repair",
        action="store_true",
        help="Cho phep Developer AI sua loi toi da mot lan.",
    )

    args = parser.parse_args(argv)

    task = input(
        "Nhap yeu cau phat trien game: "
    )

    try:
        # Chi truyen tham so bo sung khi can.
        # Giu tuong thich voi test CLI cu.
        kwargs = {
            "mode": args.mode,
        }

        if args.developer == "ai":
            kwargs["developer_mode"] = "ai"

        if args.reviewer == "ai":
            kwargs["reviewer_mode"] = "ai"

        if args.auto_repair:
            kwargs["auto_repair"] = True

        result = coordinate(
            task,
            **kwargs,
        )

    except (ValueError, OSError, RuntimeError) as error:
        print("Loi:", error)
        return

    # --------------------------------------------------
    # COORDINATOR
    # --------------------------------------------------

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

    print(
        "So lan sua:",
        result.get("repair_attempts", 0),
    )

    # --------------------------------------------------
    # PLANNER
    # --------------------------------------------------

    print("\n=== PLANNER ===")

    for step in result["plan"]:
        print("-", step)

    # --------------------------------------------------
    # DEVELOPER
    # --------------------------------------------------

    print("\n=== DEVELOPER ===")

    if "ai_developer" in result:
        generated = result["ai_developer"]

        print("\n=== FILE BAN DAU ===")
        print(generated["file_name"])

        print("\n=== GDSCRIPT BAN DAU ===")
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

    # --------------------------------------------------
    # DEVELOPER SUA LOI
    # --------------------------------------------------

    if "ai_revised_developer" in result:
        revised = result["ai_revised_developer"]

        print("\n=== DEVELOPER SUA LOI ===")

        print("File:", revised["file_name"])

        print("\n=== GDSCRIPT DA SUA ===")
        print(revised["gdscript"])

        print("\n=== GIAI THICH SUA LOI ===")
        print(revised["explanation"])

    # --------------------------------------------------
    # REVIEWER
    # --------------------------------------------------

    print("\n=== REVIEWER ===")
    print("Pipeline:", result["report"])

    if "ai_review" in result:
        review_data = result["ai_review"]

        print("\n=== AI REVIEW LAN 1 ===")
        print("Passed:", review_data["passed"])
        print("Score:", review_data["score"])
        print("Errors:", review_data["errors"])
        print("Warnings:", review_data["warnings"])
        print("Suggestions:", review_data["suggestions"])
        print(
            "Explanation:",
            review_data["explanation"],
        )

    if "ai_second_review" in result:
        second = result["ai_second_review"]

        print("\n=== AI REVIEW LAN 2 ===")
        print("Passed:", second["passed"])
        print("Score:", second["score"])
        print("Errors:", second["errors"])
        print("Warnings:", second["warnings"])
        print("Suggestions:", second["suggestions"])
        print(
            "Explanation:",
            second["explanation"],
        )

    elif (
        "ai_developer" in result
        and "ai_review" not in result
    ):
        print(
            "Chua kiem tra GDScript bang Reviewer AI."
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
