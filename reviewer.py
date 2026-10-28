
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
