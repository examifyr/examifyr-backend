# Examifyr Backend

FastAPI-based backend service for the Examifyr platform.

---

## 🧱 Tech Stack

- **Python** 3.11
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **CORS Middleware**

---

## 📁 Project Structure

```text
examifyr-backend/
├── app/
│   └── main.py          # FastAPI app entrypoint
├── .venv/               # Python virtual environment (not committed)
├── requirements.txt     # Python dependencies
├── start-local.sh       # One-command local startup script
├── README.md

---

## 🔌 API Endpoints

- `GET /health` — Returns service health status
- `GET /version` — Returns service name and version
- `POST /api/v1/quizzes/generate` — Generates a quiz (MVP)
- `GET /api/v1/quizzes/{quiz_id}` — Retrieves a generated quiz

---

## 🧪 Quiz Generation (MVP)

**Endpoint**

`POST /api/v1/quizzes/generate`

**Request**

```json
{
  "topic": "Python Programming",
  "difficulty": "medium",
  "num_questions": 3
}
```

**Response (200)**

```json
{
  "quiz_id": "9a2d9a6b-3f2a-4c34-8d1a-0e2d2e1f4b5c",
  "topic": "Python Programming",
  "difficulty": "medium",
  "questions": [
    {
      "id": 1,
      "question": "Which statement about Python Programming is correct? (medium)",
      "choices": [
        "Python Programming option A",
        "Python Programming option B",
        "Python Programming option C",
        "Python Programming option D"
      ],
      "answer_index": 2,
      "explanation": "Generated placeholder explanation."
    }
  ]
}
```

**Notes**

- Each question includes exactly 4 choices (MVP)
- `quiz_id` is generated and stored in-memory (IDs vanish after restart)
- Quizzes are generated in-memory; persistence and async generation are planned for a future sprint

**Request fields**

- `topic` (required): non-empty string, max 120 chars (whitespace trimmed)
- `difficulty` (optional): `easy` | `medium` | `hard` (default `easy`)
- `num_questions` (optional): integer between `1` and `20` (default `5`)

**Status codes**

- `200` Success
- `422` Validation error (FastAPI default)

**Validation behavior**

- Empty or whitespace-only topic returns `422`
- `num_questions` must be between `1` and `20` (inclusive)

**Validation error example (422)**

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "topic"],
      "msg": "topic must be non-empty",
      "input": "   "
    }
  ]
}
```

---

## 📥 Quiz Retrieval (MVP)

**Endpoint**

`GET /api/v1/quizzes/{quiz_id}`

**Response (200)**

```json
{
  "quiz_id": "9a2d9a6b-3f2a-4c34-8d1a-0e2d2e1f4b5c",
  "topic": "python lists",
  "difficulty": "easy",
  "questions": [
    {
      "id": 1,
      "question": "What is the primary purpose of a Python list? (easy)",
      "choices": [
        "To store an ordered, mutable collection of items.",
        "To store only unique items without order.",
        "To map keys to values in a fixed structure.",
        "To define an immutable sequence of characters."
      ],
      "answer_index": 0,
      "explanation": "Lists are ordered and mutable, ideal for sequences you need to change."
    }
  ]
}
```

**Status codes**

- `200` Success
- `404` Quiz not found

---

## ✅ Manual Smoke Test Guide

| Step | Command | Expected |
| --- | --- | --- |
| 1 | `curl -X POST http://localhost:8000/api/v1/quizzes/generate -H "Content-Type: application/json" -d '{"topic":"Python Programming","difficulty":"medium","num_questions":3}'` | `200` with `quiz_id`, `topic`, `questions` |
| 2 | `curl http://localhost:8000/api/v1/quizzes/{quiz_id}` | `200` with the same quiz payload |
| 3 | `curl -X POST http://localhost:8000/api/v1/quizzes/generate -H "Content-Type: application/json" -d '{"topic":"   ","num_questions":5}'` | `422` validation error |
| 4 | `curl -X POST http://localhost:8000/api/v1/quizzes/generate -H "Content-Type: application/json" -d '{"topic":"Math","num_questions":21}'` | `422` validation error |

---

## 🚧 MVP Limitations / Next Steps

- In-memory generation only (not persisted)
- Persistence planned (DB/Redis)
- Rate-limiting and async processing planned later
