from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, SelectField, SubmitField
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Optional, URL
from app.cursos.models import CategoriaCurso

def get_categorias_para_form():
    """
    Esta función se utiliza para obtener las categorías de la base de datos
    y las imprime en la consola para depuración.
    """
    categorias = CategoriaCurso.query.order_by(CategoriaCurso.nombre).all()
    print(f"\n--- Depuración de Categorías para el Formulario ---")
    if categorias:
        print(f"Se encontraron {len(categorias)} categorías en la base de datos:")
        for cat in categorias:
            print(f"  - ID: {cat.id}, Nombre: {cat.nombre}")
    else:
        print("¡ADVERTENCIA: No se encontraron categorías en la base de datos 'categorias_cursos'!")
        print("Asegúrate de que la tabla 'categorias_cursos' existe y contiene datos.")
    print(f"---------------------------------------------------\n")
    return categorias

class CursoForm(FlaskForm):
    # Campo para la categoría del curso
    categoria = QuerySelectField(
        'Categoría',
        # query_factory es una función que SQLAlchemy usará para obtener las opciones.
        # Aquí, obtenemos todas las categorías de la tabla 'categorias_cursos' ordenadas alfabéticamente por su nombre.
        query_factory=get_categorias_para_form,
        # get_label especifica qué atributo del objeto CategoriaCurso se usará como el texto visible en el desplegable.
        get_label='nombre',
        # allow_blank=True permite que el SelectField tenga una opción en blanco al inicio.
        allow_blank=True,
        # blank_text es el texto que se mostrará para esa opción en blanco.
        blank_text='Selecciona una categoría',
        validators=[DataRequired()] # El validador DataRequired asegura que el usuario seleccione una opción válida (no la en blanco).
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
    duracion = SelectField(
        'Duración',
        choices=[
            ('', 'Selecciona la duración'),
            ('00:30', '30 minutos'),
            ('01:00', '1 hora'),
            ('01:30', '1 hora 30 minutos'),
            ('02:00', '2 horas')
        ],
        validators=[DataRequired()]
    )
    tipo_agente = SelectField(
        'Tipo de agente capacitador',
        choices=[('Interno', 'Interno'), ('Externo', 'Externo'), ('Otro', 'Otro')],
        validators=[DataRequired()]
    )
    imagen = FileField('Imagen del curso', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo imágenes')])
    submit = SubmitField('Guardar')

    """ def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.all()] """

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
