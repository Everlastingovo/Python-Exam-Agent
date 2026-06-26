#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT/.run"
VENV_DIR="$ROOT/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
SUPPORTED_PYTHON_PATTERN='^(3\.12|3\.13)\.'

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
python_version() {
  "$1" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
PY
}

python_matches() {
  local executable="$1"
  [[ -x "$executable" ]] || return 1
  [[ "$(python_version "$executable")" =~ $SUPPORTED_PYTHON_PATTERN ]]
}

if [[ -x "$PYTHON_BIN" ]] && ! python_matches "$PYTHON_BIN"; then
  echo "Existing .venv uses Python $(python_version "$PYTHON_BIN"). Recreating .venv with Python 3.12 or 3.13."
  rm -rf "$VENV_DIR"
fi

if [[ ! -x "$PYTHON_BIN" ]]; then
  if command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv "$VENV_DIR"
  elif command -v python3.13 >/dev/null 2>&1; then
    python3.13 -m venv "$VENV_DIR"
  elif command -v python3 >/dev/null 2>&1 && [[ "$(python_version "$(command -v python3)")" =~ $SUPPORTED_PYTHON_PATTERN ]]; then
    python3 -m venv "$VENV_DIR"
  else
    echo "Python 3.12 or 3.13 was not found. Please install Python 3.12/3.13, then run ./run.sh again."
    exit 1
  fi
fi

echo "Using Python $(python_version "$PYTHON_BIN") from .venv."
"$PYTHON_BIN" -m pip install --upgrade pip
"$PYTHON_BIN" -m pip install --upgrade wheel setuptools
"$PYTHON_BIN" -m pip install --only-binary=:all: -r "$ROOT/requirements.txt"

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
