"""PydanticAI planner that converts a research question into search concepts."""

import argparse
import asyncio

from pydantic_ai import Agent, NativeOutput

from model_gateway import GatewaySettings, create_litellm_model
from research_plan import ResearchPlan

PLANNER_INSTRUCTIONS = """
Create a concise literature-search plan for the user's research question.
Copy the question into original_question. Return one to eight concise,
provider-neutral search terms that represent the main concepts. Do not return
paper titles, citations, publication metadata, or search results. Source selection
is handled by the application, not by this planner.
"""


def create_research_planner(
    *,
    api_key: str,
    base_url: str = "http://localhost:4000/v1",
    model_name: str = "research-planner",
) -> Agent[None, ResearchPlan]:
    """Build a PydanticAI agent that returns a structured ResearchPlan."""

    model = create_litellm_model(api_key=api_key, base_url=base_url, model_name=model_name)
    return Agent(model, output_type=NativeOutput(ResearchPlan), instructions=PLANNER_INSTRUCTIONS)


async def plan_research_question(
    question: str,
    *,
    agent: Agent[None, ResearchPlan] | None = None,
) -> ResearchPlan:
    """Plan searches for a question and preserve the user's original text."""

    original_question = question.strip()
    if not original_question:
        raise ValueError("The research question must not be blank.")

    planner = agent
    if planner is None:
        settings = GatewaySettings()
        planner = create_research_planner(
            api_key=settings.litellm_master_key.get_secret_value(),
            base_url=settings.litellm_base_url,
            model_name=settings.litellm_model,
        )

    result = await planner.run(original_question)
    return ResearchPlan(
        original_question=original_question,
        search_terms=result.output.search_terms,
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="Create a structured Research Atlas search plan.")
    parser.add_argument("question", help="The research question to plan searches for")
    args = parser.parse_args()

    plan = await plan_research_question(args.question)
    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
