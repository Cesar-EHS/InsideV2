from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired

class DocumentoForm(FlaskForm):
    """Formulario para alta y edición de documentos en Knowledge."""
    nombre = StringField(
        'Nombre del documento',
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(max=150, message="Máximo 150 caracteres.")
        ]
    )
    tipo = SelectField(
        'Tipo de documento',
        choices=[
            ('Registro', 'Registro'),
            ('Procedimiento', 'Procedimiento'),
            ('Reglamento', 'Reglamento'),
            ('Política', 'Política')
        ],
        validators=[DataRequired(message="Selecciona el tipo de documento.")]
    )
    categoria = SelectField(
        'Categoría',
        choices=[
            ('Operaciones', 'Operaciones'),
            ('Consultoría', 'Consultoría'),
            ('Proyectos', 'Proyectos'),
            ('Administración', 'Administración'),
            ('Recursos Humanos', 'Recursos Humanos'),
            ('Desarrollo', 'Desarrollo'),
            ('Comercial', 'Comercial')
        ],
        validators=[DataRequired(message="Selecciona la categoría.")]
    )
    archivo = FileField(
        'Archivo adjunto',
        validators=[
            FileRequired(message="Debes adjuntar un archivo."),
            FileAllowed(['pdf', 'doc', 'docx', 'xlsx', 'xls', 'ppt', 'pptx', 'png', 'jpg', 'jpeg'],
                        'Formatos permitidos: PDF, Word, Excel, PowerPoint, Imagen')
        ]
    )
    submit = SubmitField('Guardar')
