import pytest
from pydantic import ValidationError

from research_plan import ResearchPlan


def test_research_plan_normalizes_question_and_search_terms() -> None:
    plan = ResearchPlan(
        original_question="  How can AI support early pancreatic cancer detection?  ",
        search_terms=[" artificial intelligence ", "ARTIFICIAL INTELLIGENCE", "pancreatic cancer"],
    )

    assert plan.original_question == "How can AI support early pancreatic cancer detection?"
    assert plan.search_terms == ["artificial intelligence", "pancreatic cancer"]


@pytest.mark.parametrize(
    ("original_question", "search_terms"),
    [("   ", ["pancreatic cancer"]), ("research question", [" "])],
)
def test_research_plan_rejects_blank_values(
    original_question: str,
    search_terms: list[str],
) -> None:
    with pytest.raises(ValidationError):
        ResearchPlan(original_question=original_question, search_terms=search_terms)


def test_research_plan_requires_at_least_one_search_term() -> None:
    with pytest.raises(ValidationError):
        ResearchPlan(original_question="research question", search_terms=[])
