import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_por_defecto')
    
    # Configurar la ruta de la base de datos de forma más robusta
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Si hay una variable de entorno, usarla, sino usar la ruta por defecto
    database_url = os.getenv('SQLALCHEMY_DATABASE_URI')
    if database_url:
        # Si la URL de la base de datos es relativa (empieza con sqlite:///), convertirla a absoluta
        if database_url.startswith('sqlite:///') and not database_url.startswith('sqlite:////'):
            # Extraer solo el nombre del archivo después de sqlite:///
            db_file = database_url.replace('sqlite:///', '')
            # Crear ruta absoluta
            SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, db_file)}'
        else:
            SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Ruta por defecto usando la carpeta instance
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "base_datos.db")}'
    
    # Debug: mostrar la ruta final
    print(f"Database URL configurada: {SQLALCHEMY_DATABASE_URI}")
    print(f"Archivo existe: {os.path.exists(SQLALCHEMY_DATABASE_URI.replace('sqlite:///', ''))}")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
