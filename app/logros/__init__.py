from flask import Blueprint

bp_logros = Blueprint('logros', __name__, template_folder='templates', static_folder='static')

from app.logros import routes  # Importar rutas al final para evitar problemas circulares
