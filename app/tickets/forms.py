from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed, FileRequired

class TicketForm(FlaskForm):
    area = SelectField(
        'Área',
        choices=[
            ('Compras', 'Compras'),
            ('IT', 'IT'),
            ('Diseño', 'Diseño'),
            ('Soporte EHSmart', 'Soporte EHSmart'),
            ('Recursos Humanos', 'Recursos Humanos'),
            ('Desarrollo Organizacional', 'Desarrollo Organizacional'),
            ('Capacitación', 'Capacitación')
        ],
        validators=[DataRequired()]
    )
    
    categoria = SelectField(
        'Categoría', 
        choices=[
            # Compras
            ('Solicitud de compra', 'Solicitud de compra'),
            ('Cotizaciones', 'Cotizaciones'),
            ('Reembolsos', 'Reembolsos'),
            ('Seguimiento de envíos', 'Seguimiento de envíos'),
            
            # IT
            ('Soporte técnico', 'Soporte técnico'),
            ('Accesos y contraseñas', 'Accesos y contraseñas'),
            ('Red y conectividad', 'Red y conectividad'),
            ('Correo electrónico', 'Correo electrónico'),
            ('Impresoras y escáneres', 'Impresoras y escáneres'),
            ('Instalación de software', 'Instalación de software'),
            
            # Diseño
            ('Diseño de material impreso o digital', 'Diseño de material impreso o digital'),
            ('Actualización de diseño', 'Actualización de diseño'),
            ('Logotipos e identidad corporativa', 'Logotipos e identidad corporativa'),
            ('Plantillas corporativas', 'Plantillas corporativas'),
            ('Revisión de uso de marca', 'Revisión de uso de marca'),
            
            # Soporte EHSmart
            ('Acceso y usuarios', 'Acceso y usuarios'),
            ('Errores técnicos', 'Errores técnicos'),
            ('Capacitación EHSmart', 'Capacitación EHSmart'),
            ('Solicitud de soporte funcional', 'Solicitud de soporte funcional'),
            
            # Recursos Humanos
            ('Vacaciones y permisos', 'Vacaciones y permisos'),
            ('Nómina y pagos', 'Nómina y pagos'),
            ('Prestaciones y beneficios', 'Prestaciones y beneficios'),
            ('Documentación y constancias', 'Documentación y constancias'),
            
            # Desarrollo Organizacional
            ('Asesoría individual', 'Asesoría individual'),
            ('Gestión de conflictos laborales', 'Gestión de conflictos laborales'),
            ('Apoyo al desarrollo personal y profesional', 'Apoyo al desarrollo personal y profesional'),
            ('Programas de desarrollo interno', 'Programas de desarrollo interno'),
            
            # Capacitación
            ('Solicitud de curso', 'Solicitud de curso'),
            ('Alta de evento de capacitación', 'Alta de evento de capacitación'),
            ('Dudas sobre plan de formación', 'Dudas sobre plan de formación'),
            ('Registro de constancia o diploma', 'Registro de constancia o diploma')
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