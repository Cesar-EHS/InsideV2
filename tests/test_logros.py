import pytest
from app import create_app, db
from app.logros.models import Logro

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_logros_index_access(client):
    response = client.get('/logros/')
    assert response.status_code in (200, 302)  # Puede redirigir si no está autenticado

def test_logro_model():
    logro = Logro(titulo='Test', descripcion='Desc', imagen='img.png', fecha_inicio='2025-01-01', creador_id=1)
    assert logro.titulo == 'Test'
    assert logro.descripcion == 'Desc'
    assert logro.imagen == 'img.png'
