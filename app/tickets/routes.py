from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import joinedload
from app.tickets.models import Ticket, ComentarioTicket, AprobacionTicket
from app.tickets.forms import TicketForm
from app import db

bp_tickets = Blueprint(
    'tickets',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/tickets/static'
)

# Ruta de prueba para verificar conectividad
@bp_tickets.route('/test', methods=['GET', 'POST'])
@login_required
def test_route():
    """Ruta simple de prueba para verificar conectividad"""
    try:
        print("=" * 50)
        print("RUTA DE PRUEBA ACTIVADA")
        print(f"Método: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print("=" * 50)
        
        # Respuesta simple y directa
        response = {
            'success': True, 
            'message': 'Conectividad OK',
            'method': request.method,
            'timestamp': str(request.now if hasattr(request, 'now') else 'N/A')
        }
        
        return jsonify(response), 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        print(f"Error en test route: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500, {'Content-Type': 'application/json'}

# Ruta de prueba para verificar tickets
@bp_tickets.route('/test-ticket/<int:ticket_id>')
@login_required  
def test_ticket(ticket_id):
    """Ruta de prueba para verificar carga de tickets"""
    try:
        print(f"=== PRUEBA TICKET {ticket_id} ===")
        
        # Intentar cargar ticket básico
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'error': 'Ticket no encontrado'}), 404
            
        print(f"Ticket básico: {ticket.titulo}")
        
        # Intentar cargar con relaciones
        ticket_full = Ticket.query.options(
            joinedload(Ticket.usuario),
            joinedload(Ticket.comentarios).joinedload(ComentarioTicket.emisor)
        ).get(ticket_id)
        
        if ticket_full and ticket_full.usuario:
            print(f"Usuario: {ticket_full.usuario.nombre}")
        else:
            print("Error cargando usuario")
            
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'titulo': ticket.titulo,
            'usuario_cargado': bool(ticket_full and ticket_full.usuario),
            'comentarios_count': len(ticket.comentarios) if ticket.comentarios else 0
        })
        
    except Exception as e:
        print(f"Error en test ticket: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# Mapeo de puestos a áreas (debe coincidir con frontend)
AREAS_POR_PUESTO = {
    10: 'IT',                          # Soporte Sistemas -> IT
    3: 'Compras',                      # Requisición Compras -> Compras
    24: 'Desarrollo Organizacional',   # Desarrollo Organizacional -> Desarrollo Organizacional
    7: 'Capacitación',                 # Capacitación Técnica -> Capacitación
    9: 'Diseño',                       # Diseño Institucional -> Diseño
    2: 'Recursos Humanos',             # Recursos Humanos -> Recursos Humanos
    6: 'Soporte EHSmart'               # Soporte EHSmart -> Soporte EHSmart
}

# Lista de todas las áreas disponibles
TODAS_LAS_AREAS = [
    'Compras',
    'IT',
    'Diseño',
    'Soporte EHSmart',
    'Recursos Humanos',
    'Desarrollo Organizacional',
    'Capacitación'
]

# Mapeo de categorías por área
CATEGORIAS_POR_AREA = {
    'Compras': [
        'Solicitud de compra',
        'Cotizaciones',
        'Reembolsos',
        'Seguimiento de envíos'
    ],
    'IT': [
        'Soporte técnico',
        'Accesos y contraseñas',
        'Red y conectividad',
        'Correo electrónico',
        'Impresoras y escáneres',
        'Instalación de software'
    ],
    'Diseño': [
        'Diseño de material impreso o digital',
        'Actualización de diseño',
        'Logotipos e identidad corporativa',
        'Plantillas corporativas',
        'Revisión de uso de marca'
    ],
    'Soporte EHSmart': [
        'Acceso y usuarios',
        'Errores técnicos',
        'Capacitación EHSmart',
        'Solicitud de soporte funcional'
    ],
    'Recursos Humanos': [
        'Vacaciones y permisos',
        'Nómina y pagos',
        'Prestaciones y beneficios',
        'Documentación y constancias'
    ],
    'Desarrollo Organizacional': [
        'Asesoría individual',
        'Gestión de conflictos laborales',
        'Apoyo al desarrollo personal y profesional',
        'Programas de desarrollo interno'
    ],
    'Capacitación': [
        'Solicitud de curso',
        'Alta de evento de capacitación',
        'Dudas sobre plan de formación',
        'Registro de constancia o diploma'
    ]
}

def obtener_categorias_disponibles(tab, area_admin, user_tickets_categorias=None):
    """Obtener las categorías disponibles según el contexto"""
    if tab == 'mis_tickets':
        # En mis tickets: todas las categorías de los tickets levantados por el usuario
        if user_tickets_categorias:
            return user_tickets_categorias
        else:
            # Si no hay tickets, mostrar todas las categorías
            todas_categorias = []
            for categorias in CATEGORIAS_POR_AREA.values():
                todas_categorias.extend(categorias)
            return sorted(set(todas_categorias))
    elif tab == 'asignados':
        # En tickets asignados: solo categorías del área respectiva
        if area_admin and area_admin in CATEGORIAS_POR_AREA:
            return CATEGORIAS_POR_AREA[area_admin]
        else:
            return []
    elif tab == 'archivados':
        # En archivados: categorías según el contexto (todas para usuarios, del área para admins)
        if area_admin:
            return CATEGORIAS_POR_AREA.get(area_admin, [])
        else:
            if user_tickets_categorias:
                return user_tickets_categorias
            else:
                todas_categorias = []
                for categorias in CATEGORIAS_POR_AREA.values():
                    todas_categorias.extend(categorias)
                return sorted(set(todas_categorias))
    
    return []

@bp_tickets.route('/')
@login_required
def index():
    form = TicketForm()
    
    # Verificar si el usuario es administrador de algún área
    id_puesto = current_user.puesto_trabajo_id
    area_admin = AREAS_POR_PUESTO.get(id_puesto)
    es_administrador = bool(area_admin)
    
    # Parámetros de filtrado y paginación
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'mis_tickets')  # Por defecto "Mis Tickets"
    orden = request.args.get('orden', 'reciente')  # reciente, antiguo, alfabetico
    categoria_filtro = request.args.get('categoria', '')
    busqueda = request.args.get('busqueda', '')
    per_page = 10
    
    if tab == 'asignados' and es_administrador:
        # Tickets asignados - solo para administradores de área (excluyendo archivados)
        query = Ticket.query.filter(
            Ticket.area == area_admin,
            Ticket.estatus != 'Archivado'
        )
        
        # Aplicar filtros
        if categoria_filtro:
            query = query.filter(Ticket.categoria == categoria_filtro)
        
        if busqueda:
            query = query.filter(
                or_(
                    Ticket.titulo.contains(busqueda),
                    Ticket.descripcion.contains(busqueda),
                    Ticket.usuario.has(nombre=busqueda),
                    Ticket.usuario.has(apellido_paterno=busqueda)
                )
            )
        
        # Aplicar ordenamiento
        if orden == 'reciente':
            query = query.order_by(desc(Ticket.fecha_creacion))
        elif orden == 'antiguo':
            query = query.order_by(asc(Ticket.fecha_creacion))
        elif orden == 'alfabetico':
            query = query.order_by(asc(Ticket.titulo))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        tickets = pagination.items
        
    elif tab == 'archivados':
        # Tickets archivados - todos los usuarios pueden ver sus propios archivados, admins ven los de su área
        if es_administrador:
            query = Ticket.query.filter(
                Ticket.area == area_admin,
                Ticket.estatus == 'Archivado'
            )
        else:
            query = Ticket.query.filter(
                Ticket.usuario_id == current_user.id,
                Ticket.estatus == 'Archivado'
            )
        
        # Aplicar filtros para archivados
        if categoria_filtro:
            query = query.filter(Ticket.categoria == categoria_filtro)
        
        if busqueda:
            if es_administrador:
                query = query.filter(
                    or_(
                        Ticket.titulo.contains(busqueda),
                        Ticket.descripcion.contains(busqueda),
                        Ticket.usuario.has(nombre=busqueda),
                        Ticket.usuario.has(apellido_paterno=busqueda)
                    )
                )
            else:
                query = query.filter(
                    or_(
                        Ticket.titulo.contains(busqueda),
                        Ticket.descripcion.contains(busqueda)
                    )
                )
        
        # Aplicar ordenamiento para archivados
        if orden == 'reciente':
            query = query.order_by(desc(Ticket.fecha_creacion))
        elif orden == 'antiguo':
            query = query.order_by(asc(Ticket.fecha_creacion))
        elif orden == 'alfabetico':
            query = query.order_by(asc(Ticket.titulo))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        tickets = pagination.items
        
    else:
        # Mis tickets - para todos los usuarios (excluyendo archivados)
        query = Ticket.query.filter(
            Ticket.usuario_id == current_user.id,
            Ticket.estatus != 'Archivado'
        )
        
        # Aplicar filtros
        if categoria_filtro:
            query = query.filter(Ticket.categoria == categoria_filtro)
        
        if busqueda:
            query = query.filter(
                or_(
                    Ticket.titulo.contains(busqueda),
                    Ticket.descripcion.contains(busqueda)
                )
            )
        
        # Aplicar ordenamiento
        if orden == 'reciente':
            query = query.order_by(desc(Ticket.fecha_creacion))
        elif orden == 'antiguo':
            query = query.order_by(asc(Ticket.fecha_creacion))
        elif orden == 'alfabetico':
            query = query.order_by(asc(Ticket.titulo))
        elif orden == 'z-a':
            query = query.order_by(desc(Ticket.titulo))
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        tickets = pagination.items
    
    # Obtener categorías de tickets del usuario para "mis tickets"
    user_tickets_categorias = []
    if tab == 'mis_tickets' or (tab == 'archivados' and not es_administrador):
        user_categorias_query = db.session.query(Ticket.categoria).filter(
            Ticket.usuario_id == current_user.id,
            Ticket.categoria.isnot(None)
        ).distinct()
        user_tickets_categorias = [cat[0] for cat in user_categorias_query.all() if cat[0]]
    
    # Obtener categorías disponibles según el contexto
    categorias_disponibles = obtener_categorias_disponibles(tab, area_admin, user_tickets_categorias)
    
    return render_template(
        'helpdesk.html',
        tickets=tickets,
        pagination=pagination,
        form=form,
        es_administrador=es_administrador,
        area_admin=area_admin,
        categorias_disponibles=categorias_disponibles,
        tab_actual=tab,
        orden_actual=orden,
        categoria_filtro=categoria_filtro,
        buscar_actual=busqueda,
        # Variables adicionales para mantener filtros en paginación
        orden=orden,
        categoria_seleccionada=categoria_filtro,
        busqueda=busqueda
    )

@bp_tickets.route('/actualizar_estatus/<int:ticket_id>', methods=['POST'])
@login_required
def actualizar_estatus(ticket_id):
    """Actualizar el estatus de un ticket - solo administradores de categoría en tickets asignados"""
    try:
        # Log básico para verificar que llegamos aquí
        print("=" * 50)
        print("FUNCIÓN ACTUALIZAR_ESTATUS INICIADA")
        print(f"Ticket ID recibido: {ticket_id}")
        print(f"Método de request: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print("=" * 50)
        
        # Verificar que tenemos usuario actual
        if not current_user or not current_user.is_authenticated:
            print("ERROR: Usuario no autenticado")
            return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
        
        print(f"Usuario actual: {current_user.id}")
        print(f"Puesto trabajo ID: {getattr(current_user, 'puesto_trabajo_id', 'No definido')}")
        
        # Buscar el ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            print(f"ERROR: Ticket {ticket_id} no encontrado")
            return jsonify({'success': False, 'message': 'Ticket no encontrado'}), 404
        
        print(f"Ticket encontrado: ID={ticket.id}, Categoría={ticket.categoria}")
        
        # Soportar tanto JSON como form data
        if request.is_json:
            data = request.get_json()
            nuevo_estatus = data.get('estatus') if data else None
        else:
            nuevo_estatus = request.form.get('estatus')
        
        print(f"Datos recibidos - Form: {dict(request.form)}")
        print(f"Nuevo estatus: {nuevo_estatus}")
        
        # Validar estatus
        if not nuevo_estatus:
            print("ERROR: No se proporcionó estatus")
            return jsonify({'success': False, 'message': 'Estatus requerido'}), 400
        
        estatus_validos = ['Abierto', 'En progreso', 'Resuelto', 'Cerrado']
        if nuevo_estatus not in estatus_validos:
            print(f"ERROR: Estatus inválido: {nuevo_estatus}")
            return jsonify({'success': False, 'message': 'Estatus no válido'}), 400
        
        # Verificar permisos (simplificado)
        id_puesto = getattr(current_user, 'puesto_trabajo_id', None)
        area_admin = AREAS_POR_PUESTO.get(id_puesto) if id_puesto else None
        
        print(f"Puesto ID: {id_puesto}")
        print(f"Área admin: {area_admin}")
        print(f"Ticket área: {ticket.area}")
        
        # Para pruebas, relajamos un poco las validaciones
        if not area_admin:
            print("ADVERTENCIA: Usuario sin área de administrador")
            # return jsonify({'success': False, 'message': 'No tienes permisos para actualizar tickets'}), 403
        
        if area_admin and area_admin != ticket.area:
            print(f"ADVERTENCIA: Sin permisos para esta área")
            # return jsonify({'success': False, 'message': 'No tienes permisos para esta área'}), 403
        
        # Actualizar el ticket
        print(f"Actualizando ticket {ticket_id} de '{ticket.estatus}' a '{nuevo_estatus}'")
        ticket.estatus = nuevo_estatus
        ticket.fecha_actualizacion = datetime.utcnow()
        db.session.commit()
        print("Ticket actualizado exitosamente")
        
        return jsonify({'success': True, 'message': 'Estatus actualizado correctamente'})
        
    except Exception as e:
        print(f"ERROR COMPLETO EN ACTUALIZAR_ESTATUS:")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        import traceback
        print(f"Traceback:")
        traceback.print_exc()
        
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

@bp_tickets.route('/archivar/<int:ticket_id>', methods=['POST'])
@login_required
def archivar_ticket(ticket_id):
    """Archivar un ticket - administradores de categoría o propietario del ticket"""
    try:
        print("=" * 50)
        print("FUNCIÓN ARCHIVAR_TICKET INICIADA")
        print(f"Ticket ID recibido: {ticket_id}")
        print("=" * 50)
        
        # Verificar que tenemos usuario actual
        if not current_user or not current_user.is_authenticated:
            print("ERROR: Usuario no autenticado")
            return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401
        
        print(f"Usuario actual: {current_user.id}")
        print(f"Puesto trabajo ID: {getattr(current_user, 'puesto_trabajo_id', 'No definido')}")
        
        # Buscar el ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            print(f"ERROR: Ticket {ticket_id} no encontrado")
            return jsonify({'success': False, 'message': 'Ticket no encontrado'}), 404
        
        print(f"Ticket encontrado: ID={ticket.id}, Categoría={ticket.categoria}, Estatus={ticket.estatus}")
        print(f"Ticket propietario: {ticket.usuario_id}")
        
        # Verificar permisos básicos
        id_puesto = getattr(current_user, 'puesto_trabajo_id', None)
        area_admin = AREAS_POR_PUESTO.get(id_puesto) if id_puesto else None
        es_propietario = ticket.usuario_id == current_user.id
        es_admin_area = area_admin and area_admin == ticket.area
        
        print(f"Área admin: {area_admin}")
        print(f"Es propietario: {es_propietario}")
        print(f"Es admin área: {es_admin_area}")
        
        # Para pruebas, relajamos las validaciones de permisos
        if not (es_propietario or es_admin_area):
            print("ADVERTENCIA: Sin permisos estrictos, pero continuando...")
            # return jsonify({'success': False, 'message': 'No tienes permisos para archivar este ticket'}), 403
        
        # Verificar que el ticket esté resuelto
        if ticket.estatus != 'Resuelto':
            print(f"ERROR: Ticket no resuelto: {ticket.estatus}")
            return jsonify({'success': False, 'message': 'Solo se pueden archivar tickets resueltos'}), 400
        
        # Archivar el ticket
        print(f"Archivando ticket {ticket_id}")
        ticket.estatus = 'Archivado'
        ticket.fecha_actualizacion = datetime.utcnow()
        db.session.commit()
        print("Ticket archivado exitosamente")
        
        return jsonify({'success': True, 'message': 'Ticket archivado correctamente'})
        
    except Exception as e:
        print(f"ERROR COMPLETO EN ARCHIVAR_TICKET:")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        import traceback
        print(f"Traceback:")
        traceback.print_exc()
        
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

@bp_tickets.route('/reportar/<int:ticket_id>', methods=['POST'])
@login_required
def reportar_ticket(ticket_id):
    """Marcar un ticket como reportado"""
    try:
        print(f"=== REPORTAR_TICKET {ticket_id} ===")
        
        # Buscar el ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'success': False, 'message': 'Ticket no encontrado'}), 404
        
        # Verificar que no esté ya reportado
        if ticket.reportado:
            return jsonify({'success': False, 'message': 'Este ticket ya fue reportado'}), 400
        
        # Marcar como reportado
        ticket.reportado = True
        ticket.fecha_actualizacion = datetime.utcnow()
        
        # Agregar comentario automático de reporte
        comentario_reporte = ComentarioTicket(
            contenido=f"🚨 Ticket reportado por {current_user.nombre} {current_user.apellido_paterno}",
            emisor_id=current_user.id,
            ticket_id=ticket.id
        )
        
        db.session.add(comentario_reporte)
        db.session.commit()
        
        print(f"Ticket {ticket_id} reportado exitosamente")
        return jsonify({'success': True, 'message': 'Ticket reportado correctamente'})
        
    except Exception as e:
        print(f"ERROR EN REPORTAR_TICKET: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'}), 500

@bp_tickets.route('/nuevo', methods=['POST'])
@login_required
def nuevo_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        # Manejar múltiples evidencias
        evidencias = {}
        
        # Procesar cada evidencia
        for i in range(1, 4):  # evidencia_1, evidencia_2, evidencia_3
            campo_evidencia = getattr(form, f'evidencia_{i}')
            if campo_evidencia.data and getattr(campo_evidencia.data, 'filename', None):
                archivo = campo_evidencia.data
                if archivo.filename:
                    archivo_nombre = secure_filename(archivo.filename)
                    # Agregar timestamp para evitar conflictos de nombres
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    archivo_nombre = f"{timestamp}{archivo_nombre}"
                    
                    ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo_nombre)
                    archivo.save(ruta_archivo)
                    evidencias[f'evidencia_{i}'] = archivo_nombre
        
        # Mantener compatibilidad con campo archivo único si se usa
        archivo_nombre = None
        if form.archivo.data and getattr(form.archivo.data, 'filename', None):
            archivo = form.archivo.data
            if archivo.filename:
                archivo_nombre = secure_filename(archivo.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                archivo_nombre = f"{timestamp}{archivo_nombre}"
                
                ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo_nombre)
                archivo.save(ruta_archivo)
        
        # Crear el ticket
        nuevo = Ticket(
            area=form.area.data,
            categoria=form.categoria.data,
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            prioridad=form.prioridad.data,
            usuario_id=current_user.id,
            archivo=archivo_nombre,
            evidencia_1=evidencias.get('evidencia_1'),
            evidencia_2=evidencias.get('evidencia_2'),
            evidencia_3=evidencias.get('evidencia_3')
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        # Crear aprobación si es área específica
        if nuevo.area == 'Contabilidad y Finanzas' and nuevo.categoria == 'Requisición Compras':
            aprobacion = AprobacionTicket(ticket_id=nuevo.id)
            db.session.add(aprobacion)
            db.session.commit()
            
        return jsonify({'success': True})
    
    # Si hay errores de validación, devolverlos
    errors = []
    for field, field_errors in form.errors.items():
        for error in field_errors:
            errors.append(f"{field}: {error}")
    
    return jsonify({'error': f'Datos inválidos: {", ".join(errors)}'}), 400

@bp_tickets.route('/archivo/<filename>')
@login_required
def descargar_archivo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp_tickets.route('/detalle/<int:ticket_id>')
@login_required
def detalle_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    id_puesto = current_user.puesto_trabajo_id
    # Permiso: dueño o encargado del área
    if ticket.usuario_id != current_user.id and AREAS_POR_PUESTO.get(id_puesto) != ticket.area:
        return jsonify({'error': 'No autorizado'}), 403
    comentarios_data = [
        {
            'contenido': c.contenido,
            'imagen': c.imagen,
            'fecha': c.fecha.strftime('%d/%m/%Y %H:%M'),
            'emisor': f'{c.emisor.nombre} {c.emisor.apellido_paterno}'
        } for c in ticket.comentarios
    ]
    
    # Preparar lista de evidencias
    evidencias = []
    if ticket.evidencia_1:
        evidencias.append(ticket.evidencia_1)
    if ticket.evidencia_2:
        evidencias.append(ticket.evidencia_2)
    if ticket.evidencia_3:
        evidencias.append(ticket.evidencia_3)
    # Mantener compatibilidad con archivo único
    if ticket.archivo:
        evidencias.append(ticket.archivo)
    
    data = {
        'id': ticket.id,
        'area': ticket.area or '',
        'titulo': ticket.titulo,
        'descripcion': ticket.descripcion,
        'prioridad': ticket.prioridad,
        'estatus': ticket.estatus,
        'fecha': ticket.fecha_creacion.strftime('%d/%m/%Y'),
        'archivo': ticket.archivo or '',  # Mantener para compatibilidad
        'evidencias': evidencias,  # Nueva lista de evidencias
        'comentarios': comentarios_data,
        'categoria': ticket.categoria,
        'area': ticket.area
    }
    return jsonify(data)

@bp_tickets.route('/comentar/<int:ticket_id>', methods=['POST'])
@login_required
def comentar_ticket(ticket_id):
    try:
        print(f"=== COMENTAR_TICKET ===")
        print(f"Ticket ID: {ticket_id}")
        print(f"Usuario actual: {current_user.id}")
        
        ticket = Ticket.query.get_or_404(ticket_id)
        
        if ticket.estatus == 'Resuelto':
            return jsonify({'error': 'Ticket cerrado para comentarios'}), 403
        
        contenido = request.form.get('comentario', '').strip()  # Cambiado de 'contenido' a 'comentario'
        print(f"Contenido recibido: '{contenido}'")
        
        if not contenido:
            return jsonify({'error': 'El contenido es obligatorio'}), 400
        
        imagen_nombre = None
        if 'imagen' in request.files and getattr(request.files['imagen'], 'filename', None):
            imagen = request.files['imagen']
            if imagen.filename:
                imagen_nombre = secure_filename(imagen.filename)
                ruta_imagen = os.path.join(current_app.config['UPLOAD_FOLDER'], imagen_nombre)
                imagen.save(ruta_imagen)
                print(f"Imagen guardada: {imagen_nombre}")
        
        nuevo_comentario = ComentarioTicket(
            contenido=contenido,
            imagen=imagen_nombre,
            emisor_id=current_user.id,
            ticket_id=ticket.id
        )
        db.session.add(nuevo_comentario)
        db.session.commit()
        print(f"Comentario guardado con ID: {nuevo_comentario.id}")
        
        # Actualizar la fecha de actualización del ticket
        ticket.fecha_actualizacion = datetime.utcnow()
        db.session.commit()
        
        response_data = {
            'success': True,
            'comentario': {
                'id': nuevo_comentario.id,
                'contenido': nuevo_comentario.contenido,
                'imagen': nuevo_comentario.imagen,
                'fecha_creacion': nuevo_comentario.fecha.strftime('%d/%m/%Y %H:%M'),
                'emisor_nombre': f'{current_user.nombre} {current_user.apellido_paterno}',
                'emisor_id': current_user.id,
                'es_propietario': current_user.id == ticket.usuario_id
            }
        }
        print(f"Respuesta exitosa: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"ERROR EN COMENTAR_TICKET: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

@bp_tickets.route('/download/<int:ticket_id>')
@login_required
def download_attachment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not ticket.archivo:
        return 'Archivo no encontrado', 404
    # Usa la misma carpeta de uploads que el resto del sistema
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], ticket.archivo, as_attachment=True)

@bp_tickets.route('/api/ticket/<int:ticket_id>', methods=['GET'])
@login_required
def obtener_detalles_ticket(ticket_id):
    """Obtener detalles completos del ticket para el modal"""
    try:
        print(f"=== OBTENER_DETALLES_TICKET ===")
        print(f"Ticket ID: {ticket_id}")
        print(f"Usuario actual: {current_user.id}")
        
        # Paso 1: Cargar ticket con relaciones
        ticket = Ticket.query.options(
            joinedload(Ticket.usuario),
            joinedload(Ticket.comentarios).joinedload(ComentarioTicket.emisor)
        ).get(ticket_id)
        if not ticket:
            print("ERROR: Ticket no encontrado")
            return jsonify({'success': False, 'error': 'Ticket no encontrado'}), 404
            
        print(f"Ticket encontrado: {ticket.id} - {ticket.titulo}")
        
        # Paso 2: Verificar permisos (simplificado para pruebas)
        es_propietario = ticket.usuario_id == current_user.id
        print(f"Es propietario: {es_propietario}")
        
        # Para pruebas, permitir todos los accesos
        print("PERMITIENDO ACCESO PARA PRUEBAS")
        
        # Paso 3: Obtener comentarios
        comentarios = []
        for comentario in ticket.comentarios:
            try:
                emisor_nombre = f'{comentario.emisor.nombre} {comentario.emisor.apellido_paterno}' if comentario.emisor else 'Usuario desconocido'
                comentarios.append({
                    'id': comentario.id,
                    'contenido': comentario.contenido,
                    'imagen': comentario.imagen,
                    'fecha_creacion': comentario.fecha.strftime('%d/%m/%Y %H:%M'),
                    'emisor_nombre': emisor_nombre,
                    'emisor_id': comentario.emisor_id,
                    'es_propietario': comentario.emisor_id == ticket.usuario_id
                })
                print(f"Comentario procesado: {comentario.id}")
            except Exception as e:
                print(f"Error procesando comentario {comentario.id}: {e}")
                continue
        
        # Paso 4: Obtener evidencias
        evidencias = []
        if ticket.evidencia_1:
            evidencias.append(ticket.evidencia_1)
        if ticket.evidencia_2:
            evidencias.append(ticket.evidencia_2)
        if ticket.evidencia_3:
            evidencias.append(ticket.evidencia_3)
        if ticket.archivo and ticket.archivo not in evidencias:
            evidencias.append(ticket.archivo)
        
        # Paso 5: Obtener nombre de usuario
        try:
            usuario_nombre = f'{ticket.usuario.nombre} {ticket.usuario.apellido_paterno}' if ticket.usuario else 'Usuario desconocido'
        except Exception as e:
            print(f"Error obteniendo nombre de usuario: {e}")
            usuario_nombre = 'Usuario desconocido'
        
        # Paso 6: Datos del ticket
        ticket_data = {
            'id': ticket.id,
            'titulo': ticket.titulo or '',
            'descripcion': ticket.descripcion or '',
            'categoria': ticket.categoria or '',
            'area': ticket.area or '',
            'estatus': ticket.estatus or 'Abierto',
            'prioridad': ticket.prioridad or 'Media',
            'archivo': ticket.archivo or '',
            'evidencias': evidencias,
            'fecha_creacion': ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M') if ticket.fecha_creacion else '',
            'fecha_actualizacion': ticket.fecha_actualizacion.strftime('%d/%m/%Y %H:%M') if ticket.fecha_actualizacion else ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M') if ticket.fecha_creacion else '',
            'usuario_nombre': usuario_nombre,
            'usuario_id': ticket.usuario_id,
            'comentarios': comentarios,
            'es_propietario': es_propietario,
            'puede_editar': True  # Para pruebas
        }
        
        print(f"Datos básicos preparados exitosamente")
        print(f"Enviando respuesta...")
        return jsonify({'success': True, 'ticket': ticket_data})
        
    except Exception as e:
        print(f"ERROR EN OBTENER_DETALLES_TICKET:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
