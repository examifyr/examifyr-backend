#!/usr/bin/env bash
# Thin wrapper: find examifyr-infra sibling and invoke release-core.sh
# Safe to run from main: prompts to create feature branch first.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(cd "$REPO_ROOT/.." && pwd)"
INFRA_ROOT="${PROJECT_ROOT}/examifyr-infra"

if [[ ! -d "$INFRA_ROOT" || ! -f "$INFRA_ROOT/tools/release-core.sh" ]]; then
  echo "ERROR: examifyr-infra not found at $INFRA_ROOT or tools/release-core.sh missing." >&2
  echo "Ensure examifyr-infra is cloned as sibling: project/{examifyr-infra,examifyr-backend,examifyr-frontend}" >&2
  exit 1
fi

cd "$REPO_ROOT"

# Fail fast if working tree is dirty
if [[ -n "$(git status --porcelain)" ]]; then
  echo "ERROR: Working tree is dirty. Commit or stash changes first." >&2
  git status -s
  exit 1
fi

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
  git fetch origin
  git pull --ff-only "origin" "$BRANCH"
  printf "You are on '%s'. Create a new feature branch now? (y/n): " "$BRANCH"
  read -r ans
  case "${ans:-}" in
    [yY]|[yY][eE][sS])
      default_name="feature/release-$(date +%Y%m%d-%H%M)"
      printf "Enter branch name (default: %s): " "$default_name"
      read -r name
      name="${name:-$default_name}"
      [[ "$name" == feature/* ]] || name="feature/${name}"
      git checkout -b "$name"
      echo "Created and switched to branch: $name"
      ;;
    *)
      echo "Exiting. No branch created."
      exit 0
      ;;
  esac
fi

BACKEND_SMOKE=1 exec "$INFRA_ROOT/tools/release-core.sh" backend
