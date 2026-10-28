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
