from flask import Blueprint, current_app
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', static_folder='static')

def create_fotos_folder():
    fotos_path = os.path.join(current_app.root_path, 'auth', 'static', 'fotos')
    os.makedirs(fotos_path, exist_ok=True)
    return fotos_path

@auth_bp.before_app_request
def ensure_fotos_folder():
    create_fotos_folder()

from app.auth import routes  # Importa rutas para registrar en el blueprint
