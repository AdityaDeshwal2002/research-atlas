"""Shared connection setup for models served through the local LiteLLM Proxy."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    """Settings for connecting to the local LiteLLM Proxy."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().with_name(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    litellm_master_key: SecretStr
    litellm_base_url: str = "http://localhost:4000/v1"
    litellm_model: str = "research-planner"


def create_litellm_model(
    *,
    api_key: str,
    base_url: str = "http://localhost:4000/v1",
    model_name: str = "research-planner",
) -> OpenAIChatModel:
    """Create an OpenAI-compatible model client pointed at LiteLLM."""

    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    return OpenAIChatModel(model_name, provider=provider)
