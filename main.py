#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - Punto de entrada para Zeabur
Simplemente ejecuta UPDATE_SERVER_FINAL.py
"""

import sys
import os

# Asegurarse de que estamos en el directorio correcto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Ejecutar el servidor de actualizaciones
from UPDATE_SERVER_FINAL import run_server

if __name__ == "__main__":
    # Leer puerto desde variable de entorno
    port = int(os.environ.get('PORT', 8011))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"Iniciando servidor en {host}:{port}")
    run_server(host=host, port=port)
