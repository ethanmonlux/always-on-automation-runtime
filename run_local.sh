#!/usr/bin/env bash
set -euo pipefail

# Simple local runner for the sanitized demo.
# Creates/activates a virtualenv, installs deps, sets API_KEY, and runs uvicorn.
#
# Usage:
#   bash run_local.sh
#
# Windows users: see README for PowerShell commands.

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

export API_KEY="${API_KEY:-demo-key}"

exec uvicorn app.main:app --reload --port 8080
