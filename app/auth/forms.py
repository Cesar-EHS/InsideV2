from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError
from flask_wtf.file import FileAllowed, FileRequired
from app.auth.models import User, EstatusUsuario

class UserForm(FlaskForm):
    estatus_id = SelectField('Estatus', coerce=int, validators=[DataRequired()])
    foto = FileField('Foto de perfil', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Solo se permiten imágenes JPG o PNG')])
    
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=50)])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired(), Length(max=50)])
    apellido_materno = StringField('Apellido Materno', validators=[Optional(), Length(max=50)])
    
    curp = StringField('CURP', validators=[DataRequired(), Length(min=18, max=18)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    
    departamento_id = SelectField('Departamento', coerce=int, validators=[Optional()])
    proyecto_id = SelectField('Proyecto', coerce=int, validators=[Optional()])
    puesto_trabajo_id = SelectField('Puesto de trabajo', coerce=int, validators=[Optional()])
    jefe_inmediato_id = SelectField('Jefe inmediato', coerce=int, validators=[Optional()])
    ocupacion_especifica_id = SelectField('Ocupación específica', coerce=int, validators=[Optional()])
    institucion_educativa_id = SelectField('Institución educativa', coerce=int, validators=[Optional()])
    nivel_max_estudios_id = SelectField('Nivel máximo de estudios', coerce=int, validators=[Optional()])
    documento_probatorio_id = SelectField('Documento probatorio', coerce=int, validators=[Optional()])
    entidad_federativa_id = SelectField('Entidad federativa', coerce=int, validators=[Optional()])
    municipio_id = SelectField('Municipio', coerce=int, validators=[Optional()])
    
    fecha_ingreso = DateField('Fecha de ingreso', format='%Y-%m-%d', validators=[Optional()])
    
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[Optional(), EqualTo('password', message='Las contraseñas deben coincidir.')])
    
    submit = SubmitField('Guardar')

    def __init__(self, original_email=None, original_curp=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email
        self.original_curp = original_curp

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('El correo electrónico ya está registrado.')

    def validate_curp(self, curp):
        if curp.data != self.original_curp:
            user = User.query.filter_by(curp=curp.data).first()
            if user:
                raise ValidationError('La CURP ya está registrada.')

class LoginForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')


class ResetRequestForm(FlaskForm):
    email = StringField('Correo electrónico', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Enviar enlace de recuperación')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Nueva contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Restablecer contraseña')