"""Kiểm thử hai chế độ Coordinator mà không gọi API thật."""

import pytest

import coordinator
from ai_planner import AIPlannerError, GamePlan


def make_ai_plan() -> GamePlan:
    return GamePlan(
        summary="Tạo menu chính.",
        features=["Nút bắt đầu"],
        gdscript_files=["scripts/main_menu.gd"],
        scenes_and_nodes=["MainMenu.tscn: Control"],
        implementation_steps=[
            "Tạo scene menu",
            "Kết nối tín hiệu nút bắt đầu",
        ],
        test_cases=["Nhấn bắt đầu: chuyển sang màn chơi"],
        assumptions=["Dự án dùng Godot 4"],
    )


def test_default_mode_remains_offline(monkeypatch, tmp_path):
    def fail_if_ai_is_called(task):
        raise AssertionError("Không được gọi AI trong chế độ mặc định")

    monkeypatch.setattr(coordinator, "_run_ai_planner", fail_if_ai_is_called)

    result = coordinator.coordinate("Tạo menu game", output_dir=tmp_path)

    assert result["planner_mode"] == "offline"
    assert result["status"] == "planning_only"
    assert "ai_plan" not in result


def test_ai_mode_uses_structured_plan(monkeypatch, tmp_path):
    expected_plan = make_ai_plan()
    monkeypatch.setattr(
        coordinator,
        "_run_ai_planner",
        lambda task: expected_plan,
    )

    result = coordinator.coordinate(
        "Tạo menu game",
        output_dir=tmp_path,
        mode="ai",
    )

    assert result["planner_mode"] == "ai"
    assert result["status"] == "planning_only"
    assert result["plan"] == expected_plan.implementation_steps
    assert result["ai_plan"] == expected_plan.model_dump()
    assert all(item["status"] == "simulated" for item in result["work"])


def test_rejects_unknown_planner_mode(tmp_path):
    with pytest.raises(ValueError, match="offline.*ai"):
        coordinator.coordinate(
            "Tạo menu game",
            output_dir=tmp_path,
            mode="automatic",
        )


def test_ai_planner_error_is_not_hidden(monkeypatch, tmp_path):
    def fail_ai_planner(task):
        raise AIPlannerError("Lỗi AI giả lập")

    monkeypatch.setattr(coordinator, "_run_ai_planner", fail_ai_planner)

    with pytest.raises(AIPlannerError, match="Lỗi AI giả lập"):
        coordinator.coordinate(
            "Tạo menu game",
            output_dir=tmp_path,
            mode="ai",
        )


@pytest.mark.parametrize(
    ("argv", "expected_mode"),
    [
        ([], "offline"),
        (["--mode", "ai"], "ai"),
    ],
)
def test_cli_passes_selected_mode(monkeypatch, capsys, argv, expected_mode):
    captured = {}

    def fake_coordinate(task, output_dir="generated", mode="offline"):
        captured.update(task=task, mode=mode)
        return {
            "task": task,
            "status": "planning_only",
            "planner_mode": mode,
            "plan": ["Bước mô phỏng"],
            "report": {"passed": True, "errors": []},
        }

    monkeypatch.setattr("builtins.input", lambda prompt: "Tạo menu game")
    monkeypatch.setattr(coordinator, "coordinate", fake_coordinate)

    coordinator.main(argv)

    output = capsys.readouterr().out
    assert captured == {"task": "Tạo menu game", "mode": expected_mode}
    assert f"Planner mode: {expected_mode}" in output
