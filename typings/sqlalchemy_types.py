# Type annotations para SQLAlchemy
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Query
    from sqlalchemy.sql.schema import Column
    from app.auth.models import User, Proyecto
    
# Estas son las clases que usamos en el proyecto
__all__ = ['Query', 'Column', 'User', 'Proyecto']
