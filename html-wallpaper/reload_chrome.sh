#!/bin/bash
# Script para recargar el fondo de pantalla HTML con Chrome
# Lee el wallpaper configurado en start.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Leer el WALLPAPER definido en start.sh
WALLPAPER=$(grep '^WALLPAPER=' "$SCRIPT_DIR/start.sh" | head -1 | cut -d'"' -f2)
WALLPAPER_FILE="$SCRIPT_DIR/${WALLPAPER:-fondo1.html}"

echo "Reiniciando wallpaper HTML con Chrome..."

# Matar cualquier instancia anterior
pkill -f "wallpaper_chrome.py" 2>/dev/null || true
pkill -f "chrome-wallpaper-profile" 2>/dev/null || true

sleep 0.5

# Lanzar con Chrome
/usr/bin/python3 "$SCRIPT_DIR/wallpaper_chrome.py" "$WALLPAPER_FILE" &

echo "Wallpaper aplicado con Chrome: $WALLPAPER_FILE"
echo "Verifica el log en: /tmp/html-wallpaper-chrome.log"
