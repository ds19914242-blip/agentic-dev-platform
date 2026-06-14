#!/usr/bin/env bash
# Launch the Agentic Console from the platform root.
cd "$(dirname "$0")/.." || exit 1
exec python3 webui/server.py "$@"
