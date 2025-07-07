from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectField, SubmitField
)
from wtforms.validators import DataRequired, Length, Optional, URL

class CursoForm(FlaskForm):
    categoria = SelectField(
        'Categoría',
        choices=[
            ('Protección Civil', 'Protección Civil'),
            ('Seguridad Industrial', 'Seguridad Industrial'),
            ('Salud Ocupacional', 'Salud Ocupacional'),
            ('Protección Medioambiente', 'Protección Medioambiente'),
            ('Herramientas Digitales', 'Herramientas Digitales'),
            ('Desarrollo Humano', 'Desarrollo Humano'),
        ],
        validators=[DataRequired()]
    )
    modalidad = SelectField(
        'Modalidad',
        choices=[('Presencial', 'Presencial'), ('En línea', 'En línea'), ('Mixta', 'Mixta')],
        validators=[DataRequired()]
    )
    objetivo = SelectField(
        'Objetivo',
        choices=[
            ('Actualizar y perfeccionar conocimientos y habilidades', 'Actualizar y perfeccionar conocimientos y habilidades'),
            ('Proporcionar información de nuevas tecnologías', 'Proporcionar información de nuevas tecnologías'),
            ('Preparar para ocupar vacantes o puestos de nueva creación', 'Preparar para ocupar vacantes o puestos de nueva creación'),
            ('Prevenir riesgos de trabajo', 'Prevenir riesgos de trabajo'),
            ('Incremento a la Productividad', 'Incremento a la Productividad'),
        ],
        validators=[DataRequired()]
    )
    nombre = StringField('Nombre del curso', validators=[DataRequired(), Length(max=150)])
    contenido = TextAreaField('Contenido', validators=[DataRequired()])
    area_tematica = SelectField(
        'Área temática',
        choices=[
            ('6400-Higiene y seguridad en el trabajo', '6400-Higiene y seguridad en el trabajo'),
            ('5405-Ambientales', '5405-Ambientales'),
            ('3133-Formación y actualización de instructores', '3133-Formación y actualización de instructores'),
            ('7100-Relaciones humanas', '7100-Relaciones humanas'),
            ('8000-Uso de tecnologías de la información y comunicación', '8000-Uso de tecnologías de la información y comunicación'),
        ],
        validators=[DataRequired()]
    )
    duracion = StringField('Duración', validators=[DataRequired(), Length(max=50)])
    tipo_agente = SelectField(
        'Tipo de agente capacitador',
        choices=[('Interno', 'Interno'), ('Externo', 'Externo'), ('Otro', 'Otro')],
        validators=[DataRequired()]
    )
    imagen = FileField('Imagen del curso', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo imágenes')])
    submit = SubmitField('Guardar')

class ExamenForm(FlaskForm):
    titulo = StringField('Título del examen', validators=[DataRequired(), Length(max=150)])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField('Guardar')

class PreguntaForm(FlaskForm):
    texto = TextAreaField('Pregunta', validators=[DataRequired()])
    tipo = SelectField(
        'Tipo de pregunta',
        choices=[
            ('opcion_multiple', 'Opción múltiple'),
            ('verdadero_falso', 'Verdadero/Falso'),
            ('abierta', 'Respuesta abierta')
        ],
        validators=[DataRequired()]
    )
    opciones = TextAreaField('Opciones (solo para opción múltiple, separadas por línea)')
    respuesta_correcta = StringField('Respuesta correcta')
    submit = SubmitField('Guardar')

class ActividadForm(FlaskForm):
    titulo = StringField('Título de la actividad', validators=[DataRequired(), Length(max=150)])
    descripcion = TextAreaField('Descripción')
    video_url = StringField('URL del Video', validators=[Optional(), URL(message='Ingrese una URL válida')])
    submit = SubmitField('Guardar')
