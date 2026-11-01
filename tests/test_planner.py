import pytest
from pydantic_ai.models.test import TestModel
from pydantic_ai.profiles import ModelProfile

from planner import create_research_planner, plan_research_question
from research_plan import ResearchPlan


@pytest.mark.asyncio
async def test_planner_returns_a_research_plan_and_preserves_question() -> None:
    question = "How can AI support early pancreatic cancer detection?"
    agent = create_research_planner(api_key="test-proxy-key")
    test_model = TestModel(
        custom_output_text=(
            '{"original_question":"A paraphrased question from the simulated model",'
            '"search_terms":["artificial intelligence","pancreatic cancer","early detection"]}'
        ),
        profile=ModelProfile(supports_json_schema_output=True),
    )

    with agent.override(model=test_model):
        result = await plan_research_question(question, agent=agent)

    assert result == ResearchPlan(
        original_question=question,
        search_terms=["artificial intelligence", "pancreatic cancer", "early detection"],
    )
    assert test_model.last_model_request_parameters is not None
    assert test_model.last_model_request_parameters.output_mode == "native"


@pytest.mark.asyncio
async def test_planner_rejects_blank_question_before_calling_model() -> None:
    agent = create_research_planner(api_key="test-proxy-key")

    with pytest.raises(ValueError, match="must not be blank"):
        await plan_research_question("  ", agent=agent)
