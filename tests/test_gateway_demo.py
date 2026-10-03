import pytest
from pydantic_ai.models.test import TestModel

from gateway_demo import DemoResult, create_agent


@pytest.mark.asyncio
async def test_agent_returns_validated_demo_result() -> None:
    agent = create_agent(api_key="test-proxy-key")
    test_model = TestModel(custom_output_args={"answer": "The simulated gateway succeeded."})

    with agent.override(model=test_model):
        result = await agent.run("Return a gateway confirmation.")

    assert result.output == DemoResult(answer="The simulated gateway succeeded.")
