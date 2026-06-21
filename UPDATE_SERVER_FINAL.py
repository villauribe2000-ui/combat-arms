#!/usr/bin/env python3
"""
UPDATE_SERVER_FINAL.py
Servidor HTTP que sirve actualizaciones para el Launcher V3
Sirve Client.zip desde UpdateServer/Client.zip
Puerto: 8011
"""

import os
import sys
import json
import hashlib
import logging
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rutas
BASE_DIR = Path(__file__).parent
UPDATE_SERVER_DIR = BASE_DIR / "UpdateServer"
CLIENT_ZIP = UPDATE_SERVER_DIR / "Client.zip"

# Crear directorio si no existe
UPDATE_SERVER_DIR.mkdir(exist_ok=True)

class UpdateHandler(BaseHTTPRequestHandler):
    """Manejador de solicitudes HTTP para actualizaciones"""
    
    def do_HEAD(self):
        """Maneja solicitudes HEAD (para verificar tamaño)"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == "/update/download":
            if not CLIENT_ZIP.exists():
                self.send_error(404, "Not Found")
                return
            
            file_size = CLIENT_ZIP.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Length", str(file_size))
            self.end_headers()
        else:
            self.send_error(404, "Not Found")
    
    def do_GET(self):
        """Maneja solicitudes GET"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        logger.info(f"GET request: {path}")
        
        if path == "/update/status":
            self.send_json_response({
                "status": "online",
                "version": "1.0.0",
                "message": "Servidor de actualizaciones en línea"
            })
        
        elif path == "/update/version":
            version_file = UPDATE_SERVER_DIR / "version.json"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(data)
            else:
                self.send_json_response({
                    "version": "1.0.0",
                    "build": "20062026",
                    "release_date": "2026-06-20",
                    "changes": ["Initial release"]
                })
        
        elif path == "/update/files":
            files_file = UPDATE_SERVER_DIR / "files.json"
            if files_file.exists():
                with open(files_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(data)
            else:
                self.send_json_response({"files": []})
        
        elif path == "/update/download":
            self.handle_download()
        
        elif path == "/update/news":
            news_file = UPDATE_SERVER_DIR / "news.json"
            if news_file.exists():
                with open(news_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(data)
            else:
                self.send_json_response({"news": []})
        
        elif path == "/update/maintenance":
            maint_file = UPDATE_SERVER_DIR / "maintenance.json"
            if maint_file.exists():
                with open(maint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(data)
            else:
                self.send_json_response({"maintenance": False})
        
        elif path == "/update/servers":
            servers_file = UPDATE_SERVER_DIR / "servers.json"
            if servers_file.exists():
                with open(servers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.send_json_response(data)
            else:
                self.send_json_response({"servers": []})
        
        else:
            self.send_error(404, "Not Found")
    
    def handle_download(self):
        """Maneja la descarga de Client.zip"""
        if not CLIENT_ZIP.exists():
            logger.error(f"Client.zip no encontrado en {CLIENT_ZIP}")
            self.send_json_response(
                {"error": "Client.zip not found on server"},
                status_code=404
            )
            return
        
        try:
            file_size = CLIENT_ZIP.stat().st_size
            
            # Calcular SHA256
            sha256_hash = hashlib.sha256()
            with open(CLIENT_ZIP, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            file_hash = sha256_hash.hexdigest()
            
            logger.info(f"Enviando Client.zip ({file_size} bytes, SHA256: {file_hash})")
            
            # Enviar headers
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Length", str(file_size))
            self.send_header("X-File-Hash", file_hash)
            self.send_header("Content-Disposition", "attachment; filename=Client.zip")
            self.end_headers()
            
            # Enviar archivo en chunks
            with open(CLIENT_ZIP, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            
            logger.info("Descarga completada exitosamente")
        
        except Exception as e:
            logger.error(f"Error durante descarga: {e}")
            self.send_error(500, str(e))
    
    def send_json_response(self, data, status_code=200):
        """Envía respuesta JSON"""
        response = json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)
    
    def log_message(self, format, *args):
        """Suprime logs por defecto"""
        pass


def run_server(host="0.0.0.0", port=8011):
    """Inicia el servidor HTTP"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, UpdateHandler)
    
    logger.info(f"✓ Servidor escuchando en http://0.0.0.0:{port}/update/")
    logger.info(f"✓ Conéctate desde otros PCs usando tu IP local (ej: http://192.168.x.x:8011)")
    logger.info(f"✓ Client.zip ubicado en: {CLIENT_ZIP}")
    
    if CLIENT_ZIP.exists():
        logger.info(f"✓ Tamaño de Client.zip: {CLIENT_ZIP.stat().st_size / (1024*1024):.1f} MB")
    else:
        logger.warning(f"⚠ Client.zip no encontrado (las descargas fallarán hasta que se agregue)")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor detenido por usuario")
        httpd.shutdown()


if __name__ == "__main__":
    # Leer puerto desde variable de entorno (para Zeabur)
    port = int(os.environ.get('PORT', 8011))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Iniciando servidor sin Cliente (solo información de servidores)")
    run_server(host=host, port=port)
