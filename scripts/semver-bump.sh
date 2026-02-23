#!/usr/bin/env bash
# Semantic version bump based on conventional commits since last tag.
# Usage: ./scripts/semver-bump.sh [--dry-run|--apply]

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="${REPO_ROOT}/VERSION"
MODE=""

# Parse flags
for arg in "$@"; do
  case "$arg" in
    --dry-run) MODE="dry-run" ;;
    --apply)   MODE="apply" ;;
  esac
done

if [[ -z "$MODE" ]]; then
  echo "Usage: $0 --dry-run | --apply" >&2
  exit 1
fi

# Ensure VERSION file exists
if [[ ! -f "$VERSION_FILE" ]]; then
  echo "0.1.0" > "$VERSION_FILE"
fi

cd "$REPO_ROOT"

# Read current version (strip any leading v)
current="$(cat "$VERSION_FILE" | tr -d '[:space:]')"
current="${current#v}"
if [[ ! "$current" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: Invalid VERSION format: $current (expected X.Y.Z)" >&2
  exit 1
fi

# Latest tag
latest_tag="$(git describe --tags --abbrev=0 2>/dev/null || echo "")"

# Commits since last tag
if [[ -n "$latest_tag" ]]; then
  commits="$(git log "$latest_tag"..HEAD --pretty=format:%B 2>/dev/null || true)"
else
  commits="$(git log --pretty=format:%B 2>/dev/null || true)"
fi

# Determine highest bump from commits
bump="none"
breaking_re='^[a-z]+(\([^)]+\))?!:'
while IFS= read -r line; do
  [[ -z "$line" ]] && continue
  if [[ "$line" == *"BREAKING CHANGE"* ]] || [[ "$line" =~ $breaking_re ]]; then
    bump="major"
    break
  fi
  if [[ "$line" == feat:* ]]; then
    [[ "$bump" != "major" ]] && bump="minor"
  fi
  if [[ "$line" == fix:* ]] || [[ "$line" == refactor:* ]] || [[ "$line" == perf:* ]]; then
    if [[ "$bump" == "none" ]]; then
      bump="patch"
    fi
  fi
done <<< "$commits"

# Calculate next version
major="${current%%.*}"
rest="${current#*.}"
minor="${rest%%.*}"
patch="${rest#*.}"

case "$bump" in
  major)
    next="$((major + 1)).0.0"
    ;;
  minor)
    next="${major}.$((minor + 1)).0"
    ;;
  patch)
    next="${major}.${minor}.$((patch + 1))"
    ;;
  none)
    echo "No version bump required."
    exit 0
    ;;
esac

if [[ "$MODE" == "dry-run" ]]; then
  echo "Current version: $current"
  echo "Latest tag:      ${latest_tag:-<none>}"
  echo "Bump type:       $bump"
  echo "Next version:    $next"
  exit 0
fi

# --apply
echo "$next" > "$VERSION_FILE"
git add VERSION
git commit -m "chore: bump version to v${next}"
git tag "v${next}"
echo "Bumped to v${next}"
echo "  VERSION updated"
echo "  Committed"
echo "  Tagged v${next}"
echo "  (not pushed)"
