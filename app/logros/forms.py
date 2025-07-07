from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from flask_wtf.file import FileAllowed
from datetime import date


class LogroForm(FlaskForm):
    titulo = StringField(
        'Título',
        validators=[
            DataRequired(message='El título es obligatorio.'),
            Length(max=100, message='El título no debe exceder 100 caracteres.')
        ]
    )
    descripcion = TextAreaField(
        'Descripción',
        validators=[
            DataRequired(message='La descripción es obligatoria.')
        ]
    )
    imagen = FileField(
        'Imagen del Logro (PNG)',
        validators=[
            DataRequired(message='Debes subir una imagen en formato PNG.'),
            FileAllowed(['png'], 'Solo se permiten archivos PNG.')
        ]
    )
    fecha_inicio = DateField(
        'Fecha de Inicio',
        format='%Y-%m-%d',
        validators=[DataRequired(message='La fecha de inicio es obligatoria.')]
    )
    fecha_fin = DateField(
        'Fecha de Término (opcional)',
        format='%Y-%m-%d',
        validators=[Optional()],
        render_kw={"placeholder": "Opcional"}
    )
    submit = SubmitField('Guardar Logro')

    def validate_fecha_fin(self, field):
        if field.data and self.fecha_inicio.data and field.data < self.fecha_inicio.data:
            raise ValidationError('La fecha de término no puede ser anterior a la fecha de inicio.')


class EvidenciaForm(FlaskForm):
    archivo = FileField(
        'Evidencia (imagen o PDF)',
        validators=[
            DataRequired(message='Debes subir un archivo como evidencia.'),
            FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Formatos permitidos: JPG, JPEG, PNG, PDF.')
        ]
    )
    submit = SubmitField('Enviar Evidencia')
