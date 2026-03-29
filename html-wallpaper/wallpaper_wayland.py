#!/usr/bin/env python3
"""
Wallpaper HTML para GNOME Wayland.
Ventana GTK tipo DESKTOP + WebKit2 para renderizar HTML como fondo real.
Sin dependencias X11 — sin xwinwrap, wmctrl, xprop.

La ventana DESKTOP se posiciona detrás de todas las demás ventanas,
actuando como fondo de escritorio nativo.
"""
import os, sys, signal

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
try:
    gi.require_version("WebKit2", "4.1")
except ValueError:
    gi.require_version("WebKit2", "4.0")

from gi.repository import Gtk, Gdk, WebKit2, GLib


def main():
    html_file = sys.argv[1] if len(sys.argv) > 1 else None
    if not html_file or not os.path.isfile(html_file):
        print(f"Uso: {sys.argv[0]} <archivo.html>")
        sys.exit(1)

    # Señales para cerrar limpiamente
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, Gtk.main_quit)
    GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, Gtk.main_quit)

    # Info del monitor
    display = Gdk.Display.get_default()
    monitor = display.get_primary_monitor() or display.get_monitor(0)
    geo = monitor.get_geometry()
    scale = monitor.get_scale_factor()
    width = geo.width
    height = geo.height

    print(f"[wallpaper] Monitor: {width}x{height} (scale {scale})")

    # ── Ventana ──
    # IMPORTANTE: set_type_hint DEBE ir ANTES de show_all/realize
    win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    win.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
    win.set_title("HTML-Wallpaper")
    win.set_decorated(False)
    win.set_skip_taskbar_hint(True)
    win.set_skip_pager_hint(True)
    win.set_keep_below(True)
    win.set_accept_focus(False)
    win.set_can_focus(False)
    win.stick()
    win.set_default_size(width, height)

    # ── WebView ──
    webview = WebKit2.WebView()
    settings = webview.get_settings()
    settings.set_enable_javascript(True)
    settings.set_enable_smooth_scrolling(True)
    try:
        settings.set_enable_webgl(True)
    except Exception:
        pass
    try:
        settings.set_hardware_acceleration_policy(
            WebKit2.HardwareAccelerationPolicy.ALWAYS
        )
    except Exception:
        pass

    # Fondo negro mientras carga
    rgba = Gdk.RGBA()
    rgba.parse("rgba(0,0,0,1)")
    try:
        webview.set_background_color(rgba)
    except Exception:
        pass

    uri = f"file://{os.path.abspath(html_file)}"
    print(f"[wallpaper] Cargando: {uri}")
    webview.load_uri(uri)

    win.add(webview)
    win.connect("destroy", Gtk.main_quit)

    # Mostrar — SIN fullscreen() para que no se comporte como app
    win.show_all()

    # Reforzar posición detrás de todo cada 3 segundos
    def enforce_below():
        try:
            gdk_win = win.get_window()
            if gdk_win:
                win.set_keep_below(True)
                gdk_win.lower()
        except Exception:
            pass
        return True  # mantener el timer

    GLib.timeout_add_seconds(3, enforce_below)

    print("[wallpaper] Ventana DESKTOP activa ✔ (sin fullscreen)")
    Gtk.main()


if __name__ == "__main__":
    main()
