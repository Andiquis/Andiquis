#!/bin/bash
# Script para recargar el fondo de pantalla HTML
# Simplemente ejecuta start.sh que ya maneja todo

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Reiniciando wallpaper HTML..."
exec bash "$SCRIPT_DIR/start.sh"
