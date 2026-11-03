
"""Kiem thu tich hop 3 AI Agent bang mock, khong goi API."""

from types import SimpleNamespace

import pytest

import coordinator


def fake_result(**values):
    """Tao doi tuong gia co model_dump()."""
    return SimpleNamespace(
        **values,
        model_dump=lambda: values.copy(),
    )


@pytest.fixture
def mock_ai_pipeline(monkeypatch):
    """Gia lap Planner, Developer va pipeline offline."""

    calls = {
        "planner": 0,
        "developer": 0,
        "reviewer": 0,
    }

    plan = fake_result(
        implementation_steps=[
            "Tao script sword_slash.gd",
            "Them cooldown 3 giay",
        ],
    )

    generated = fake_result(
        file_name="sword_slash.gd",
        gdscript=(
            "extends Node\n"
            "signal skill_activated(damage: int)\n"
            "func use_skill() -> bool:\n"
            "    return true\n"
        ),
        explanation="Script kiem thu gia lap.",
    )

    def fake_planner(task):
        calls["planner"] += 1
        return plan

    def fake_developer(task):
        calls["developer"] += 1
        assert "sword_slash.gd" in task
        return generated

    def fake_pipeline(task, output_dir, planner_func):
        steps = planner_func(task)
        return {
            "task": task,
            "plan": steps,
            "work": [],
            "report": {
                "passed": True,
                "checked": len(steps),
                "mode": "offline simulation",
            },
        }

    monkeypatch.setattr(
        coordinator, "_run_ai_planner", fake_planner
    )
    monkeypatch.setattr(
        coordinator, "_run_ai_developer", fake_developer
    )
    monkeypatch.setattr(
        coordinator, "run_pipeline", fake_pipeline
    )

    return calls, generated


@pytest.mark.parametrize(
    ("review_passed", "expected_status"),
    [
        (True, "reviewed_for_manual_approval"),
        (False, "review_changes_required"),
    ],
)
def test_ai_reviewer_handles_pass_and_fail(
    monkeypatch,
    tmp_path,
    mock_ai_pipeline,
    review_passed,
    expected_status,
):
    calls, generated = mock_ai_pipeline

    def fake_reviewer(task, gdscript):
        calls["reviewer"] += 1

        assert "sword_slash.gd" in task
        assert gdscript == generated.gdscript

        return fake_result(
            passed=review_passed,
            score=8 if review_passed else 5,
            errors=[] if review_passed else ["Thieu hitbox"],
            warnings=["Chua kiem thu Godot Engine"],
            suggestions=["Kiem tra trong Godot"],
            explanation="Ket qua AI gia lap",
        )

    monkeypatch.setattr(
        coordinator,
        "_run_ai_reviewer",
        fake_reviewer,
    )

    result = coordinator.coordinate(
        "Tao ky nang sword_slash.gd",
        output_dir=tmp_path,
        mode="ai",
        developer_mode="ai",
        reviewer_mode="ai",
    )

    assert result["status"] == expected_status
    assert result["ai_review"]["passed"] is review_passed
    assert result["ai_developer"]["gdscript"] == generated.gdscript
    assert result["reviewer_mode"] == "ai"

    assert calls == {
        "planner": 1,
        "developer": 1,
        "reviewer": 1,
    }

    assert list(tmp_path.iterdir()) == []


def test_reviewer_offline_does_not_call_ai(
    monkeypatch,
    tmp_path,
    mock_ai_pipeline,
):
    calls, _ = mock_ai_pipeline

    def fail_reviewer(task, gdscript):
        raise AssertionError("Khong duoc goi Reviewer AI")

    monkeypatch.setattr(
        coordinator,
        "_run_ai_reviewer",
        fail_reviewer,
    )

    result = coordinator.coordinate(
        "Tao ky nang sword_slash.gd",
        output_dir=tmp_path,
        mode="ai",
        developer_mode="ai",
    )

    assert result["status"] == "generated_for_manual_review"
    assert "ai_review" not in result
    assert calls["developer"] == 1
    assert calls["reviewer"] == 0


def test_reviewer_ai_requires_developer_ai(tmp_path):
    with pytest.raises(ValueError, match="Developer AI"):
        coordinator.coordinate(
            "Tao ky nang kiem",
            output_dir=tmp_path,
            mode="ai",
            developer_mode="offline",
            reviewer_mode="ai",
        )


def test_rejects_invalid_reviewer_mode(tmp_path):
    with pytest.raises(ValueError, match="Reviewer mode"):
        coordinator.coordinate(
            "Tao ky nang kiem",
            output_dir=tmp_path,
            reviewer_mode="invalid",
        )
