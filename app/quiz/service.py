import logging
from uuid import UUID, uuid4

from app.quiz.generator import QuizGenerator
from app.quiz.models import QuizGenerateResponse
from app.quiz.repo import QuizRepository

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self, generator: QuizGenerator, repository: QuizRepository) -> None:
        self._generator = generator
        self._repository = repository

    def generate_quiz(
        self, topic: str, difficulty: str, num_questions: int
    ) -> QuizGenerateResponse:
        logger.info(
            "Generating quiz",
            extra={
                "topic": topic,
                "difficulty": difficulty,
                "num_questions": num_questions,
            },
        )
        quiz_id = uuid4()
        questions = self._generator.generate(topic, difficulty, num_questions)
        quiz = QuizGenerateResponse(
            quiz_id=quiz_id,
            topic=topic,
            difficulty=difficulty,
            questions=questions,
        )
        self._repository.save(quiz)
        logger.info("Quiz generated successfully", extra={"quiz_id": str(quiz_id)})
        return quiz

    def get_quiz(self, quiz_id: UUID) -> QuizGenerateResponse | None:
        quiz = self._repository.get(quiz_id)
        if quiz is None:
            logger.warning("Quiz not found", extra={"quiz_id": str(quiz_id)})
        else:
            logger.info("Quiz retrieved successfully", extra={"quiz_id": str(quiz_id)})
        return quiz
