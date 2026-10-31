
from main import run_pipeline
from reviewer import review_player_behavior


def coordinate(task: str, output_dir="generated") -> dict:
    """Dieu phoi 3 vai tro va tong hop ket qua."""

    # 1. Goi pipeline Planner -> Developer -> Reviewer
    result = run_pipeline(task, output_dir=output_dir)

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


def main():
    task = input("Nhap yeu cau phat trien game: ")

    try:
        result = coordinate(task)
    except (ValueError, OSError) as error:
        print("Loi:", error)
        return

    print("\n=== COORDINATOR ===")
    print("Yeu cau:", result["task"])
    print("Trang thai:", result["status"])

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
