#!/bin/bash
# Redirige a start.sh (fuente única de configuración del wallpaper)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/start.sh"
