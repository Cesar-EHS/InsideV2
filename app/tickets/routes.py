from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
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

# Mapeo de puestos a categorías (debe coincidir con frontend)
CATEGORIAS = {
    10: 'Soporte Sistemas',
    3: 'Requisición Compras',
    24: 'Desarrollo Organizacional',
    7: 'Capacitación Técnica',
    9: 'Diseño Institucional',
    2: 'Recursos Humanos',
    6: 'Soporte EHSmart'
}

@bp_tickets.route('/')
@login_required
def index():
    form = TicketForm()
    id_puesto = current_user.puesto_trabajo_id
    categoria = CATEGORIAS.get(id_puesto)
    tickets_usuario = Ticket.query.filter_by(usuario_id=current_user.id).all()
    tickets_gestion = Ticket.query.filter_by(categoria=categoria).all() if categoria else []
    return render_template(
        'helpdesk.html',
        tickets_usuario=tickets_usuario,
        tickets_gestion=tickets_gestion,
        form=form,
        es_encargado=bool(tickets_gestion),
        categorias_encargadas=CATEGORIAS
    )

@bp_tickets.route('/nuevo', methods=['POST'])
@login_required
def nuevo_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        archivo_nombre = None
        if form.archivo.data and getattr(form.archivo.data, 'filename', None):
            archivo = form.archivo.data
            if archivo.filename:
                archivo_nombre = secure_filename(archivo.filename)
                ruta_archivo = os.path.join(current_app.config['UPLOAD_FOLDER'], archivo_nombre)
                archivo.save(ruta_archivo)
        nuevo = Ticket(
            categoria=form.categoria.data,
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            prioridad=form.prioridad.data,
            usuario_id=current_user.id,
            archivo=archivo_nombre
        )
        db.session.add(nuevo)
        db.session.commit()
        if nuevo.categoria == 'Requisición Compras':
            aprobacion = AprobacionTicket(ticket_id=nuevo.id)
            db.session.add(aprobacion)
            db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Datos inválidos'}), 400

@bp_tickets.route('/archivo/<filename>')
@login_required
def descargar_archivo(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp_tickets.route('/detalle/<int:ticket_id>')
@login_required
def detalle_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    id_puesto = current_user.puesto_trabajo_id
    # Permiso: dueño o encargado de la categoría
    if ticket.usuario_id != current_user.id and CATEGORIAS.get(id_puesto) != ticket.categoria:
        return jsonify({'error': 'No autorizado'}), 403
    comentarios_data = [
        {
            'contenido': c.contenido,
            'imagen': c.imagen,
            'fecha': c.fecha.strftime('%d/%m/%Y %H:%M'),
            'emisor': f'{c.emisor.nombre} {c.emisor.apellido_paterno}'
        } for c in ticket.comentarios
    ]
    data = {
        'id': ticket.id,
        'titulo': ticket.titulo,
        'descripcion': ticket.descripcion,
        'prioridad': ticket.prioridad,
        'estatus': ticket.estatus,
        'fecha': ticket.fecha_creacion.strftime('%d/%m/%Y'),
        'archivo': ticket.archivo or '',
        'comentarios': comentarios_data,
        'categoria': ticket.categoria
    }
    return jsonify(data)

@bp_tickets.route('/estatus/<int:ticket_id>', methods=['POST'])
@login_required
def cambiar_estatus(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    id_puesto = current_user.puesto_trabajo_id
    if CATEGORIAS.get(id_puesto) != ticket.categoria:
        return jsonify({'error': 'No autorizado'}), 403
    # Soportar JSON y form-data
    if request.is_json:
        estatus_nuevo = request.json.get('estatus')
    else:
        estatus_nuevo = request.form.get('estatus')
    if estatus_nuevo not in ['Abierto', 'En progreso', 'Resuelto']:
        return jsonify({'error': 'Estatus inválido'}), 400
    ticket.estatus = estatus_nuevo
    db.session.commit()
    return jsonify({'success': True})

@bp_tickets.route('/comentar/<int:ticket_id>', methods=['POST'])
@login_required
def comentar_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.estatus == 'Resuelto':
        return jsonify({'error': 'Ticket cerrado para comentarios'}), 403
    contenido = request.form.get('contenido', '').strip()
    if not contenido:
        return jsonify({'error': 'El contenido es obligatorio'}), 400
    imagen_nombre = None
    if 'imagen' in request.files and getattr(request.files['imagen'], 'filename', None):
        imagen = request.files['imagen']
        if imagen.filename:
            imagen_nombre = secure_filename(imagen.filename)
            ruta_imagen = os.path.join(current_app.config['UPLOAD_FOLDER'], imagen_nombre)
            imagen.save(ruta_imagen)
    nuevo_comentario = ComentarioTicket(
        contenido=contenido,
        imagen=imagen_nombre,
        emisor_id=current_user.id,
        ticket_id=ticket.id
    )
    db.session.add(nuevo_comentario)
    db.session.commit()
    return jsonify({
        'success': True,
        'comentario': {
            'contenido': nuevo_comentario.contenido,
            'imagen': nuevo_comentario.imagen,
            'fecha': nuevo_comentario.fecha.strftime('%d/%m/%Y %H:%M'),
            'emisor': f'{current_user.nombre} {current_user.apellido_paterno}'
        }
    })

@bp_tickets.route('/download/<int:ticket_id>')
@login_required
def download_attachment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not ticket.archivo:
        return 'Archivo no encontrado', 404
    # Usa la misma carpeta de uploads que el resto del sistema
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], ticket.archivo, as_attachment=True)
