#!/usr/bin/env bash
# Run the om (darshana) test suite in the project venv.
# Usage: .claude/tools/test.sh [extra pytest args]
set -euo pipefail
cd "$(dirname "$0")/../.."
exec .venv/bin/python3 -m pytest tests/ -x "$@"
