import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_generate_quiz_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "topic": "Python Programming",
            "difficulty": "medium",
            "num_questions": 3,
        }
        response = await client.post("/api/v1/quizzes/generate", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "quiz_id" in data
    assert "topic" in data
    assert "questions" in data
    assert data["topic"] == payload["topic"]
    assert len(data["questions"]) == 3
    assert 0 <= data["questions"][0]["answer_index"] <= 3


@pytest.mark.asyncio
async def test_generate_quiz_validation_empty_topic():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "   ", "num_questions": 5}
        response = await client.post("/api/v1/quizzes/generate", json=payload)

    assert response.status_code == 422
    assert "topic must be non-empty" in response.text


@pytest.mark.asyncio
async def test_generate_quiz_bounds():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "Math", "num_questions": 21}
        response = await client.post("/api/v1/quizzes/generate", json=payload)

    assert response.status_code == 422
