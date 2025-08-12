from datetime import datetime, timedelta, timezone
from typing import Optional, List, Any
from flask import session, request  # type: ignore[misc]
# Eliminamos la importación de wraps ya que no se usa
import re

class LoginAttemptManager:
    MAX_ATTEMPTS: int = 5
    LOCKOUT_TIME: int = 15  # minutos

    @staticmethod
    def get_attempts() -> int:
        return session.get('login_attempts', 0)

    @staticmethod
    def get_lockout_time() -> Optional[float]:
        return session.get('lockout_until', None)

    @staticmethod
    def increment_attempts() -> None:
        attempts: int = session.get('login_attempts', 0) + 1
        session['login_attempts'] = attempts
        if attempts >= LoginAttemptManager.MAX_ATTEMPTS:
            session['lockout_until'] = (datetime.now() + timedelta(minutes=LoginAttemptManager.LOCKOUT_TIME)).timestamp()

    @staticmethod
    def reset_attempts() -> None:
        session.pop('login_attempts', None)
        session.pop('lockout_until', None)

    @staticmethod
    def is_locked_out() -> bool:
        lockout_time = session.get('lockout_until')
        if lockout_time:
            if datetime.now().timestamp() < lockout_time:
                return True
            else:
                LoginAttemptManager.reset_attempts()
        return False

class PasswordPolicy:
    MIN_LENGTH: int = 8
    REQUIRES_UPPER: bool = True
    REQUIRES_LOWER: bool = True
    REQUIRES_DIGIT: bool = True
    REQUIRES_SPECIAL: bool = True

    @staticmethod
    def validate_password(password: str) -> List[str]:
        """
        Valida que la contraseña cumpla con los requisitos de seguridad.
        
        Args:
            password: La contraseña a validar
            
        Returns:
            Lista de errores encontrados. Lista vacía si la contraseña es válida.
        """
        errors: List[str] = []
        if len(password) < PasswordPolicy.MIN_LENGTH:
            errors.append(f"La contraseña debe tener al menos {PasswordPolicy.MIN_LENGTH} caracteres")
        
        if PasswordPolicy.REQUIRES_UPPER and not any(c.isupper() for c in password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")
        
        if PasswordPolicy.REQUIRES_LOWER and not any(c.islower() for c in password):
            errors.append("La contraseña debe contener al menos una letra minúscula")
        
        if PasswordPolicy.REQUIRES_DIGIT and not any(c.isdigit() for c in password):
            errors.append("La contraseña debe contener al menos un número")
        
        if PasswordPolicy.REQUIRES_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("La contraseña debe contener al menos un carácter especial")
        
        return errors

def log_activity(user_id: int, activity_type: str, details: Optional[str] = None) -> None:
    """
    Registra actividad relacionada con la autenticación.
    
    Args:
        user_id: ID del usuario que realizó la actividad
        activity_type: Tipo de actividad (login, logout, password_change, etc.)
        details: Detalles adicionales de la actividad (opcional)
    """
    from app import db
    from flask import request
    
    class UserActivity(db.Model):  # type: ignore
        __tablename__ = 'auth_activity_log'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
        activity_type = db.Column(db.String(50), nullable=False)
        details = db.Column(db.Text, nullable=True)
        ip_address = db.Column(db.String(45), nullable=True)
        user_agent = db.Column(db.String(255), nullable=True)
        timestamp = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    activity: Any = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        details=details,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string
    )
    db.session.add(activity)  # type: ignore[attr-defined]
    db.session.commit()  # type: ignore[attr-defined]
