from uuid import UUID, uuid4

from app.quiz.generator import QuizGenerator
from app.quiz.models import QuizGenerateResponse
from app.quiz.repo import QuizRepository


class QuizService:
    def __init__(self, generator: QuizGenerator, repository: QuizRepository) -> None:
        self._generator = generator
        self._repository = repository

    def generate_quiz(
        self, topic: str, difficulty: str, num_questions: int
    ) -> QuizGenerateResponse:
        quiz_id = uuid4()
        questions = self._generator.generate(topic, difficulty, num_questions)
        quiz = QuizGenerateResponse(
            quiz_id=quiz_id,
            topic=topic,
            difficulty=difficulty,
            questions=questions,
        )
        self._repository.save(quiz)
        return quiz

    def get_quiz(self, quiz_id: UUID) -> QuizGenerateResponse | None:
        return self._repository.get(quiz_id)
