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
  if formatted=$(printf '%s' "$body" | python3 -c 'import json,sys; data=json.load(sys.stdin); print(json.dumps(data, indent=2, sort_keys=True))' 2>/dev/null); then
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
    response=$(curl -sS --max-time 10 -X "$method" "$url" \
      -H "Content-Type: application/json" \
      -d "$payload" \
      -w "\n%{http_code}")
    RESPONSE_BODY="${response%$'\n'*}"
    RESPONSE_STATUS="${response##*$'\n'}"
  else
    local response
    response=$(curl -sS --max-time 10 -X "$method" "$url" -w "\n%{http_code}")
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

if quiz_id=$(printf '%s' "$RESPONSE_BODY" | python3 -c 'import json,sys; data=json.load(sys.stdin); required={"quiz_id","topic","difficulty","questions"}; missing=required-set(data.keys()); sys.exit(f"Missing keys: {missing}") if missing else None; quiz_id=data.get("quiz_id"); sys.exit("quiz_id is empty") if not quiz_id else None; sys.exit(f"topic mismatch: {data.get(\"topic\")}") if data.get("topic")!="Python lists" else None; sys.exit(f"difficulty mismatch: {data.get(\"difficulty\")}") if data.get("difficulty")!="easy" else None; sys.exit(f"questions length mismatch: {len(data.get(\"questions\", []))}") if len(data.get("questions", []))!=3 else None; [sys.exit("choices length mismatch") if len(q.get("choices", []))!=4 else None for q in data.get("questions", [])]; [sys.exit("answer_index out of range") if not (0<=q.get("answer_index",-1)<=3) else None for q in data.get("questions", [])]; print(quiz_id)'); then
  pass "Generate quiz"
else
  fail "Generate quiz response validation failed" "$RESPONSE_BODY"
fi

# D) Get quiz by ID
request "GET" "$BASE_URL/api/v1/quizzes/$quiz_id"
if [ "$RESPONSE_STATUS" != "200" ]; then
  fail "Get quiz by id (expected 200)" "$RESPONSE_BODY"
fi
if ! EXPECTED_QUIZ_ID="$quiz_id" printf '%s' "$RESPONSE_BODY" | python3 -c 'import json,os,sys; data=json.load(sys.stdin); expected=os.environ["EXPECTED_QUIZ_ID"]; sys.exit("quiz_id mismatch") if data.get("quiz_id") != expected else None; sys.exit("missing questions") if "questions" not in data else None'; then
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
