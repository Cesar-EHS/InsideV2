from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory, url_for
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import joinedload
from app.tickets.models import Ticket, ComentarioTicket, AprobacionTicket, CategoriaTicket
from app.tickets.forms import TicketForm, EditTicketForm
from app.auth.models import User, Departamento, PermisosTickets
from app import db

bp_tickets = Blueprint(
    'tickets',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/tickets/static'
)

def puede_administrar_departamento(usuario_id, departamento_id):
    """Verificar si un usuario puede administrar tickets de un departamento específico"""
    # Verificar si es administrador general
    usuario = User.query.get(usuario_id)
    if usuario and hasattr(usuario, 'rol') and usuario.rol in ['admin', 'Administrador']:
        return True
    
    # Verificar permisos específicos de departamento
    permiso = PermisosTickets.query.filter_by(
        usuario_id=usuario_id,
        departamento_id=departamento_id,
        activo=True
    ).first()
    
    return permiso is not None

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
            'timestamp': str(datetime.now())
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
            joinedload(Ticket.usuario),  # type: ignore
            joinedload(Ticket.comentarios).joinedload(ComentarioTicket.emisor)  # type: ignore
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

def obtener_categorias_disponibles(tab, departamentos_ids, user_tickets_categorias=None):
    """Obtener las categorías disponibles según el contexto"""
    if tab == 'mis_tickets':
        # En mis tickets: todas las categorías de los tickets levantados por el usuario
        if user_tickets_categorias:
            return user_tickets_categorias
        else:
            # Si no hay tickets, mostrar todas las categorías
            todas_categorias = db.session.query(CategoriaTicket.nombre).all()
            return sorted([cat.nombre for cat in todas_categorias])
    elif tab == 'asignados':
        # En tickets asignados: solo categorías de los departamentos gestionados
        if departamentos_ids:
            categorias = db.session.query(CategoriaTicket.nombre).filter(
                CategoriaTicket.departamento_id.in_(departamentos_ids)
            ).all()
            return [cat.nombre for cat in categorias]
        else:
            return []
    elif tab == 'archivados':
        # En archivados: categorías según el contexto (todas para usuarios, de departamentos para gestores)
        if departamentos_ids:
            categorias = db.session.query(CategoriaTicket.nombre).filter(
                CategoriaTicket.departamento_id.in_(departamentos_ids)
            ).all()
            return [cat.nombre for cat in categorias]
        else:
            if user_tickets_categorias:
                return user_tickets_categorias
            else:
                todas_categorias = db.session.query(CategoriaTicket.nombre).all()
                return sorted([cat.nombre for cat in todas_categorias])
    
    return []

@bp_tickets.route('/')
@login_required
def index():
    form = TicketForm()
    
    # Verificar si el usuario tiene permisos para gestionar departamentos
    departamentos_gestionados = db.session.query(PermisosTickets).filter_by(
        usuario_id=current_user.id,
        activo=True
    ).all()
    
    # El usuario es gestor si tiene al menos un departamento asignado
    es_gestor = len(departamentos_gestionados) > 0
    departamentos_ids = [p.departamento_id for p in departamentos_gestionados]
    
    # Parámetros de filtrado y paginación
    page = request.args.get('page', 1, type=int)
    tab = request.args.get('tab', 'mis_tickets')  # Por defecto "Mis Tickets"
    orden = request.args.get('orden', 'reciente')  # reciente, antiguo, alfabetico
    categoria_filtro = request.args.get('categoria', '')
    busqueda = request.args.get('busqueda', '')
    per_page = 10
    
    if tab == 'asignados' and es_gestor:
        # Tickets asignados - solo para gestores de departamento (excluyendo archivados)
        query = Ticket.query.filter(
            Ticket.departamento_id.in_(departamentos_ids),
            Ticket.estatus != 'Archivado'
        )
        
        # Aplicar filtros
        if categoria_filtro:
            query = query.join(CategoriaTicket, Ticket.categoria_id == CategoriaTicket.id).filter(
                CategoriaTicket.nombre == categoria_filtro
            )
        
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
        # Tickets archivados - todos los usuarios pueden ver sus propios archivados, gestores ven los de sus departamentos
        if es_gestor:
            query = Ticket.query.filter(
                or_(
                    Ticket.usuario_id == current_user.id,  # Sus propios tickets
                    Ticket.departamento_id.in_(departamentos_ids)  # Tickets de departamentos que gestiona
                ),
                Ticket.estatus == 'Archivado'
            )
        else:
            query = Ticket.query.filter(
                Ticket.usuario_id == current_user.id,
                Ticket.estatus == 'Archivado'
            )
        
        # Aplicar filtros para archivados
        if categoria_filtro:
            query = query.join(CategoriaTicket, Ticket.categoria_id == CategoriaTicket.id).filter(
                CategoriaTicket.nombre == categoria_filtro
            )
        
        if busqueda:
            if es_gestor:
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
            query = query.join(CategoriaTicket, Ticket.categoria_id == CategoriaTicket.id).filter(
                CategoriaTicket.nombre == categoria_filtro
            )
        
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
    if tab == 'mis_tickets' or (tab == 'archivados' and not es_gestor):
        user_categorias_query = db.session.query(CategoriaTicket.nombre).join(
            Ticket, Ticket.categoria_id == CategoriaTicket.id
        ).filter(
            Ticket.usuario_id == current_user.id
        ).distinct()
        user_tickets_categorias = [cat[0] for cat in user_categorias_query.all() if cat[0]]
    
    # Obtener categorías disponibles según el contexto
    categorias_disponibles = obtener_categorias_disponibles(tab, departamentos_ids, user_tickets_categorias)
    
    return render_template(
        'helpdesk.html',
        tickets=tickets,
        pagination=pagination,
        form=form,
        es_administrador=es_gestor,
        area_admin=departamentos_ids,
        categorias_disponibles=categorias_disponibles,
        tab_actual=tab,
        orden_actual=orden,
        categoria_filtro=categoria_filtro,
        buscar_actual=busqueda,
        # Variables adicionales para mantener filtros en paginación
        orden=orden,
        categoria_seleccionada=categoria_filtro,
        busqueda=busqueda,
        now=datetime.now,
        csrf_token=generate_csrf
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
        
        print(f"Ticket encontrado: ID={ticket.id}, Categoría={ticket.categoria_obj.nombre if ticket.categoria_obj else 'Sin categoría'}")
        
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
        
        # Verificar permisos usando el nuevo sistema de PermisosTickets - SOLO gestores y administradores
        permisos = PermisosTickets.query.filter_by(usuario_id=current_user.id).all()
        departamentos_gestionados = [p.departamento_id for p in permisos]
        
        print(f"Usuario ID: {current_user.id}")
        print(f"Departamentos gestionados: {departamentos_gestionados}")
        print(f"Ticket departamento: {ticket.departamento.nombre if ticket.departamento else 'Sin departamento'}")
        
        # Verificar si puede administrar este ticket - SOLO gestores de departamento o administradores
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        es_gestor_departamento = ticket.departamento_id in departamentos_gestionados
        
        if not (es_administrador or es_gestor_departamento):
            print(f"ERROR: Sin permisos para administrar ticket del departamento {ticket.departamento_id}")
            return jsonify({'success': False, 'message': 'Solo los gestores del departamento pueden modificar el estatus del ticket'}), 403
        
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
        comentario_reporte = ComentarioTicket(  # type: ignore
            contenido=f"🚨 Ticket reportado por {current_user.nombre} {current_user.apellido_paterno}",  # type: ignore
            emisor_id=current_user.id,  # type: ignore
            ticket_id=ticket.id  # type: ignore
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
        
        # Crear el ticket con los nuevos campos
        nuevo = Ticket(  # type: ignore
            departamento_id=form.departamento_id.data,  # type: ignore
            categoria_id=form.categoria_id.data,  # type: ignore
            titulo=form.titulo.data,  # type: ignore
            descripcion=form.descripcion.data,  # type: ignore
            prioridad=form.prioridad.data,  # type: ignore
            usuario_id=current_user.id,  # type: ignore
            archivo=archivo_nombre,  # type: ignore
            evidencia_1=evidencias.get('evidencia_1'),  # type: ignore
            evidencia_2=evidencias.get('evidencia_2'),  # type: ignore
            evidencia_3=evidencias.get('evidencia_3')  # type: ignore
        )
        
        db.session.add(nuevo)
        db.session.commit()
        
        # Crear aprobación si es categoría específica (mantener lógica existente adaptada)
        # Nota: Esta lógica se puede adaptar según las nuevas categorías
        if nuevo.categoria_id:  # Se puede especificar la lógica según ID de categoría
            pass  # Agregar lógica específica según necesidades
            
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
    
    # Verificar permisos usando el nuevo sistema
    permisos = PermisosTickets.query.filter_by(usuario_id=current_user.id).all()
    departamentos_gestionados = [p.departamento_id for p in permisos]
    
    # Permiso: dueño, administrador o gestor del departamento
    puede_ver = (
        ticket.usuario_id == current_user.id or
        (hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']) or
        ticket.departamento_id in departamentos_gestionados
    )
    
    if not puede_ver:
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
        'area': ticket.departamento.nombre if ticket.departamento else '',
        'titulo': ticket.titulo,
        'descripcion': ticket.descripcion,
        'prioridad': ticket.prioridad,
        'estatus': ticket.estatus,
        'fecha': ticket.fecha_creacion.strftime('%d/%m/%Y'),
        'archivo': ticket.archivo or '',  # Mantener para compatibilidad
        'evidencias': evidencias,  # Nueva lista de evidencias
        'comentarios': comentarios_data,
        'categoria': ticket.categoria_obj.nombre if ticket.categoria_obj else '',
        'area': ticket.departamento.nombre if ticket.departamento else ''
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
        
        nuevo_comentario = ComentarioTicket(  # type: ignore
            contenido=contenido,  # type: ignore
            imagen=imagen_nombre,  # type: ignore
            emisor_id=current_user.id,  # type: ignore
            ticket_id=ticket.id  # type: ignore
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
            joinedload(Ticket.usuario),  # type: ignore
            joinedload(Ticket.comentarios).joinedload(ComentarioTicket.emisor)  # type: ignore
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
                
                # Obtener foto del emisor usando la misma lógica que en home
                emisor_foto = '/static/default_user.png'  # Valor por defecto
                if comentario.emisor and hasattr(comentario.emisor, 'foto_url'):
                    try:
                        emisor_foto = comentario.emisor.foto_url
                    except Exception:
                        emisor_foto = '/static/default_user.png'
                
                comentarios.append({
                    'id': comentario.id,
                    'contenido': comentario.contenido,
                    'imagen': comentario.imagen,
                    'fecha': comentario.fecha.strftime('%d/%m/%Y %H:%M'),
                    'emisor_nombre': emisor_nombre,
                    'emisor_id': comentario.emisor_id,
                    'emisor_foto': emisor_foto,
                    'es_propietario': comentario.emisor_id == ticket.usuario_id
                })
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
        
        # Verificar permisos para cambiar estatus - SOLO gestores de departamento y administradores
        es_administrador_local = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        
        # Verificar permisos usando el nuevo sistema de departamentos
        puede_administrar_dept = puede_administrar_departamento(current_user.id, ticket.departamento_id) if ticket.departamento_id else False
        
        # SOLO gestores de departamento o administradores pueden cambiar estatus (NO el propietario)
        puede_cambiar_estatus = es_administrador_local or puede_administrar_dept
        
        # Determinar si es gestor de categoría (usando el sistema de departamentos)
        es_gestor_categoria = puede_administrar_dept
        
        # Paso 7: Datos del ticket
        ticket_data = {
            'id': ticket.id,
            'titulo': ticket.titulo or '',
            'descripcion': ticket.descripcion or '',
            'categoria': ticket.categoria_obj.nombre if ticket.categoria_obj else '',
            'departamento': ticket.departamento.nombre if ticket.departamento else '',
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
            'puede_editar': True,  # Para pruebas
            'puede_cambiar_estatus': puede_cambiar_estatus,
            'es_gestor_categoria': es_gestor_categoria
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


@bp_tickets.route('/api/cambiar-estatus/<int:ticket_id>', methods=['POST'])
@login_required
def cambiar_estatus_ticket(ticket_id):
    """Cambiar el estatus de un ticket"""
    try:
        print(f"=== CAMBIAR_ESTATUS_TICKET ===")
        print(f"Ticket ID: {ticket_id}")
        print(f"Usuario actual: {current_user.id}")
        
        # Verificar que se reciban datos JSON
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type debe ser application/json'}), 400
        
        data = request.get_json()
        nuevo_estatus = data.get('estatus')
        
        # Validar el estatus
        estatuses_validos = ['Abierto', 'En progreso', 'Resuelto', 'Cerrado']
        if nuevo_estatus not in estatuses_validos:
            return jsonify({'success': False, 'error': 'Estatus no válido'}), 400
        
        # Buscar el ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({'success': False, 'error': 'Ticket no encontrado'}), 404
        
        # Verificar permisos - SOLO gestores de departamento y administradores
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        
        # Verificar si es gestor del departamento usando PermisosTickets
        permisos = PermisosTickets.query.filter_by(usuario_id=current_user.id).all()
        departamentos_gestionados = [p.departamento_id for p in permisos]
        es_gestor_departamento = ticket.departamento_id in departamentos_gestionados
        
        # SOLO gestores de departamento o administradores pueden cambiar el estatus
        if not (es_administrador or es_gestor_departamento):
            return jsonify({'success': False, 'error': 'Solo los gestores del departamento pueden modificar el estatus del ticket'}), 403
        
        # Actualizar el estatus
        estatus_anterior = ticket.estatus
        ticket.estatus = nuevo_estatus
        ticket.fecha_actualizacion = datetime.now()
        
        db.session.commit()
        
        print(f"Estatus cambiado de '{estatus_anterior}' a '{nuevo_estatus}'")
        
        return jsonify({
            'success': True, 
            'message': 'Estatus actualizado correctamente',
            'ticket_id': ticket_id,
            'estatus_anterior': estatus_anterior,
            'estatus_nuevo': nuevo_estatus
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR EN CAMBIAR_ESTATUS_TICKET:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ====================
# RUTAS PARA VER Y EDITAR TICKETS
# ====================

@bp_tickets.route('/ver/<int:ticket_id>')
@login_required
def ver_ticket(ticket_id):
    """Ver detalles de un ticket"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Verificar permisos
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        
        # Verificar si es gestor del departamento
        permisos = PermisosTickets.query.filter_by(usuario_id=current_user.id).all()
        departamentos_gestionados = [p.departamento_id for p in permisos]
        es_gestor_departamento = ticket.departamento_id in departamentos_gestionados
        
        puede_ver = (ticket.usuario_id == current_user.id or es_administrador or es_gestor_departamento)
        
        if not puede_ver:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'No tienes permisos para ver este ticket'}), 403
            return render_template('error.html', mensaje="No tienes permisos para ver este ticket"), 403
            
        # Cargar comentarios
        comentarios = ComentarioTicket.query.filter_by(ticket_id=ticket_id)\
                                         .order_by(ComentarioTicket.fecha.asc()).all()
        
        # Preparar datos de comentarios
        comentarios_data = []
        for comentario in comentarios:
            usuario_comentario = User.query.get(comentario.emisor_id)
            # Usar la misma lógica que en home para obtener la foto
            if usuario_comentario and hasattr(usuario_comentario, 'foto_url') and usuario_comentario.foto_url:
                foto_url = usuario_comentario.foto_url
                print(f"Debug - Usuario {usuario_comentario.nombre} tiene foto: {usuario_comentario.foto}, URL generada: {foto_url}")
            else:
                foto_url = url_for('static', filename='default_user.png')
                if usuario_comentario:
                    print(f"Debug - Usuario {usuario_comentario.nombre} SIN foto válida. Foto field: {usuario_comentario.foto if hasattr(usuario_comentario, 'foto') else 'N/A'}")
                else:
                    print(f"Debug - Usuario no encontrado para comentario {comentario.id}")
            
            comentarios_data.append({
                'id': comentario.id,
                'contenido': comentario.contenido,
                'fecha': comentario.fecha.strftime('%d/%m/%Y %H:%M'),  # Usar mismo formato que home
                'emisor_id': comentario.emisor_id,
                'emisor_nombre': f"{usuario_comentario.nombre} {usuario_comentario.apellido_paterno}" if usuario_comentario else "Usuario Desconocido",
                'emisor_foto': foto_url,
                'es_mio': comentario.emisor_id == current_user.id
            })
        
        # Preparar evidencias
        evidencias = []
        for i in range(1, 4):
            evidencia = getattr(ticket, f'evidencia_{i}', None)
            if evidencia:
                evidencias.append({
                    'nombre': evidencia,
                    'url': f"/tickets/uploads/{evidencia}"
                })
        
        # Devolver datos JSON para el modal integrado
        return jsonify({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'titulo': ticket.titulo,
                'descripcion': ticket.descripcion,
                'area': ticket.departamento.nombre if ticket.departamento else '',
                'categoria': ticket.categoria_obj.nombre if ticket.categoria_obj else '',
                'prioridad': ticket.prioridad,
                'estatus': ticket.estatus,
                'fecha_creacion': ticket.fecha_creacion.isoformat() if ticket.fecha_creacion else None,
                'fecha_actualizacion': ticket.fecha_actualizacion.isoformat() if ticket.fecha_actualizacion else None,
                'nombre_solicitante': ticket.usuario.nombre + ' ' + ticket.usuario.apellido_paterno if ticket.usuario else 'N/A'
            },
            'comentarios': comentarios_data,
            'evidencias': evidencias,
            'es_administrador': es_administrador or es_gestor_departamento
        })
                             
    except Exception as e:
        print(f"Error al ver ticket {ticket_id}: {e}")
        return render_template('error.html', mensaje="Error al cargar el ticket"), 500


@bp_tickets.route('/editar/<int:ticket_id>')
@login_required
def editar_ticket(ticket_id):
    """Mostrar formulario para editar ticket"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Verificar permisos
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        
        # Verificar si es gestor del departamento
        permisos = PermisosTickets.query.filter_by(usuario_id=current_user.id).all()
        departamentos_gestionados = [p.departamento_id for p in permisos]
        es_gestor_departamento = ticket.departamento_id in departamentos_gestionados
        
        puede_editar = (ticket.usuario_id == current_user.id or es_administrador or es_gestor_departamento)
        
        if not puede_editar:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'No tienes permisos para editar este ticket'}), 403
            return render_template('error.html', mensaje="No tienes permisos para editar este ticket"), 403
            
        # No permitir editar tickets archivados
        if hasattr(ticket, 'archivado') and ticket.archivado:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'error': 'No se pueden editar tickets archivados'}), 403
            return render_template('error.html', mensaje="No se pueden editar tickets archivados"), 403
        
        # Devolver datos JSON para el modal integrado
        return jsonify({
            'success': True,
            'ticket': {
                'id': ticket.id,
                'titulo': ticket.titulo,
                'descripcion': ticket.descripcion,
                'area': ticket.departamento.nombre if ticket.departamento else '',
                'categoria': ticket.categoria_obj.nombre if ticket.categoria_obj else '',
                'prioridad': ticket.prioridad,
                'estatus': ticket.estatus,
                'fecha_creacion': ticket.fecha_creacion.isoformat() if ticket.fecha_creacion else None,
                'evidencia_1': ticket.evidencia_1,
                'evidencia_2': ticket.evidencia_2,
                'evidencia_3': ticket.evidencia_3
            },
            'es_administrador': es_administrador
        })
                             
    except Exception as e:
        print(f"Error al cargar formulario de edición para ticket {ticket_id}: {e}")
        return render_template('error.html', mensaje="Error al cargar el formulario de edición"), 500


@bp_tickets.route('/actualizar/<int:ticket_id>', methods=['POST'])
@login_required
def actualizar_ticket(ticket_id):
    """Actualizar un ticket existente"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Verificar permisos
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        puede_editar = (ticket.usuario_id == current_user.id or es_administrador)
        
        if not puede_editar:
            return jsonify({'success': False, 'error': 'No tienes permisos para editar este ticket'}), 403
            
        # No permitir editar tickets archivados
        if hasattr(ticket, 'archivado') and ticket.archivado:
            return jsonify({'success': False, 'error': 'No se pueden editar tickets archivados'}), 403
        
        # Actualizar campos básicos
        if 'titulo' in request.form:
            ticket.titulo = request.form['titulo']
        if 'descripcion' in request.form:
            ticket.descripcion = request.form['descripcion']
        if 'departamento_id' in request.form:
            ticket.departamento_id = int(request.form['departamento_id'])
        if 'categoria_id' in request.form:
            ticket.categoria_id = int(request.form['categoria_id'])
        if 'prioridad' in request.form:
            ticket.prioridad = request.form['prioridad']
            
        # Solo administradores pueden cambiar el estatus
        if es_administrador and 'estatus' in request.form:
            ticket.estatus = request.form['estatus']
        
        # Actualizar fecha de modificación
        ticket.fecha_actualizacion = datetime.now()
        
        # Manejar nuevas evidencias si se suben
        for i in range(1, 4):
            campo_nueva_evidencia = f'nueva_evidencia_{i}'
            if campo_nueva_evidencia in request.files:
                archivo = request.files[campo_nueva_evidencia]
                if archivo and archivo.filename:
                    archivo_nombre = secure_filename(archivo.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    archivo_nombre = f"{timestamp}{archivo_nombre}"
                    
                    ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo_nombre)
                    archivo.save(ruta_archivo)
                    
                    # Encontrar el primer slot vacío para la evidencia
                    for j in range(1, 4):
                        if getattr(ticket, f'evidencia_{j}', None) is None:
                            setattr(ticket, f'evidencia_{j}', archivo_nombre)
                            break
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Ticket actualizado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al actualizar ticket {ticket_id}: {e}")
        return jsonify({'success': False, 'error': 'Error al actualizar el ticket'}), 500


@bp_tickets.route('/archivar/<int:ticket_id>', methods=['POST'])
@login_required
def archivar_ticket(ticket_id):
    """Archivar un ticket (solo el creador del ticket)"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Solo el creador del ticket puede archivarlo
        if ticket.usuario_id != current_user.id:
            return jsonify({'success': False, 'error': 'Solo el creador del ticket puede archivarlo'}), 403
        
        # Solo se pueden archivar tickets resueltos o cerrados
        if ticket.estatus not in ['Resuelto', 'Cerrado']:
            return jsonify({'success': False, 'error': 'Solo se pueden archivar tickets resueltos o cerrados'}), 400
        
        # Cambiar estatus a 'Archivado'
        ticket.estatus = 'Archivado'
        ticket.fecha_actualizacion = datetime.now()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Ticket archivado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al archivar ticket {ticket_id}: {e}")
        return jsonify({'success': False, 'error': 'Error al archivar el ticket'}), 500


@bp_tickets.route('/uploads/<filename>')
@login_required
def uploads(filename):
    """Servir archivos de evidencia"""
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return "Archivo no encontrado", 404


@bp_tickets.route('/eliminar-evidencia/<int:ticket_id>/<int:numero>', methods=['POST'])
@login_required
def eliminar_evidencia(ticket_id, numero):
    """Eliminar una evidencia específica de un ticket"""
    try:
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # Verificar permisos
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        puede_editar = (ticket.usuario_id == current_user.id or es_administrador)
        
        if not puede_editar:
            return jsonify({'success': False, 'error': 'No tienes permisos para editar este ticket'}), 403
            
        # No permitir editar tickets archivados
        if hasattr(ticket, 'archivado') and ticket.archivado:
            return jsonify({'success': False, 'error': 'No se pueden editar tickets archivados'}), 403
        
        # Validar número de evidencia
        if numero not in [1, 2, 3]:
            return jsonify({'success': False, 'error': 'Número de evidencia inválido'}), 400
        
        # Obtener la evidencia actual
        evidencia_campo = f'evidencia_{numero}'
        evidencia_actual = getattr(ticket, evidencia_campo, None)
        
        if not evidencia_actual:
            return jsonify({'success': False, 'error': 'No hay evidencia en esta posición'}), 400
        
        # Intentar eliminar el archivo físico
        try:
            ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], evidencia_actual)
            if os.path.exists(ruta_archivo):
                os.remove(ruta_archivo)
        except Exception as e:
            print(f"Error al eliminar archivo físico: {e}")
            # No fallar la operación si no se puede eliminar el archivo físico
        
        # Limpiar el campo en la base de datos
        setattr(ticket, evidencia_campo, None)
        ticket.fecha_actualizacion = datetime.now()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Evidencia {numero} eliminada correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar evidencia {numero} del ticket {ticket_id}: {e}")
        return jsonify({'success': False, 'error': 'Error al eliminar la evidencia'}), 500


@bp_tickets.route('/cambiar-estado/<int:ticket_id>', methods=['POST'])
@login_required
def cambiar_estado_ticket(ticket_id):
    """Cambiar el estado de un ticket (solo administradores)"""
    try:
        # Verificar permisos de administrador
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        if not es_administrador:
            return jsonify({'success': False, 'error': 'Solo los administradores pueden cambiar el estado'}), 403
            
        ticket = Ticket.query.get_or_404(ticket_id)
        
        # No permitir cambiar estado de tickets archivados
        if hasattr(ticket, 'archivado') and ticket.archivado:
            return jsonify({'success': False, 'error': 'No se puede cambiar el estado de tickets archivados'}), 403
        
        nuevo_estado = request.form.get('estado', '').strip()
        
        if not nuevo_estado:
            return jsonify({'success': False, 'error': 'El estado es obligatorio'}), 400
        
        estados_validos = ['Abierto', 'En Progreso', 'Resuelto', 'Cerrado']
        if nuevo_estado not in estados_validos:
            return jsonify({'success': False, 'error': 'Estado no válido'}), 400
        
        estado_anterior = ticket.estatus
        ticket.estatus = nuevo_estado
        ticket.fecha_actualizacion = datetime.now()
        
        # Agregar comentario automático del cambio de estado
        comentario_estado = ComentarioTicket(  # type: ignore
            contenido=f"Estado cambiado de '{estado_anterior}' a '{nuevo_estado}'",  # type: ignore
            emisor_id=current_user.id,  # type: ignore
            ticket_id=ticket_id  # type: ignore
        )
        
        db.session.add(comentario_estado)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Estado cambiado a {nuevo_estado}',
            'nuevo_estado': nuevo_estado
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al cambiar estado del ticket {ticket_id}: {e}")
        return jsonify({'success': False, 'error': 'Error al cambiar el estado'}), 500


@bp_tickets.route('/test-simple', methods=['POST', 'GET'])
def test_simple():
    """Endpoint de prueba muy simple"""
    print("=== TEST SIMPLE ENDPOINT ===")
    return jsonify({'success': True, 'message': 'Test endpoint working'})


@bp_tickets.route('/comentario-nuevo/<int:ticket_id>', methods=['POST'])
@login_required  
def comentario_nuevo(ticket_id):
    """Endpoint para comentarios de tickets - VERSIÓN FINAL"""
    print(f"\n=== COMENTARIO_NUEVO FINAL ===")
    print(f"¡ENDPOINT EJECUTÁNDOSE!")
    print(f"Ticket ID: {ticket_id}")
    print(f"Usuario: {current_user.id}")
    print(f"Request form: {dict(request.form)}")
    
    try:
        contenido = request.form.get('contenido')
        print(f"Contenido: '{contenido}'")
        
        if not contenido or not contenido.strip():
            return jsonify({"success": False, "message": "Contenido vacío"}), 400
        
        # Verificar ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return jsonify({"success": False, "message": "Ticket no encontrado"}), 404
        
        # Crear comentario
        comentario = ComentarioTicket()
        comentario.contenido = contenido.strip()
        comentario.ticket_id = ticket_id
        comentario.emisor_id = current_user.id
        
        db.session.add(comentario)
        db.session.commit()
        
        print("¡COMENTARIO GUARDADO!")
        
        return jsonify({
            "success": True,
            "message": "Comentario agregado exitosamente",
            "comentario": {
                "id": comentario.id,
                "contenido": comentario.contenido,
                "fecha": comentario.fecha.strftime('%d/%m/%Y %H:%M'),  # Usar mismo formato que home
                "emisor_id": comentario.emisor_id,
                "emisor_nombre": f"{current_user.nombre} {current_user.apellido_paterno}",
                "emisor_foto": getattr(current_user, 'foto_url', url_for('static', filename='default_user.png'))
            }
        }), 201
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500


@bp_tickets.route('/api/comentario/<int:ticket_id>', methods=['POST'])
@login_required
def agregar_comentario(ticket_id):
    """Agregar un comentario a un ticket"""
    try:
        print(f"=== AGREGAR_COMENTARIO ===")
        print(f"Ticket ID: {ticket_id}")
        print(f"Usuario actual: {current_user.id}")
        print(f"Request method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Request data: {request.data}")
        
        # Verificar si el request tiene JSON
        if not request.is_json:
            print("ERROR: Request no es JSON")
            return jsonify({'success': False, 'error': 'Content-Type debe ser application/json'}), 400
        
        # Obtener el ticket
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            print("ERROR: Ticket no encontrado")
            return jsonify({'success': False, 'error': 'Ticket no encontrado'}), 404
        
        print(f"Ticket encontrado: {ticket.id} - {ticket.titulo}")
        
        # Obtener datos del request
        try:
            data = request.get_json()
            print(f"Datos JSON parseados: {data}")
        except Exception as e:
            print(f"ERROR parseando JSON: {e}")
            return jsonify({'success': False, 'error': 'Error al parsear JSON'}), 400
        
        if not data:
            print("ERROR: No se recibieron datos JSON")
            return jsonify({'success': False, 'error': 'No se recibieron datos'}), 400
            
        contenido = data.get('contenido', '').strip() if data else ''
        print(f"Contenido: '{contenido}'")
        
        if not contenido:
            print("ERROR: Contenido vacío")
            return jsonify({'success': False, 'error': 'El contenido del comentario es requerido'}), 400
        
        # Crear el comentario
        nuevo_comentario = ComentarioTicket()
        nuevo_comentario.contenido = contenido
        nuevo_comentario.emisor_id = current_user.id
        nuevo_comentario.ticket_id = ticket_id
        
        print(f"Creando comentario: {contenido}")
        
        # Actualizar fecha de actualización del ticket
        ticket.fecha_actualizacion = datetime.utcnow()
        
        # Guardar en base de datos
        db.session.add(nuevo_comentario)
        db.session.commit()
        
        print(f"Comentario guardado exitosamente con ID: {nuevo_comentario.id}")
        
        return jsonify({
            'success': True,
            'message': 'Comentario agregado correctamente',
            'comentario': {
                'id': nuevo_comentario.id,
                'contenido': nuevo_comentario.contenido,
                'fecha_creacion': nuevo_comentario.fecha.strftime('%d/%m/%Y %H:%M'),
                'emisor_nombre': f'{current_user.nombre} {current_user.apellido_paterno}',
                'emisor_id': current_user.id,
                'es_propietario': current_user.id == ticket.usuario_id
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"ERROR AL AGREGAR COMENTARIO:")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Error al agregar el comentario'}), 500


@bp_tickets.route('/api/categorias/<int:departamento_id>')
@login_required
def api_categorias_by_departamento(departamento_id):
    """Obtener categorías de tickets filtradas por departamento"""
    try:
        # Por ahora devolver todas las categorías activas
        # En el futuro se puede implementar filtrado por departamento
        categorias = CategoriaTicket.query.filter_by(activo=True).order_by(CategoriaTicket.nombre).all()
        
        categorias_data = [
            {
                'id': cat.id,
                'nombre': cat.nombre,
                'descripcion': cat.descripcion
            }
            for cat in categorias
        ]
        
        return jsonify({
            'success': True,
            'categorias': categorias_data
        })
        
    except Exception as e:
        print(f"Error en api_categorias_by_departamento: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener categorías'}), 500


@bp_tickets.route('/api/departamentos')
@login_required
def api_departamentos_tickets():
    """Obtener departamentos activos para tickets"""
    try:
        # Obtener todos los departamentos y filtrar por activo si existe el campo
        departamentos = Departamento.query.order_by(Departamento.nombre).all()
        departamentos_activos = [d for d in departamentos if getattr(d, 'activo', True)]
        
        departamentos_data = [
            {
                'id': dept.id,
                'nombre': dept.nombre,
                'descripcion': dept.descripcion
            }
            for dept in departamentos_activos
        ]
        
        return jsonify({
            'success': True,
            'departamentos': departamentos_data
        })
        
    except Exception as e:
        print(f"Error en api_departamentos_tickets: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener departamentos'}), 500
