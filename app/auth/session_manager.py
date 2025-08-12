from datetime import datetime, timedelta
from typing import Optional
from app import db
from flask import current_app
from app.auth.activity_log import log_activity

class SessionManager:
    """Gestiona las sesiones de usuario."""
    
    @staticmethod
    def create_session(user_id: int, session_id: str) -> None:
        """
        Crea una nueva sesión para un usuario.
        """
        # Primero invalidamos cualquier otra sesión activa
        ActiveSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).update({
            'is_active': False,
            'ended_at': datetime.utcnow()
        })
        
        # Creamos la nueva sesión
        session = ActiveSession(
            user_id=user_id,
            session_id=session_id
        )
        db.session.add(session)
        db.session.commit()
        
        log_activity('session_start', f'Nueva sesión iniciada para usuario {user_id}')
    
    @staticmethod
    def end_session(session_id: str) -> None:
        """
        Finaliza una sesión específica.
        """
        session = ActiveSession.query.filter_by(
            session_id=session_id,
            is_active=True
        ).first()
        
        if session:
            session.is_active = False
            session.ended_at = datetime.utcnow()
            db.session.commit()
            log_activity('session_end', f'Sesión finalizada para usuario {session.user_id}')
    
    @staticmethod
    def is_session_valid(session_id: str) -> bool:
        """
        Verifica si una sesión es válida y no ha expirado.
        """
        session = ActiveSession.query.filter_by(
            session_id=session_id,
            is_active=True
        ).first()
        
        if not session:
            return False
            
        # Verificar timeout por inactividad
        timeout_minutes = current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
        if datetime.utcnow() - session.last_activity > timedelta(minutes=timeout_minutes):
            SessionManager.end_session(session_id)
            return False
            
        return True
    
    @staticmethod
    def update_last_activity(session_id: str) -> None:
        """
        Actualiza el timestamp de última actividad de una sesión.
        """
        session = ActiveSession.query.filter_by(
            session_id=session_id,
            is_active=True
        ).first()
        
        if session:
            session.last_activity = datetime.utcnow()
            db.session.commit()

class ActiveSession(db.Model):  # type: ignore
    """Modelo para rastrear sesiones activas."""
    __tablename__ = 'active_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __init__(self, user_id: int, session_id: str):
        self.user_id = user_id
        self.session_id = session_id
