from __future__ import annotations
from datetime import datetime
from typing import Optional, Any, TypeVar, Type
from app import db
from flask import request
from flask_login import current_user
from sqlalchemy.ext.declarative import DeclarativeMeta

# Definir un tipo para el modelo base
ModelType = TypeVar("ModelType", bound=DeclarativeMeta)

# Base model para todos los modelos
class BaseModel(db.Model):  # type: ignore[misc,valid-type]
    """Clase base abstracta para todos los modelos."""
    __abstract__ = True
    __allow_unmapped__ = True

class UserActivityLog(BaseModel):
    """Modelo para registrar actividad de usuarios."""
    __tablename__ = 'user_activity_log'

    id: int = db.Column(db.Integer, primary_key=True)  # type: ignore[misc]
    user_id: Optional[int] = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)  # type: ignore[misc]
    activity_type: str = db.Column(db.String(50), nullable=False)  # type: ignore[misc]
    details: Optional[str] = db.Column(db.String(500))  # type: ignore[misc]
    ip_address: Optional[str] = db.Column(db.String(45))  # type: ignore[misc]
    user_agent: Optional[str] = db.Column(db.String(200))  # type: ignore[misc]
    timestamp: datetime = db.Column(db.DateTime, default=datetime.utcnow)  # type: ignore[misc]
    status: str = db.Column(db.String(20))  # type: ignore[misc]
    
    def __init__(self, activity_type: str, details: Optional[str] = None, 
                user_id: Optional[int] = None, status: str = "success") -> None:
        """
        Inicializa un nuevo registro de actividad.
        
        Args:
            activity_type: Tipo de actividad (login, logout, password_change, etc.)
            details: Detalles adicionales sobre la actividad
            user_id: ID del usuario que realizó la actividad
            status: Estado de la actividad (success/failed)
        """
        self.activity_type = activity_type
        self.details = details
        self.user_id = user_id or (current_user.id if not current_user.is_anonymous else None)
        self.ip_address = request.remote_addr
        self.user_agent = request.user_agent.string if request.user_agent else None
        self.status = status

    def __repr__(self) -> str:
        """Devuelve una representación legible del registro de actividad."""
        return f'<UserActivityLog {self.activity_type} by user {self.user_id} at {self.timestamp}>'

def log_activity(activity_type: str, details: Optional[str] = None, 
                user_id: Optional[int] = None, status: str = "success") -> None:
    """
    Registra una actividad en el log con retry agresivo.
    
    Args:
        activity_type: Tipo de actividad (login, logout, password_change, etc.)
        details: Detalles adicionales sobre la actividad
        user_id: ID del usuario que realizó la actividad
        status: Estado de la actividad (success/failed)
    """
    from app.database_manager import db_manager
    
    def _do_log():
        log_entry = UserActivityLog(
            activity_type=activity_type,
            details=details,
            user_id=user_id,
            status=status
        )
        db.session.add(log_entry)
        db.session.commit()
    
    db_manager.execute_with_retry(_do_log)
