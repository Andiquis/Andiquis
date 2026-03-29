# Tutorial: Cambiar Fondos HTML de Manera Permanente

## 📋 Resumen

Este sistema permite usar archivos HTML como fondo de pantalla interactivo en Ubuntu con Xorg/X11.

## 🔄 Cambiar Fondo Permanentemente

### Método 1: Usando sed (Recomendado)

```bash
# Cambiar a fondo5.html
sed -i 's|fondo[0-9]\.html|fondo5.html|g' ~/.config/autostart/html-wallpaper.desktop

# Cambiar a fondo2.html
sed -i 's|fondo[0-9]\.html|fondo2.html|g' ~/.config/autostart/html-wallpaper.desktop

# Cambiar a wallpaper.html
sed -i 's|fondo[0-9]\.html|wallpaper.html|g' ~/.config/autostart/html-wallpaper.desktop
```

### Método 2: Edición Manual

```bash
# Abrir el archivo de autostart
nano ~/.config/autostart/html-wallpaper.desktop

# Cambiar esta línea:
# Exec=/home/andi/vXcode/html-wallpaper/wallpaper-html.sh /home/andi/vXcode/html-wallpaper/fondo4.html

# Por tu HTML deseado:
# Exec=/home/andi/vXcode/html-wallpaper/wallpaper-html.sh /home/andi/vXcode/html-wallpaper/fondo6.html
```

## ⚡ Aplicar Cambio Inmediatamente

Después de cambiar el autostart, aplica el nuevo fondo:

```bash
# Matar proceso actual
pkill -f wallpaper_html_window.py
pkill -f wallpaper-html.sh

# Esperar un momento
sleep 2

# Lanzar nuevo fondo
cd /home/andi/vXcode/html-wallpaper
./wallpaper-html.sh fondo9.html  # Cambiar por tu HTML deseado
```

## 📁 Fondos Disponibles

```bash
# Ver todos los fondos disponibles
ls /home/andi/vXcode/html-wallpaper/*.html
```

Actualmente tienes:

- `fondo1.html` - Cyberpunk con typing effect
- `fondo2.html` - [Descripción pendiente]
- `fondo3.html` - [Descripción pendiente]
- `fondo4.html` - **ACTUAL**
- `fondo5.html` - [Descripción pendiente]
- `fondo6.html` - [Descripción pendiente]
- `wallpaper.html` - [Descripción pendiente]

## 🔍 Verificar Configuración Actual

```bash
# Ver qué fondo está configurado permanentemente
cat ~/.config/autostart/html-wallpaper.desktop | grep Exec

# Ver qué proceso está corriendo
ps aux | grep wallpaper_html_window.py | grep -v grep

# Ver logs del sistema
tail -f /tmp/html-wallpaper.log
```

## 🚨 Solución de Problemas

### Si no se ve el fondo:

```bash
# Verificar que estás en Xorg (no Wayland)
echo $XDG_SESSION_TYPE  # Debe decir "x11"

# Verificar que el archivo HTML existe
ls -la /home/andi/vXcode/html-wallpaper/fondo*.html

# Revisar logs de errores
cat /tmp/html-wallpaper.log
cat /tmp/html-wallpaper-python.log
```

### Si el autostart no funciona:

```bash
# Verificar que el autostart está habilitado
cat ~/.config/autostart/html-wallpaper.desktop | grep "X-GNOME-Autostart-enabled"

# Debe decir: X-GNOME-Autostart-enabled=true
```

## 📝 Crear Tu Propio Fondo

1. Crea un nuevo archivo HTML en `/home/andi/vXcode/html-wallpaper/`
2. Asegúrate de que sea responsive y funcione bien como fondo
3. Úsalo con: `./wallpaper-html.sh tu-archivo.html`

## ⚙️ Script de Cambio Rápido

Puedes crear un alias en tu `~/.zshrc`:

```bash
# Agregar al final de ~/.zshrc
alias cambiar-fondo='function _cf() {
    pkill -f wallpaper_html_window.py 2>/dev/null || true
    pkill -f wallpaper-html.sh 2>/dev/null || true
    sleep 1
    sed -i "s|fondo[0-9]\.html|$1|g" ~/.config/autostart/html-wallpaper.desktop
    cd /home/andi/vXcode/html-wallpaper && ./wallpaper-html.sh "$1" >/dev/null 2>&1 &
    echo "✅ Fondo cambiado a: $1"
}; _cf'

# Recarga el shell
source ~/.zshrc

# Uso:
cambiar-fondo fondo3.html
cambiar-fondo wallpaper.html
```

---

**Última actualización:** 14 de enero de 2026  
**Fondo actual:** fondo4.html  
**Sistema:** Ubuntu + GNOME + Xorg/X11
