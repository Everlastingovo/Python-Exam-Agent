#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
RUN_DIR="$ROOT/.run"

stop_existing() {
  local name="$1"
  local pid_file="$RUN_DIR/$name.pid"
  if [[ ! -f "$pid_file" ]]; then
    echo "$name is not running."
    return
  fi

  local old_pid
  old_pid="$(cat "$pid_file" || true)"
  if [[ "$old_pid" =~ ^[0-9]+$ ]] && kill -0 "$old_pid" 2>/dev/null; then
    kill "$old_pid" 2>/dev/null || true
    echo "Stopped $name (PID $old_pid)."
  else
    echo "$name process was already stopped."
  fi
  rm -f "$pid_file"
}

stop_existing backend
stop_existing frontend
