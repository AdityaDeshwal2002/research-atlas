"""Small PydanticAI structured-output check through the local LiteLLM gateway."""

import asyncio

from pydantic import BaseModel
from pydantic_ai import Agent

from model_gateway import GatewaySettings, create_litellm_model


class DemoResult(BaseModel):
    """The minimal structured result returned by the M2 gateway demo."""

    answer: str


def create_agent(
    *,
    api_key: str,
    base_url: str = "http://localhost:4000/v1",
    model_name: str = "research-planner",
) -> Agent[None, DemoResult]:
    """Build an agent that speaks the OpenAI-compatible LiteLLM API."""

    return Agent(
        create_litellm_model(api_key=api_key, base_url=base_url, model_name=model_name),
        output_type=DemoResult,
        instructions="Return a concise confirmation in the required answer field.",
    )


async def main() -> None:
    settings = GatewaySettings()
    agent = create_agent(
        api_key=settings.litellm_master_key.get_secret_value(),
        base_url=settings.litellm_base_url,
        model_name=settings.litellm_model,
    )
    result = await agent.run("Confirm that the model gateway request succeeded.")
    print(result.output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
