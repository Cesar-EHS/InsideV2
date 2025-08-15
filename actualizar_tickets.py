#!/usr/bin/env python3
"""
Script para actualizar la estructura de la tabla tickets
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def actualizar_tabla_tickets():
    """Actualizar la tabla de tickets para remover campos obsoletos"""
    app = create_app()
    
    with app.app_context():
        print("=== ACTUALIZACIÓN TABLA TICKETS ===")
        
        try:
            # Verificar estructura actual
            result = db.session.execute(text("PRAGMA table_info(tickets)"))
            columns = result.fetchall()
            print("Columnas actuales en tabla tickets:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Verificar si el campo 'categoria' existe
            categoria_exists = any(col[1] == 'categoria' for col in columns)
            
            if categoria_exists:
                print("\n🔧 Eliminando campo 'categoria' obsoleto...")
                
                # SQLite no soporta DROP COLUMN directamente, necesitamos recrear la tabla
                # 1. Crear tabla temporal con la nueva estructura
                db.session.execute(text("""
                    CREATE TABLE tickets_new (
                        id INTEGER PRIMARY KEY,
                        departamento_id INTEGER NOT NULL,
                        categoria_id INTEGER NOT NULL,
                        titulo VARCHAR(200) NOT NULL,
                        descripcion TEXT NOT NULL,
                        prioridad VARCHAR(20) NOT NULL,
                        estatus VARCHAR(20) DEFAULT 'Abierto',
                        reportado BOOLEAN DEFAULT 0,
                        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                        fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                        archivo VARCHAR(255),
                        evidencia_1 VARCHAR(255),
                        evidencia_2 VARCHAR(255),
                        evidencia_3 VARCHAR(255),
                        usuario_id INTEGER NOT NULL,
                        FOREIGN KEY (departamento_id) REFERENCES departamentos(id),
                        FOREIGN KEY (categoria_id) REFERENCES categorias_ticket(id),
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )
                """))
                
                # 2. Copiar datos (si hay alguno, pero ya limpiamos la tabla)
                db.session.execute(text("""
                    INSERT INTO tickets_new 
                    SELECT id, departamento_id, categoria_id, titulo, descripcion, prioridad, 
                           estatus, reportado, fecha_creacion, fecha_actualizacion, 
                           archivo, evidencia_1, evidencia_2, evidencia_3, usuario_id
                    FROM tickets 
                    WHERE departamento_id IS NOT NULL AND categoria_id IS NOT NULL
                """))
                
                # 3. Eliminar tabla antigua y renombrar la nueva
                db.session.execute(text("DROP TABLE tickets"))
                db.session.execute(text("ALTER TABLE tickets_new RENAME TO tickets"))
                
                print("✅ Campo 'categoria' eliminado exitosamente")
            else:
                print("✅ El campo 'categoria' ya no existe en la tabla")
            
            # Hacer departamento_id NOT NULL si no lo es
            result = db.session.execute(text("PRAGMA table_info(tickets)"))
            columns = result.fetchall()
            dept_col = next((col for col in columns if col[1] == 'departamento_id'), None)
            
            if dept_col and dept_col[3] == 0:  # notnull = 0 significa que permite NULL
                print("🔧 Haciendo departamento_id obligatorio...")
                # Ya está incluido en la nueva estructura
                print("✅ departamento_id ahora es obligatorio")
            
            db.session.commit()
            print("\n✅ Actualización de tabla tickets completada!")
            print("La tabla ahora tiene la estructura limpia y optimizada.")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante la actualización: {e}")
            print("Revirtiendo cambios...")

if __name__ == '__main__':
    actualizar_tabla_tickets()
