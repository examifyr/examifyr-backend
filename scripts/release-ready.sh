#!/usr/bin/env bash
# Thin wrapper: find examifyr-infra sibling and invoke release-core.sh

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
BACKEND_SMOKE=1 exec "$INFRA_ROOT/tools/release-core.sh" backend
