from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired
from app.auth.models import Departamento
from app.tickets.models import CategoriaTicket

class TicketForm(FlaskForm):
    departamento_id = SelectField(
        'Departamento',
        coerce=int,
        validators=[DataRequired(message="Por favor selecciona un departamento")]
    )
    
    categoria_id = SelectField(
        'Categoría', 
        coerce=int,
        validators=[DataRequired(message="Por favor selecciona una categoría")]
    )

    titulo = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    descripcion = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10)])

    prioridad = SelectField(
        'Prioridad', 
        choices=[
            ('Baja', 'Baja'),
            ('Media', 'Media'),
            ('Alta', 'Alta'),
            ('Urgente', 'Urgente')
        ],
        validators=[DataRequired()]
    )

    # Campos para múltiples evidencias
    evidencia_1 = FileField('Evidencia 1', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx'], 'Formato no permitido'),
    ])
    
    evidencia_2 = FileField('Evidencia 2', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx'], 'Formato no permitido'),
    ])
    
    evidencia_3 = FileField('Evidencia 3', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx'], 'Formato no permitido'),
    ])

    # Mantener el campo archivo para compatibilidad
    archivo = FileField('Archivo adjunto (opcional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx'], 'Formato no permitido'),
    ])

    submit = SubmitField('Crear Ticket')
    
    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        
        # Cargar departamentos (sin filtrar por activo inicialmente para evitar errores)
        try:
            departamentos = Departamento.query.order_by(Departamento.nombre).all()
            # Filtrar solo los activos si el campo existe
            departamentos_activos = [d for d in departamentos if getattr(d, 'activo', True)]
            self.departamento_id.choices = [(0, 'Selecciona un departamento')] + [  # type: ignore
                (d.id, d.nombre) for d in departamentos_activos
            ]
        except Exception as e:
            print(f"Error cargando departamentos: {e}")
            self.departamento_id.choices = [(0, 'Selecciona un departamento')]  # type: ignore
        
        # Cargar categorías activas
        try:
            categorias = CategoriaTicket.query.filter_by(activo=True).order_by(CategoriaTicket.nombre).all()
            self.categoria_id.choices = [(0, 'Selecciona una categoría')] + [  # type: ignore
                (c.id, c.nombre) for c in categorias
            ]
        except Exception as e:
            print(f"Error cargando categorías: {e}")
            self.categoria_id.choices = [(0, 'Selecciona una categoría')]  # type: ignore

class EditTicketForm(FlaskForm):
    """Formulario para editar tickets existentes."""
    departamento_id = SelectField(
        'Departamento',
        coerce=int,
        validators=[DataRequired(message="Por favor selecciona un departamento")]
    )
    
    categoria_id = SelectField(
        'Categoría', 
        coerce=int,
        validators=[DataRequired(message="Por favor selecciona una categoría")]
    )

    titulo = StringField('Título', validators=[DataRequired(), Length(min=5, max=200)])
    descripcion = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10)])

    prioridad = SelectField(
        'Prioridad', 
        choices=[
            ('Baja', 'Baja'),
            ('Media', 'Media'),
            ('Alta', 'Alta'),
            ('Urgente', 'Urgente')
        ],
        validators=[DataRequired()]
    )

    estado = SelectField(
        'Estado', 
        choices=[
            ('Abierto', 'Abierto'),
            ('En Proceso', 'En Proceso'),
            ('Cerrado', 'Cerrado')
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField('Actualizar Ticket')
    
    def __init__(self, *args, **kwargs):
        super(EditTicketForm, self).__init__(*args, **kwargs)
        
        # Cargar departamentos (sin filtrar por activo inicialmente para evitar errores)
        try:
            departamentos = Departamento.query.order_by(Departamento.nombre).all()
            # Filtrar solo los activos si el campo existe
            departamentos_activos = [d for d in departamentos if getattr(d, 'activo', True)]
            self.departamento_id.choices = [  # type: ignore
                (d.id, d.nombre) for d in departamentos_activos
            ]
        except Exception as e:
            print(f"Error cargando departamentos: {e}")
            self.departamento_id.choices = []  # type: ignore
        
        # Cargar categorías activas
        try:
            categorias = CategoriaTicket.query.filter_by(activo=True).order_by(CategoriaTicket.nombre).all()
            self.categoria_id.choices = [  # type: ignore
                (c.id, c.nombre) for c in categorias
            ]
        except Exception as e:
            print(f"Error cargando categorías: {e}")
            self.categoria_id.choices = []  # type: ignore