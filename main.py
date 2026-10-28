
from pathlib import Path

from planner import plan_task
from developer import develop, generate_player
from reviewer import review, review_player


def run_pipeline(task: str, output_dir="generated") -> dict:
    """Chay Planner, Developer va Reviewer."""

    plan = plan_task(task)
    work = develop(plan)
    report = review(plan, work)

    result = {
        "task": task.strip(),
        "plan": plan,
        "work": work,
        "report": report
    }

    task_lower = task.lower()

    if "nhan vat" in task_lower or "nhân vật" in task_lower:
        file_path = generate_player(output_dir)
        source_report = review_player(file_path)

        result["generated_file"] = str(file_path)
        result["source_report"] = source_report

    return result


def main() -> None:
    task = input("Nhap yeu cau: ")

    try:
        result = run_pipeline(task)
    except (ValueError, OSError) as error:
        print(f"Loi: {error}")
        return

    print("\n[Planner]")
    for step in result["plan"]:
        print("-", step)

    print("\n[Developer]")
    for item in result["work"]:
        print("-", item["step"], "=>", item["status"])

    print("\n[Reviewer - mo phong]")
    print(result["report"])

    if "generated_file" in result:
        print("\n[Developer - tao ma nguon]")
        print("File:", result["generated_file"])

        print("\n[Reviewer - kiem tra ma nguon]")
        print(result["source_report"])

        if result["source_report"]["passed"]:
            print("\nKET QUA: PASS")
        else:
            print("\nKET QUA: FAIL")


if __name__ == "__main__":
    main()
