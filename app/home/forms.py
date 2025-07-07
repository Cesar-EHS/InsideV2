from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf.file import FileAllowed

class PostForm(FlaskForm):
    content = TextAreaField(
        'Contenido',
        validators=[DataRequired(message="El contenido es obligatorio."), Length(max=5000)]
    )
    image = FileField(
        'Imagen',
        validators=[
            FileAllowed(['jpg', 'png', 'jpeg'], 'Solo se permiten imágenes JPG, PNG o JPEG.'),
            Optional()
        ]
    )
    submit = SubmitField('Publicar')
