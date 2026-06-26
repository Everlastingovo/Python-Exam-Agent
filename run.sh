#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT/.run"
VENV_DIR="$ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"

mkdir -p "$RUN_DIR"
cd "$ROOT"

stop_existing() {
  local name="$1"
  local pid_file="$RUN_DIR/$name.pid"
  if [[ -f "$pid_file" ]]; then
    local old_pid
    old_pid="$(cat "$pid_file" || true)"
    if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
      kill "$old_pid" 2>/dev/null || true
    fi
    rm -f "$pid_file"
  fi
}

wait_for_port() {
  local port="$1"
  local name="$2"
  for _ in {1..40}; do
    if "$PYTHON_BIN" - "$port" >/dev/null 2>&1 <<'PY'
import socket
import sys

port = int(sys.argv[1])
with socket.create_connection(("127.0.0.1", port), timeout=0.5):
    pass
PY
    then
      echo "$name is ready on port $port."
      return
    fi
    sleep 0.5
  done
  echo "Warning: $name did not answer on port $port yet. Check .run/$name.log."
}

echo "==> Preparing Python environment"
if [[ ! -x "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv "$VENV_DIR"
  else
    echo "Python 3 was not found. Please install Python 3.12 or newer."
    exit 1
  fi
fi

"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install -r "$ROOT/requirements.txt"

echo "==> Restarting project servers"
stop_existing backend
stop_existing frontend

(
  cd "$ROOT/backend"
  PYTHONPATH="$ROOT/backend" "$PYTHON_BIN" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
) >"$RUN_DIR/backend.log" 2>&1 &
echo "$!" > "$RUN_DIR/backend.pid"

(
  cd "$ROOT/frontend"
  "$PYTHON_BIN" -m http.server 3000
) >"$RUN_DIR/frontend.log" 2>&1 &
echo "$!" > "$RUN_DIR/frontend.pid"

wait_for_port 8000 backend
wait_for_port 3000 frontend

echo "==> Ready"
echo "Frontend: http://localhost:3000"
echo "Backend docs: http://localhost:8000/docs"
echo "Logs: .run/backend.log and .run/frontend.log"
echo "Stop servers: ./stop.sh"

if command -v open >/dev/null 2>&1; then
  open "http://localhost:3000"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:3000" >/dev/null 2>&1 || true
fi
