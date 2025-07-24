from datetime import datetime
from app import db
from flask_login import UserMixin
from app.auth.models import User


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=True)  # Nuevo campo área
    categoria = db.Column(db.String(100), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    prioridad = db.Column(db.String(20), nullable=False)  # Baja, Media, Alta, Urgente
    estatus = db.Column(db.String(20), default='Abierto')  # Abierto, En progreso, Resuelto, Cerrado, Archivado
    reportado = db.Column(db.Boolean, default=False)  # Para marcar tickets reportados
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Archivos múltiples
    archivo = db.Column(db.String(255))  # Mantener para compatibilidad
    evidencia_1 = db.Column(db.String(255))  # Primera evidencia
    evidencia_2 = db.Column(db.String(255))  # Segunda evidencia
    evidencia_3 = db.Column(db.String(255))  # Tercera evidencia

    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario = db.relationship(User, backref='tickets_creados')

    comentarios = db.relationship('ComentarioTicket', backref='ticket', cascade='all, delete-orphan')
    aprobacion = db.relationship('AprobacionTicket', uselist=False, backref='ticket')

    def __repr__(self):
        return f'<Ticket {self.id}: {self.titulo}>'
    
    @property
    def nombre_solicitante(self):
        """Devuelve el nombre completo del solicitante"""
        if self.usuario:
            return f"{self.usuario.nombre} {self.usuario.apellido_paterno}"
        return "Usuario no encontrado"
    
    @property
    def evidencias(self):
        """Devuelve una lista de todas las evidencias no vacías"""
        evidencias = []
        for campo in [self.evidencia_1, self.evidencia_2, self.evidencia_3]:
            if campo:
                evidencias.append(campo)
        # Incluir archivo si existe para compatibilidad
        if self.archivo:
            evidencias.append(self.archivo)
        return evidencias


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
