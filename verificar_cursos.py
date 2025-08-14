#!/usr/bin/env python3
"""
Script para verificar y actualizar la estructura de la tabla cursos
"""

import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'base_datos.db')

def verificar_estructura_cursos():
    """Verificar estructura actual de la tabla cursos"""
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar columnas existentes
        cursor.execute("PRAGMA table_info(cursos);")
        columnas = cursor.fetchall()
        
        print("Columnas actuales en tabla cursos:")
        for columna in columnas:
            print(f"  - {columna[1]} ({columna[2]})")
        
        # Columnas que deberían existir según el modelo
        columnas_necesarias = [
            'modalidad_id', 'categoria_id', 'objetivo_id', 
            'area_tematica_id', 'tipo_agente_id'
        ]
        
        columnas_existentes = [col[1] for col in columnas]
        columnas_faltantes = [col for col in columnas_necesarias if col not in columnas_existentes]
        
        if columnas_faltantes:
            print(f"\nColumnas faltantes: {columnas_faltantes}")
            agregar_columnas_faltantes(cursor, columnas_faltantes)
            conn.commit()
        else:
            print("\n✅ Todas las columnas necesarias están presentes")
            
    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
        
    finally:
        if conn:
            conn.close()

def agregar_columnas_faltantes(cursor, columnas_faltantes):
    """Agregar columnas faltantes a la tabla cursos"""
    
    print("\nAgregando columnas faltantes...")
    
    for columna in columnas_faltantes:
        try:
            sql = f"ALTER TABLE cursos ADD COLUMN {columna} INTEGER;"
            cursor.execute(sql)
            print(f"  ✅ Agregada columna: {columna}")
        except sqlite3.Error as e:
            print(f"  ❌ Error agregando {columna}: {e}")

if __name__ == "__main__":
    print("Verificando estructura de tabla cursos...")
    verificar_estructura_cursos()
    print("Proceso completado.")
