#!/usr/bin/env python
"""
Script para aplicar migraciones sin iniciar Flask
"""

import os
import sys
from flask import Flask
from flask_migrate import Migrate, upgrade
from app import create_app, db

# Crear la aplicación Flask
app = create_app()

# Configurar migrate
migrate = Migrate(app, db)

with app.app_context():
    try:
        print("Aplicando migraciones...")
        upgrade()
        print("✅ Migraciones aplicadas exitosamente!")
    except Exception as e:
        print(f"❌ Error al aplicar migraciones: {e}")
        sys.exit(1)
