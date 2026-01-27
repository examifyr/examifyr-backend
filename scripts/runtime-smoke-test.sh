#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

pass() {
  echo "PASS: $1"
}

fail() {
  echo "FAIL: $1"
  if [ -n "${2:-}" ]; then
    echo "$2"
  fi
  exit 1
}

print_json_if_possible() {
  local body="$1"
  if formatted=$(printf '%s' "$body" | python3 - <<'PY' 2>/dev/null); then
import json
import sys

data = json.load(sys.stdin)
print(json.dumps(data, indent=2, sort_keys=True))
PY
    echo "$formatted"
  else
    echo "$body"
  fi
}

request() {
  local method="$1"
  local url="$2"
  local payload="${3:-}"

  if [ -n "$payload" ]; then
    local response
    response=$(curl -sS -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$payload" \
      -w "\n%{http_code}")
    RESPONSE_BODY="${response%$'\n'*}"
    RESPONSE_STATUS="${response##*$'\n'}"
  else
    local response
    response=$(curl -sS -X "$method" "$url" -w "\n%{http_code}")
    RESPONSE_BODY="${response%$'\n'*}"
    RESPONSE_STATUS="${response##*$'\n'}"
  fi
}

echo "Running runtime smoke tests against $BASE_URL"

# A) Health check
request "GET" "$BASE_URL/health"
if [ "$RESPONSE_STATUS" != "200" ]; then
  fail "Health check (expected 200)" "$RESPONSE_BODY"
fi
echo "Health response:"
print_json_if_possible "$RESPONSE_BODY"
pass "Health check"

# B) Version check
request "GET" "$BASE_URL/version"
if [ "$RESPONSE_STATUS" != "200" ]; then
  fail "Version check (expected 200)" "$RESPONSE_BODY"
fi
pass "Version check"

# C) Generate quiz
payload_generate='{"topic":"Python lists","difficulty":"easy","num_questions":3}'
request "POST" "$BASE_URL/api/v1/quizzes/generate" "$payload_generate"
if [ "$RESPONSE_STATUS" != "200" ]; then
  fail "Generate quiz (expected 200)" "$RESPONSE_BODY"
fi

if quiz_id=$(printf '%s' "$RESPONSE_BODY" | python3 - <<'PY'); then
import json
import sys

data = json.load(sys.stdin)
required = {"quiz_id", "topic", "difficulty", "questions"}
missing = required - set(data.keys())
if missing:
    raise SystemExit(f"Missing keys: {missing}")

quiz_id = data["quiz_id"]
if not quiz_id:
    raise SystemExit("quiz_id is empty")
if data["topic"] != "Python lists":
    raise SystemExit(f"topic mismatch: {data['topic']}")
if data["difficulty"] != "easy":
    raise SystemExit(f"difficulty mismatch: {data['difficulty']}")
if len(data["questions"]) != 3:
    raise SystemExit(f"questions length mismatch: {len(data['questions'])}")
for question in data["questions"]:
    if len(question.get("choices", [])) != 4:
        raise SystemExit("choices length mismatch")
    answer_index = question.get("answer_index", -1)
    if not (0 <= answer_index <= 3):
        raise SystemExit("answer_index out of range")

print(quiz_id)
PY
  pass "Generate quiz"
else
  fail "Generate quiz response validation failed" "$RESPONSE_BODY"
fi

# D) Get quiz by ID
request "GET" "$BASE_URL/api/v1/quizzes/$quiz_id"
if [ "$RESPONSE_STATUS" != "200" ]; then
  fail "Get quiz by id (expected 200)" "$RESPONSE_BODY"
fi
if ! printf '%s' "$RESPONSE_BODY" | python3 - <<PY; then
import json
import sys

data = json.load(sys.stdin)
if data.get("quiz_id") != "$quiz_id":
    raise SystemExit("quiz_id mismatch")
PY
  fail "Get quiz validation failed" "$RESPONSE_BODY"
fi
pass "Get quiz by ID"

# E) Validation error
payload_invalid='{"topic":"   ","difficulty":"easy","num_questions":3}'
request "POST" "$BASE_URL/api/v1/quizzes/generate" "$payload_invalid"
if [ "$RESPONSE_STATUS" != "422" ]; then
  fail "Validation error (expected 422)" "$RESPONSE_BODY"
fi
if [[ "$RESPONSE_BODY" != *"topic must be non-empty"* ]]; then
  fail "Validation error body missing message" "$RESPONSE_BODY"
fi
echo "Validation error response:"
print_json_if_possible "$RESPONSE_BODY"
pass "Validation error for empty topic"

# F) Not found
request "GET" "$BASE_URL/api/v1/quizzes/not-a-real-id"
if [ "$RESPONSE_STATUS" != "404" ]; then
  fail "Not found (expected 404)" "$RESPONSE_BODY"
fi
pass "Not found for invalid quiz id"
