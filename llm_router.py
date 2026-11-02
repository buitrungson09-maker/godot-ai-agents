"""Chọn model cho AI Planner mà không thực hiện request mạng."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Literal
from urllib.parse import urlparse

from agents import Model, OpenAIChatCompletionsModel
from openai import AsyncOpenAI


ProviderName = Literal["direct", "omniroute"]


@dataclass(frozen=True)
class LLMConfig:
    """Cấu hình tối thiểu để tạo model; API key không xuất hiện trong repr."""

    provider: ProviderName
    model: str
    api_key: str = field(repr=False)
    base_url: str | None = None
    timeout_seconds: float = 30.0
    max_retries: int = 1


def _required(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Chưa cấu hình biến môi trường {name}.")
    return value


def _read_timeout(environ: Mapping[str, str]) -> float:
    raw_value = environ.get("LLM_TIMEOUT_SECONDS", "30").strip()
    try:
        timeout = float(raw_value)
    except ValueError as error:
        raise ValueError("LLM_TIMEOUT_SECONDS phải là một số.") from error
    if timeout <= 0:
        raise ValueError("LLM_TIMEOUT_SECONDS phải lớn hơn 0.")
    return timeout


def _read_max_retries(environ: Mapping[str, str]) -> int:
    raw_value = environ.get("LLM_MAX_RETRIES", "1").strip()
    try:
        max_retries = int(raw_value)
    except ValueError as error:
        raise ValueError("LLM_MAX_RETRIES phải là số nguyên.") from error
    if max_retries < 0:
        raise ValueError("LLM_MAX_RETRIES không được âm.")
    return max_retries


def _validate_base_url(base_url: str) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("OMNIROUTE_BASE_URL phải là URL HTTP hoặc HTTPS hợp lệ.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("OMNIROUTE_BASE_URL không được chứa thông tin xác thực.")
    return base_url.rstrip("/") + "/"


def load_llm_config(environ: Mapping[str, str] | None = None) -> LLMConfig:
    """Đọc cấu hình provider từ biến môi trường mà không kết nối mạng."""

    values = os.environ if environ is None else environ
    provider = values.get("LLM_PROVIDER", "direct").strip().lower()

    if provider == "direct":
        api_key = _required(values, "OPENAI_API_KEY")
        model = _required(values, "OPENAI_MODEL")
        return LLMConfig(
            provider="direct",
            model=model,
            api_key=api_key,
        )

    if provider == "omniroute":
        return LLMConfig(
            provider="omniroute",
            model=_required(values, "OMNIROUTE_MODEL"),
            api_key=_required(values, "OMNIROUTE_API_KEY"),
            base_url=_validate_base_url(_required(values, "OMNIROUTE_BASE_URL")),
            timeout_seconds=_read_timeout(values),
            max_retries=_read_max_retries(values),
        )

    raise ValueError("LLM_PROVIDER phải là 'direct' hoặc 'omniroute'.")


def build_model(config: LLMConfig) -> str | Model:
    """Tạo model SDK cho đúng một provider, không fallback và không gọi API."""

    if config.provider == "direct":
        return config.model

    if config.provider == "omniroute":
        if config.base_url is None:
            raise ValueError("OmniRoute cần base_url.")
        client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout_seconds,
            max_retries=config.max_retries,
        )
        return OpenAIChatCompletionsModel(
            model=config.model,
            openai_client=client,
            strict_feature_validation=True,
        )

    raise ValueError("Provider không được hỗ trợ.")


def build_model_from_env(environ: Mapping[str, str] | None = None) -> str | Model:
    """Đọc cấu hình và tạo model cho AI Planner."""

    return build_model(load_llm_config(environ))
