from datetime import datetime
from app.auth.models import User
from app import db

class Curso(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)  # Relación con Categoría
    categoria = db.relationship('Categoria', back_populates='cursos')
    modalidad = db.Column(db.String(20), nullable=False)  # Presencial, En línea, Mixta
    objetivo = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    area_tematica = db.Column(db.String(100), nullable=False)
    duracion = db.Column(db.String(50), nullable=False)
    tipo_agente = db.Column(db.String(50), nullable=False)  # Interno, Externo, Otro
    creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    imagen = db.Column(db.String(255), nullable=True)  # Ruta de la imagen del curso

    inscripciones = db.relationship('Inscripcion', back_populates='curso', cascade='all, delete-orphan')
    examenes = db.relationship('Examen', back_populates='curso', cascade='all, delete-orphan')
    actividades = db.relationship('Actividad', back_populates='curso', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Curso {self.nombre}>'


class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    avance = db.Column(db.Float, default=0.0)  # porcentaje de avance: 0 a 100
    activo = db.Column(db.Boolean, default=True)  # controla si está inscrito actualmente

    curso = db.relationship('Curso', back_populates='inscripciones')
    usuario = db.relationship(User, back_populates='inscripciones')

    # Registra resultados de examenes y actividades
    examenes_realizados = db.relationship('ExamenResultado', back_populates='inscripcion', cascade='all, delete-orphan')
    actividades_realizadas = db.relationship('ActividadResultado', back_populates='inscripcion', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Inscripcion usuario {self.usuario_id} curso {self.curso_id}>'


class Examen(db.Model):
    __tablename__ = 'examenes'

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    curso = db.relationship('Curso', back_populates='examenes')
    preguntas = db.relationship('Pregunta', back_populates='examen', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Examen {self.titulo} curso {self.curso_id}>'


class Pregunta(db.Model):
    __tablename__ = 'preguntas'

    id = db.Column(db.Integer, primary_key=True)
    examen_id = db.Column(db.Integer, db.ForeignKey('examenes.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # Ejemplo: 'opcion_multiple', 'verdadero_falso', 'abierta'
    opciones = db.Column(db.Text, nullable=True)  # JSON string con opciones para opción múltiple
    respuesta_correcta = db.Column(db.Text, nullable=True)  # Respuesta correcta o clave para comparar

    examen = db.relationship('Examen', back_populates='preguntas')

    def __repr__(self):
        return f'<Pregunta {self.id} examen {self.examen_id}>'


class ExamenResultado(db.Model):
    __tablename__ = 'examen_resultados'

    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey('inscripciones.id'), nullable=False)
    examen_id = db.Column(db.Integer, db.ForeignKey('examenes.id'), nullable=False)
    calificacion = db.Column(db.Float, nullable=True)
    fecha_realizado = db.Column(db.DateTime, default=datetime.utcnow)

    inscripcion = db.relationship('Inscripcion', back_populates='examenes_realizados')
    examen = db.relationship('Examen')

    def __repr__(self):
        return f'<ExamenResultado examen {self.examen_id} inscripcion {self.inscripcion_id}>'


class Actividad(db.Model):
    __tablename__ = 'actividades'

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    video_url = db.Column(db.String(255), nullable=True)  # Nuevo campo para URL de video
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    curso = db.relationship('Curso', back_populates='actividades')

    def __repr__(self):
        return f'<Actividad {self.titulo} curso {self.curso_id}>'


class ActividadResultado(db.Model):
    __tablename__ = 'actividad_resultados'

    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey('inscripciones.id'), nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    entregado = db.Column(db.Boolean, default=False)
    fecha_entregado = db.Column(db.DateTime, nullable=True)
    calificacion = db.Column(db.Float, nullable=True)
    retroalimentacion = db.Column(db.Text, nullable=True)

    inscripcion = db.relationship('Inscripcion', back_populates='actividades_realizadas')
    actividad = db.relationship('Actividad')

    def __repr__(self):
        return f'<ActividadResultado actividad {self.actividad_id} inscripcion {self.inscripcion_id}>'


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

    cursos = db.relationship('Curso', back_populates='categoria')

    def __repr__(self):
        return f'<Categoria {self.nombre}>'
