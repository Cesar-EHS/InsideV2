from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import url_for

class User(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    inscripciones = db.relationship('Inscripcion', back_populates='usuario')

    id = db.Column(db.Integer, primary_key=True)
    estatus_id = db.Column(db.Integer, db.ForeignKey('estatus_usuarios.id'), nullable=False)
    estatus = db.relationship('EstatusUsuario', backref='usuarios')

    foto = db.Column(db.String(255), nullable=True)  # Aquí puedes guardar la ruta o nombre del archivo

    nombre = db.Column(db.String(50), nullable=False)
    apellido_paterno = db.Column(db.String(50), nullable=False)
    apellido_materno = db.Column(db.String(50), nullable=True)

    curp = db.Column(db.String(18), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    departamento_id = db.Column(db.Integer, db.ForeignKey('departamentos.id'), nullable=True)
    departamento = db.relationship('Departamento', backref='usuarios')

    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyectos.id'), nullable=True)
    proyecto = db.relationship('Proyecto', backref='usuarios')

    puesto_trabajo_id = db.Column(db.Integer, db.ForeignKey('puestos_trabajo.id'), nullable=True)
    puesto_trabajo = db.relationship('PuestoTrabajo', backref='usuarios')

    jefe_inmediato_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    jefe_inmediato = db.relationship('User', remote_side=[id], backref='subordinados')

    ocupacion_especifica_id = db.Column(db.Integer, db.ForeignKey('ocupaciones.id'), nullable=True)
    ocupacion_especifica = db.relationship('Ocupacion', backref='usuarios')

    institucion_educativa_id = db.Column(db.Integer, db.ForeignKey('instituciones_educativas.id'), nullable=True)
    institucion_educativa = db.relationship('InstitucionEducativa', backref='usuarios')

    nivel_max_estudios_id = db.Column(db.Integer, db.ForeignKey('niveles_estudios.id'), nullable=True)
    nivel_max_estudios = db.relationship('NivelEstudio', backref='usuarios')

    documento_probatorio_id = db.Column(db.Integer, db.ForeignKey('documentos_probatorios.id'), nullable=True)
    documento_probatorio = db.relationship('DocumentoProbatorio', backref='usuarios')

    entidad_federativa_id = db.Column(db.Integer, db.ForeignKey('entidades_federativas.id'), nullable=True)
    entidad_federativa = db.relationship('EntidadFederativa', backref='usuarios')

    municipio_id = db.Column(db.Integer, db.ForeignKey('municipios.id'), nullable=True)
    municipio = db.relationship('Municipio', backref='usuarios')

    fecha_ingreso = db.Column(db.Date, nullable=True)

    password_hash = db.Column(db.String(128), nullable=False)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email} - {self.nombre} {self.apellido_paterno}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    @property 
    def foto_url(self):
        if self.foto:
            return url_for('auth.static', filename='fotos/' + self.foto)
        return url_for('auth.static', filename='fotos/default.jpg')

# Tablas auxiliares para catálogos

class EstatusUsuario(db.Model):
    __tablename__ = 'estatus_usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), unique=True, nullable=False)  # Ejemplo: Activo, Suspendido


class Departamento(db.Model):
    __tablename__ = 'departamentos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class Proyecto(db.Model):
    __tablename__ = 'proyectos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class PuestoTrabajo(db.Model):
    __tablename__ = 'puestos_trabajo'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class Ocupacion(db.Model):
    __tablename__ = 'ocupaciones'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class InstitucionEducativa(db.Model):
    __tablename__ = 'instituciones_educativas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)


class NivelEstudio(db.Model):
    __tablename__ = 'niveles_estudios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class DocumentoProbatorio(db.Model):
    __tablename__ = 'documentos_probatorios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class EntidadFederativa(db.Model):
    __tablename__ = 'entidades_federativas'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)


class Municipio(db.Model):
    __tablename__ = 'municipios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), unique=True, nullable=False)
    entidad_federativa_id = db.Column(db.Integer, db.ForeignKey('entidades_federativas.id'))
    entidad_federativa = db.relationship('EntidadFederativa', backref='municipios')
