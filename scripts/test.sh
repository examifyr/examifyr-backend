#!/usr/bin/env bash
set -euo pipefail

if [ ! -x "./.venv/bin/python" ]; then
  python3 -m venv .venv
fi

./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pytest -q