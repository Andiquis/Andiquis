#!/bin/bash
# ╔══════════════════════════════════════════════════════════════╗
# ║  HTML Wallpaper - Wayland/GNOME                             ║
# ║                                                             ║
# ║  Renderiza un archivo HTML como fondo de pantalla real       ║
# ║  usando Chrome headless + gsettings.                        ║
# ║                                                             ║
# ║  Cambia WALLPAPER y REFRESH para personalizar.              ║
# ║                                                             ║
# ║  Fondos disponibles:                                        ║
# ║    fondo1.html ... fondo11.html, wallpaper.html             ║
# ╚══════════════════════════════════════════════════════════════╝

# ============================================================
# >>> CONFIGURACIÓN <<<
# ============================================================
WALLPAPER="fondo11.html"
REFRESH=10          # segundos entre actualizaciones (0 = una sola captura)
# ============================================================

# --- No necesitas modificar nada debajo de esta línea ---

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HTML_FILE="$SCRIPT_DIR/$WALLPAPER"
OUTPUT_DIR="/tmp/html-wallpaper"
OUTPUT_PNG="$OUTPUT_DIR/wallpaper.png"
LOCKFILE="$OUTPUT_DIR/wallpaper.lock"

# Verificar que el archivo existe
if [[ ! -f "$HTML_FILE" ]]; then
    echo "❌ ERROR: No se encontró: $HTML_FILE"
    echo ""
    echo "Archivos HTML disponibles:"
    ls "$SCRIPT_DIR"/*.html 2>/dev/null | while read f; do
        echo "  - $(basename "$f")"
    done
    exit 1
fi

# Verificar Chrome
CHROME=""
for cmd in google-chrome google-chrome-stable chromium-browser chromium; do
    if command -v "$cmd" &>/dev/null; then
        CHROME="$cmd"
        break
    fi
done

if [[ -z "$CHROME" ]]; then
    echo "❌ ERROR: No se encontró Google Chrome ni Chromium"
    exit 1
fi

# Detectar resolución del monitor
RESOLUTION=$(python3 -c "
import gi; gi.require_version('Gdk','3.0')
from gi.repository import Gdk
d=Gdk.Display.get_default()
m=d.get_primary_monitor() or d.get_monitor(0)
g=m.get_geometry(); s=m.get_scale_factor()
print(f'{g.width*s},{g.height*s}')
" 2>/dev/null || echo "1680,1050")
WIDTH="${RESOLUTION%,*}"
HEIGHT="${RESOLUTION#*,}"

echo "🖥️  HTML Wallpaper (Wayland) — Chrome Headless"
echo "   Archivo: $WALLPAPER"
echo "   Resolución: ${WIDTH}x${HEIGHT}"
echo "   Refresh: ${REFRESH}s"
echo "   Chrome: $CHROME"

# Crear directorio de salida
mkdir -p "$OUTPUT_DIR"

# Matar instancias anteriores de este script (excepto la actual)
if [[ -f "$LOCKFILE" ]]; then
    OLD_PID=$(cat "$LOCKFILE" 2>/dev/null)
    if [[ -n "$OLD_PID" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
        echo "🔄 Deteniendo instancia anterior (PID: $OLD_PID)..."
        kill "$OLD_PID" 2>/dev/null
        sleep 1
    fi
fi
echo $$ > "$LOCKFILE"

# Guardar wallpaper original para restaurar al detener
ORIGINAL_URI=$(gsettings get org.gnome.desktop.background picture-uri 2>/dev/null)
ORIGINAL_URI_DARK=$(gsettings get org.gnome.desktop.background picture-uri-dark 2>/dev/null)
ORIGINAL_OPTIONS=$(gsettings get org.gnome.desktop.background picture-options 2>/dev/null)
echo "$ORIGINAL_URI" > "$OUTPUT_DIR/original_uri.txt"
echo "$ORIGINAL_URI_DARK" > "$OUTPUT_DIR/original_uri_dark.txt"
echo "$ORIGINAL_OPTIONS" > "$OUTPUT_DIR/original_options.txt"

# Limpiar al salir
cleanup() {
    echo ""
    echo "🛑 Deteniendo HTML Wallpaper..."
    rm -f "$LOCKFILE"
    # Restaurar wallpaper original
    if [[ -f "$OUTPUT_DIR/original_uri.txt" ]]; then
        local orig
        orig=$(cat "$OUTPUT_DIR/original_uri.txt")
        gsettings set org.gnome.desktop.background picture-uri "$orig" 2>/dev/null
        orig=$(cat "$OUTPUT_DIR/original_uri_dark.txt")
        gsettings set org.gnome.desktop.background picture-uri-dark "$orig" 2>/dev/null
        orig=$(cat "$OUTPUT_DIR/original_options.txt")
        gsettings set org.gnome.desktop.background picture-options "$orig" 2>/dev/null
        echo "🔙 Wallpaper original restaurado"
    fi
    exit 0
}
trap cleanup SIGTERM SIGINT SIGHUP

# ── Función de captura ──
capture() {
    # Chrome headless: renderiza el HTML y captura screenshot
    "$CHROME" \
        --headless=new \
        --disable-gpu \
        --no-sandbox \
        --disable-software-rasterizer \
        --disable-dev-shm-usage \
        --hide-scrollbars \
        --window-size="${WIDTH},${HEIGHT}" \
        --screenshot="$OUTPUT_PNG" \
        "file://${HTML_FILE}" \
        2>/dev/null

    if [[ -f "$OUTPUT_PNG" ]]; then
        # Establecer como wallpaper real de GNOME
        gsettings set org.gnome.desktop.background picture-uri "file://${OUTPUT_PNG}"
        gsettings set org.gnome.desktop.background picture-uri-dark "file://${OUTPUT_PNG}"
        gsettings set org.gnome.desktop.background picture-options "zoom"
        return 0
    else
        return 1
    fi
}

# ── Primera captura ──
echo "📸 Capturando wallpaper..."
if capture; then
    echo "✅ Fondo de pantalla aplicado: $WALLPAPER"
else
    echo "❌ Error en la primera captura"
    cleanup
    exit 1
fi

# ── Configurar autostart ──
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/html-wallpaper.desktop"
mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=HTML Wallpaper
Comment=Wallpaper HTML dinámico (Wayland) - $WALLPAPER
Exec=$SCRIPT_DIR/start.sh
Terminal=false
Hidden=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
EOF

echo "💾 Autostart configurado"

# ── Loop de actualización ──
if [[ "$REFRESH" -gt 0 ]]; then
    echo "🔄 Actualizando cada ${REFRESH}s (Ctrl+C para detener)"
    while true; do
        sleep "$REFRESH"
        capture && printf "\r📸 Actualizado: $(date +%H:%M:%S)  " || true
    done
else
    echo "📌 Captura única (sin loop de actualización)"
    echo "   Para detener: pkill -f 'start.sh'"
    # Mantener vivo para que trap funcione
    wait
fi
