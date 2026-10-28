import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from planner import plan_task
from developer import develop
from reviewer import review
from main import run_pipeline


def test_normal_pipeline():
    result = run_pipeline("Tao nhan vat di chuyen 2D")
    assert len(result["plan"]) == 3
    assert result["report"]["passed"] is True


def test_empty_input():
    with pytest.raises(ValueError):
        plan_task("  ")


def test_empty_plan():
    with pytest.raises(ValueError):
        develop([])


def test_missing_work():
    assert review(["A"], [])["passed"] is False


def test_wrong_order():
    assert review(["A", "B"], [
        {"step": "B", "status": "simulated"},
        {"step": "A", "status": "simulated"},
    ])["passed"] is False


def test_invalid_status():
    assert review(["A"], [{"step": "A", "status": "failed"}])["passed"] is False

from planner import plan_task


def test_planner_character():
    plan = plan_task("Tao nhan vat game 2D")
    assert len(plan) == 3
    assert "nhan vat" in plan[0].lower()


def test_planner_menu():
    plan = plan_task("Tao menu game")
    assert len(plan) == 3
    assert "menu" in plan[0].lower()


def test_planner_combat():
    plan = plan_task("Tao he thong chien dau")
    assert len(plan) == 3
    assert "chien dau" in plan[0].lower()


def test_planner_default():
    plan = plan_task("Tao he thong luu game")
    assert len(plan) == 3
    assert "Phan tich" in plan[0]
from developer import generate_player


def test_generate_player(tmp_path):
    file_path = generate_player(str(tmp_path))

    assert file_path.exists()
    assert file_path.name == "player.py"
    assert "class Player:" in file_path.read_text(encoding="utf-8")


def test_generated_player_compiles(tmp_path):
    file_path = generate_player(str(tmp_path))

    source = file_path.read_text(encoding="utf-8")
    compile(source, str(file_path), "exec")
    
from reviewer import review_player


def test_review_player_valid(tmp_path):
    file_path = generate_player(str(tmp_path))
    result = review_player(file_path)

    assert result["passed"] is True
    assert result["errors"] == []


def test_review_player_missing_file(tmp_path):
    result = review_player(tmp_path / "missing.py")

    assert result["passed"] is False
    assert "File khong ton tai" in result["errors"]


def test_review_player_syntax_error(tmp_path):
    file_path = tmp_path / "player.py"
    file_path.write_text("class Player(", encoding="utf-8")

    result = review_player(file_path)

    assert result["passed"] is False


def test_review_player_missing_method(tmp_path):
    file_path = tmp_path / "player.py"
    file_path.write_text(
        "class Player:\n"
        "    def __init__(self):\n"
        "        pass\n",
        encoding="utf-8"
    )

    result = review_player(file_path)

    assert result["passed"] is False
    assert "Thieu ham move" in result["errors"]
    assert "Thieu ham get_position" in result["errors"]

from main import run_pipeline


def test_pipeline_generates_player(tmp_path):
    result = run_pipeline(
        "Tao nhan vat game 2D",
        output_dir=str(tmp_path)
    )

    assert result["source_report"]["passed"] is True
    assert (tmp_path / "player.py").exists()


def test_pipeline_other_task(tmp_path):
    result = run_pipeline(
        "Tao menu game",
        output_dir=str(tmp_path)
    )

    assert "generated_file" not in result
    assert not (tmp_path / "player.py").exists()
