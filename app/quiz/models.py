from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class QuizGenerateRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=120)
    difficulty: Literal["easy", "medium", "hard"] = "easy"
    num_questions: int = Field(default=5, ge=1, le=20)

    @field_validator("topic")
    @classmethod
    def normalize_topic(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("topic must be non-empty")
        return cleaned


class QuizQuestion(BaseModel):
    id: int
    question: str
    choices: list[str] = Field(min_items=4, max_items=4)
    answer_index: int = Field(ge=0, le=3)
    explanation: str


class QuizGenerateResponse(BaseModel):
    quiz_id: UUID
    topic: str
    difficulty: str
    questions: list[QuizQuestion]
