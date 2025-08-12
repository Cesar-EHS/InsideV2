#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos iniciales
"""

from app import create_app, db
from app.auth.models import (
    User, EstatusUsuario, Departamento, Proyecto, PuestoTrabajo,
    Ocupacion, InstitucionEducativa, NivelEstudio, DocumentoProbatorio,
    EntidadFederativa, Municipio
)

def create_initial_data():
    """Crear datos iniciales para el sistema."""
    
    # Crear estados de usuario
    estatus_data = [
        {'nombre': 'Activo', 'descripcion': 'Usuario activo en el sistema'},
        {'nombre': 'Inactivo', 'descripcion': 'Usuario inactivo temporalmente'},
        {'nombre': 'Suspendido', 'descripcion': 'Usuario suspendido'},
        {'nombre': 'En Proceso', 'descripcion': 'Usuario en proceso de activación'}
    ]
    
    for estatus in estatus_data:
        if not EstatusUsuario.query.filter_by(nombre=estatus['nombre']).first():
            nuevo_estatus = EstatusUsuario(**estatus)
            db.session.add(nuevo_estatus)
    
    # Crear departamentos
    departamentos_data = [
        {'nombre': 'Tecnología', 'descripcion': 'Departamento de Tecnología de la Información'},
        {'nombre': 'Recursos Humanos', 'descripcion': 'Departamento de Recursos Humanos'},
        {'nombre': 'Administración', 'descripcion': 'Departamento Administrativo'},
        {'nombre': 'Ventas', 'descripcion': 'Departamento de Ventas'},
        {'nombre': 'Marketing', 'descripcion': 'Departamento de Marketing'},
        {'nombre': 'Finanzas', 'descripcion': 'Departamento de Finanzas'}
    ]
    
    for depto in departamentos_data:
        if not Departamento.query.filter_by(nombre=depto['nombre']).first():
            nuevo_depto = Departamento(**depto)
            db.session.add(nuevo_depto)
    
    # Crear proyectos
    proyectos_data = [
        {'nombre': 'Inside V2', 'descripcion': 'Sistema integral de gestión empresarial'},
        {'nombre': 'Sistema de Tickets', 'descripcion': 'Sistema de gestión de tickets de soporte'},
        {'nombre': 'Portal Educativo', 'descripcion': 'Plataforma educativa online'},
        {'nombre': 'App Móvil', 'descripcion': 'Aplicación móvil corporativa'},
        {'nombre': 'Sistema de Inventarios', 'descripcion': 'Sistema de control de inventarios'}
    ]
    
    for proyecto in proyectos_data:
        if not Proyecto.query.filter_by(nombre=proyecto['nombre']).first():
            nuevo_proyecto = Proyecto(**proyecto)
            db.session.add(nuevo_proyecto)
    
    # Crear puestos de trabajo
    puestos_data = [
        {'nombre': 'Desarrollador Full Stack', 'descripcion': 'Desarrollo completo de aplicaciones'},
        {'nombre': 'Analista de Sistemas', 'descripcion': 'Análisis y diseño de sistemas'},
        {'nombre': 'Gerente de Proyecto', 'descripcion': 'Gestión y coordinación de proyectos'},
        {'nombre': 'Diseñador UX/UI', 'descripcion': 'Diseño de experiencia e interfaces de usuario'},
        {'nombre': 'Administrador de Base de Datos', 'descripcion': 'Administración de bases de datos'},
        {'nombre': 'Especialista en Seguridad', 'descripcion': 'Seguridad informática'},
        {'nombre': 'Coordinador de RRHH', 'descripcion': 'Coordinación de recursos humanos'}
    ]
    
    for puesto in puestos_data:
        if not PuestoTrabajo.query.filter_by(nombre=puesto['nombre']).first():
            nuevo_puesto = PuestoTrabajo(**puesto)
            db.session.add(nuevo_puesto)
    
    # Crear ocupaciones
    ocupaciones_data = [
        {'nombre': 'Programador Senior', 'descripcion': 'Programador con experiencia avanzada'},
        {'nombre': 'Programador Junior', 'descripcion': 'Programador en desarrollo'},
        {'nombre': 'Consultor Técnico', 'descripcion': 'Consultoría especializada'},
        {'nombre': 'Líder Técnico', 'descripcion': 'Liderazgo técnico de equipos'},
        {'nombre': 'Arquitecto de Software', 'descripcion': 'Diseño de arquitecturas de software'}
    ]
    
    for ocupacion in ocupaciones_data:
        if not Ocupacion.query.filter_by(nombre=ocupacion['nombre']).first():
            nueva_ocupacion = Ocupacion(**ocupacion)
            db.session.add(nueva_ocupacion)
    
    # Crear instituciones educativas
    instituciones_data = [
        {'nombre': 'Universidad Nacional Autónoma de México', 'descripcion': 'UNAM'},
        {'nombre': 'Instituto Politécnico Nacional', 'descripcion': 'IPN'},
        {'nombre': 'Tecnológico de Monterrey', 'descripcion': 'ITESM'},
        {'nombre': 'Universidad Autónoma Metropolitana', 'descripcion': 'UAM'},
        {'nombre': 'Universidad Iberoamericana', 'descripcion': 'UIA'},
        {'nombre': 'Instituto Tecnológico y de Estudios Superiores de Occidente', 'descripcion': 'ITESO'}
    ]
    
    for inst in instituciones_data:
        if not InstitucionEducativa.query.filter_by(nombre=inst['nombre']).first():
            nueva_inst = InstitucionEducativa(**inst)
            db.session.add(nueva_inst)
    
    # Crear niveles de estudio
    niveles_data = [
        {'nombre': 'Primaria', 'descripcion': 'Educación primaria'},
        {'nombre': 'Secundaria', 'descripcion': 'Educación secundaria'},
        {'nombre': 'Preparatoria', 'descripcion': 'Educación media superior'},
        {'nombre': 'Técnico Superior', 'descripcion': 'Educación técnica superior'},
        {'nombre': 'Licenciatura', 'descripcion': 'Educación superior'},
        {'nombre': 'Maestría', 'descripcion': 'Postgrado nivel maestría'},
        {'nombre': 'Doctorado', 'descripcion': 'Postgrado nivel doctorado'}
    ]
    
    for nivel in niveles_data:
        if not NivelEstudio.query.filter_by(nombre=nivel['nombre']).first():
            nuevo_nivel = NivelEstudio(**nivel)
            db.session.add(nuevo_nivel)
    
    # Crear documentos probatorios
    documentos_data = [
        {'nombre': 'Certificado de Primaria', 'descripcion': 'Certificado de estudios de primaria'},
        {'nombre': 'Certificado de Secundaria', 'descripcion': 'Certificado de estudios de secundaria'},
        {'nombre': 'Certificado de Preparatoria', 'descripcion': 'Certificado de estudios de preparatoria'},
        {'nombre': 'Título Técnico', 'descripcion': 'Título de estudios técnicos'},
        {'nombre': 'Título de Licenciatura', 'descripcion': 'Título de licenciatura'},
        {'nombre': 'Cédula Profesional', 'descripcion': 'Cédula profesional'},
        {'nombre': 'Título de Maestría', 'descripcion': 'Título de maestría'},
        {'nombre': 'Título de Doctorado', 'descripcion': 'Título de doctorado'},
        {'nombre': 'Constancia de Estudios', 'descripcion': 'Constancia de estudios en curso'},
        {'nombre': 'Diploma', 'descripcion': 'Diploma de estudios especializados'}
    ]
    
    for doc in documentos_data:
        if not DocumentoProbatorio.query.filter_by(nombre=doc['nombre']).first():
            nuevo_doc = DocumentoProbatorio(**doc)
            db.session.add(nuevo_doc)
    
    # Crear entidades federativas
    entidades_data = [
        'Aguascalientes', 'Baja California', 'Baja California Sur', 'Campeche',
        'Chiapas', 'Chihuahua', 'Ciudad de México', 'Coahuila', 'Colima',
        'Durango', 'Estado de México', 'Guanajuato', 'Guerrero', 'Hidalgo',
        'Jalisco', 'Michoacán', 'Morelos', 'Nayarit', 'Nuevo León', 'Oaxaca',
        'Puebla', 'Querétaro', 'Quintana Roo', 'San Luis Potosí', 'Sinaloa',
        'Sonora', 'Tabasco', 'Tamaulipas', 'Tlaxcala', 'Veracruz', 'Yucatán', 'Zacatecas'
    ]
    
    for entidad in entidades_data:
        if not EntidadFederativa.query.filter_by(nombre=entidad).first():
            nueva_entidad = EntidadFederativa(nombre=entidad)
            db.session.add(nueva_entidad)
    
    # Commit para obtener IDs
    db.session.commit()
    
    # Crear algunos municipios de ejemplo
    cdmx = EntidadFederativa.query.filter_by(nombre='Ciudad de México').first()
    if cdmx:
        municipios_cdmx = [
            'Álvaro Obregón', 'Azcapotzalco', 'Benito Juárez', 'Coyoacán',
            'Cuajimalpa', 'Gustavo A. Madero', 'Iztacalco', 'Iztapalapa',
            'Magdalena Contreras', 'Miguel Hidalgo', 'Milpa Alta', 'Tláhuac',
            'Tlalpan', 'Venustiano Carranza', 'Xochimilco'
        ]
        
        for municipio in municipios_cdmx:
            if not Municipio.query.filter_by(nombre=municipio, entidad_federativa_id=cdmx.id).first():
                nuevo_municipio = Municipio(nombre=municipio, entidad_federativa_id=cdmx.id)
                db.session.add(nuevo_municipio)
    
    # Crear usuario administrador de ejemplo
    admin_estatus = EstatusUsuario.query.filter_by(nombre='Activo').first()
    depto_ti = Departamento.query.filter_by(nombre='Tecnología').first()
    puesto_admin = PuestoTrabajo.query.filter_by(nombre='Administrador del Sistema').first()
    
    if not User.query.filter_by(email='admin@inside.com').first() and admin_estatus:
        admin_user = User(
            nombre='Administrador',
            apellido_paterno='Sistema',
            apellido_materno='Inside',
            curp='ADSI850101HMCNSR01',
            email='admin@inside.com',
            telefono='5555555555',
            estatus_id=admin_estatus.id,
            departamento_id=depto_ti.id if depto_ti else None,
            puesto_trabajo_id=puesto_admin.id if puesto_admin else 1,  # ID 1 debe ser admin
            fecha_ingreso=db.func.current_date()
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        print("Usuario administrador creado: admin@inside.com / admin123")
    
    db.session.commit()
    print("Datos iniciales creados exitosamente!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_initial_data()
