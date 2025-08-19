from flask import render_template, Blueprint
from flask_login import login_required, current_user
from datetime import datetime
from app.perfil import perfil_bp

@perfil_bp.route('/')
@login_required
def perfil():
    # Aquí se pueden consultar logros, constancias y organigrama del usuario
    return render_template('perfil/perfil.html', user=current_user, now=datetime.now())
