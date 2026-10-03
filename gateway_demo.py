"""Small PydanticAI structured-output check through the local LiteLLM gateway."""

import asyncio
from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_settings import BaseSettings, SettingsConfigDict


class DemoResult(BaseModel):
    """The minimal structured result returned by the M2 gateway demo."""

    answer: str


class DemoSettings(BaseSettings):
    """Local connection settings; credentials are read from the ignored .env file."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().with_name(".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    litellm_master_key: SecretStr
    litellm_base_url: str = "http://localhost:4000/v1"
    litellm_model: str = "research-planner"


def create_agent(
    *,
    api_key: str,
    base_url: str = "http://localhost:4000/v1",
    model_name: str = "research-planner",
) -> Agent[None, DemoResult]:
    """Build an agent that speaks the OpenAI-compatible LiteLLM API."""

    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    model = OpenAIChatModel(model_name, provider=provider)
    return Agent(
        model,
        output_type=DemoResult,
        instructions="Return a concise confirmation in the required answer field.",
    )


async def main() -> None:
    settings = DemoSettings()
    agent = create_agent(
        api_key=settings.litellm_master_key.get_secret_value(),
        base_url=settings.litellm_base_url,
        model_name=settings.litellm_model,
    )
    result = await agent.run("Confirm that the model gateway request succeeded.")
    print(result.output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
