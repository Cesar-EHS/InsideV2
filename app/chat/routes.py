from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Conversation, Message

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/list_users')
@login_required
def list_users():
    # Lista usuarios activos o con conversación
    users = User.query.filter(User.id != current_user.id).all()
    # Puedes filtrar por departamento, etc.
    data = [
        {
            'id': u.id,
            'nombre': f"{u.nombre} {u.apellido_paterno}",
            'foto': u.foto,
            'departamento': u.departamento.nombre if u.departamento else ''
        } for u in users
    ]
    return jsonify(data)

@chat_bp.route('/conversation/<int:user_id>')
@login_required
def get_conversation(user_id):
    # Busca o crea la conversación
    convo = Conversation.query.filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == user_id)) |
        ((Conversation.user2_id == current_user.id) & (Conversation.user1_id == user_id))
    ).first()
    if not convo:
        convo = Conversation(user1_id=current_user.id, user2_id=user_id)
        db.session.add(convo)
        db.session.commit()
    messages = Message.query.filter_by(conversation_id=convo.id).order_by(Message.timestamp.asc()).all()
    data = [
        {
            'id': m.id,
            'sender_id': m.sender_id,
            'content': m.content,
            'file_url': m.file_url,
            'timestamp': m.timestamp.strftime('%H:%M'),
            'is_read': m.is_read
        } for m in messages
    ]
    return jsonify({'conversation_id': convo.id, 'messages': data})

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    convo_id = request.form.get('conversation_id')
    content = request.form.get('message')
    file_url = request.form.get('file_url')
    convo = Conversation.query.get(convo_id)
    if not convo:
        return jsonify({'error': 'Conversación no encontrada'}), 404
    msg = Message(conversation_id=convo.id, sender_id=current_user.id, content=content, file_url=file_url)
    db.session.add(msg)
    db.session.commit()
    return jsonify({'status': 'ok', 'message_id': msg.id})
