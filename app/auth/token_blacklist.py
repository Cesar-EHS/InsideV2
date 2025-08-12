from __future__ import annotations
from datetime import datetime
from app import db
from typing import Optional

class TokenBlacklist(db.Model):  # type: ignore[misc]
    """Modelo para almacenar tokens invalidados."""
    __tablename__ = 'token_blacklist'
    __allow_unmapped__ = True
    
    # Campos principales
    id: int = db.Column(db.Integer, primary_key=True)  # type: ignore[misc]
    token: str = db.Column(db.String(500), unique=True, nullable=False)  # type: ignore[misc]
    blacklisted_on: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # type: ignore[misc]
    type: str = db.Column(db.String(20), nullable=False)  # type: ignore[misc] # 'access', 'refresh', 'reset'

    # Campos de auditoría
    created_at: datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # type: ignore[misc]
    updated_at: Optional[datetime] = db.Column(db.DateTime, onupdate=datetime.utcnow)  # type: ignore[misc]

    def __init__(self, token: str, type_: str = 'access') -> None:
        """Inicializa un nuevo registro de token en lista negra.
        
        Args:
            token: El token a poner en lista negra
            type_: El tipo de token ('access', 'refresh', 'reset')
        """
        self.token = token
        self.type = type_
        self.blacklisted_on = datetime.utcnow()

    def __repr__(self) -> str:
        """Devuelve una representación legible del objeto."""
        return f'<TokenBlacklist {self.token[:10]}... ({self.type})>'

    @classmethod
    def check_blacklist(cls, token: str) -> bool:
        """Verifica si un token está en la lista negra.
        
        Args:
            token: El token a verificar
        
        Returns:
            bool: True si el token está en lista negra, False en caso contrario
        """
        return cls.query.filter_by(token=token).first() is not None

    @staticmethod
    def is_blacklisted(token: str) -> bool:
        """Verifica si un token está en la lista negra."""
        return TokenBlacklist.query.filter_by(token=token).first() is not None
