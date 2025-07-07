from datetime import datetime
from app import db
from flask_login import UserMixin
from app.auth.models import User


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.String(20), nullable=False)  # Baja, Media, Alta, Urgente
    estatus = db.Column(db.String(20), default='Abierto')  # Abierto, En progreso, Resuelto
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    archivo = db.Column(db.String(255))  # Ruta al archivo

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = db.relationship(User, backref='tickets_creados')

    comentarios = db.relationship('ComentarioTicket', backref='ticket', cascade='all, delete-orphan')
    aprobacion = db.relationship('AprobacionTicket', uselist=False, backref='ticket')


class ComentarioTicket(db.Model):
    __tablename__ = 'comentarios_ticket'

    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(255))
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    emisor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)

    emisor = db.relationship(User, backref='comentarios_tickets')


class AprobacionTicket(db.Model):
    __tablename__ = 'aprobaciones_ticket'

    id = db.Column(db.Integer, primary_key=True)
    estatus = db.Column(db.String(20), default='Pendiente')  # Pendiente, Aprobado, Rechazado
    observaciones = db.Column(db.Text)
    fecha_revision = db.Column(db.DateTime)

    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    aprobador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    aprobador = db.relationship(User, backref='aprobaciones_realizadas')
