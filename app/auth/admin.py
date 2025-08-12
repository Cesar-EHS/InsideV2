from typing import Any, Callable, Optional, Protocol, runtime_checkable, cast
from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import login_required, current_user  # type: ignore
from app import db
from app.models.auth import AuthConfig  # type: ignore
from app.auth.models import User  # type: ignore
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm  # type: ignore
from wtforms import StringField, FileField, TextAreaField, IntegerField, SubmitField  # type: ignore
from wtforms.validators import DataRequired, Length, NumberRange  # type: ignore
from flask_wtf.file import FileAllowed  # type: ignore
import os
from functools import wraps

@runtime_checkable
class AuthConfigProtocol(Protocol):
    """Protocol for AuthConfig model"""
    company_name: str
    login_message: Optional[str]
    lockout_attempts: int
    lockout_time: int
    session_timeout: int
    company_logo: Optional[str]
    login_background: Optional[str]

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates', static_folder='static')

def admin_required(f: Callable[..., Any]) -> Callable[..., Any]:  # type: ignore[type-arg]
    """Decorator that checks if the current user is an admin."""
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:  # type: ignore[type-arg]
        if (not hasattr(current_user, 'is_authenticated') or  # type: ignore
            not current_user.is_authenticated or  # type: ignore
            not hasattr(current_user, 'puesto_trabajo_id') or
            cast(User, current_user).puesto_trabajo_id not in [2, 5, 7, 8, 23, 24]):  # IDs de puestos administrativos
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('home.home'))  # type: ignore[return-value]
        return f(*args, **kwargs)
    return decorated_function

class AuthConfigForm(FlaskForm):
    company_name = StringField('Nombre de la Empresa', validators=[DataRequired(), Length(max=100)])
    company_logo = FileField('Logo de la Empresa', validators=[
        FileAllowed(['jpg', 'png'], 'Solo se permiten imágenes jpg o png!')
    ])
    login_background = FileField('Imagen de Fondo del Login', validators=[
        FileAllowed(['jpg', 'png'], 'Solo se permiten imágenes jpg o png!')
    ])
    login_message = TextAreaField('Mensaje de Bienvenida')
    lockout_attempts = IntegerField('Intentos antes de bloqueo', validators=[DataRequired(), NumberRange(min=1, max=10)])
    lockout_time = IntegerField('Tiempo de bloqueo (minutos)', validators=[DataRequired(), NumberRange(min=1, max=60)])
    session_timeout = IntegerField('Tiempo de inactividad antes de cerrar sesión (minutos)', 
                                 validators=[DataRequired(), NumberRange(min=5, max=120)])
    submit = SubmitField('Guardar Configuración')

@auth_bp.route('/config', methods=['GET', 'POST'])
@login_required
@admin_required
def auth_config() -> Any:  # type: ignore[type-arg]
    """Página de configuración de autenticación.

    Returns:
        Any: Vista renderizada o redirección
    """
    form = AuthConfigForm()
    
    # Get current configuration
    config = AuthConfig.get_config()  # type: ignore[attr-defined]
    if not isinstance(config, AuthConfigProtocol):
        flash('Error loading configuration', 'error')
        return redirect(url_for('home.home'))
    
    if form.validate_on_submit():  # type: ignore[attr-defined]
        # Get form data with type assertions where needed
        if form.company_name.data is None or form.lockout_attempts.data is None or \
           form.lockout_time.data is None or form.session_timeout.data is None:
            flash('Invalid form data', 'error')
            return redirect(url_for('auth.auth_config'))
        
        # Update configuration fields
        config.company_name = form.company_name.data
        config.login_message = form.login_message.data  # type: ignore[assignment]
        config.lockout_attempts = form.lockout_attempts.data
        config.lockout_time = form.lockout_time.data
        config.session_timeout = form.session_timeout.data

        # Manejo de logo
        if form.company_logo.data:
            filename = secure_filename(form.company_logo.data.filename)
            filepath = os.path.join(current_app.root_path, 'auth', 'static', 'images', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            form.company_logo.data.save(filepath)
            config.company_logo = filename

        # Manejo de imagen de fondo
        if form.login_background.data:
            filename = secure_filename(form.login_background.data.filename)
            filepath = os.path.join(current_app.root_path, 'auth', 'static', 'images', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            form.login_background.data.save(filepath)
            config.login_background = filename

        db.session.commit()
        flash('Configuración actualizada exitosamente.', 'success')
        return redirect(url_for('auth.auth_config'))

    # Prellenar el formulario con la configuración actual
    if request.method == 'GET':
        form.company_name.data = config.company_name  # type: ignore[assignment]
        form.login_message.data = config.login_message  # type: ignore[assignment]
        form.lockout_attempts.data = config.lockout_attempts  # type: ignore[assignment]
        form.lockout_time.data = config.lockout_time  # type: ignore[assignment]
        form.session_timeout.data = config.session_timeout  # type: ignore[assignment]

    return render_template('auth/config.html', form=form, config=config)
