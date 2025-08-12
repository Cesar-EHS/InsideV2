#!/usr/bin/env python
"""
Script para limpiar tablas temporales y agregar columnas directamente
"""

import sqlite3

# Ruta de la base de datos
db_path = r"instance\base_datos.db"

try:
    print("Conectando a la base de datos...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Limpiar tablas temporales de alembic
    print("Limpiando tablas temporales...")
    cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_evento")
    cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_comment")
    cursor.execute("DROP TABLE IF EXISTS _alembic_tmp_reaction")
    
    # ============= TABLA POST =============
    print("\n=== Verificando tabla 'post' ===")
    cursor.execute("PRAGMA table_info(post)")
    columns = cursor.fetchall()
    post_columns = [col[1] for col in columns]
    print(f"Columnas existentes: {post_columns}")
    
    if 'active' not in post_columns:
        print("Agregando columna 'active' a post...")
        cursor.execute("ALTER TABLE post ADD COLUMN active BOOLEAN NOT NULL DEFAULT 1")
    
    # ============= TABLA COMMENT =============
    print("\n=== Verificando tabla 'comment' ===")
    cursor.execute("PRAGMA table_info(comment)")
    columns = cursor.fetchall()
    comment_columns = [col[1] for col in columns]
    print(f"Columnas existentes: {comment_columns}")
    
    if 'active' not in comment_columns:
        print("Agregando columna 'active' a comment...")
        cursor.execute("ALTER TABLE comment ADD COLUMN active BOOLEAN NOT NULL DEFAULT 1")
    
    # ============= TABLA EVENTO =============
    print("\n=== Verificando tabla 'evento' ===")
    cursor.execute("PRAGMA table_info(evento)")
    columns = cursor.fetchall()
    evento_columns = [col[1] for col in columns]
    print(f"Columnas existentes: {evento_columns}")
    
    # Lista de columnas que necesitamos en evento
    evento_columns_needed = [
        ("location", "VARCHAR(255)"),
        ("type", "VARCHAR(50) DEFAULT 'meeting'"),
        ("max_attendees", "INTEGER"),
        ("is_recurring", "BOOLEAN DEFAULT 0"),
        ("recurrence_pattern", "VARCHAR(100)"),
        ("reminder_sent", "BOOLEAN DEFAULT 0"),
        ("created_by", "INTEGER NOT NULL DEFAULT 1"),
        ("active", "BOOLEAN NOT NULL DEFAULT 1")
    ]
    
    # Agregar cada columna si no existe
    for column_name, column_type in evento_columns_needed:
        if column_name not in evento_columns:
            try:
                sql = f"ALTER TABLE evento ADD COLUMN {column_name} {column_type}"
                print(f"Agregando columna a evento: {column_name}")
                cursor.execute(sql)
            except Exception as e:
                print(f"Error agregando {column_name} a evento: {e}")
    
    # ============= TABLA REACTION =============
    print("\n=== Verificando tabla 'reaction' ===")
    cursor.execute("PRAGMA table_info(reaction)")
    columns = cursor.fetchall()
    reaction_columns = [col[1] for col in columns]
    print(f"Columnas existentes: {reaction_columns}")
    
    # Reaction no tiene active en el modelo actual, así que no la agregamos
    
    # ============= VERIFICAR TABLAS ESPECIALES =============
    print("\n=== Verificando tabla 'event_attendees' ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='event_attendees'")
    table_exists = cursor.fetchone()
    print(f"¿Existe tabla 'event_attendees'?: {table_exists is not None}")
    
    conn.commit()
    
    # ============= VERIFICACIÓN FINAL =============
    print("\n=== VERIFICACIÓN FINAL ===")
    
    # Post
    cursor.execute("PRAGMA table_info(post)")
    post_final = [col[1] for col in cursor.fetchall()]
    print(f"Post columnas finales: {post_final}")
    
    # Comment
    cursor.execute("PRAGMA table_info(comment)")
    comment_final = [col[1] for col in cursor.fetchall()]
    print(f"Comment columnas finales: {comment_final}")
    
    # Evento
    cursor.execute("PRAGMA table_info(evento)")
    evento_final = [col[1] for col in cursor.fetchall()]
    print(f"Evento columnas finales: {evento_final}")
    
    # Actualizar la versión de alembic
    print("\nActualizando versión de alembic...")
    cursor.execute("UPDATE alembic_version SET version_num = 'all_tables_fixed'")
    conn.commit()
    
    cursor.execute("SELECT version_num FROM alembic_version")
    version = cursor.fetchone()
    print(f"Nueva versión: {version[0] if version else 'No definida'}")
    
    conn.close()
    print("\n✅ Base de datos actualizada correctamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if 'conn' in locals():
        conn.rollback()
        conn.close()
