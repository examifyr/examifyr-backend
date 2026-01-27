import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def _post_quiz(client: AsyncClient, payload: dict) -> dict:
    response = await client.post("/api/v1/quizzes/generate", json=payload)
    return {"status": response.status_code, "json": response.json(), "text": response.text}


@pytest.mark.asyncio
async def test_generate_quiz_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "topic": "Python Programming",
            "difficulty": "medium",
            "num_questions": 3,
        }
        result = await _post_quiz(client, payload)

    assert result["status"] == 200
    data = result["json"]
    assert set(data.keys()) == {"quiz_id", "topic", "difficulty", "questions"}
    assert data["topic"] == payload["topic"]
    assert len(data["questions"]) == 3
    for question in data["questions"]:
        assert len(question["choices"]) == 4
        assert 0 <= question["answer_index"] <= 3


@pytest.mark.asyncio
async def test_generate_quiz_and_retrieve():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "python lists", "difficulty": "easy", "num_questions": 2}
        result = await _post_quiz(client, payload)

        quiz_id = result["json"]["quiz_id"]
        get_response = await client.get(f"/api/v1/quizzes/{quiz_id}")

    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["quiz_id"] == quiz_id
    assert fetched["topic"] == "python lists"
    assert len(fetched["questions"]) == 2


@pytest.mark.asyncio
async def test_generate_quiz_validation_empty_topic():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "   ", "num_questions": 5}
        result = await _post_quiz(client, payload)

    assert result["status"] == 422
    assert "topic must be non-empty" in result["text"]


@pytest.mark.asyncio
async def test_generate_quiz_bounds():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "Math", "num_questions": 21}
        result = await _post_quiz(client, payload)

    assert result["status"] == 422


@pytest.mark.asyncio
async def test_get_quiz_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/quizzes/{uuid.uuid4()}")

    assert response.status_code == 404
