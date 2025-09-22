from datetime import datetime, timezone
from typing import List
from app.auth.models import User
from app import db

class Curso(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    creador_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    modalidad_id = db.Column(db.Integer, db.ForeignKey('modalidades.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias_cursos.id'), nullable=False)
    objetivo_id = db.Column(db.Integer, db.ForeignKey('objetivos.id'), nullable=False)
    area_tematica_id = db.Column(db.Integer, db.ForeignKey('areas_tematicas_cursos.id'), nullable=False)
    tipo_agente_id = db.Column(db.Integer, db.ForeignKey('tipos_agente.id'), nullable=False)
    duracion = db.Column(db.String(50), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    imagen = db.Column(db.String(255))
    estado = db.Column(db.String(50), default='Activo', nullable=True)  # Activo, Inactivo
    video_url = db.Column(db.String(255))
    eliminado = db.Column(db.Integer, default=0)  # 0 = no eliminado, 1 = eliminado

    #Relaciones de todas las tablas, relacion en cuanto a modelos ORM no de 
    modalidad = db.relationship('Modalidad', backref='cursos')
    objetivo = db.relationship('Objetivo', backref='cursos')
    area_tematica = db.relationship('AreaTematicaCurso', backref='cursos')
    tipo_agente = db.relationship('TipoAgente', backref='cursos')
    categoria = db.relationship('CategoriaCurso', backref='cursos')
    creador = db.relationship('User', backref='cursos')
    examenes = db.relationship('Examen', back_populates='curso', cascade='all, delete-orphan')
    inscripciones = db.relationship('Inscripcion', back_populates='curso', cascade='all, delete-orphan')
    archivos = db.relationship('Archivo', back_populates='curso', cascade='all, delete-orphan')

    #Relación para las secciones del curso.
    secciones = db.relationship('Seccion', back_populates='curso', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Curso {self.nombre}>'


class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    avance = db.Column(db.Float, default=0.0)  # porcentaje de avance: 0 a 100
    activo = db.Column(db.Boolean, default=True)  # controla si está inscrito actualmente
    fecha_ultimo_acceso = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=True)

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
    tipo_examen_id = db.Column(db.Integer, db.ForeignKey('tipos_examen.id'), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    fecha_inicio = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=True)
    fecha_cierre = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=True)
    duracion_minutos = db.Column(db.Integer, nullable=True)  # Duración en minutos
    intentos_permitidos = db.Column(db.Integer, default=3)  # Número de intentos permitidos

    curso = db.relationship('Curso', back_populates='examenes')
    preguntas = db.relationship('Pregunta', back_populates='examen', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Examen {self.titulo} curso {self.curso_id}>'
    
class TipoExamen(db.Model):
    __tablename__= 'tipos_examen'

    #Columnas
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return super().__repr__() + f'TipoExamen {self.nombre}'
    

class ExamenResultado(db.Model):
    __tablename__ = 'examenes_resultados'

    #Columnas
    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey('inscripciones.id'), nullable=False)
    examen_id = db.Column(db.Integer, db.ForeignKey('examenes.id'), nullable=False)
    
    numero_intento = db.Column(db.Integer, nullable=False, default=1)
    calificacion = db.Column(db.Float, nullable=True)
    fecha_realizado = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    inscripcion = db.relationship('Inscripcion', back_populates='examenes_realizados')
    examen = db.relationship('Examen')

    respuestas = db.relationship('ExamenRespuestaUsuario', back_populates='resultado', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ExamenResultado examen {self.examen_id} inscripcion {self.inscripcion_id}>'

class ExamenRespuestaUsuario(db.Model):
    __tablename__ = 'examenes_respuestas_usuarios'

    #Columnas
    id = db.Column(db.Integer, primary_key=True)
    examen_resultado_id = db.Column(db.Integer, db.ForeignKey('examenes_resultados.id'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas.id'), nullable=False)
    respuesta_texto = db.Column(db.Text, nullable=True)  # Respuesta del usuario
    pregunta_opcion_id = db.Column(db.Integer, db.ForeignKey('preguntas_opciones.id'), nullable=True)

    resultado = db.relationship('ExamenResultado', back_populates='respuestas')

    def __repr__(self):
        return super().__repr__() + f'ExamenRespuestaUsuario examen_resultado {self.examen_resultado_id} pregunta {self.pregunta_id}'


class Pregunta(db.Model):
    __tablename__ = 'preguntas'

    id = db.Column(db.Integer, primary_key=True)
    examen_id = db.Column(db.Integer, db.ForeignKey('examenes.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    tipo_pregunta = db.Column(db.Integer, db.ForeignKey('tipos_pregunta'), nullable=False)  # Ejemplo: 'opcion_multiple', 'verdadero_falso', 'abierta'

    #Relaciones bidireccionales entre modelos.
    examen = db.relationship('Examen', back_populates='preguntas')
    opciones = db.relationship('PreguntaOpcion', back_populates='pregunta', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pregunta {self.id} examen {self.examen_id}>'
    
class TipoPregunta(db.Model):
    __tablename__ = 'tipos_pregunta'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return super().__repr__() + f'TipoPregunta {self.nombre}'
    
class PreguntaImagen(db.Model):
    __tablename__ = 'preguntas_imagenes'

    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas.id'), nullable=False)
    ruta_imagen = db.Column(db.Text, nullable=False)  # Ruta de la imagen en el sistema
    descripcion = db.Column(db.Text, nullable=True)

    #Crea buna relacion directa, desde PreguntaImagen puedo acceder a la pregunta con .pregunta
    # y desde Pregunta puedo acceder a todas sus imagenes con .imagenes
    pregunta = db.relationship('Pregunta', backref='imagenes')

    def __repr__(self):
        return f'<PreguntaImagen {self.id} pregunta {self.pregunta_id}>'
    
class PreguntaOpcion(db.Model):
    __tablename__ = 'preguntas_opciones'

    id = db.Column(db.Integer, primary_key=True)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('preguntas.id'), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    es_correcta = db.Column(db.Boolean, default=False)

    pregunta = db.relationship('Pregunta', back_populates='opciones')

    def __repr__(self):
        return f'<PreguntaOpcion {self.texto} pregunta {self.pregunta_id}>'

class Seccion(db.Model):
    __tablename__ = 'secciones'

    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    orden = db.Column(db.Integer, nullable=False)  # Orden de la sección dentro del curso
    
    curso = db.relationship('Curso', back_populates='secciones')
    actividades = db.relationship('Actividad', back_populates='seccion', cascade='all, delete-orphan', order_by='Actividad.orden')

    def __repr__(self):
        return f'<Seccion {self.nombre} curso {self.curso_id}>'


class Actividad(db.Model):
    __tablename__ = 'actividades'

    id = db.Column(db.Integer, primary_key=True)
    seccion_id = db.Column(db.Integer, db.ForeignKey('secciones.id'), nullable=False)
    titulo = db.Column(db.String(150), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)
    fecha_entrega = db.Column(db.DateTime, nullable=True)
    tipo_actividad = db.Column(db.String(50), nullable=False) # 'video', 'documento', 'examen'
    orden = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'tipo': self.tipo_actividad
            # Añade cualquier otro campo que necesites en tu JavaScript
        }

    seccion = db.relationship('Seccion', back_populates='actividades')
    videos = db.relationship('ActividadVideo', back_populates='actividad', cascade='all, delete-orphan')
    documentos = db.relationship('ActividadDocumento', back_populates='actividad', cascade='all, delete-orphan')
    examenes = db.relationship('ActividadExamen', back_populates='actividad', cascade='all, delete-orphan')
    # Relación con los resultados de los usuarios
    resultados = db.relationship('ActividadResultado', back_populates='actividad', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Actividad {self.titulo} curso seccion {self.seccion_id}>'

class ActividadVideo(db.Model):
    __tablename__ = 'actividades_videos'
    id = db.Column(db.Integer, primary_key=True)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    actividad = db.relationship('Actividad', back_populates='videos')

class ActividadDocumento(db.Model):
    __tablename__ = 'actividades_documentos'
    id = db.Column(db.Integer, primary_key=True)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    nombre_documento = db.Column(db.String(255), nullable=False)
    ruta_documento = db.Column(db.String(255), nullable=False)  # Ruta del archivo en el sistema
    actividad = db.relationship('Actividad', back_populates='documentos')

class ActividadExamen(db.Model):
    __tablename__ = 'actividades_examenes'
    id = db.Column(db.Integer, primary_key=True)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    examen_id = db.Column(db.Integer, db.ForeignKey('examenes.id'), nullable=False)
    actividad = db.relationship('Actividad', back_populates='examenes')
    examen = db.relationship('Examen')

class ActividadResultado(db.Model):
    __tablename__ = 'actividad_resultados'

    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey('inscripciones.id'), nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey('actividades.id'), nullable=False)
    entregado = db.Column(db.Boolean, default=False)
    fecha_entregado = db.Column(db.DateTime, nullable=True)
    calificacion = db.Column(db.Float, nullable=True)
    retroalimentacion = db.Column(db.Text, nullable=True)
    examen_resultado_id = db.Column(db.Integer, db.ForeignKey('examenes_resultados.id'), nullable=True)  # <-- Nuevo campo

    inscripcion = db.relationship('Inscripcion', back_populates='actividades_realizadas')
    actividad = db.relationship('Actividad')
    examen_resultado = db.relationship('ExamenResultado')

    def __repr__(self):
        return f'<ActividadResultado actividad {self.actividad_id} inscripcion {self.inscripcion_id}>'


class CategoriaCurso(db.Model):
    __tablename__ = 'categorias_cursos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=True)

    # Aqui hacemos la relacion con el modelo de Curso
    # cursos = db.relationship('Curso', back_populates='categoria')

    def __repr__(self):
        return f'<CategoriaCurso {self.nombre}>'

class Modalidad(db.Model):
    __tablename__ = 'modalidades'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self):
        return f'<Modalidad {self.nombre}>'
    
class Objetivo(db.Model):
    __tablename__ = 'objetivos'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f'<Objetivo {self.descripcion}>'

class AreaTematicaCurso(db.Model):
    __tablename__ = 'areas_tematicas_cursos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<AreaTematica {self.nombre}>'

class TipoAgente(db.Model):
    __tablename__ = 'tipos_agente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False, unique=True)

    def __repr__(self):
        return f'<TipoAgente {self.nombre}>'

class Archivo(db.Model):
    __tablename__ = 'archivos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    ruta = db.Column(db.String(255), nullable=False)  # Ruta del archivo en el sistema
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id'), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

    curso = db.relationship('Curso', back_populates='archivos')

    def __repr__(self):
        return f'<Archivo {self.nombre}>'