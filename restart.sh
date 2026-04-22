#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/runtime/hermes-gateway.pid"   # 改成实际路径

# Activate venv
if [ -f "$SCRIPT_DIR/venv/bin/activate" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
else
    echo "ERROR: venv not found at $SCRIPT_DIR/venv"
    exit 1
fi

echo "==> Pulling latest code..."
git pull

echo "==> Reinstalling deps..."
pip install -e ".[all]" -q

echo "==> Stopping existing hermes gateway..."
pkill -f "hermes.*gateway|gateway.*hermes" || true

# wait until process exits
for i in {1..10}; do
    if ! pgrep -af "hermes.*gateway|gateway.*hermes" >/dev/null; then
        break
    fi
    sleep 1
done

if pgrep -af "hermes.*gateway|gateway.*hermes" >/dev/null; then
    echo "ERROR: Existing gateway process is still running:"
    pgrep -af "hermes.*gateway|gateway.*hermes"
    exit 1
fi

# remove stale pid file
if [ -f "$PID_FILE" ]; then
    old_pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    if [ -n "${old_pid:-}" ] && ! ps -p "$old_pid" >/dev/null 2>&1; then
        echo "==> Removing stale PID file: $PID_FILE"
        rm -f "$PID_FILE"
    fi
fi

echo "==> Starting hermes gateway..."
exec hermes gateway