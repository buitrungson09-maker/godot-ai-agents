"""Kiểm thử LLM Router mà không gửi request mạng."""

import importlib

import pytest

from agents import OpenAIChatCompletionsModel

import llm_router
from llm_router import LLMConfig, build_model, build_model_from_env, load_llm_config


def test_module_import_needs_no_api_configuration(monkeypatch):
    for name in (
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "OMNIROUTE_API_KEY",
        "OMNIROUTE_MODEL",
        "OMNIROUTE_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)

    assert importlib.reload(llm_router) is llm_router


def test_direct_is_default_and_keeps_current_openai_settings():
    config = load_llm_config(
        {
            "OPENAI_API_KEY": "direct-key-not-real",
            "OPENAI_MODEL": "direct-test-model",
        }
    )

    assert config.provider == "direct"
    assert build_model(config) == "direct-test-model"


def test_direct_does_not_use_omniroute_settings():
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_model_from_env(
            {
                "LLM_PROVIDER": "direct",
                "OMNIROUTE_API_KEY": "gateway-key-not-real",
                "OMNIROUTE_MODEL": "gateway-model",
                "OMNIROUTE_BASE_URL": "http://127.0.0.1:20128/v1",
            }
        )


def test_direct_ignores_omniroute_network_limits():
    config = load_llm_config(
        {
            "LLM_PROVIDER": "direct",
            "OPENAI_API_KEY": "direct-key-not-real",
            "OPENAI_MODEL": "direct-test-model",
            "LLM_TIMEOUT_SECONDS": "invalid-for-omniroute",
            "LLM_MAX_RETRIES": "invalid-for-omniroute",
        }
    )

    assert build_model(config) == "direct-test-model"


@pytest.mark.parametrize(
    ("missing_name", "remaining"),
    [
        (
            "OMNIROUTE_API_KEY",
            {
                "OMNIROUTE_MODEL": "provider/model",
                "OMNIROUTE_BASE_URL": "http://127.0.0.1:20128/v1",
            },
        ),
        (
            "OMNIROUTE_MODEL",
            {
                "OMNIROUTE_API_KEY": "gateway-key-not-real",
                "OMNIROUTE_BASE_URL": "http://127.0.0.1:20128/v1",
            },
        ),
        (
            "OMNIROUTE_BASE_URL",
            {
                "OMNIROUTE_API_KEY": "gateway-key-not-real",
                "OMNIROUTE_MODEL": "provider/model",
            },
        ),
    ],
)
def test_omniroute_requires_its_own_settings(missing_name, remaining):
    with pytest.raises(ValueError, match=missing_name):
        load_llm_config({"LLM_PROVIDER": "omniroute", **remaining})


def test_omniroute_builds_chat_completions_model_without_request():
    config = load_llm_config(
        {
            "LLM_PROVIDER": "omniroute",
            "OMNIROUTE_API_KEY": "gateway-key-not-real",
            "OMNIROUTE_MODEL": "provider/model",
            "OMNIROUTE_BASE_URL": "http://127.0.0.1:20128/v1",
            "LLM_TIMEOUT_SECONDS": "12.5",
            "LLM_MAX_RETRIES": "0",
        }
    )

    model = build_model(config)

    assert isinstance(model, OpenAIChatCompletionsModel)
    assert model.model == "provider/model"
    assert str(model._client.base_url) == "http://127.0.0.1:20128/v1/"
    assert model._client.max_retries == 0


def test_api_key_is_hidden_from_config_repr():
    secret = "secret-value-must-not-appear"
    config = LLMConfig(
        provider="omniroute",
        model="provider/model",
        api_key=secret,
        base_url="http://127.0.0.1:20128/v1/",
    )

    assert secret not in repr(config)


@pytest.mark.parametrize("provider", ["automatic", "", "openrouter"])
def test_rejects_unknown_provider(provider):
    with pytest.raises(ValueError, match="direct.*omniroute"):
        load_llm_config({"LLM_PROVIDER": provider})


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("LLM_TIMEOUT_SECONDS", "zero", "phải là một số"),
        ("LLM_TIMEOUT_SECONDS", "0", "lớn hơn 0"),
        ("LLM_MAX_RETRIES", "1.5", "số nguyên"),
        ("LLM_MAX_RETRIES", "-1", "không được âm"),
    ],
)
def test_rejects_invalid_network_limits(name, value, message):
    environ = {
        "LLM_PROVIDER": "omniroute",
        "OMNIROUTE_API_KEY": "gateway-key-not-real",
        "OMNIROUTE_MODEL": "provider/model",
        "OMNIROUTE_BASE_URL": "http://127.0.0.1:20128/v1",
        name: value,
    }

    with pytest.raises(ValueError, match=message):
        load_llm_config(environ)


def test_rejects_invalid_omniroute_url():
    with pytest.raises(ValueError, match="URL HTTP hoặc HTTPS"):
        load_llm_config(
            {
                "LLM_PROVIDER": "omniroute",
                "OMNIROUTE_API_KEY": "gateway-key-not-real",
                "OMNIROUTE_MODEL": "provider/model",
                "OMNIROUTE_BASE_URL": "not-a-url",
            }
        )


def test_rejects_credentials_in_url_without_leaking_them():
    secret = "url-secret-must-not-appear"

    with pytest.raises(ValueError) as error_info:
        load_llm_config(
            {
                "LLM_PROVIDER": "omniroute",
                "OMNIROUTE_API_KEY": "gateway-key-not-real",
                "OMNIROUTE_MODEL": "provider/model",
                "OMNIROUTE_BASE_URL": f"https://user:{secret}@gateway.example/v1",
            }
        )

    assert secret not in str(error_info.value)
