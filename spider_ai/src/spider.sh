#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

install_tor_if_missing() {
  if command -v tor >/dev/null 2>&1; then
    return 0
  fi

  echo "Tor was not found. Installing Tor..."

  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update && sudo apt-get install -y tor || apt-get update && apt-get install -y tor
  elif command -v brew >/dev/null 2>&1; then
    brew install tor
  elif command -v yum >/dev/null 2>&1; then
    yum install -y tor
  elif command -v dnf >/dev/null 2>&1; then
    dnf install -y tor
  else
    echo "Could not install Tor automatically on this system. Please install Tor manually and ensure it runs on 127.0.0.1:9050."
    exit 1
  fi
}

install_ollama_if_missing() {
  if command -v ollama >/dev/null 2>&1; then
    return 0
  fi

  echo "Ollama was not found. Installing Ollama..."

  if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://ollama.com/install.sh | sh
  else
    echo "Could not install Ollama automatically because curl is not available. Please install Ollama manually."
    exit 1
  fi
}

start_tor_if_possible() {
  if command -v tor >/dev/null 2>&1; then
    if ! pgrep -x tor >/dev/null 2>&1; then
      echo "Starting Tor daemon..."
      tor >/dev/null 2>&1 &
      sleep 2 || true
    fi
  fi
}

start_ollama_if_possible() {
  if command -v ollama >/dev/null 2>&1; then
    if ! pgrep -x ollama >/dev/null 2>&1; then
      echo "Starting Ollama service..."
      ollama serve >/dev/null 2>&1 &
      sleep 2 || true
    fi
  fi
}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python3 was not found in PATH. Please install Python 3 first."
  exit 1
fi

VENV_DIR="$SCRIPT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment in $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install --quiet requests beautifulsoup4 rich "requests[socks]"

install_tor_if_missing
install_ollama_if_missing
start_tor_if_possible
start_ollama_if_possible

if command -v nc >/dev/null 2>&1; then
  if nc -z 127.0.0.1 9050 >/dev/null 2>&1; then
    echo "Tor SOCKS proxy detected on 127.0.0.1:9050"
  else
    echo "Warning: Tor is not running on 127.0.0.1:9050; .onion support will not work until Tor is started."
  fi
else
  echo "Warning: nc is not installed, so the Tor port check was skipped."
fi

if command -v curl >/dev/null 2>&1; then
  if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "Ollama is available on http://127.0.0.1:11434"
  else
    echo "Warning: Ollama is not running on http://127.0.0.1:11434"
  fi
fi

echo "Starting Spider AI..."
exec python main.py "$@"
