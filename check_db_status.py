#!/usr/bin/env python
"""
Script para verificar el estado de la base de datos
"""

import sqlite3
import os

# Ruta de la base de datos
db_path = r"C:\Users\ehsta.LAPTOP-IDIICLND\OneDrive\Escritorio\Inside V2\instance\base_datos.db"

try:
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== Verificando estructura de la tabla 'post' ===")
    cursor.execute("PRAGMA table_info(post)")
    columns = cursor.fetchall()
    post_columns = [col[1] for col in columns]
    print(f"Columnas en 'post': {post_columns}")
    print(f"¿Existe 'active'?: {'active' in post_columns}")
    
    print("\n=== Verificando estructura de la tabla 'evento' ===")
    cursor.execute("PRAGMA table_info(evento)")
    columns = cursor.fetchall()
    evento_columns = [col[1] for col in columns]
    print(f"Columnas en 'evento': {evento_columns}")
    
    expected_columns = ['location', 'type', 'max_attendees', 'is_recurring', 'recurrence_pattern', 'reminder_sent', 'created_by', 'active']
    missing_columns = [col for col in expected_columns if col not in evento_columns]
    print(f"Columnas faltantes: {missing_columns}")
    
    print("\n=== Verificando tabla 'event_attendees' ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_attendees'")
    table_exists = cursor.fetchone()
    print(f"¿Existe tabla 'event_attendees'?: {table_exists is not None}")
    
    print("\n=== Verificando versión de migración actual ===")
    try:
        cursor.execute("SELECT version_num FROM alembic_version")
        current_version = cursor.fetchone()
        print(f"Versión actual: {current_version[0] if current_version else 'No definida'}")
    except Exception as e:
        print(f"Error al obtener versión: {e}")
    
    conn.close()
    
except Exception as e:
    print(f"Error al conectar con la base de datos: {e}")
