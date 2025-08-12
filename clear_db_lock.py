#!/usr/bin/env python3
"""
Script para limpiar bloqueos de la base de datos SQLite
"""
import sqlite3
import os
import time

db_path = "instance/base_datos.db"
journal_path = "instance/base_datos.db-journal"

print("Intentando limpiar bloqueos de base de datos...")

# Intentar eliminar el journal file
if os.path.exists(journal_path):
    try:
        os.remove(journal_path)
        print(f"Journal file eliminado: {journal_path}")
    except Exception as e:
        print(f"No se pudo eliminar journal file: {e}")

# Conectar a la base de datos y realizar operaciones básicas
try:
    print("Conectando a la base de datos...")
    conn = sqlite3.connect(db_path, timeout=5.0)
    
    # Configurar pragmas para mejor concurrencia
    cursor = conn.cursor()
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=1000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA busy_timeout=30000")
    
    # Verificar que la base de datos esté accesible
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
    result = cursor.fetchone()
    print(f"Base de datos accesible. Primera tabla: {result}")
    
    # Hacer un commit simple para limpiar cualquier transacción pendiente
    conn.commit()
    print("Commit realizado exitosamente")
    
    cursor.close()
    conn.close()
    print("Base de datos limpiada exitosamente!")
    
except Exception as e:
    print(f"Error al limpiar la base de datos: {e}")

print("Script completado.")
