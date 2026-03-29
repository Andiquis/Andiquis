#!/usr/bin/env python3
"""
Servidor HTTP local que proporciona datos del sistema para el wallpaper HTML.
Proporciona endpoints para Battery, Network, Memory, etc.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import psutil
import threading
import time

class SystemDataHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/system':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Recopilar datos del sistema
            data = {
                'cpu': psutil.cpu_percent(interval=0.1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
                'battery': self.get_battery_info(),
                'network': self.get_network_info()
            }
            
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_error(404)
    
    def get_battery_info(self):
        """Obtiene información de la batería."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': round(battery.percent),
                    'charging': battery.power_plugged,
                    'available': True
                }
        except:
            pass
        return {'available': False, 'percent': 0, 'charging': False}
    
    def get_network_info(self):
        """Obtiene estadísticas de red."""
        try:
            net_io = psutil.net_io_counters()
            # Guardar valores anteriores para calcular velocidad
            if not hasattr(self.server, 'last_net_io'):
                self.server.last_net_io = {'bytes_sent': net_io.bytes_sent, 'bytes_recv': net_io.bytes_recv, 'time': time.time()}
                return {'speed_mbps': 0, 'available': True}
            
            # Calcular velocidad
            time_diff = time.time() - self.server.last_net_io['time']
            if time_diff > 0:
                bytes_recv_diff = net_io.bytes_recv - self.server.last_net_io['bytes_recv']
                speed_bps = (bytes_recv_diff * 8) / time_diff  # bits per second
                speed_mbps = round(speed_bps / (1024 * 1024), 1)  # Mbps
                
                # Actualizar valores
                self.server.last_net_io = {'bytes_sent': net_io.bytes_sent, 'bytes_recv': net_io.bytes_recv, 'time': time.time()}
                
                return {'speed_mbps': speed_mbps, 'available': True}
        except:
            pass
        return {'available': False, 'speed_mbps': 0}
    
    def log_message(self, format, *args):
        # Silenciar logs
        pass


def run_server(port=8765):
    server = HTTPServer(('localhost', port), SystemDataHandler)
    print(f"Servidor de datos del sistema corriendo en http://localhost:{port}")
    print("Endpoints disponibles:")
    print(f"  - http://localhost:{port}/api/system")
    server.serve_forever()


if __name__ == '__main__':
    run_server()
