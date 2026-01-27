import uuid

import pytest
from httpx import ASGITransport, AsyncClient, Response

from app.main import app


async def _post_quiz(client: AsyncClient, payload: dict) -> Response:
    return await client.post("/api/v1/quizzes/generate", json=payload)


@pytest.mark.asyncio
async def test_generate_quiz_success() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "topic": "Python Programming",
            "difficulty": "medium",
            "num_questions": 3,
        }
        response = await _post_quiz(client, payload)

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"quiz_id", "topic", "difficulty", "questions"}
    assert data["topic"] == payload["topic"]
    assert len(data["questions"]) == 3
    for question in data["questions"]:
        assert len(question["choices"]) == 4
        assert 0 <= question["answer_index"] <= 3


@pytest.mark.asyncio
async def test_generate_quiz_and_retrieve() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "python lists", "difficulty": "easy", "num_questions": 2}
        response = await _post_quiz(client, payload)

        quiz_id = response.json()["quiz_id"]
        get_response = await client.get(f"/api/v1/quizzes/{quiz_id}")

    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["quiz_id"] == quiz_id
    assert fetched["topic"] == "python lists"
    assert len(fetched["questions"]) == 2


@pytest.mark.asyncio
async def test_generate_quiz_validation_empty_topic() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "   ", "num_questions": 5}
        response = await _post_quiz(client, payload)

    assert response.status_code == 422
    assert "topic must be non-empty" in response.text


@pytest.mark.asyncio
async def test_generate_quiz_bounds() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "Math", "num_questions": 21}
        response = await _post_quiz(client, payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_quiz_not_found() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/quizzes/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_quiz_generation_is_deterministic() -> None:
    """Verify that identical inputs produce identical question content."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"topic": "python lists", "difficulty": "easy", "num_questions": 3}

        response1 = await _post_quiz(client, payload)
        response2 = await _post_quiz(client, payload)

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.json()
    data2 = response2.json()

    assert data1["quiz_id"] != data2["quiz_id"]

    assert len(data1["questions"]) == len(data2["questions"])
    for q1, q2 in zip(data1["questions"], data2["questions"]):
        assert q1["question"] == q2["question"]
        assert q1["choices"] == q2["choices"]
        assert q1["answer_index"] == q2["answer_index"]
        assert q1["explanation"] == q2["explanation"]
