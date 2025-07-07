# app/home/__init__.py

import os
from flask import Blueprint, current_app

home_bp = Blueprint('home', __name__, template_folder='templates', static_folder='static', static_url_path='/home/static')
upload_dir = os.path.join('app', 'static', 'uploads')
os.makedirs(upload_dir, exist_ok=True)

from app.home import routes
