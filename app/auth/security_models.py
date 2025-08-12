from datetime import datetime
from typing import Optional, Any
from flask_login import UserMixin
from app import db
from werkzeug.security import check_password_hash, generate_password_hash

# Base model with common attributes
class TimestampMixin:
    """Adds timestamp fields to a model."""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(db.Model, UserMixin, TimestampMixin):  # type: ignore
    """User model with enhanced security features."""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50))
    curp = db.Column(db.String(18), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    foto = db.Column(db.String(100))
    fecha_ingreso = db.Column(db.Date)
    
    # Foreign Keys
    estatus_id = db.Column(db.Integer, db.ForeignKey('estatus_usuario.id'), nullable=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'))
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'))
    puesto_trabajo_id = db.Column(db.Integer, db.ForeignKey('puesto_trabajo.id'))
    jefe_inmediato_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    ocupacion_especifica_id = db.Column(db.Integer, db.ForeignKey('ocupacion.id'))
    institucion_educativa_id = db.Column(db.Integer, db.ForeignKey('institucion_educativa.id'))
    nivel_max_estudios_id = db.Column(db.Integer, db.ForeignKey('nivel_estudio.id'))
    documento_probatorio_id = db.Column(db.Integer, db.ForeignKey('documento_probatorio.id'))
    entidad_federativa_id = db.Column(db.Integer, db.ForeignKey('entidad_federativa.id'))
    municipio_id = db.Column(db.Integer, db.ForeignKey('municipio.id'))
    
    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime)
    locked_until = db.Column(db.DateTime)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    estatus = db.relationship('EstatusUsuario', backref='usuarios')
    departamento = db.relationship('Departamento', backref='usuarios')
    proyecto = db.relationship('Proyecto', backref='usuarios')
    puesto_trabajo = db.relationship('PuestoTrabajo', backref='usuarios')
    jefe_inmediato = db.relationship('User', remote_side=[id], backref='subordinados')
    ocupacion = db.relationship('Ocupacion', backref='usuarios')
    institucion_educativa = db.relationship('InstitucionEducativa', backref='usuarios')
    nivel_max_estudios = db.relationship('NivelEstudio', backref='usuarios')
    documento_probatorio = db.relationship('DocumentoProbatorio', backref='usuarios')
    entidad_federativa = db.relationship('EntidadFederativa', backref='usuarios')
    municipio = db.relationship('Municipio', backref='usuarios')

    # Security tables relationships
    history_changes = db.relationship('UserHistoryChange', backref='usuario', lazy='dynamic')
    changes_made = db.relationship('UserHistoryChange', 
                                 backref='changed_by_usuario',
                                 lazy='dynamic',
                                 foreign_keys='UserHistoryChange.changed_by_id')

class TokenBlacklist(db.Model):  # type: ignore
    """Model for storing blacklisted tokens."""
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(20), nullable=False)

class UserHistoryChange(db.Model):  # type: ignore
    """Model for tracking changes in user profiles."""
    __tablename__ = 'user_history_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(500))
    new_value = db.Column(db.String(500))
    changed_by_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)
