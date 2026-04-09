#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate venv
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "ERROR: venv not found at $SCRIPT_DIR/venv"
    exit 1
fi

# Pull latest code
echo "==> Pulling latest code..."
git pull

# Reinstall deps if pyproject.toml changed
if git diff HEAD@{1} --name-only 2>/dev/null | grep -qE "pyproject\.toml|requirements\.txt"; then
    echo "==> Dependencies changed, reinstalling..."
    pip install -e ".[all]" -q
else
    echo "==> Dependencies unchanged, skipping install."
fi

# Start gateway
echo "==> Starting hermes gateway..."
hermes gateway
