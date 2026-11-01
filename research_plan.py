"""Validated, provider-neutral research search plans."""

from pydantic import BaseModel, Field, field_validator


class ResearchPlan(BaseModel):
    """The user's research question and concepts to use in later source searches."""

    original_question: str = Field(
        min_length=1,
        description="The user's research question, copied without changing its meaning.",
    )
    search_terms: list[str] = Field(
        min_length=1,
        max_length=8,
        description="A short list of provider-neutral concepts for literature searches.",
    )

    @field_validator("original_question")
    @classmethod
    def normalize_original_question(cls, value: str) -> str:
        question = value.strip()
        if not question:
            raise ValueError("The original question must not be blank.")
        return question

    @field_validator("search_terms")
    @classmethod
    def normalize_search_terms(cls, values: list[str]) -> list[str]:
        terms = [value.strip() for value in values]
        if any(not term for term in terms):
            raise ValueError("Search terms must not be blank.")

        unique_terms: dict[str, str] = {}
        for term in terms:
            unique_terms.setdefault(term.casefold(), term)
        return list(unique_terms.values())
