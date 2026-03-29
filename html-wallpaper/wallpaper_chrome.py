#!/usr/bin/env python3
"""Wallpaper HTML usando Chrome/Chromium en modo kiosk.

Este script lanza Chrome en modo kiosk (pantalla completa sin bordes)
con todas las APIs habilitadas, incluyendo Battery API y Network Information API.

Uso:
  python3 wallpaper_chrome.py /ruta/a/fondo.html
"""

import os
import sys
import subprocess
import time

LOG_FILE = "/tmp/html-wallpaper-chrome.log"


def log(msg: str) -> None:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg, flush=True)


def find_chrome():
    """Busca el ejecutable de Chrome/Chromium en el sistema."""
    possible_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/usr/bin/chrome",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Intentar con 'which'
    try:
        result = subprocess.run(["which", "google-chrome"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    try:
        result = subprocess.run(["which", "chromium"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None


def get_screen_resolution():
    """Obtiene la resolución de la pantalla usando xrandr."""
    try:
        result = subprocess.run(
            ["xrandr"], 
            capture_output=True, 
            text=True
        )
        for line in result.stdout.split('\n'):
            if ' connected primary' in line or ' connected' in line:
                # Buscar algo como "1920x1080"
                import re
                match = re.search(r'(\d+)x(\d+)', line)
                if match:
                    return f"{match.group(1)},{match.group(2)}"
    except:
        pass
    return "1920,1080"  # Default


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 wallpaper_chrome.py /ruta/a/archivo.html")
        sys.exit(1)
    
    html_file = sys.argv[1]
    
    if not os.path.exists(html_file):
        log(f"ERROR: No existe el archivo: {html_file}")
        sys.exit(1)
    
    # Convertir a URL
    html_url = f"file://{os.path.abspath(html_file)}"
    
    # Buscar Chrome
    chrome_path = find_chrome()
    if not chrome_path:
        log("ERROR: No se encontró Chrome/Chromium instalado")
        sys.exit(1)
    
    log(f"Usando navegador: {chrome_path}")
    log(f"Cargando: {html_url}")
    
    # Obtener resolución
    resolution = get_screen_resolution()
    log(f"Resolución detectada: {resolution}")
    
    # Directorio temporal para profile de Chrome
    profile_dir = "/tmp/chrome-wallpaper-profile"
    os.makedirs(profile_dir, exist_ok=True)
    
    # Comando de Chrome con todas las flags necesarias
    chrome_cmd = [
        chrome_path,
        f"--user-data-dir={profile_dir}",
        "--app=" + html_url,  # Modo app sin barra de direcciones
        f"--window-size={resolution}",
        f"--window-position=0,0",
        "--no-default-browser-check",
        "--no-first-run",
        "--disable-infobars",
        "--disable-session-crashed-bubble",
        "--disable-features=TranslateUI",
        "--disable-restore-session-state",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--autoplay-policy=no-user-gesture-required",
        # Habilitar APIs importantes
        "--enable-features=NetworkInformationDownlinkMax",
        # Permisos para APIs
        "--disable-web-security",  # Para desarrollo local
        "--allow-file-access-from-files",
    ]
    
    try:
        log("Iniciando Chrome...")
        # Lanzar Chrome en background
        process = subprocess.Popen(
            chrome_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Esperar a que Chrome inicie y cree la ventana
        time.sleep(3)
        
        # Intentar mover la ventana al fondo
        try:
            # Obtener el ID de la ventana de Chrome que acabamos de abrir
            result = subprocess.run(
                ["xdotool", "search", "--name", os.path.basename(html_file)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                window_id = result.stdout.strip().split('\n')[0]
                log(f"Ventana encontrada: {window_id}")
                
                # Mover al fondo y quitar decoraciones
                subprocess.run(["wmctrl", "-i", "-r", window_id, "-b", "add,below"], check=False)
                subprocess.run(["wmctrl", "-i", "-r", window_id, "-b", "remove,above"], check=False)
                subprocess.run(["wmctrl", "-i", "-r", window_id, "-b", "add,skip_taskbar"], check=False)
                subprocess.run(["wmctrl", "-i", "-r", window_id, "-b", "add,skip_pager"], check=False)
                
                # Intentar cambiar el tipo de ventana a desktop
                subprocess.run([
                    "xdotool", "windowmove", window_id, "0", "0"
                ], check=False)
                
                # Cambiar el tipo de ventana usando xprop
                subprocess.run([
                    "xprop", "-id", window_id,
                    "-f", "_NET_WM_WINDOW_TYPE", "32a",
                    "-set", "_NET_WM_WINDOW_TYPE", "_NET_WM_WINDOW_TYPE_DESKTOP"
                ], check=False)
                
                log("Ventana configurada como fondo de escritorio")
            else:
                log("No se pudo encontrar la ventana de Chrome")
                
        except subprocess.TimeoutExpired:
            log("Timeout buscando ventana de Chrome")
        except Exception as e:
            log(f"Advertencia: No se pudo configurar como fondo: {e}")
        
        log("Chrome wallpaper iniciado correctamente")
        
        # Esperar a que Chrome termine
        process.wait()
        
    except KeyboardInterrupt:
        log("Deteniendo...")
        if process:
            process.terminate()
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
