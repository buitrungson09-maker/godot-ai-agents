
def plan_task(task: str) -> list[str]:
    """Phan loai yeu cau va tao ke hoach 3 buoc."""

    if not isinstance(task, str) or not task.strip():
        raise ValueError("Yeu cau khong duoc rong")

    task = task.strip()
    task_lower = task.lower()

    if "nhan vat" in task_lower or "nhân vật" in task_lower:
        return [
            "Thiet ke nhan vat game 2D",
            "Lap trinh di chuyen nhan vat",
            "Kiem thu di chuyen va va cham"
        ]

    elif "menu" in task_lower:
        return [
            "Thiet ke giao dien menu",
            "Lap trinh xu ly nut bam",
            "Kiem thu chuc nang menu"
        ]

    elif "chien dau" in task_lower or "chiến đấu" in task_lower:
        return [
            "Thiet ke he thong chien dau",
            "Lap trinh sat thuong va mau",
            "Kiem thu he thong chien dau"
        ]

    else:
        return [
            f"Phan tich: {task}",
            "Xay dung demo Python nho",
            "Kiem thu va ghi bao cao"
        ]
