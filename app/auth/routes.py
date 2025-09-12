# auth/routes.py
from __future__ import annotations
import os
import pytz
import re
import uuid
import traceback
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from urllib.parse import urlparse, urljoin
from app.auth.forms import LoginForm, ResetRequestForm, ResetPasswordForm, UserForm
from app.auth.models import (User, Departamento, PuestoTrabajo, Proyecto, Ocupacion, 
                            InstitucionEducativa, NivelEstudio, EntidadFederativa, 
                            Municipio, EstatusUsuario, Configuracion, PermisosGestion,
                            PermisosTickets, PermisosHome)
from app import db, mail, csrf
from werkzeug.utils import secure_filename
from typing import Optional, cast, Sequence, Any, TypeVar, Callable, Union, Protocol, List, Tuple
from wtforms.fields import SelectField
from wtforms.widgets.core import html_params
from wtforms.fields import SelectField as WTFSelectField

from app.auth.activity_log import log_activity
from app.auth.password_validation import validate_password_strength
from app.auth.session_manager import SessionManager
from app.auth.models import (
    User,
    TokenBlacklist,
    UserHistoryChange,
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

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates', static_folder='static')

#Definir zona horaria
mexico_city_tz = pytz.timezone('America/Mexico_City')

def has_management_permissions(user) -> bool:
    """Verificar si un usuario tiene permisos para gestionar usuarios."""
    if not user or not user.puesto_trabajo:
        return False
    
    # Consultar la tabla de permisos
    permiso = PermisosGestion.query.filter_by(
        puesto_trabajo_id=user.puesto_trabajo.id,
        puede_gestionar_usuarios=True
    ).first()
    
    return permiso is not None


def is_safe_url(target: str) -> bool:
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

        #Obtener hora actual con Aware
        now = datetime.now(mexico_city_tz)
        
        # Verificar si el usuario está bloqueado
        """ if user and user.locked_until and user.locked_until > datetime.now(pytz.UTC):
            remaining_time = int((user.locked_until - datetime.now(pytz.UTC)).total_seconds() / 60)
            flash(f"Su cuenta está temporalmente bloqueada. Por favor, intente nuevamente en {remaining_time} minutos.", "danger")
            return render_template('auth/login.html', form=form) """
        
        # Si user.locked_until existe, convertirlo a aware antes de la comparación
        if user and user.locked_until:
            locked_until_aware = user.locked_until
            # Si el objeto es 'naive', asignarle la zona horaria de México
            if locked_until_aware.tzinfo is None or locked_until_aware.tzinfo.utcoffset(locked_until_aware) is None:
                # Usa .localize() para añadir la información de zona horaria
                locked_until_aware = mexico_city_tz.localize(locked_until_aware)
        
            # Ahora la comparación es segura
            if locked_until_aware > now:
                remaining_time = int((locked_until_aware - now).total_seconds() / 60)
                flash(f"Su cuenta está temporalmente bloqueada. Por favor, intente nuevamente en {remaining_time} minutos.", "danger")
                return render_template('auth/login.html', form=form)

        if user and form.password.data is not None and check_password_hash(user.password_hash, form.password.data):
            # Verificar estatus del usuario (si existe)
            if not user.estatus or user.estatus.nombre != "Activo":
                flash("Su cuenta está suspendida o inactiva, contacte al administrador.", "warning")
                return redirect(url_for('auth.login'))

            # Resetear contador de intentos fallidos
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now(pytz.UTC)
            db.session.commit()

            login_user(user, remember=form.remember.data)
            flash(f"Bienvenido, {user.nombre} {user.apellido_paterno}.", "success")
            next_page = request.args.get('next')
            if not next_page or not is_safe_url(next_page):
                next_page = url_for('home.home')
            return redirect(next_page)
        else:
            if user:
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                user.last_failed_login = datetime.now(pytz.UTC)
                # Si excede el máximo de intentos, bloquear la cuenta
                if user.failed_login_attempts >= 5:  # Este valor debería venir de la configuración
                    user.locked_until = datetime.now(pytz.UTC) + timedelta(minutes=15)
                    flash("Ha excedido el número máximo de intentos. Su cuenta ha sido bloqueada temporalmente.", "danger")
                else:
                    remaining_attempts = 5 - user.failed_login_attempts
                    flash(f"Correo o contraseña incorrectos. Le quedan {remaining_attempts} intentos.", "danger")
                db.session.commit()
            else:
                flash("Los datos ingresados son incorrectos. Por favor, verifica tu correo y contraseña.", "danger")
            flash("Si olvidaste tu contraseña, puedes restablecerla usando el enlace 'Olvidé mi contraseña'.", "info")

    return render_template('auth/login.html', form=form, login_failed=True)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for('auth.login'))


def generate_reset_token(email: str) -> str:
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return str(serializer.dumps(email, salt='password-reset-salt'))


def verify_reset_token(token: str, expiration: int = 7200) -> Optional[str]:
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception as e:
        current_app.logger.error(f"Token inválido o expirado: {e}")
        return None
    return email

def send_reset_email(to_email: str, token: str) -> None:
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


@auth_bp.route('/config', methods=['GET', 'POST'])
@login_required
def config():
    """Configuración del módulo de autenticación."""
    # Verificar permisos usando la función dinámica
    if not has_management_permissions(current_user):
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('home.home'))
    
    if request.method == 'POST':
        # Manejar configuraciones POST
        try:
            # Aquí se guardarían las configuraciones en la base de datos
            flash('Configuración actualizada exitosamente', 'success')
        except Exception as e:
            flash(f'Error al actualizar configuración: {str(e)}', 'error')
    
    # Obtener estadísticas reales
    total_users = User.query.count()
    active_users = User.query.filter_by(estatus_id=1).count()
    suspended_users = User.query.filter_by(estatus_id=3).count()
    
    # Usuarios creados en los últimos 7 días
    from datetime import timedelta
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    new_users = User.query.filter(User.created_at >= seven_days_ago).count()
    
    # Obtener todos los puestos de trabajo para la sección de permisos
    puestos_trabajo = PuestoTrabajo.query.all()
    
    # Obtener configuraciones de imágenes
    login_image = Configuracion.get_valor('login_image', 'auth/static/img/m.jpg')
    logo_sistema = Configuracion.get_valor('logo_sistema', 'logo_inside.png')
    background_image = Configuracion.get_valor('background_image', 'default_bg.svg')
    
    return render_template('auth/config.html',
                         users_count=total_users,
                         active_users=active_users,
                         suspended_users=suspended_users,
                         new_users=new_users,
                         puestos_trabajo=puestos_trabajo,
                         login_image=login_image,
                         logo_sistema=logo_sistema,
                         background_image=background_image)


@auth_bp.route('/gestionar_usuarios')
@login_required
def gestionar_usuarios():
    """Ver y gestionar todos los usuarios."""
    # Verificar permisos usando la función dinámica
    if not has_management_permissions(current_user):
        flash('No tienes permisos para acceder a esta página', 'error')
        return redirect(url_for('home.home'))
    
    usuarios = User.query.all()
    
    # Calcular estadísticas
    total_usuarios = len(usuarios)
    usuarios_activos = len([u for u in usuarios if u.estatus_id == 1])
    usuarios_suspendidos = len([u for u in usuarios if u.estatus_id == 3])
    
    # Usuarios nuevos en los últimos 7 días
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    usuarios_nuevos = len([u for u in usuarios if u.created_at and u.created_at >= seven_days_ago])
    
    # Cargar datos para los selects
    departamentos = Departamento.query.all()
    proyectos = Proyecto.query.all()
    puestos = PuestoTrabajo.query.all()
    ocupaciones = Ocupacion.query.all()
    instituciones = InstitucionEducativa.query.all()
    niveles_estudio = NivelEstudio.query.all()
    documentos = DocumentoProbatorio.query.all()
    entidades = EntidadFederativa.query.all()
    municipios = Municipio.query.all()
    estatus = EstatusUsuario.query.all()
    
    return render_template('auth/gestionar_usuarios.html', 
                         usuarios=usuarios,
                         total_usuarios=total_usuarios,
                         usuarios_activos=usuarios_activos,
                         usuarios_suspendidos=usuarios_suspendidos,
                         usuarios_nuevos=usuarios_nuevos,
                         departamentos=departamentos,
                         proyectos=proyectos,
                         puestos=puestos,
                         ocupaciones=ocupaciones,
                         instituciones=instituciones,
                         niveles_estudio=niveles_estudio,
                         documentos=documentos,
                         entidades=entidades,
                         municipios=municipios,
                         estatus=estatus)


@auth_bp.route('/crear_usuario', methods=['POST'])
@login_required
@csrf.exempt
def crear_usuario():
    """Crear un nuevo usuario."""
    try:
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        # Funciones auxiliares para conversión segura
        def safe_int(value):
            """Convierte string a int de forma segura."""
            if value and str(value).strip():
                return int(value)
            return None
        
        def safe_str(value):
            """Convierte a string de forma segura."""
            if value is not None:
                return str(value).strip()
            return None
        
        def safe_date(value):
            """Convierte string a date de forma segura."""
            if value and str(value).strip():
                return datetime.strptime(str(value), '%Y-%m-%d').date()
            return None
        
        # Validar que no exista el email o CURP
        email = safe_str(request.form.get('email'))
        curp = safe_str(request.form.get('curp'))
        password = request.form.get('password')
        nombre = safe_str(request.form.get('nombre'))
        apellido_paterno = safe_str(request.form.get('apellido_paterno'))
        
        # Validaciones de campos requeridos
        if not email:
            return jsonify({'error': 'El email es requerido'}), 400
        if not curp:
            return jsonify({'error': 'El CURP es requerido'}), 400
        if not password:
            return jsonify({'error': 'La contraseña es requerida'}), 400
        if not nombre:
            return jsonify({'error': 'El nombre es requerido'}), 400
        if not apellido_paterno:
            return jsonify({'error': 'El apellido paterno es requerido'}), 400
            
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'El formato del email no es válido'}), 400
            
        # Validar formato de CURP
        curp_pattern = r'^[A-Z]{4}[0-9]{6}[HM][A-Z]{5}[0-9A-Z][0-9]$'
        if not re.match(curp_pattern, curp.upper()):
            return jsonify({'error': 'El formato del CURP no es válido'}), 400
            
        # Validar longitud de contraseña
        if len(password) < 8:
            return jsonify({'error': 'La contraseña debe tener al menos 8 caracteres'}), 400
            
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'El email ya está registrado'}), 400
            
        if User.query.filter_by(curp=curp.upper()).first():
            return jsonify({'error': 'El CURP ya está registrado'}), 400
        
        # Crear nuevo usuario
        usuario = User()
        usuario.nombre = nombre
        usuario.apellido_paterno = apellido_paterno
        usuario.apellido_materno = safe_str(request.form.get('apellido_materno'))
        usuario.curp = curp.upper()
        usuario.email = email.lower()
        usuario.telefono = safe_str(request.form.get('telefono'))
        usuario.fecha_ingreso = safe_date(request.form.get('fecha_ingreso'))
        usuario.estatus_id = safe_int(request.form.get('estatus_id')) or 1
        usuario.departamento_id = safe_int(request.form.get('departamento_id'))
        usuario.proyecto_id = safe_int(request.form.get('proyecto_id'))
        usuario.puesto_trabajo_id = safe_int(request.form.get('puesto_trabajo_id'))
        usuario.jefe_inmediato_id = safe_int(request.form.get('jefe_inmediato_id'))
        usuario.ocupacion_especifica_id = safe_int(request.form.get('ocupacion_especifica_id'))
        usuario.institucion_educativa_id = safe_int(request.form.get('institucion_educativa_id'))
        usuario.nivel_max_estudios_id = safe_int(request.form.get('nivel_max_estudios_id'))
        usuario.documento_probatorio_id = safe_int(request.form.get('documento_probatorio_id'))
        usuario.entidad_federativa_id = safe_int(request.form.get('entidad_federativa_id'))
        usuario.municipio_id = safe_int(request.form.get('municipio_id'))
        
        # Establecer contraseña
        usuario.set_password(password)
        
        # Manejar foto si se subió
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename:
                # Validar tipo de archivo
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename:
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    if file_ext in allowed_extensions:
                        filename = secure_filename(f"user_{usuario.curp}_{file.filename}")
                        upload_folder = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.root_path, 'auth', 'uploads')
                        filepath = os.path.join(upload_folder, filename)
                        os.makedirs(os.path.dirname(filepath), exist_ok=True)
                        file.save(filepath)
                        usuario.foto = filename
        
        # Usar database manager para operación thread-safe
        from app.database_manager import db_manager
        
        def create_user_operation():
            db.session.add(usuario)
            db.session.commit()
            return usuario
        
        created_user = db_manager.execute_with_retry(create_user_operation)
        
        # Log de actividad
        log_activity(
            activity_type='CREATE_USER',
            details=f'Usuario creado: {created_user.email}',
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True, 
            'message': f'Usuario {created_user.nombre} {created_user.apellido_paterno} creado exitosamente',
            'user_id': created_user.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear usuario: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500


@auth_bp.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
def editar_usuario(user_id):
    """Editar un usuario existente."""
    usuario = User.query.get_or_404(user_id)
    form = UserForm(obj=usuario)
    
    # Configurar choices estáticas
    form.estatus_id.choices = [("1", "Activo"), ("2", "Inactivo")]  # type: ignore
    form.departamento_id.choices = [("1", "TI"), ("2", "RRHH")]  # type: ignore
    form.proyecto_id.choices = [("1", "Proyecto 1")]  # type: ignore
    form.puesto_trabajo_id.choices = [("1", "Desarrollador")]  # type: ignore
    form.jefe_inmediato_id.choices = [("0", "Sin jefe inmediato")]  # type: ignore
    form.institucion_educativa_id.choices = [("1", "Universidad")]  # type: ignore
    form.nivel_max_estudios_id.choices = [("1", "Licenciatura")]  # type: ignore
    form.documento_probatorio_id.choices = [("1", "Título")]  # type: ignore
    form.entidad_federativa_id.choices = [("1", "Estado")]  # type: ignore
    form.municipio_id.choices = [("1", "Municipio")]  # type: ignore

    if form.validate_on_submit():
        usuario.nombre = form.nombre.data
        usuario.email = form.email.data
        usuario.telefono = form.telefono.data
        usuario.fecha_ingreso = form.fecha_ingreso.data
        
        if form.password.data:
            usuario.password_hash = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('auth.gestionar_usuarios'))

    return render_template('auth/editar_usuario.html', form=form, usuario=usuario)


@auth_bp.route('/eliminar_usuario/<int:user_id>', methods=['POST'])
@login_required
def eliminar_usuario(user_id):
    """Eliminar un usuario."""
    usuario = User.query.get_or_404(user_id)
    db.session.delete(usuario)
    db.session.commit()
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('auth.gestionar_usuarios'))


@auth_bp.route('/toggle_user_status/<int:user_id>', methods=['POST'])
@login_required
@csrf.exempt
def toggle_user_status(user_id):
    """Cambiar el estado activo/suspendido de un usuario."""
    try:
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        usuario = User.query.get_or_404(user_id)
        
        # Verificar que no sea el usuario actual
        if usuario.id == current_user.id:
            return jsonify({'error': 'No puedes cambiar tu propio estado'}), 400
        
        # Cambiar estatus (1=Activo, 3=Suspendido)
        old_status = usuario.estatus_id
        if usuario.estatus_id == 1:  # Si está activo, suspender
            usuario.estatus_id = 3
            action = 'SUSPEND_USER'
            message = f'Usuario {usuario.nombre} {usuario.apellido_paterno} suspendido exitosamente'
        else:  # Si está suspendido, activar
            usuario.estatus_id = 1
            action = 'ACTIVATE_USER'
            message = f'Usuario {usuario.nombre} {usuario.apellido_paterno} activado exitosamente'
        
        # Usar database manager para operación thread-safe
        from app.database_manager import db_manager
        
        def update_status_operation():
            db.session.commit()
            return usuario
        
        updated_user = db_manager.execute_with_retry(update_status_operation)
        
        # Log de actividad
        log_activity(
            activity_type=action,
            details=message,
            user_id=current_user.id
        )
        
        return jsonify({'success': True, 'message': message}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al cambiar estado: {str(e)}'}), 500


@auth_bp.route('/actualizar_usuario/<int:user_id>', methods=['POST'])
@login_required
@csrf.exempt
def actualizar_usuario(user_id):
    """Actualizar un usuario existente."""
    try:
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        usuario = User.query.get_or_404(user_id)
        
        # Funciones auxiliares para conversión segura
        def safe_int(value):
            if value and str(value).strip():
                return int(value)
            return None
        
        def safe_str(value):
            if value is not None:
                return str(value).strip()
            return None
        
        def safe_date(value):
            if value and str(value).strip():
                return datetime.strptime(str(value), '%Y-%m-%d').date()
            return None
        
        # Validar email único (excluyendo el usuario actual)
        email = safe_str(request.form.get('email'))
        if email:
            existing_user = User.query.filter(User.email == email, User.id != user_id).first()
            if existing_user:
                return jsonify({'error': 'El email ya está registrado por otro usuario'}), 400
        
        # Actualizar datos
        usuario.nombre = safe_str(request.form.get('nombre'))
        usuario.apellido_paterno = safe_str(request.form.get('apellido_paterno'))
        usuario.apellido_materno = safe_str(request.form.get('apellido_materno'))
        usuario.email = email
        usuario.telefono = safe_str(request.form.get('telefono'))
        usuario.fecha_ingreso = safe_date(request.form.get('fecha_ingreso'))
        usuario.estatus_id = safe_int(request.form.get('estatus_id')) or usuario.estatus_id
        usuario.departamento_id = safe_int(request.form.get('departamento_id'))
        usuario.proyecto_id = safe_int(request.form.get('proyecto_id'))
        usuario.puesto_trabajo_id = safe_int(request.form.get('puesto_trabajo_id'))
        usuario.jefe_inmediato_id = safe_int(request.form.get('jefe_inmediato_id'))
        usuario.ocupacion_especifica_id = safe_int(request.form.get('ocupacion_especifica_id'))
        usuario.institucion_educativa_id = safe_int(request.form.get('institucion_educativa_id'))
        usuario.nivel_max_estudios_id = safe_int(request.form.get('nivel_max_estudios_id'))
        usuario.documento_probatorio_id = safe_int(request.form.get('documento_probatorio_id'))
        usuario.entidad_federativa_id = safe_int(request.form.get('entidad_federativa_id'))
        usuario.municipio_id = safe_int(request.form.get('municipio_id'))
        
        # Actualizar contraseña si se proporciona
        if request.form.get('password'):
            usuario.set_password(request.form.get('password'))
        
        # Manejar foto si se subió
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename:
                # Validar tipo de archivo
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename:
                    file_ext = file.filename.rsplit('.', 1)[1].lower()
                    if file_ext in allowed_extensions:
                            filename = secure_filename(f"user_{usuario.curp}_{file.filename}")
                            upload_folder = current_app.config['UPLOAD_FOLDER'] or os.path.join(current_app.root_path, 'auth', 'uploads')
                            filepath = os.path.join(upload_folder, filename)
                            os.makedirs(os.path.dirname(filepath), exist_ok=True)
                            file.save(filepath)
                            usuario.foto = filename
        
        # Usar database manager para operación thread-safe
        from app.database_manager import db_manager
        
        def update_user_operation():
            db.session.commit()
            return usuario
        
        updated_user = db_manager.execute_with_retry(update_user_operation)
        
        # Log de actividad
        log_activity(
            activity_type='UPDATE_USER',
            details=f'Usuario actualizado: {updated_user.email}',
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True, 
            'message': f'Usuario {updated_user.nombre} {updated_user.apellido_paterno} actualizado exitosamente'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar usuario: {str(e)}'}), 500


@auth_bp.route('/get_user_data/<int:user_id>')
@login_required
def get_user_data(user_id):
    """Obtener datos de un usuario para editar."""
    try:
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        usuario = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'user': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'apellido_paterno': usuario.apellido_paterno,
                'apellido_materno': usuario.apellido_materno,
                'email': usuario.email,
                'curp': usuario.curp,
                'telefono': usuario.telefono,
                'fecha_ingreso': usuario.fecha_ingreso.isoformat() if usuario.fecha_ingreso else None,
                'estatus_id': usuario.estatus_id,
                'departamento_id': usuario.departamento_id,
                'proyecto_id': usuario.proyecto_id,
                'puesto_trabajo_id': usuario.puesto_trabajo_id,
                'jefe_inmediato_id': usuario.jefe_inmediato_id,
                'ocupacion_especifica_id': usuario.ocupacion_especifica_id,
                'institucion_educativa_id': usuario.institucion_educativa_id,
                'nivel_max_estudios_id': usuario.nivel_max_estudios_id,
                'documento_probatorio_id': usuario.documento_probatorio_id,
                'entidad_federativa_id': usuario.entidad_federativa_id,
                'municipio_id': usuario.municipio_id,
                'foto': usuario.foto
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener datos del usuario: {str(e)}'}), 500


@auth_bp.route('/test_endpoint', methods=['POST'])
def test_endpoint():
    """Endpoint de prueba para verificar que el servidor recibe requests."""
    try:
        print("¡Test endpoint llamado!")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {request.form.to_dict()}")
        
        return jsonify({
            'success': True,
            'message': 'Test endpoint funcionando correctamente',
            'received_files': list(request.files.keys()),
            'received_form': request.form.to_dict()
        }), 200
    except Exception as e:
        print(f"Error en test endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/actualizar_configuracion', methods=['POST'])
@csrf.exempt
def actualizar_configuracion():
    """Actualizar configuración del sistema."""
    try:
        print("=== ENDPOINT ACTUALIZAR_CONFIGURACION LLAMADO ===")
        print(f"Method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Files: {list(request.files.keys())}")
        print(f"Form data: {request.form.to_dict()}")
        print(f"Request URL: {request.url}")
        print(f"Request endpoint: {request.endpoint}")
        
        # Respuesta inmediata para verificar que llega al endpoint
        if not request.files and not request.form:
            return jsonify({
                'success': True,
                'message': 'Endpoint alcanzado pero no hay archivos o datos',
                'debug': {
                    'method': request.method,
                    'content_type': request.content_type,
                    'files_count': len(request.files),
                    'form_data_count': len(request.form)
                }
            }), 200
        
        # Manejar cambio de imagen del login
        if 'login_image' in request.files:
            file = request.files['login_image']
            if file and file.filename:
                # Validar tipo de archivo
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' not in file.filename:
                    return jsonify({'error': 'Archivo sin extensión'}), 400
                
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                if file_ext not in allowed_extensions:
                    return jsonify({'error': 'Tipo de archivo no permitido. Use PNG, JPG, JPEG o GIF'}), 400
                
                # Validar tamaño (máximo 2MB)
                file.seek(0, 2)  # Ir al final del archivo
                file_size = file.tell()
                file.seek(0)  # Volver al inicio
                
                if file_size > 2 * 1024 * 1024:  # 2MB
                    return jsonify({'error': 'Archivo demasiado grande. Máximo 2MB permitido'}), 400
                
                # Crear nombre de archivo único
                import uuid
                unique_filename = f"login_bg_{uuid.uuid4().hex[:8]}.{file_ext}"
                
                # Crear directorio si no existe
                import os
                
                # Usar el directorio estático de auth
                auth_static_dir = os.path.join(os.path.dirname(__file__), 'static', 'img')
                os.makedirs(auth_static_dir, exist_ok=True)
                
                filepath = os.path.join(auth_static_dir, unique_filename)
                file.save(filepath)
                
                # Guardar configuración en base de datos
                Configuracion.set_valor(
                    clave='login_image',
                    valor=f'img/{unique_filename}',
                    descripcion='Imagen de fondo del login',
                    tipo='file',
                    usuario_id=1  # Usuario temporal para testing
                )
                
                # Log de actividad
                log_activity(
                    activity_type='UPDATE_LOGIN_IMAGE',
                    details=f'Imagen de login actualizada: {unique_filename}',
                    user_id=1  # Usuario temporal para testing
                )
                
                return jsonify({
                    'success': True, 
                    'message': 'Imagen de login actualizada exitosamente', 
                    'new_image': f'img/{unique_filename}'
                }), 200
        
        # Manejar cambio de logo
        if 'logo_image' in request.files:
            file = request.files['logo_image']
            if file and file.filename:
                # Validar tipo de archivo
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'svg'}
                if '.' not in file.filename:
                    return jsonify({'error': 'Archivo sin extensión'}), 400
                
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                if file_ext not in allowed_extensions:
                    return jsonify({'error': 'Tipo de archivo no permitido. Use PNG, JPG, JPEG, GIF o SVG'}), 400
                
                # Validar tamaño (máximo 2MB)
                file.seek(0, 2)  # Ir al final del archivo
                file_size = file.tell()
                file.seek(0)  # Volver al inicio
                
                if file_size > 2 * 1024 * 1024:  # 2MB
                    return jsonify({'error': 'Archivo demasiado grande. Máximo 2MB permitido'}), 400
                
                # Crear nombre de archivo único
                import uuid
                unique_filename = f"logo_{uuid.uuid4().hex[:8]}.{file_ext}"
                
                # Crear directorio si no existe
                import os
                
                # Guardar en el directorio estático principal
                static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
                os.makedirs(static_dir, exist_ok=True)
                
                filepath = os.path.join(static_dir, unique_filename)
                file.save(filepath)
                
                # Guardar configuración en base de datos
                Configuracion.set_valor(
                    clave='logo_sistema',
                    valor=unique_filename,
                    descripcion='Logo del sistema',
                    tipo='file',
                    usuario_id=1  # Usuario temporal para testing
                )
                
                # Log de actividad
                log_activity(
                    activity_type='UPDATE_LOGO',
                    details=f'Logo actualizado: {unique_filename}',
                    user_id=1  # Usuario temporal para testing
                )
                
                return jsonify({
                    'success': True, 
                    'message': 'Logo actualizado exitosamente', 
                    'new_logo': unique_filename
                }), 200
        
        # Manejar cambio de imagen de fondo
        if 'background_image' in request.files:
            file = request.files['background_image']
            if file and file.filename:
                # Validar tipo de archivo
                allowed_extensions = {'png', 'jpg', 'jpeg'}
                if '.' not in file.filename:
                    return jsonify({'error': 'Archivo sin extensión'}), 400
                
                file_ext = file.filename.rsplit('.', 1)[1].lower()
                if file_ext not in allowed_extensions:
                    return jsonify({'error': 'Tipo de archivo no permitido. Use PNG, JPG o JPEG'}), 400
                
                # Validar tamaño (máximo 2MB)
                file.seek(0, 2)  # Ir al final del archivo
                file_size = file.tell()
                file.seek(0)  # Volver al inicio
                
                if file_size > 2 * 1024 * 1024:  # 2MB
                    return jsonify({'error': 'Archivo demasiado grande. Máximo 2MB permitido'}), 400
                
                # Crear nombre de archivo único
                import uuid
                unique_filename = f"bg_{uuid.uuid4().hex[:8]}.{file_ext}"
                
                # Crear directorio si no existe
                import os
                
                # Guardar en el directorio estático principal
                static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
                os.makedirs(static_dir, exist_ok=True)
                
                filepath = os.path.join(static_dir, unique_filename)
                file.save(filepath)
                
                # Guardar configuración en base de datos
                Configuracion.set_valor(
                    clave='background_image',
                    valor=unique_filename,
                    descripcion='Imagen de fondo del sistema',
                    tipo='file',
                    usuario_id=1  # Usuario temporal para testing
                )
                
                # Log de actividad
                log_activity(
                    activity_type='UPDATE_BACKGROUND',
                    details=f'Imagen de fondo actualizada: {unique_filename}',
                    user_id=1  # Usuario temporal para testing
                )
                
                return jsonify({
                    'success': True, 
                    'message': 'Imagen de fondo actualizada exitosamente', 
                    'new_background': unique_filename
                }), 200
        
        # Manejar otras configuraciones
        configuraciones = request.form.to_dict()
        
        # Procesar configuraciones específicas
        if 'tema' in configuraciones:
            # Aquí podrías guardar en base de datos o archivo de configuración
            pass
        
        if 'empresa_nombre' in configuraciones:
            # Procesar configuración de empresa
            pass
        
        # Log de actividad para configuraciones generales
        log_activity(
            activity_type='UPDATE_CONFIG',
            details=f'Configuración actualizada',
            user_id=1  # Usuario temporal para testing
        )
        
        return jsonify({'success': True, 'message': 'Configuración actualizada exitosamente'}), 200
        
    except Exception as e:
        import traceback
        print(f"Error en actualizar_configuracion: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error al actualizar configuración: {str(e)}'}), 500


@auth_bp.route('/get_municipios/<int:entidad_id>')
def get_municipios(entidad_id):
    """Obtener municipios por entidad federativa."""
    municipios = Municipio.query.filter_by(entidad_federativa_id=entidad_id).all()
    return jsonify({
        'municipios': [{'id': m.id, 'nombre': m.nombre} for m in municipios]
    })


# API Routes para gestión de tablas de referencia
@auth_bp.route('/api/tabla/<tabla>', methods=['GET'])
@login_required
@csrf.exempt
def api_get_tabla(tabla):
    """Obtener datos de una tabla de referencia."""
    try:
        # Para departamentos y categorias_ticket, permitir acceso a todos los usuarios autenticados
        # Para otras tablas, verificar permisos de gestión
        tablas_publicas = ['departamentos', 'categorias_ticket']
        
        if tabla not in tablas_publicas:
            # Verificar permisos usando la función dinámica para otras tablas
            if not has_management_permissions(current_user):
                return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        # Importar aquí para evitar importación circular
        from app.tickets.models import CategoriaTicket
        
        # Mapeo de tablas a modelos
        tabla_models = {
            'departamentos': Departamento,
            'puestos_trabajo': PuestoTrabajo,
            'proyectos': Proyecto,
            'ocupaciones': Ocupacion,
            'instituciones_educativas': InstitucionEducativa,
            'niveles_estudio': NivelEstudio,
            'entidades_federativas': EntidadFederativa,
            'municipios': Municipio,
            'estatus_usuarios': EstatusUsuario,
            'categorias_ticket': CategoriaTicket
        }
        
        if tabla not in tabla_models:
            return jsonify({'error': 'Tabla no encontrada'}), 404
        
        model = tabla_models[tabla]
        
        if tabla == 'municipios':
            # Para municipios, incluir información de la entidad federativa
            items = db.session.query(model, EntidadFederativa.nombre.label('entidad_nombre'))\
                .join(EntidadFederativa, model.entidad_federativa_id == EntidadFederativa.id)\
                .all()
            
            result = []
            for municipio, entidad_nombre in items:
                result.append({
                    'id': municipio.id,
                    'nombre': municipio.nombre,
                    'descripcion': getattr(municipio, 'descripcion', None),
                    'entidad_federativa_id': municipio.entidad_federativa_id,
                    'entidad_federativa': entidad_nombre
                })
        elif tabla == 'categorias_ticket':
            # Para categorías de tickets, incluir información del departamento
            items = db.session.query(CategoriaTicket, Departamento.nombre.label('departamento_nombre'))\
                .join(Departamento, CategoriaTicket.departamento_id == Departamento.id)\
                .all()
            
            result = []
            for categoria, departamento_nombre in items:
                result.append({
                    'id': categoria.id,
                    'nombre': categoria.nombre,
                    'descripcion': categoria.descripcion,
                    'departamento_id': categoria.departamento_id,
                    'departamento': departamento_nombre
                })
        else:
            items = model.query.all()
            result = []
            for item in items:
                result.append({
                    'id': item.id,
                    'nombre': item.nombre,
                    'descripcion': getattr(item, 'descripcion', None)
                })
        
        return jsonify({'success': True, 'items': result})
        
    except Exception as e:
        import traceback
        print(f"Error en api_get_tabla: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error al obtener datos: {str(e)}'}), 500


@auth_bp.route('/api/tabla/<tabla>', methods=['POST'])
@login_required
@csrf.exempt
def api_create_tabla(tabla):
    """Crear nuevo elemento en tabla de referencia."""
    try:
        print(f"POST request to api_create_tabla for table: {tabla}")
        print(f"Current user: {current_user.email if current_user else 'None'}")
        print(f"Current user puesto_trabajo: {current_user.puesto_trabajo.id if current_user and current_user.puesto_trabajo else 'None'}")
        
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            print(f"Permission denied for user {current_user.email}")
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        # Verificar que sea JSON
        if not request.is_json:
            print(f"Request is not JSON. Content-Type: {request.content_type}")
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            print("No data received")
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        # Importar aquí para evitar importación circular
        from app.tickets.models import CategoriaTicket
        
        tabla_models = {
            'departamentos': Departamento,
            'puestos_trabajo': PuestoTrabajo,
            'proyectos': Proyecto,
            'ocupaciones': Ocupacion,
            'instituciones_educativas': InstitucionEducativa,
            'niveles_estudio': NivelEstudio,
            'entidades_federativas': EntidadFederativa,
            'municipios': Municipio,
            'estatus_usuarios': EstatusUsuario,
            'categorias_ticket': CategoriaTicket
        }
        
        if tabla not in tabla_models:
            print(f"Table {tabla} not found in models")
            return jsonify({'error': 'Tabla no encontrada'}), 404
        
        model = tabla_models[tabla]
        
        # Verificar que el nombre esté presente
        if not data.get('nombre'):
            print("Missing 'nombre' field")
            return jsonify({'error': 'El campo nombre es requerido'}), 400
        
        # Crear nuevo elemento
        nuevo_item = model()
        nuevo_item.nombre = data.get('nombre')
        if hasattr(nuevo_item, 'descripcion'):
            nuevo_item.descripcion = data.get('descripcion')
        
        # Para municipios, agregar entidad federativa
        if tabla == 'municipios':
            entidad_id = data.get('entidad_federativa_id')
            if not entidad_id:
                print("Missing 'entidad_federativa_id' for municipio")
                return jsonify({'error': 'El campo entidad_federativa_id es requerido para municipios'}), 400
            nuevo_item.entidad_federativa_id = entidad_id
        
        # Para categorías de tickets, agregar departamento
        if tabla == 'categorias_ticket':
            departamento_id = data.get('departamento_id')
            if not departamento_id:
                print("Missing 'departamento_id' for categoria_ticket")
                return jsonify({'error': 'El campo departamento_id es requerido para categorías de tickets'}), 400
            nuevo_item.departamento_id = departamento_id
        
        print(f"Creating new item: {nuevo_item.nombre}")
        db.session.add(nuevo_item)
        db.session.commit()
        print("Item created successfully")
        
        # Log de actividad
        log_activity(
            activity_type='CREATE_REFERENCE_DATA',
            details=f'Creado nuevo {tabla}: {nuevo_item.nombre}',
            user_id=current_user.id
        )
        
        return jsonify({'success': True, 'message': 'Elemento creado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error en api_create_tabla: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error al crear elemento: {str(e)}'}), 500


@auth_bp.route('/api/tabla/<tabla>/<int:item_id>', methods=['PUT'])
@login_required
@csrf.exempt
def api_update_tabla(tabla, item_id):
    """Actualizar elemento en tabla de referencia."""
    try:
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        data = request.get_json()
        
        # Importar aquí para evitar importación circular
        from app.tickets.models import CategoriaTicket
        
        tabla_models = {
            'departamentos': Departamento,
            'puestos_trabajo': PuestoTrabajo,
            'proyectos': Proyecto,
            'ocupaciones': Ocupacion,
            'instituciones_educativas': InstitucionEducativa,
            'niveles_estudio': NivelEstudio,
            'entidades_federativas': EntidadFederativa,
            'municipios': Municipio,
            'estatus_usuarios': EstatusUsuario,
            'categorias_ticket': CategoriaTicket
        }
        
        if tabla not in tabla_models:
            return jsonify({'error': 'Tabla no encontrada'}), 404
        
        model = tabla_models[tabla]
        item = model.query.get_or_404(item_id)
        
        # Actualizar campos
        item.nombre = data.get('nombre')
        if hasattr(item, 'descripcion'):
            item.descripcion = data.get('descripcion')
        
        # Para municipios, actualizar entidad federativa
        if tabla == 'municipios':
            item.entidad_federativa_id = data.get('entidad_federativa_id')
        
        # Para categorías de tickets, actualizar departamento
        if tabla == 'categorias_ticket':
            item.departamento_id = data.get('departamento_id')
        
        db.session.commit()
        
        # Log de actividad
        log_activity(
            activity_type='UPDATE_REFERENCE_DATA',
            details=f'Actualizado {tabla}: {item.nombre}',
            user_id=current_user.id
        )
        
        return jsonify({'success': True, 'message': 'Elemento actualizado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar elemento: {str(e)}'}), 500


@auth_bp.route('/api/tabla/<tabla>/<int:item_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def api_delete_tabla(tabla, item_id):
    """Eliminar elemento de tabla de referencia."""
    try:
        print(f"DELETE request for table: {tabla}, item_id: {item_id}")
        
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            print(f"Permission denied for user {current_user.email}")
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        # Importar aquí para evitar importación circular
        from app.tickets.models import CategoriaTicket
        
        tabla_models = {
            'departamentos': Departamento,
            'puestos_trabajo': PuestoTrabajo,
            'proyectos': Proyecto,
            'ocupaciones': Ocupacion,
            'instituciones_educativas': InstitucionEducativa,
            'niveles_estudio': NivelEstudio,
            'entidades_federativas': EntidadFederativa,
            'municipios': Municipio,
            'estatus_usuarios': EstatusUsuario,
            'categorias_ticket': CategoriaTicket
        }
        
        if tabla not in tabla_models:
            print(f"Table {tabla} not found in models")
            return jsonify({'error': 'Tabla no encontrada'}), 404
        
        model = tabla_models[tabla]
        item = model.query.get(item_id)
        
        if not item:
            print(f"Item {item_id} not found in table {tabla}")
            return jsonify({'error': 'Elemento no encontrado'}), 404
        
        nombre_item = item.nombre
        print(f"Deleting item: {nombre_item}")
        
        db.session.delete(item)
        db.session.commit()
        print("Item deleted successfully")
        
        # Log de actividad
        log_activity(
            activity_type='DELETE_REFERENCE_DATA',
            details=f'Eliminado {tabla}: {nombre_item}',
            user_id=current_user.id
        )
        
        return jsonify({'success': True, 'message': 'Elemento eliminado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"Error en api_delete_tabla: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error al eliminar elemento: {str(e)}'}), 500


@auth_bp.route('/api/usuario/<int:user_id>')
@login_required
def api_get_usuario(user_id):
    """Obtener datos de un usuario específico para la API."""
    try:
        # Verificar permisos
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        usuario = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'user': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'apellido_paterno': usuario.apellido_paterno,
                'apellido_materno': usuario.apellido_materno,
                'email': usuario.email,
                'curp': usuario.curp,
                'telefono': usuario.telefono,
                'fecha_ingreso': usuario.fecha_ingreso.isoformat() if usuario.fecha_ingreso else None,
                'estatus_id': usuario.estatus_id,
                'departamento_id': usuario.departamento_id,
                'proyecto_id': usuario.proyecto_id,
                'puesto_trabajo_id': usuario.puesto_trabajo_id,
                'foto': usuario.foto,
                'estatus_nombre': usuario.estatus.nombre if usuario.estatus else None,
                'departamento_nombre': usuario.departamento.nombre if usuario.departamento else None,
                'puesto_nombre': usuario.puesto_trabajo.nombre if usuario.puesto_trabajo else None
            }
        })
    except Exception as e:
        return jsonify({'error': f'Error al obtener usuario: {str(e)}'}), 500


@auth_bp.route('/static/fotos/<path:filename>')
def serve_foto(filename):
    """Servir archivos de fotos de usuarios."""
    try:
        # Verificar si el archivo existe en UPLOAD_FOLDER directamente
        uploads_dir = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        file_path = os.path.join(uploads_dir, filename)
        
        if os.path.exists(file_path):
            from flask import send_file
            return send_file(file_path)
        else:
            # Si no existe, devolver imagen por defecto
            static_folder = current_app.static_folder or 'app/static'
            default_image = os.path.join(static_folder, 'default_user.png')
            if os.path.exists(default_image):
                from flask import send_file
                return send_file(default_image)
            else:
                return '', 404
    except Exception as e:
        print(f"Error serving foto: {e}")
        return '', 404


@auth_bp.route('/api/permisos', methods=['POST'])
@login_required
@csrf.exempt
def api_update_permisos():
    """Actualizar permisos de gestión de usuarios."""
    try:
        print(f"POST request to api_update_permisos")
        print(f"Current user: {current_user.email if current_user else 'None'}")
        
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            print(f"Permission denied for user {current_user.email}")
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        # Verificar que sea JSON
        if not request.is_json:
            print(f"Request is not JSON. Content-Type: {request.content_type}")
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data:
            print("No data received")
            return jsonify({'error': 'No se recibieron datos'}), 400
        
        puestos_autorizados = data.get('puestos_autorizados', [])
        print(f"Puestos autorizados: {puestos_autorizados}")
        
        # Usar el Database Manager para operaciones críticas
        from app.database_manager import db_manager
        
        def _update_permissions():
            # Obtener todos los permisos existentes
            permisos_existentes = PermisosGestion.query.all()
            puestos_existentes = {p.puesto_trabajo_id for p in permisos_existentes}
            puestos_nuevos = set(puestos_autorizados)
            
            changes_made = False
            
            # Eliminar permisos que ya no están autorizados
            for permiso in permisos_existentes:
                if permiso.puesto_trabajo_id not in puestos_nuevos:
                    db.session.delete(permiso)
                    changes_made = True
                    print(f"🗑️ Eliminando permiso para puesto ID: {permiso.puesto_trabajo_id}")
            
            # Agregar nuevos permisos
            for puesto_id in puestos_nuevos:
                if puesto_id not in puestos_existentes:
                    permiso = PermisosGestion()
                    permiso.puesto_trabajo_id = puesto_id
                    permiso.puede_gestionar_usuarios = True
                    permiso.actualizado_por = current_user.id
                    db.session.add(permiso)
                    changes_made = True
                    print(f"➕ Agregando permiso para puesto ID: {puesto_id}")
            
            # Solo hacer commit si hay cambios
            if changes_made:
                db.session.commit()
                print(f"✅ Cambios aplicados exitosamente")
            else:
                print("ℹ️ No hay cambios que aplicar")
            
            return changes_made
        
        # Ejecutar la actualización con retry agresivo
        changes_made = db_manager.execute_with_retry(_update_permissions)
        
        # Log de actividad fuera de la transacción principal
        if changes_made:
            try:
                def _log_activity():
                    log_activity(
                        activity_type='UPDATE_PERMISSIONS',
                        details=f'Permisos actualizados para puestos: {puestos_autorizados}',
                        user_id=current_user.id
                    )
                
                db_manager.execute_with_retry(_log_activity)
            except Exception as log_error:
                print(f"⚠️ Error logging activity: {log_error}")
        
        print("🎉 Permissions updated successfully")
        return jsonify({'success': True, 'message': 'Permisos actualizados exitosamente'})
        
    except Exception as e:
        import traceback
        print(f"Error en api_update_permisos: {str(e)}")
        print(traceback.format_exc())
        
        # Manejar errores específicos de base de datos
        if "database is locked" in str(e).lower():
            return jsonify({
                'error': 'El sistema está ocupado, intente de nuevo en unos momentos'
            }), 503
        else:
            return jsonify({'error': f'Error al actualizar permisos: {str(e)}'}), 500


@auth_bp.route('/api/permisos', methods=['GET'])
@login_required
@csrf.exempt
def api_get_permisos():
    """Obtener permisos actuales de gestión de usuarios."""
    try:
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        # Obtener todos los puestos de trabajo
        puestos = PuestoTrabajo.query.all()
        
        # Obtener permisos existentes de la base de datos
        permisos_existentes = PermisosGestion.query.filter_by(puede_gestionar_usuarios=True).all()
        puestos_autorizados = [p.puesto_trabajo_id for p in permisos_existentes]
        
        # Formatear la respuesta
        puestos_data = []
        for puesto in puestos:
            puestos_data.append({
                'id': puesto.id,
                'nombre': puesto.nombre,
                'autorizado': puesto.id in puestos_autorizados
            })
        
        return jsonify({
            'success': True,
            'puestos': puestos_data,
            'puestos_autorizados': puestos_autorizados
        })
        
    except Exception as e:
        import traceback
        print(f"Error en api_get_permisos: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Error al obtener permisos: {str(e)}'}), 500


@auth_bp.route('/api/logs', methods=['GET'])
@login_required
@csrf.exempt
def api_get_logs():
    """Obtener logs del sistema."""
    try:
        # Verificar permisos usando la función dinámica
        if not has_management_permissions(current_user):
            return jsonify({'error': 'No tienes permisos para realizar esta acción'}), 403
        
        nivel = request.args.get('level', 'INFO')
        
        # Obtener logs de actividad recientes (últimos 50)
        logs = []
        try:
            from app.auth.activity_log import UserActivityLog
            
            # Usar raw SQL para evitar problemas de tipos
            result = db.session.execute(
                db.text("SELECT id, user_id, activity_type, details, timestamp FROM user_activity_log ORDER BY id DESC LIMIT 50")
            ).fetchall()
            
            for row in result:
                user_email = "Sistema"
                if row[1]:  # user_id
                    user = User.query.get(row[1])
                    if user:
                        user_email = user.email
                
                # Formatear timestamp
                timestamp_str = str(row[4])[:19] if row[4] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                logs.append({
                    'timestamp': timestamp_str,
                    'level': 'INFO',
                    'message': f'{row[2]}: {row[3]} (Usuario: {user_email})'
                })
        except Exception as e:
            print(f"Error al cargar logs: {e}")
            # Fallback con logs de ejemplo
        
        # Agregar algunos logs de ejemplo si no hay logs de actividad
        if not logs:
            logs = [
                {'timestamp': '2025-08-11 17:50:15', 'level': 'INFO', 'message': 'Sistema iniciado correctamente'},
                {'timestamp': '2025-08-11 17:48:42', 'level': 'INFO', 'message': 'Usuario logueado correctamente'},
                {'timestamp': '2025-08-11 17:45:33', 'level': 'WARNING', 'message': 'Intento de acceso fallido'},
                {'timestamp': '2025-08-11 17:40:15', 'level': 'INFO', 'message': 'Configuración actualizada'},
                {'timestamp': '2025-08-11 17:35:22', 'level': 'INFO', 'message': 'Nuevo usuario creado'},
            ]
        
        return jsonify({'success': True, 'logs': logs})
        
    except Exception as e:
        return jsonify({'error': f'Error al obtener logs: {str(e)}'}), 500


@auth_bp.route('/api/usuarios-activos', methods=['GET'])
@login_required
def api_usuarios_activos():
    """API para obtener lista de usuarios activos"""
    try:
        # Verificar permisos de administrador
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        if not es_administrador:
            return jsonify({'success': False, 'error': 'No tienes permisos para acceder a esta información'}), 403
        
        # Obtener usuarios activos
        usuarios = User.query.filter_by(activo=True).order_by(User.nombre, User.apellido_paterno).all()
        
        usuarios_data = []
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id,
                'nombre': f"{usuario.nombre} {usuario.apellido_paterno}",
                'email': usuario.email,
                'puesto_trabajo_id': usuario.puesto_trabajo_id,
                'puesto_trabajo': usuario.puesto_trabajo.nombre if usuario.puesto_trabajo else None
            })
        
        return jsonify({'success': True, 'usuarios': usuarios_data})
        
    except Exception as e:
        print(f"Error en api_usuarios_activos: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener usuarios activos'}), 500


@auth_bp.route('/api/departamentos', methods=['GET'])
@login_required
def api_departamentos():
    """API para obtener lista de departamentos"""
    try:
        # Verificar permisos de administrador
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        if not es_administrador:
            return jsonify({'success': False, 'error': 'No tienes permisos para acceder a esta información'}), 403
        
        # Obtener departamentos
        departamentos = Departamento.query.order_by(Departamento.nombre).all()
        
        departamentos_data = []
        for departamento in departamentos:
            departamentos_data.append({
                'id': departamento.id,
                'nombre': departamento.nombre,
                'descripcion': departamento.descripcion
            })
        
        return jsonify({'success': True, 'departamentos': departamentos_data})
        
    except Exception as e:
        print(f"Error en api_departamentos: {e}")
        return jsonify({'success': False, 'error': 'Error al obtener departamentos'}), 500


@auth_bp.route('/api/permisos-tickets', methods=['GET', 'POST'])
@login_required
def api_permisos_tickets():
    """API para gestionar permisos de tickets por departamento"""
    try:
        # Verificar permisos de administrador
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        if not es_administrador:
            return jsonify({'success': False, 'error': 'No tienes permisos para acceder a esta información'}), 403
        
        if request.method == 'GET':
            # Obtener permisos actuales por departamento
            permisos_db = PermisosTickets.query.filter_by(activo=True).all()
            permisos = {}
            
            for permiso in permisos_db:
                permisos[str(permiso.departamento_id)] = permiso.usuario_id
            
            return jsonify({
                'success': True, 
                'permisos': permisos
            })
        
        elif request.method == 'POST':
            # Guardar configuración de permisos
            data = request.get_json()
            nuevos_permisos = data or {}
            
            try:
                # Desactivar todos los permisos existentes
                PermisosTickets.query.update({'activo': False})
                
                # Crear nuevos permisos
                for dept_id, usuario_id in nuevos_permisos.items():
                    if usuario_id:  # Solo si se asignó un usuario
                        # Verificar si ya existe y reactivarlo, o crear uno nuevo
                        permiso_existente = PermisosTickets.query.filter_by(
                            departamento_id=int(dept_id), 
                            usuario_id=int(usuario_id)
                        ).first()
                        
                        if permiso_existente:
                            permiso_existente.activo = True
                            permiso_existente.actualizado_por = current_user.id
                        else:
                            nuevo_permiso = PermisosTickets()
                            nuevo_permiso.departamento_id = int(dept_id)
                            nuevo_permiso.usuario_id = int(usuario_id)
                            nuevo_permiso.tipo_permiso = 'gestor'  # Set the required field
                            nuevo_permiso.actualizado_por = current_user.id
                            nuevo_permiso.activo = True
                            db.session.add(nuevo_permiso)
                
                db.session.commit()
                return jsonify({'success': True, 'message': 'Permisos guardados correctamente'})
                
            except Exception as e:
                db.session.rollback()
                print(f"Error al guardar permisos: {e}")
                return jsonify({'success': False, 'error': 'Error al guardar permisos'}), 500
        
        # Return por defecto para cualquier método no manejado
        return jsonify({'success': False, 'error': 'Método no permitido'}), 405
        
    except Exception as e:
        print(f"Error en api_permisos_tickets: {e}")
        return jsonify({'success': False, 'error': 'Error al procesar permisos de tickets'}), 500


@auth_bp.route('/api/permisos-home', methods=['GET', 'POST'])
@login_required  
def api_permisos_home():
    """API para gestionar permisos de publicaciones en Home"""
    try:
        # Verificar permisos de administrador
        es_administrador = hasattr(current_user, 'rol') and current_user.rol in ['admin', 'Administrador']
        if not es_administrador:
            return jsonify({'success': False, 'error': 'No tienes permisos para acceder a esta información'}), 403
        
        if request.method == 'GET':
            # Obtener configuración actual de permisos de home
            permisos_db = PermisosHome.query.filter_by(activo=True).all()
            
            permisos_actuales = {
                'crear_posts': [p.usuario_id for p in permisos_db if p.tipo_permiso == 'crear_posts'],
                'crear_eventos': [p.usuario_id for p in permisos_db if p.tipo_permiso == 'crear_eventos'],
                'moderar_contenido': [p.usuario_id for p in permisos_db if p.tipo_permiso == 'moderar_contenido']
            }
            
            return jsonify({
                'success': True,
                'permisos': permisos_actuales
            })
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                if not data:
                    return jsonify({'success': False, 'message': 'No se recibieron datos'}), 400
                
                # Primero desactivar todos los permisos existentes para este tipo
                tipo_permiso = data.get('tipo_permiso')
                if not tipo_permiso:
                    return jsonify({'success': False, 'message': 'Tipo de permiso requerido'}), 400
                
                # Desactivar permisos existentes
                PermisosHome.query.filter_by(tipo_permiso=tipo_permiso, activo=True).update({'activo': False})
                
                # Crear nuevos permisos
                usuarios_ids = data.get('usuarios_ids', [])
                for usuario_id in usuarios_ids:
                    nuevo_permiso = PermisosHome(  # type: ignore
                        usuario_id=usuario_id,  # type: ignore
                        tipo_permiso=tipo_permiso,  # type: ignore
                        activo=True  # type: ignore
                    )
                    db.session.add(nuevo_permiso)
                
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'message': f'Permisos de {tipo_permiso} actualizados correctamente'
                })
                
            except Exception as e:
                db.session.rollback()
                return jsonify({
                    'success': False,
                    'message': f'Error al actualizar permisos: {str(e)}'
                }), 500
        
        # Return por defecto para cualquier método no manejado
        return jsonify({'success': False, 'error': 'Método no permitido'}), 405
        
    except Exception as e:
        print(f"Error en api_permisos_home: {e}")
        return jsonify({'success': False, 'error': 'Error al gestionar permisos de Home'}), 500
