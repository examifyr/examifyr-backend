from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.quiz.generator import DeterministicQuizGenerator
from app.quiz.models import QuizGenerateRequest, QuizGenerateResponse
from app.quiz.normalizer import normalize_topic
from app.quiz.repo import InMemoryQuizRepository
from app.quiz.service import QuizService

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


quiz_service = QuizService(
    generator=DeterministicQuizGenerator(),
    repository=InMemoryQuizRepository(),
)


@app.post("/api/v1/quizzes/generate", response_model=QuizGenerateResponse)
async def generate_quiz(payload: QuizGenerateRequest):
    normalized_topic = normalize_topic(payload.topic)
    return quiz_service.generate_quiz(
        normalized_topic,
        payload.difficulty,
        payload.num_questions,
    )


@app.get("/api/v1/quizzes/{quiz_id}", response_model=QuizGenerateResponse)
async def get_quiz(quiz_id: UUID):
    quiz = quiz_service.get_quiz(quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz
