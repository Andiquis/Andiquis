#!/usr/bin/env python3
"""Wallpaper HTML interactivo en X11 creando una ventana propia (sin GtkPlug).

Esto evita el problema de tamaño (200x200) que aparece con GtkPlug en algunos
entornos GNOME/Mutter.

- Crea una ventana fullscreen, sin decoraciones.
- Carga el HTML con WebKit2.
- Intenta marcarla como tipo DESKTOP y enviarla al fondo.

Uso:
  HTML_FILE_PATH=/ruta/a/fondo.html python3 wallpaper_html_window.py

Logs:
  /tmp/html-wallpaper-python.log
"""

from __future__ import annotations

import os
import re
import subprocess
import time

LOG_FILE = "/tmp/html-wallpaper-python.log"


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg, flush=True)


def sh(cmd: list[str]) -> None:
    try:
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def get_workarea_from_xprop() -> tuple[int, int, int, int] | None:
    """Devuelve (x, y, w, h) desde _NET_WORKAREA usando xprop.

    Ejemplo:
      _NET_WORKAREA(CARDINAL) = 0, 44, 1920, 1156
    """
    try:
        out = subprocess.check_output(["xprop", "-root", "_NET_WORKAREA"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        return None

    m = re.search(r"=\s*([0-9]+),\s*([0-9]+),\s*([0-9]+),\s*([0-9]+)", out)
    if not m:
        return None
    x, y, w, h = (int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)))
    return x, y, w, h


def get_desktop_geometry_from_xprop() -> tuple[int, int] | None:
    """Devuelve (w, h) desde _NET_DESKTOP_GEOMETRY usando xprop.

    Ejemplo:
      _NET_DESKTOP_GEOMETRY(CARDINAL) = 1920, 1200
    """
    try:
        out = subprocess.check_output(
            ["xprop", "-root", "_NET_DESKTOP_GEOMETRY"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None

    m = re.search(r"=\s*([0-9]+),\s*([0-9]+)", out)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def main() -> int:
    html_file = os.environ.get("HTML_FILE_PATH")
    if not html_file or not os.path.exists(html_file):
        log(f"ERROR: HTML_FILE_PATH inválido: {html_file}")
        return 2

    import gi  # type: ignore

    gi.require_version("Gdk", "3.0")
    gi.require_version("Gtk", "3.0")
    try:
        gi.require_version("WebKit2", "4.1")
    except Exception:
        gi.require_version("WebKit2", "4.0")

    from gi.repository import Gdk, Gtk, WebKit2  # type: ignore

    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.set_title("HTML Wallpaper")
    win.set_decorated(False)
    win.set_skip_taskbar_hint(True)
    win.set_skip_pager_hint(True)
    win.set_keep_below(True)
    win.set_accept_focus(False)
    win.stick()

    # IMPORTANTE (GNOME): el panel superior siempre va encima.
    # Para que el wallpaper se vea "a pantalla completa" como fondo del escritorio,
    # lo correcto es ocupar la WORKAREA (área sin panel/dock), no cubrir el panel.
    # _NET_WORKAREA: x, y, width, height (por escritorio). Para 1 monitor suele ser:
    #   0, <alto_panel>, ancho, alto_sin_panel
    # Nota: NO usamos win.fullscreen() porque Mutter tiende a forzar el tamaño del monitor
    # completo (incluyendo el panel). En su lugar, aplicamos geometría workarea tras realize.

    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
    box.set_hexpand(True)
    box.set_vexpand(True)

    webview = WebKit2.WebView()
    webview.set_hexpand(True)
    webview.set_vexpand(True)

    settings = webview.get_settings()
    settings.set_enable_javascript(True)
    try:
        settings.set_enable_webgl(True)
    except Exception:
        pass

    rgba = Gdk.RGBA()
    rgba.parse("rgba(0,0,0,1)")
    try:
        webview.set_background_color(rgba)
    except Exception:
        pass

    uri = f"file://{os.path.abspath(html_file)}"
    log(f"Loading {uri}")
    webview.load_uri(uri)

    box.pack_start(webview, True, True, 0)
    win.add(box)

    def on_realize(_):
        gdk_win = win.get_window()
        if not gdk_win:
            return
        # Obtener XID
        try:
            xid = gdk_win.get_xid()
        except Exception:
            return

        log(f"Realized XID={hex(xid)}")

        # Ajustar al tamaño completo del monitor (fullscreen real).
        try:
            geom = get_desktop_geometry_from_xprop()
            if geom is not None:
                w, h = geom
                x, y = 0, 0
                log(f"Applying FULLSCREEN x={x} y={y} w={w} h={h}")
                win.move(x, y)
                win.resize(w, h)
                sh(["wmctrl", "-ir", hex(xid), "-e", f"0,{x},{y},{w},{h}"])

                # Refuerzo: Mutter puede re-ajustar la ventana tras realize. Reaplicamos.
                time.sleep(0.2)
                sh(["wmctrl", "-ir", hex(xid), "-e", f"0,{x},{y},{w},{h}"])
            else:
                # Fallback a WORKAREA si no hay _NET_DESKTOP_GEOMETRY.
                wa = get_workarea_from_xprop()
                if wa is not None:
                    x, y, w, h = wa
                    log(f"Applying WORKAREA x={x} y={y} w={w} h={h}")
                    win.move(x, y)
                    win.resize(w, h)
                    sh(["wmctrl", "-ir", hex(xid), "-e", f"0,{x},{y},{w},{h}"])
        except Exception as e:
            log(f"WARN: cannot apply geometry: {type(e).__name__}: {e}")

        # Marcar tipo desktop y mandarla al fondo (mejor esfuerzo)
        sh(["xprop", "-id", hex(xid), "-f", "_NET_WM_WINDOW_TYPE", "32a", "-set", "_NET_WM_WINDOW_TYPE", "_NET_WM_WINDOW_TYPE_DESKTOP"])
        sh(["wmctrl", "-ir", hex(xid), "-b", "add,below,sticky,skip_taskbar,skip_pager"])

    win.connect("realize", on_realize)
    win.connect("destroy", Gtk.main_quit)

    win.show_all()
    Gtk.main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
