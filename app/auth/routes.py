# auth/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from urllib.parse import urlparse, urljoin
from app.auth.forms import LoginForm, ResetRequestForm, ResetPasswordForm
from app.auth.models import User
from app import db, mail
from flask import abort
from werkzeug.utils import secure_filename
from app.auth.forms import UserForm
from app.auth.models import (
    User,
    EstatusUsuario,
    Departamento,
    Proyecto,
    PuestoTrabajo,
    Ocupacion,
    InstitucionEducativa,
    NivelEstudio,
    DocumentoProbatorio,
    EntidadFederativa,
    Municipio
)
from flask_login import login_required
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates', static_folder='static')


def is_safe_url(target):
    # Validar que la url sea local para prevenir open redirects
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.estatus.nombre != "Activo":
                flash("Su cuenta está suspendida o inactiva, contacte al administrador.", "warning")
                return redirect(url_for('auth.login'))

            login_user(user, remember=form.remember.data)
            flash(f"Bienvenido, {user.nombre} {user.apellido_paterno}.", "success")
            next_page = request.args.get('next')
            if not next_page or not is_safe_url(next_page):
                next_page = url_for('home.home')
            return redirect(next_page)
        else:
            flash("Correo o contraseña incorrectos.", "danger")

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('auth.login'))


def generate_reset_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='password-reset-salt')


def verify_reset_token(token, expiration=7200):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception as e:
        current_app.logger.error(f"Token inválido o expirado: {e}")
        return None
    return email

def send_reset_email(to_email, token):
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    subject = "Restablecer Contraseña - Inside"
    sender = current_app.config['MAIL_DEFAULT_SENDER']
    body = f"""
Para restablecer su contraseña, haga clic en el siguiente enlace:
{reset_url}
Si usted no solicitó este cambio, por favor ignore este mensaje.
Este enlace es válido por 1 hora.
"""
    html = render_template('reset_password_email.html', reset_url=reset_url)
    msg = Message(subject=subject, sender=sender, recipients=[to_email])
    msg.body = body
    msg.html = html
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Error enviando correo a {to_email}: {e}")
        raise e

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = generate_reset_token(user.email)
            send_reset_email(user.email, token)
            flash('Se ha enviado un enlace para restablecer su contraseña al correo proporcionado.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('No existe una cuenta registrada con ese correo.', 'warning')

    return render_template('auth/reset_password_request.html', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))

    email = verify_reset_token(token)
    if not email:
        flash('El enlace para restablecer la contraseña es inválido o ha expirado.', 'danger')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(form.password.data)
            db.session.commit()
            flash('Su contraseña ha sido actualizada correctamente.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Usuario no encontrado.', 'danger')
            return redirect(url_for('auth.reset_password_request'))

    return render_template('auth/reset_password.html', form=form, token=token)


@auth_bp.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    form = UserForm()

    # Cargar opciones para campos SelectField antes de procesar POST
    form.estatus_id.choices = [(e.id, e.nombre) for e in EstatusUsuario.query.order_by(EstatusUsuario.nombre).all()]
    form.departamento_id.choices = [(d.id, d.nombre) for d in Departamento.query.order_by(Departamento.nombre).all()]
    form.proyecto_id.choices = [(p.id, p.nombre) for p in Proyecto.query.order_by(Proyecto.nombre).all()]
    form.puesto_trabajo_id.choices = [(pt.id, pt.nombre) for pt in PuestoTrabajo.query.order_by(PuestoTrabajo.nombre).all()]
    jefes = User.query.filter_by(estatus_id=1).order_by(User.nombre, User.apellido_paterno).all()  # Ajusta el filtro estatus si quieres
    form.jefe_inmediato_id.choices = [(0, 'Sin jefe inmediato')] + [(j.id, f"{j.nombre} {j.apellido_paterno} {j.apellido_materno}") for j in jefes]
    form.institucion_educativa_id.choices = [(i.id, i.nombre) for i in InstitucionEducativa.query.order_by(InstitucionEducativa.nombre).all()]
    form.nivel_max_estudios_id.choices = [(n.id, n.nombre) for n in NivelEstudio.query.order_by(NivelEstudio.nombre).all()]
    form.documento_probatorio_id.choices = [(d.id, d.nombre) for d in DocumentoProbatorio.query.order_by(DocumentoProbatorio.nombre).all()]
    form.entidad_federativa_id.choices = [(e.id, e.nombre) for e in EntidadFederativa.query.order_by(EntidadFederativa.nombre).all()]
    form.municipio_id.choices = [(m.id, m.nombre) for m in Municipio.query.order_by(Municipio.nombre).all()]
    form.ocupacion_especifica_id.choices = [(o.id, o.nombre) for o in Ocupacion.query.order_by(Ocupacion.nombre).all()]

    if form.validate_on_submit():
        foto_filename = None
        if form.foto.data:
           foto_file = form.foto.data
           filename = secure_filename(foto_file.filename)
           fotos_path = os.path.join(current_app.root_path, 'auth', 'static', 'fotos')
           os.makedirs(fotos_path, exist_ok=True)  
           file_path = os.path.join(fotos_path, filename)
           foto_file.save(file_path)
           foto_filename = filename 

        nuevo_usuario = User(
            estatus_id=form.estatus_id.data,
            foto=foto_filename,
            nombre=form.nombre.data,
            apellido_paterno=form.apellido_paterno.data,
            apellido_materno=form.apellido_materno.data,
            curp=form.curp.data,
            email=form.email.data,
            departamento_id=form.departamento_id.data,
            proyecto_id=form.proyecto_id.data,
            puesto_trabajo_id=form.puesto_trabajo_id.data,
            jefe_inmediato_id=form.jefe_inmediato_id.data,
            ocupacion_especifica_id=form.ocupacion_especifica_id.data,
            institucion_educativa_id=form.institucion_educativa_id.data,
            nivel_max_estudios_id=form.nivel_max_estudios_id.data,
            documento_probatorio_id=form.documento_probatorio_id.data,
            entidad_federativa_id=form.entidad_federativa_id.data,
            municipio_id=form.municipio_id.data,
            fecha_ingreso=form.fecha_ingreso.data,
            password_hash = generate_password_hash(form.password.data) if form.password.data else None
        )

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('auth.crear_usuario'))  # Cambia esta ruta si es necesario

    usuarios = User.query.order_by(User.nombre).all()
    return render_template('auth/crear_usuario.html', form=form, usuarios=usuarios)
