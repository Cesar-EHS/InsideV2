#!/usr/bin/env python3
"""
Script para migrar los datos existentes de tickets al nuevo formato
con áreas y categorías actualizadas
"""
import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.tickets.models import Ticket

def migrate_ticket_data():
    """Migrar datos existentes de tickets al nuevo formato"""
    
    # Mapeo de categorías viejas a nuevas áreas y categorías
    migration_map = {
        'Soporte Sistemas': {
            'area': 'IT',
            'categoria': 'Soporte técnico'
        },
        'Requisición Compras': {
            'area': 'Compras',
            'categoria': 'Solicitud de compra'
        },
        'Desarrollo Organizacional': {
            'area': 'Desarrollo Organizacional',
            'categoria': 'Asesoría individual'
        },
        'Capacitación Técnica': {
            'area': 'Capacitación',
            'categoria': 'Solicitud de curso'
        },
        'Diseño Institucional': {
            'area': 'Diseño',
            'categoria': 'Diseño de material impreso o digital'
        },
        'Recursos Humanos': {
            'area': 'Recursos Humanos',
            'categoria': 'Documentación y constancias'
        },
        'Soporte EHSmart': {
            'area': 'Soporte EHSmart',
            'categoria': 'Errores técnicos'
        },
        'clima laboral': {
            'area': 'Desarrollo Organizacional',
            'categoria': 'Gestión de conflictos laborales'
        }
    }
    
    app = create_app()
    
    with app.app_context():
        print("Iniciando migración de datos de tickets...")
        
        # Obtener todos los tickets existentes
        tickets = Ticket.query.all()
        print(f"Encontrados {len(tickets)} tickets para migrar")
        
        updated_count = 0
        
        for ticket in tickets:
            old_categoria = ticket.categoria
            
            # Si el área está vacía, asignar basado en la categoría antigua
            if not ticket.area and old_categoria in migration_map:
                ticket.area = migration_map[old_categoria]['area']
                print(f"Ticket #{ticket.id}: Asignada área '{ticket.area}' basada en categoría '{old_categoria}'")
                updated_count += 1
            
            # Actualizar categoría si coincide con el mapeo
            if old_categoria in migration_map:
                new_categoria = migration_map[old_categoria]['categoria']
                if ticket.categoria != new_categoria:
                    print(f"Ticket #{ticket.id}: Categoría '{old_categoria}' -> '{new_categoria}'")
                    ticket.categoria = new_categoria
                    updated_count += 1
        
        # Guardar cambios
        try:
            db.session.commit()
            print(f"\n✅ Migración completada exitosamente!")
            print(f"📊 Tickets actualizados: {updated_count}")
            
            # Mostrar estadísticas finales
            print("\n📈 Estadísticas finales por área:")
            areas = db.session.query(Ticket.area, db.func.count(Ticket.id)).group_by(Ticket.area).all()
            for area, count in areas:
                print(f"  - {area or 'Sin área'}: {count} tickets")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error durante la migración: {str(e)}")
            return False
        
        return True

if __name__ == '__main__':
    success = migrate_ticket_data()
    if success:
        print("\n🎉 Migración de datos completada correctamente!")
    else:
        print("\n💥 La migración falló. Revisa los errores anteriores.")
        sys.exit(1)
