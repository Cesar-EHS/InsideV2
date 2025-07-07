from flask import Blueprint

bp_crecehs = Blueprint('crecehs', __name__, template_folder='templates', static_folder='static')

from app.crecehs import routes
from app.cursos.models import Categoria  # Usar el modelo Categoria desde el módulo cursos
