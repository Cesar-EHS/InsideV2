from flask import Blueprint, request, render_template, jsonify, url_for, current_app
from app.home.models import Post, Evento
from app.knowledge.models import Documento
from app.tickets.models import Ticket
from sqlalchemy import or_

search_bp = Blueprint('search', __name__, url_prefix='/buscar')

@search_bp.route('/')
def search():
    return render_template('search_results.html')

@search_bp.route('/api')
def search_api():
    term = request.args.get('q', '').strip()
    if not term:
        return jsonify({
            'publicaciones': [],
            'eventos': [],
            'documentos': [],
            'tickets': []
        })
    publicaciones = Post.query.filter(
        Post.content.ilike(f"%{term}%")
    ).all()
    eventos = Evento.query.filter(
        Evento.titulo.ilike(f"%{term}%")
    ).all()
    documentos = Documento.query.filter(
        or_(
            Documento.nombre.ilike(f"%{term}%"),
            Documento.tipo.ilike(f"%{term}%")
        )
    ).all()
    tickets = Ticket.query.filter(
        or_(
            Ticket.titulo.ilike(f"%{term}%"),
            Ticket.descripcion.ilike(f"%{term}%")
        )
    ).all()
    def user_avatar(user, size=8):
        if user and getattr(user, 'foto', None):
            return url_for('auth.static', filename=f'fotos/{user.foto}')
        return url_for('static', filename='default_user.png')
    return jsonify({
        'publicaciones': [
            {
                'user_nombre': pub.user.nombre if pub.user else 'Desconocido',
                'user_avatar': user_avatar(pub.user),
                'timestamp': pub.timestamp.strftime('%d/%m/%Y %H:%M') if pub.timestamp else 'Fecha no disponible',
                'content': (pub.content[:200] + ('...' if len(pub.content) > 200 else '')) if pub.content else '',
                'image_filename': pub.image_filename,
                'image_url': url_for('static', filename=f'uploads/{pub.image_filename}') if pub.image_filename else None
            } for pub in publicaciones
        ],
        'eventos': [
            {
                'titulo': ev.titulo,
                'descripcion': (ev.descripcion[:180] + ('...' if len(ev.descripcion) > 180 else '')) if ev.descripcion else '',
                'fecha': ev.fecha.strftime('%d/%m/%Y') if ev.fecha else 'No definida',
                'hora': ev.hora.strftime('%H:%M') if ev.hora else 'No definida',
                'link_teams': ev.link_teams,
                'created_at': ev.created_at.strftime('%d/%m/%Y %H:%M') if ev.created_at else ''
            } for ev in eventos
        ],
        'documentos': [
            {
                'nombre': doc.nombre,
                'tipo': doc.tipo,
                'categoria': doc.categoria,
                'fecha_carga': doc.fecha_carga.strftime('%d/%m/%Y') if doc.fecha_carga else '',
                'archivo': doc.archivo,
                'archivo_url': url_for('static', filename=f'uploads/{doc.archivo}') if doc.archivo else None
            } for doc in documentos
        ],
        'tickets': [
            {
                'user_nombre': ticket.usuario.nombre if getattr(ticket, 'usuario', None) else 'Desconocido',
                'user_avatar': user_avatar(getattr(ticket, 'usuario', None), 7),
                'fecha_creacion': ticket.fecha_creacion.strftime('%d/%m/%Y %H:%M') if ticket.fecha_creacion else 'No disponible',
                'titulo': ticket.titulo,
                'descripcion': (ticket.descripcion[:120] + ('...' if len(ticket.descripcion) > 120 else '')) if ticket.descripcion else '',
                'prioridad': ticket.prioridad,
                'estatus': ticket.estatus,
                'categoria': ticket.categoria,
                'archivo_url': url_for('tickets.download_attachment', ticket_id=ticket.id) if ticket.archivo else None
            } for ticket in tickets
        ]
    })