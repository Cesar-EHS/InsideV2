from flask import Flask, redirect, url_for  # Importación corregida
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from config import Config
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
import os

csrf = CSRFProtect()

# Cargar variables de entorno desde archivo .env
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
load_dotenv(dotenv_path)

# Inicialización de extensiones
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
cors = CORS()
socketio = SocketIO()
jwt = JWTManager()


def create_app(config_name=None):
    app = Flask(__name__)
    if config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)

    # Crear carpeta de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Inicializar extensiones con la app
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Cambia 'auth.login' si tu endpoint de login tiene otro nombre
    login_manager.login_message = "Por favor, inicia sesión para continuar."
    login_manager.login_message_category = "warning"
    mail.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)

    # IMPORTANTE: importar modelo User aquí para evitar importaciones circulares
    from app.auth.models import User
    from app.models import Conversation, Message  # <-- Importa los modelos de chat para migraciones
    # Registrar función user_loader para flask-login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprints
    from app.search.routes import search_bp
    from app.auth.routes import auth_bp as auth_blueprint
    from app.home.routes import home_bp as home_blueprint
    from app.cursos.routes import bp_cursos as cursos_blueprint
    from app.tickets.routes import bp_tickets as tickets_blueprint
    from app.perfil import perfil_bp as perfil_blueprint
    from app.knowledge.routes import knowledge_bp as knowledge_blueprint
    from app.logros.routes import bp_logros as logros_blueprint
    from app.chat.routes import chat_bp
    # from app.crecehs import bp_crecehs

    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(home_blueprint, url_prefix='/home')
    app.register_blueprint(cursos_blueprint, url_prefix='/cursos')
    app.register_blueprint(tickets_blueprint, url_prefix='/tickets')
    app.register_blueprint(perfil_blueprint, url_prefix='/perfil')
    app.register_blueprint(knowledge_blueprint, url_prefix='/knowledge')
    app.register_blueprint(logros_blueprint, url_prefix='/logros')
    app.register_blueprint(search_bp)
    app.register_blueprint(chat_bp)
    # app.register_blueprint(bp_crecehs, url_prefix='/crecehs')

    # Ruta para servir archivos de uploads (imágenes y evidencias)
    from flask import send_from_directory
    @app.route('/uploads/<path:filename>')
    def uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # Ruta raíz que redirige a /home
    @app.route('/')
    def root():
        return redirect(url_for('home.home'))

    return app