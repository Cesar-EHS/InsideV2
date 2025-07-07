from flask import Blueprint

bp_cursos = Blueprint(
    'cursos', 
    __name__, 
    url_prefix='/cursos',
    template_folder='templates',
    static_folder='static',
    static_url_path='/cursos/static'
)

from app.cursos import routes  # Importa las rutas para registrar los endpoints
