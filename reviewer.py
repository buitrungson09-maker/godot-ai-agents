
import ast
from pathlib import Path


def review(plan: list[str], work: list[dict[str, str]]) -> dict:
    """Kiem tra ket qua mo phong cua 3 Agent."""
    expected = [step for step in plan]
    actual = [item.get("step") for item in work]

    passed = bool(expected) and expected == actual and all(
        item.get("status") == "simulated" for item in work
    )

    return {
        "passed": passed,
        "checked": len(work),
        "mode": "offline simulation"
    }


def review_player(file_path: str | Path) -> dict:
    """Kiem tra file Player Python do Developer tao ra."""

    path = Path(file_path)
    errors = []

    if not path.is_file():
        return {
            "passed": False,
            "errors": ["File khong ton tai"],
            "mode": "source review"
        }

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeError, OSError) as exc:
        return {
            "passed": False,
            "errors": [str(exc)],
            "mode": "source review"
        }

    player_classes = [
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Player"
    ]

    if not player_classes:
        errors.append("Thieu class Player")
    else:
        methods = {
            node.name for node in player_classes[0].body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        for required in ("__init__", "move", "get_position"):
            if required not in methods:
                errors.append(f"Thieu ham {required}")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "mode": "source review"
    }

def review_player_behavior(file_path: str | Path) -> dict:
    """Kiem tra hanh vi Player ma khong chay file duoc tao."""

    source_report = review_player(file_path)

    if not source_report["passed"]:
        return {
            "passed": False,
            "errors": source_report["errors"],
            "mode": "behavior review"
        }

    path = Path(file_path)
    tree = ast.parse(path.read_text(encoding="utf-8"))

    player_class = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Player"
    )

    methods = {
        node.name: node
        for node in player_class.body
        if isinstance(node, ast.FunctionDef)
    }

    errors = []

    move_method = methods["move"]

    # Kiem tra 4 huong di chuyen duoc khai bao
    directions = {
        node.value
        for node in ast.walk(move_method)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
    }

    for direction in ("up", "down", "left", "right"):
        if direction not in directions:
            errors.append(f"Thieu huong di chuyen: {direction}")

    return {
        "passed": len(errors) == 0,
        "errors": errors,
        "mode": "behavior review"
    }
