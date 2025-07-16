from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired

class TicketForm(FlaskForm):
    categoria = SelectField(
        'Área', 
        choices=[
            ('Soporte Sistemas', 'Soporte Sistemas'),
            ('Requisición Compras', 'Requisición Compras'),
            ('Desarrollo Organizacional', 'Desarrollo Organizacional'),
            ('Capacitación Técnica', 'Capacitación Técnica'),
            ('Diseño Institucional', 'Diseño Institucional'),
            ('Recursos Humanos', 'Recursos Humanos'),
            ('Soporte EHSmart', 'Soporte EHSmart')
        ],
        validators=[DataRequired()]
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

    archivo = FileField('Archivo adjunto (opcional)', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'pdf', 'doc', 'docx', 'xls', 'xlsx'], 'Formato no permitido'),
    ])

    submit = SubmitField('Crear Ticket')