from typing import Protocol
from uuid import UUID

from app.quiz.models import QuizGenerateResponse


class QuizRepository(Protocol):
    def save(self, quiz: QuizGenerateResponse) -> None:
        ...

    def get(self, quiz_id: UUID) -> QuizGenerateResponse | None:
        ...


class InMemoryQuizRepository:
    def __init__(self) -> None:
        self._quizzes: dict[UUID, QuizGenerateResponse] = {}

    def save(self, quiz: QuizGenerateResponse) -> None:
        self._quizzes[quiz.quiz_id] = quiz

    def get(self, quiz_id: UUID) -> QuizGenerateResponse | None:
        return self._quizzes.get(quiz_id)
