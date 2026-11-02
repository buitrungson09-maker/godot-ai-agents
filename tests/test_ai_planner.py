"""Kiểm thử AI Planner mà không gọi OpenAI API thật."""

from types import SimpleNamespace

import pytest
from agents import OpenAIChatCompletionsModel

import ai_planner
from ai_planner import AIPlannerError, GamePlan, plan_task_ai


def make_plan() -> GamePlan:
    """Tạo một kế hoạch hợp lệ dùng chung trong các bài kiểm thử."""

    return GamePlan(
        summary="Tạo nhân vật di chuyển trong game 2D.",
        features=["Di chuyển bốn hướng"],
        gdscript_files=["scripts/player.gd"],
        scenes_and_nodes=["Player.tscn: CharacterBody2D"],
        implementation_steps=["Tạo scene Player"],
        test_cases=["Nhấn sang phải: nhân vật di chuyển sang phải"],
        assumptions=["Dự án dùng Godot 4"],
    )


def configure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cấu hình biến giả; các giá trị này không phải thông tin xác thực thật."""

    monkeypatch.setenv("LLM_PROVIDER", "direct")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")


def test_module_imports_successfully():
    assert ai_planner.GamePlan is GamePlan
    assert callable(ai_planner.plan_task_ai)


def test_game_plan_json_schema():
    schema = GamePlan.model_json_schema()

    assert schema["type"] == "object"
    assert set(schema["required"]) == set(GamePlan.model_fields)
    assert schema["properties"]["summary"]["type"] == "string"
    assert schema["properties"]["features"]["type"] == "array"
    assert schema["properties"]["features"]["items"]["type"] == "string"


@pytest.mark.parametrize("task", ["", "   ", None])
def test_rejects_empty_or_non_string_input(task):
    with pytest.raises(ValueError, match="không được rỗng"):
        plan_task_ai(task)


def test_rejects_missing_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "direct")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        plan_task_ai("Tạo nhân vật")


def test_rejects_missing_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "direct")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    with pytest.raises(ValueError, match="OPENAI_MODEL"):
        plan_task_ai("Tạo nhân vật")


def test_returns_valid_plan_without_calling_api(monkeypatch):
    configure_environment(monkeypatch)
    expected_plan = make_plan()
    captured = {}

    def fake_run_sync(agent, *, input, max_turns, run_config):
        captured.update(
            agent=agent,
            input=input,
            max_turns=max_turns,
            run_config=run_config,
        )
        return SimpleNamespace(final_output=expected_plan)

    monkeypatch.setattr(ai_planner.Runner, "run_sync", fake_run_sync)

    result = plan_task_ai("  Tạo nhân vật  ")

    assert result is expected_plan
    assert captured["input"] == "Tạo nhân vật"
    assert captured["max_turns"] == 1
    assert captured["run_config"].tracing_disabled is True
    assert captured["agent"].model == "test-model"
    assert captured["agent"].output_type is GamePlan


def test_omniroute_model_is_used_without_calling_api(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "omniroute")
    monkeypatch.setenv("OMNIROUTE_API_KEY", "gateway-key-not-real")
    monkeypatch.setenv("OMNIROUTE_MODEL", "provider/model")
    monkeypatch.setenv("OMNIROUTE_BASE_URL", "http://127.0.0.1:20128/v1")
    expected_plan = make_plan()
    captured = {}

    def fake_run_sync(agent, **kwargs):
        captured["model"] = agent.model
        return SimpleNamespace(final_output=expected_plan)

    monkeypatch.setattr(ai_planner.Runner, "run_sync", fake_run_sync)

    result = plan_task_ai("Tạo nhân vật")

    assert result is expected_plan
    assert isinstance(captured["model"], OpenAIChatCompletionsModel)
    assert captured["model"].model == "provider/model"


def test_rejects_invalid_planner_output(monkeypatch):
    configure_environment(monkeypatch)
    monkeypatch.setattr(
        ai_planner.Runner,
        "run_sync",
        lambda *args, **kwargs: SimpleNamespace(final_output={"summary": "sai"}),
    )

    with pytest.raises(ValueError, match="đúng cấu trúc"):
        plan_task_ai("Tạo nhân vật")


def test_wraps_runner_failure(monkeypatch):
    configure_environment(monkeypatch)

    def fail_run_sync(*args, **kwargs):
        raise ConnectionError("simulated API outage")

    monkeypatch.setattr(ai_planner.Runner, "run_sync", fail_run_sync)

    with pytest.raises(AIPlannerError, match="dịch vụ AI") as error_info:
        plan_task_ai("Tạo nhân vật")

    assert isinstance(error_info.value.__cause__, ConnectionError)
