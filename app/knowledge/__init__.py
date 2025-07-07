"""
Blueprint de Knowledge: gestiona rutas, templates y estáticos del módulo de gestión documental.
"""

from flask import Blueprint

knowledge_bp = Blueprint(
    'knowledge',
    __name__,
    template_folder='templates',
    static_folder='static',        # Carpeta relativa dentro de app/knowledge/
    static_url_path='/knowledge/static'  # URL pública para archivos estáticos del blueprint
)

# Importar rutas al final para evitar problemas de dependencias circulares
from . import routes
