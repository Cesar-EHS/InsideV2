from datetime import datetime
from flask_login import UserMixin
from app.auth.models import User
from app import db

class Logro(db.Model):
    __tablename__ = 'logros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(255), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=True)

    creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    creador = db.relationship(User, backref=db.backref('logros_creados', lazy='dynamic'))
    evidencias = db.relationship('EvidenciaLogro', backref='logro', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def fecha_vencida(self):
        if self.fecha_fin:
            return self.fecha_fin < datetime.utcnow().date()
        return False


class EvidenciaLogro(db.Model):
    __tablename__ = 'evidencias_logro'

    id = db.Column(db.Integer, primary_key=True)
    archivo = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    estatus = db.Column(db.String(20), default='Pendiente')  # Valores: Pendiente, Aprobado, Denegado

    logro_id = db.Column(db.Integer, db.ForeignKey('logros.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)

    usuario = db.relationship(User, backref=db.backref('evidencias_logro', lazy='dynamic'))
