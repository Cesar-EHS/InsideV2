from flask import Blueprint

perfil_bp = Blueprint('perfil', __name__, template_folder='templates', static_folder='static')

from app.perfil import routes
