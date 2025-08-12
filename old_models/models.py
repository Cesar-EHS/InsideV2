from __future__ import annotations
from typing import Optional, Any, cast
from datetime import datetime
import pytz
from flask import url_for
from flask_login import UserMixin  # type: ignore
# Ignorar advertencias de tipos para las funciones de werkzeug
from werkzeug.security import generate_password_hash as _generate_password_hash  # type: ignore
from werkzeug.security import check_password_hash as _check_password_hash  # type: ignore
from app import db

class User(db.Model, UserMixin):  # type: ignore[misc]
    __tablename__ = 'usuarios'
    __allow_unmapped__ = True
    
    # Campos para control de acceso
    failed_login_attempts: int = db.Column(db.Integer, default=0)  # type: ignore
    last_failed_login: Optional[datetime] = db.Column(db.DateTime(timezone=True))  # type: ignore
    locked_until: Optional[datetime] = db.Column(db.DateTime(timezone=True))  # type: ignore
    last_login: Optional[datetime] = db.Column(db.DateTime(timezone=True))  # type: ignore
    inscripciones: Any = db.relationship('Inscripcion', back_populates='usuario')  # type: ignore

    id: int = db.Column(db.Integer, primary_key=True)  # type: ignore
    estatus_id: int = db.Column(db.Integer, db.ForeignKey('estatus_usuarios.id'), nullable=False)  # type: ignore
    estatus = db.relationship('EstatusUsuario', backref='usuarios')  # type: ignore

    foto: Optional[str] = db.Column(db.String(255), nullable=True)  # type: ignore

    nombre: str = db.Column(db.String(50), nullable=False)  # type: ignore
    apellido_paterno: str = db.Column(db.String(50), nullable=False)  # type: ignore
    apellido_materno: Optional[str] = db.Column(db.String(50), nullable=True)  # type: ignore

    curp: str = db.Column(db.String(18), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)

    departamento_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=True)
    departamento: Optional[Departamento] = db.relationship('Departamento', backref='usuarios')

    proyecto_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=True)
    proyecto: Optional[Proyecto] = db.relationship('Proyecto', backref='usuarios')

    puesto_trabajo_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('puestos_trabajo.id'), nullable=True)
    puesto_trabajo: Optional[PuestoTrabajo] = db.relationship('PuestoTrabajo', backref='usuarios')

    jefe_inmediato_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    jefe_inmediato: Optional[User] = db.relationship('User', remote_side=[id], backref='subordinados')

    ocupacion_especifica_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('ocupaciones.id'), nullable=True)
    ocupacion_especifica: Optional[Ocupacion] = db.relationship('Ocupacion', backref='usuarios')

    institucion_educativa_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('instituciones_educativas.id'), nullable=True)
    institucion_educativa: Optional[InstitucionEducativa] = db.relationship('InstitucionEducativa', backref='usuarios')

    nivel_max_estudios_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('niveles_estudios.id'), nullable=True)
    nivel_max_estudios: Optional[NivelEstudio] = db.relationship('NivelEstudio', backref='usuarios')

    documento_probatorio_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('documentos_probatorios.id'), nullable=True)
    documento_probatorio: Optional[DocumentoProbatorio] = db.relationship('DocumentoProbatorio', backref='usuarios')

    entidad_federativa_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('entidades_federativas.id'), nullable=True)
    entidad_federativa: Optional[EntidadFederativa] = db.relationship('EntidadFederativa', backref='usuarios')

    municipio_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('municipios.id'), nullable=True)
    municipio: Optional[Municipio] = db.relationship('Municipio', backref='usuarios')

    fecha_ingreso: Optional[datetime] = db.Column(db.Date, nullable=True)

    password_hash = db.Column(db.String(128), nullable=False)

    fecha_creacion = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    fecha_actualizacion = db.Column(
        db.DateTime(timezone=True), 
        default=lambda: datetime.now(pytz.UTC),
        onupdate=lambda: datetime.now(pytz.UTC)
    )

    def __repr__(self) -> str:
        return f'<User {self.email} - {self.nombre} {self.apellido_paterno}>'

    def set_password(self, password: str) -> None:
        self.password_hash = cast(str, _generate_password_hash(password))

    def check_password(self, password: str) -> bool:
        return cast(bool, _check_password_hash(cast(str, self.password_hash), password))
    
    @property 
    def foto_url(self) -> str:
        if self.foto:
            return url_for('auth.static', filename='fotos/' + self.foto)
        return url_for('auth.static', filename='fotos/default.jpg')

# Tablas auxiliares para catálogos

class EstatusUsuario(db.Model):  # type: ignore[misc]
    __tablename__ = 'estatus_usuarios'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(20), unique=True, nullable=False)  # Ejemplo: Activo, Suspendido


class Departamento(db.Model):  # type: ignore[misc]
    __tablename__ = 'departamentos'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), unique=True, nullable=False)


class Proyecto(db.Model):  # type: ignore[misc]
    __tablename__ = 'proyectos'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), unique=True, nullable=False)


class PuestoTrabajo(db.Model):  # type: ignore[misc]
    __tablename__ = 'puestos_trabajo'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), unique=True, nullable=False)


class Ocupacion(db.Model):  # type: ignore[misc]
    __tablename__ = 'ocupaciones'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), unique=True, nullable=False)


class InstitucionEducativa(db.Model):  # type: ignore[misc]
    __tablename__ = 'instituciones_educativas'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(150), unique=True, nullable=False)


class NivelEstudio(db.Model):  # type: ignore[misc]
    __tablename__ = 'niveles_estudios'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), unique=True, nullable=False)


class DocumentoProbatorio(db.Model):  # type: ignore[misc]
    __tablename__ = 'documentos_probatorios'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), unique=True, nullable=False)


class EntidadFederativa(db.Model):  # type: ignore[misc]
    __tablename__ = 'entidades_federativas'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(100), unique=True, nullable=False)


class Municipio(db.Model):  # type: ignore[misc]
    __tablename__ = 'municipios'
    __allow_unmapped__ = True

    id: int = db.Column(db.Integer, primary_key=True)
    nombre: str = db.Column(db.String(150), unique=True, nullable=False)
    entidad_federativa_id: int = db.Column(db.Integer, db.ForeignKey('entidades_federativas.id'))
    entidad_federativa: EntidadFederativa = db.relationship('EntidadFederativa', backref='municipios')
