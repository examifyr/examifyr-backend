import random
from uuid import UUID, uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Literal

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"service": "examifyr-backend", "version": "0.1.0"}


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
    choices: list[str] = Field(min_length=4, max_length=4)
    answer_index: int = Field(ge=0, le=3)
    explanation: str


class QuizGenerateResponse(BaseModel):
    quiz_id: UUID
    topic: str
    difficulty: str
    questions: list[QuizQuestion]


def build_questions(topic: str, difficulty: str, num_questions: int) -> list[QuizQuestion]:
    templates = [
        "Which statement about {topic} is correct?",
        "Pick the best answer related to {topic}.",
        "In {topic}, which option fits best?",
        "Choose the correct {topic} concept.",
    ]
    questions: list[QuizQuestion] = []
    for i in range(num_questions):
        choices = [
            f"{topic} option A",
            f"{topic} option B",
            f"{topic} option C",
            f"{topic} option D",
        ]
        question_text = random.choice(templates).format(topic=topic)
        questions.append(
            QuizQuestion(
                id=i + 1,
                question=f"{question_text} ({difficulty})",
                choices=choices,
                answer_index=random.randint(0, 3),
                explanation="Generated placeholder explanation.",
            )
        )
    return questions


@app.post("/api/v1/quizzes/generate", response_model=QuizGenerateResponse)
async def generate_quiz(payload: QuizGenerateRequest):
    # TODO: Consider async generation and persistence in a future sprint.
    return QuizGenerateResponse(
        quiz_id=uuid4(),
        topic=payload.topic,
        difficulty=payload.difficulty,
        questions=build_questions(
            payload.topic,
            payload.difficulty,
            payload.num_questions,
        ),
    )
