
from unittest.mock import Mock, call

import pytest

import coordinator


def make_result(**data):
    """Tao doi tuong AI gia lap co model_dump()."""
    result = Mock()
    for key, value in data.items():
        setattr(result, key, value)
    result.model_dump.return_value = data
    return result


@pytest.fixture
def setup_agents(monkeypatch):
    """Gia lap Planner va Developer, khong goi API."""

    planner = make_result(
        implementation_steps=["Tao ky nang chem kiem"]
    )

    developer = make_result(
        file_name="sword_slash.gd",
        gdscript="extends Node2D\n# original",
        explanation="Ma ban dau",
    )

    pipeline = Mock(return_value={
        "task": "Tao ky nang chem kiem",
        "plan": ["Tao ky nang chem kiem"],
        "report": {"passed": True},
    })

    monkeypatch.setattr(
        coordinator, "run_pipeline", pipeline
    )
    monkeypatch.setattr(
        coordinator, "_run_ai_planner",
        Mock(return_value=planner),
    )
    monkeypatch.setattr(
        coordinator, "_run_ai_developer",
        Mock(return_value=developer),
    )

    return developer


def run_auto_repair():
    return coordinator.coordinate(
        "Tao ky nang chem kiem",
        mode="ai",
        developer_mode="ai",
        reviewer_mode="ai",
        auto_repair=True,
    )


def test_reviewer_pass_no_repair(
    monkeypatch, setup_agents
):
    """PASS lan dau thi khong sua."""

    reviewer = Mock(return_value=make_result(
        passed=True,
        score=9,
        errors=[],
        warnings=[],
        suggestions=[],
        explanation="Dat yeu cau",
    ))

    repair = Mock()

    monkeypatch.setattr(
        coordinator, "_run_ai_reviewer", reviewer
    )
    monkeypatch.setattr(
        coordinator, "_run_ai_repair", repair
    )

    result = run_auto_repair()

    assert result["status"] == (
        "reviewed_for_manual_approval"
    )
    assert result["repair_attempts"] == 0
    assert reviewer.call_count == 1
    repair.assert_not_called()


def test_reviewer_fail_then_repair_pass(
    monkeypatch, setup_agents
):
    """FAIL -> sua mot lan -> PASS."""

    first = make_result(
        passed=False,
        score=5,
        errors=["Thieu xu ly damage"],
        warnings=[],
        suggestions=[],
        explanation="Can sua",
    )

    second = make_result(
        passed=True,
        score=9,
        errors=[],
        warnings=[],
        suggestions=[],
        explanation="Da dat",
    )

    reviewer = Mock(side_effect=[first, second])

    repaired = make_result(
        file_name="sword_slash.gd",
        gdscript="extends Node2D\n# repaired",
        explanation="Da sua damage",
    )

    repair = Mock(return_value=repaired)

    monkeypatch.setattr(
        coordinator, "_run_ai_reviewer", reviewer
    )
    monkeypatch.setattr(
        coordinator, "_run_ai_repair", repair
    )

    result = run_auto_repair()

    assert result["status"] == (
        "reviewed_for_manual_approval"
    )
    assert result["repair_attempts"] == 1
    assert reviewer.call_count == 2
    repair.assert_called_once_with(
        "Tao ky nang chem kiem",
        "extends Node2D\n# original",
        ["Thieu xu ly damage"],
    )
    assert "ai_second_review" in result
    assert result["ai_revised_developer"]["gdscript"] == (
        "extends Node2D\n# repaired"
    )


def test_reviewer_fail_after_repair(
    monkeypatch, setup_agents
):
    """FAIL -> sua mot lan -> van FAIL -> dung."""

    first = make_result(
        passed=False,
        score=4,
        errors=["Thieu hitbox"],
        warnings=[],
        suggestions=[],
        explanation="Can sua",
    )

    second = make_result(
        passed=False,
        score=6,
        errors=["Hitbox chua dung"],
        warnings=[],
        suggestions=[],
        explanation="Van can sua",
    )

    reviewer = Mock(side_effect=[first, second])

    repair = Mock(return_value=make_result(
        file_name="sword_slash.gd",
        gdscript="extends Node2D\n# repaired",
        explanation="Da thu sua",
    ))

    monkeypatch.setattr(
        coordinator, "_run_ai_reviewer", reviewer
    )
    monkeypatch.setattr(
        coordinator, "_run_ai_repair", repair
    )

    result = run_auto_repair()

    assert result["status"] == (
        "review_changes_required"
    )
    assert result["repair_attempts"] == 1
    assert reviewer.call_count == 2
    assert repair.call_count == 1


def test_auto_repair_requires_three_ai_agents():
    """Khong bat auto-repair neu thieu AI Agent."""

    with pytest.raises(ValueError):
        coordinator.coordinate(
            "Tao ky nang",
            mode="offline",
            developer_mode="offline",
            reviewer_mode="offline",
            auto_repair=True,
        )
