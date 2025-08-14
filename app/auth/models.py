from __future__ import annotations
from datetime import datetime
from typing import Optional, Any, cast, TypeVar, Type
from flask_login import UserMixin
from app import db
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.exc import OperationalError
import time
import random

# Definir un tipo para el modelo base
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

def db_retry_operation(operation, max_retries=5, base_delay=0.1):
    """
    Ejecuta una operación de base de datos con retry logic robusto.
    
    Args:
        operation: Función a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Delay base en segundos
    
    Returns:
        Resultado de la operación
    
    Raises:
        OperationalError: Si todos los reintentos fallan
    """
    for attempt in range(max_retries):
        try:
            return operation()
        except OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                # Exponential backoff con jitter
                delay = base_delay * (2 ** attempt) + random.uniform(0, 0.1)
                print(f"Database locked, intento {attempt + 1}/{max_retries}, esperando {delay:.2f}s...")
                time.sleep(delay)
                
                # Rollback para limpiar la sesión
                try:
                    db.session.rollback()
                except:
                    pass
            else:
                raise e
    
    raise OperationalError("Database locked después de todos los intentos", None, None)  # type: ignore

# Base model para todos los modelos
class BaseModel(db.Model):  # type: ignore[misc,valid-type]
    """Clase base abstracta para todos los modelos."""
    __abstract__ = True
    __allow_unmapped__ = True

# Base model with common attributes
class TimestampMixin:
    """Adds timestamp fields to a model."""
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class EstatusUsuario(BaseModel):
    """Model for user status."""
    __tablename__ = 'estatus_usuarios'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    es_activo = db.Column(db.Boolean, default=True)

class Departamento(BaseModel):
    """Model for departments."""
    __tablename__ = 'departamentos'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True, nullable=False)

class Proyecto(BaseModel):
    """Model for projects."""
    __tablename__ = 'proyectos'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

class PuestoTrabajo(BaseModel):
    """Model for job positions."""
    __tablename__ = 'puestos_trabajo'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

class Ocupacion(BaseModel):
    """Model for occupations."""
    __tablename__ = 'ocupaciones'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

class InstitucionEducativa(BaseModel):
    """Model for educational institutions."""
    __tablename__ = 'instituciones_educativas'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

class NivelEstudio(BaseModel):
    """Model for education levels."""
    __tablename__ = 'niveles_estudio'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

class DocumentoProbatorio(BaseModel):
    """Model for supporting documents."""
    __tablename__ = 'documentos_probatorios'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

class EntidadFederativa(BaseModel):
    """Model for federal entities."""
    __tablename__ = 'entidades_federativas'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(200))

class Municipio(BaseModel):
    """Model for municipalities."""
    __tablename__ = 'municipios'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    entidad_federativa_id = db.Column(db.Integer, db.ForeignKey('entidades_federativas.id'), nullable=False)
    entidad_federativa = db.relationship('EntidadFederativa', backref='municipios')

class User(BaseModel, UserMixin, TimestampMixin):
    """User model with enhanced security features."""
    __tablename__ = 'usuarios'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50))
    curp = db.Column(db.String(18), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    password_hash = db.Column(db.String(256))
    foto = db.Column(db.String(255))
    fecha_ingreso = db.Column(db.Date)
    rol = db.Column(db.String(50), default='usuario')
    activo = db.Column(db.Boolean, default=True)
    
    # Foreign Keys
    estatus_id = db.Column(db.Integer, db.ForeignKey('estatus_usuarios.id'), nullable=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'))
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'))
    puesto_trabajo_id = db.Column(db.Integer, db.ForeignKey('puestos_trabajo.id'))
    jefe_inmediato_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    ocupacion_especifica_id = db.Column(db.Integer, db.ForeignKey('ocupaciones.id'))
    institucion_educativa_id = db.Column(db.Integer, db.ForeignKey('instituciones_educativas.id'))
    nivel_max_estudios_id = db.Column(db.Integer, db.ForeignKey('niveles_estudio.id'))
    documento_probatorio_id = db.Column(db.Integer, db.ForeignKey('documentos_probatorios.id'))
    entidad_federativa_id = db.Column(db.Integer, db.ForeignKey('entidades_federativas.id'))
    municipio_id = db.Column(db.Integer, db.ForeignKey('municipios.id'))
    
    # Security fields
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime(timezone=True))
    locked_until = db.Column(db.DateTime(timezone=True))
    last_login = db.Column(db.DateTime(timezone=True))
    
    # Relationships
    estatus = db.relationship('EstatusUsuario', backref='usuarios')
    departamento = db.relationship('Departamento', backref='usuarios')
    proyecto = db.relationship('Proyecto', backref='usuarios')
    puesto_trabajo = db.relationship('PuestoTrabajo', backref='usuarios')
    jefe_inmediato = db.relationship('User', remote_side=[id], backref='subordinados', foreign_keys=[jefe_inmediato_id])
    ocupacion_especifica = db.relationship('Ocupacion', backref='usuarios')
    institucion_educativa = db.relationship('InstitucionEducativa', backref='usuarios')
    nivel_max_estudios = db.relationship('NivelEstudio', backref='usuarios')
    documento_probatorio = db.relationship('DocumentoProbatorio', backref='usuarios')
    entidad_federativa = db.relationship('EntidadFederativa', backref='usuarios')
    municipio = db.relationship('Municipio', backref='usuarios')
    inscripciones = db.relationship('Inscripcion', back_populates='usuario')

    # Password management methods
    def set_password(self, password):
        """Set the password hash for the user."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
        
    def increment_failed_logins(self):
        """Increment the failed login attempts counter."""
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        self.last_failed_login = datetime.utcnow()
        db.session.commit()

    def reset_failed_logins(self):
        """Reset the failed login attempts counter and related fields."""
        self.failed_login_attempts = 0
        self.last_failed_login = None
        self.locked_until = None
        db.session.commit()

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

    @property
    def foto_url(self):
        """Get the user photo URL or default image."""
        from flask import url_for, has_request_context
        try:
            if self.foto:
                if has_request_context():
                    return url_for('auth.serve_foto', filename=self.foto)
                else:
                    # Construir URL manualmente cuando no hay contexto de petición
                    return f'/auth/static/fotos/{self.foto}'
            
            if has_request_context():
                return url_for('static', filename='default_user.png')
            else:
                return '/static/default_user.png'
        except Exception:
            # Fallback en caso de cualquier error
            return '/static/default_user.png'

    @property
    def nombre_completo(self):
        """Get the full name of the user."""
        return f"{self.nombre} {self.apellido_paterno}"

    # Security tables relationships
    historial_cambios = db.relationship('UserHistoryChange', 
                                       foreign_keys='[UserHistoryChange.user_id]',
                                       backref='usuario', 
                                       lazy='dynamic')
    cambios_realizados = db.relationship('UserHistoryChange', 
                                       foreign_keys='[UserHistoryChange.changed_by_id]',
                                       backref='changed_by_usuario',
                                       lazy='dynamic')

class TokenBlacklist(BaseModel):
    """Model for storing blacklisted tokens."""
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(20), nullable=False)

class UserHistoryChange(BaseModel):
    """Model for tracking changes in user profiles."""
    __tablename__ = 'historial_cambios_usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    field_name = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(500))
    new_value = db.Column(db.String(500))
    changed_by_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    changed_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)


class Configuracion(BaseModel):
    """Model for system configuration."""
    __tablename__ = 'configuraciones'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), nullable=False, unique=True)
    valor = db.Column(db.Text)
    descripcion = db.Column(db.String(200))
    tipo = db.Column(db.String(50), default='string')  # string, file, json, etc.
    actualizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_actualizacion = db.Column(db.DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'clave': self.clave,
            'valor': self.valor,
            'descripcion': self.descripcion,
            'tipo': self.tipo,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    @classmethod
    def get_valor(cls, clave: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value by key."""
        config = cls.query.filter_by(clave=clave).first()
        return config.valor if config else default
    
    @classmethod
    def set_valor(cls, clave: str, valor: str, descripcion: str = '', tipo: str = 'string', usuario_id: Optional[int] = None):
        """Set configuration value with aggressive retry logic."""
        from app.database_manager import db_manager
        
        def _do_update():
            # Buscar configuración existente
            config = cls.query.filter_by(clave=clave).first()
            if config:
                config.valor = valor
                config.descripcion = descripcion
                config.tipo = tipo
                config.actualizado_por = usuario_id
                config.fecha_actualizacion = datetime.utcnow()
            else:
                config = cls(  # type: ignore
                    clave=clave,  # type: ignore
                    valor=valor,  # type: ignore
                    descripcion=descripcion,  # type: ignore
                    tipo=tipo,  # type: ignore
                    actualizado_por=usuario_id  # type: ignore
                )
                db.session.add(config)
            
            # Hacer commit inmediato
            db.session.commit()
            return config
        
        return db_manager.execute_with_retry(_do_update)


class PermisosGestion(BaseModel):
    """Model for management permissions."""
    __tablename__ = 'permisos_gestion'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    puesto_trabajo_id = db.Column(db.Integer, db.ForeignKey('puestos_trabajo.id'), nullable=False)
    puede_gestionar_usuarios = db.Column(db.Boolean, default=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    actualizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relación con PuestoTrabajo
    puesto = db.relationship('PuestoTrabajo', backref='permisos_gestion')
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'puesto_trabajo_id': self.puesto_trabajo_id,
            'puesto_nombre': self.puesto.nombre if self.puesto else None,
            'puede_gestionar_usuarios': self.puede_gestionar_usuarios,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }


class PermisosTickets(BaseModel):
    """Model for tickets permissions by department."""
    __tablename__ = 'permisos_tickets'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    actualizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    usuario = db.relationship('User', foreign_keys=[usuario_id], backref='permisos_tickets_asignados')
    departamento = db.relationship('Departamento', backref='permisos_asignados')
    actualizado_por_usuario = db.relationship('User', foreign_keys=[actualizado_por])
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario_nombre': f"{self.usuario.nombre} {self.usuario.apellido_paterno}" if self.usuario else None,
            'departamento_id': self.departamento_id,
            'departamento_nombre': self.departamento.nombre if self.departamento else None,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }


class PermisosHome(BaseModel):
    """Model for home permissions."""
    __tablename__ = 'permisos_home'
    __allow_unmapped__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_permiso = db.Column(db.String(50), nullable=False)  # crear_posts, crear_eventos, moderar_contenido
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    actualizado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con User
    usuario = db.relationship('User', foreign_keys=[usuario_id], backref='permisos_home_asignados')
    actualizado_por_usuario = db.relationship('User', foreign_keys=[actualizado_por])
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'tipo_permiso': self.tipo_permiso,
            'usuario_id': self.usuario_id,
            'usuario_nombre': f"{self.usuario.nombre} {self.usuario.apellido_paterno}" if self.usuario else None,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        }
