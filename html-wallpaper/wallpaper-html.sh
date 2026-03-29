#!/usr/bin/env bash
set -euo pipefail

# Wallpaper HTML interactivo para Ubuntu en Xorg/X11.
# Carga un HTML en el fondo usando xwinwrap + WebKit2 (GtkPlug).
#
# Requisito: estar en Xorg (XDG_SESSION_TYPE=x11).
# Requisito: xwinwrap instalado.
# Requisito: python3-gi + gir1.2-webkit2-4.0/4.1.
#
# Uso:
#   ./wallpaper-html.sh /ruta/al/fondo.html
#
# Logs:
#   /tmp/html-wallpaper.log
#   /tmp/html-wallpaper-python.log

LOG_FILE="/tmp/html-wallpaper.log"
# Nota: con process substitution + pipefail pueden aparecer códigos 141 (SIGPIPE)
# si el consumidor (VS Code/terminal) corta la salida. Por eso evitamos que eso
# interrumpa el flujo principal.
exec 1> >(tee -a "$LOG_FILE" || true)
exec 2>&1

echo "[wallpaper] start $(date)"

echo "[wallpaper] XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-}" 
if [[ "${XDG_SESSION_TYPE:-}" != "x11" ]]; then
  echo "[wallpaper] ERROR: necesitas iniciar sesión en Xorg/X11 (no Wayland)."
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HTML_FILE="${1:-$SCRIPT_DIR/fondo4.html}"

if [[ ! -f "$HTML_FILE" ]]; then
  echo "[wallpaper] ERROR: no existe: $HTML_FILE"
  exit 1
fi

# Resolver xwinwrap
XWINWRAP="xwinwrap"
if [[ -x "$HOME/.local/bin/xwinwrap" ]]; then
  XWINWRAP="$HOME/.local/bin/xwinwrap"
elif [[ -x "/usr/local/bin/xwinwrap" ]]; then
  XWINWRAP="/usr/local/bin/xwinwrap"
fi

if ! command -v "$XWINWRAP" >/dev/null 2>&1; then
  echo "[wallpaper] ERROR: xwinwrap no encontrado"
  exit 1
fi

echo "[wallpaper] Using xwinwrap: $XWINWRAP"

echo "[wallpaper] killing previous instances..."
pkill -f "wallpaper_html.py" 2>/dev/null || true
pkill -f "wallpaper_html_window.py" 2>/dev/null || true
pkill -f "html-wallpaper-impl.py" 2>/dev/null || true
pkill -f "xwinwrap" 2>/dev/null || true

# Esperar a que el escritorio termine (útil al autostart)
sleep 2

RESOLUTION="$(xdpyinfo 2>/dev/null | awk '/dimensions:/{print $2; exit}' || true)"
WIDTH=${RESOLUTION%x*}
HEIGHT=${RESOLUTION#*x}
WIDTH=${WIDTH:-1920}
HEIGHT=${HEIGHT:-1080}

export HTML_FILE_PATH="$HTML_FILE"

# Inicializa log del python para saber si llega a ejecutarse.
PY_LOG="/tmp/html-wallpaper-python.log"
echo "" >> "$PY_LOG" || true
echo "[wallpaper] python log: $PY_LOG" 

echo "[wallpaper] resolution ${WIDTH}x${HEIGHT}"
echo "[wallpaper] html $HTML_FILE"

# Flags recomendadas para que NO se note como ventana:
# -b  : below
# -nf : no focus
# -ni : ignore input
# -st/-sp : no taskbar/pager
# -s  : sticky
# -fs : fullscreen

echo "[wallpaper] launching python window compositor..."
env HTML_FILE_PATH="$HTML_FILE" /usr/bin/python3 "$SCRIPT_DIR/wallpaper_html_window.py" &

echo "[wallpaper] started pid=$!"
