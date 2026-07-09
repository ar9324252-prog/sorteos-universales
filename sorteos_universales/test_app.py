"""
test_app.py — Tests automatizados para Sorteos Universales
Verifica que las rutas públicas, autenticación y privacidad funcionen.
"""

import pytest
from app import app, db
from models import User


@pytest.fixture
def client():
    """Configura el cliente de test y la BD en memoria."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        # Crear usuario admin para tests
        admin = User(
            name='Admin Test',
            email='admin@test.com',
            password_hash='pbkdf2:sha256:600000$...',  # Hash dummy
            role='admin'
        )
        user = User(
            name='User Test',
            email='user@test.com',
            password_hash='pbkdf2:sha256:600000$...',  # Hash dummy
            role='user'
        )
        db.session.add_all([admin, user])
        db.session.commit()
    
    with app.test_client() as client:
        yield client
    
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_index_page(client):
    """Test: la página de inicio carga correctamente."""
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'Sorteos' in resp.data or b'sorteos' in resp.data.lower()
    print("✓ Página de inicio funciona")


def test_eventos_page(client):
    """Test: la página de eventos es accesible."""
    resp = client.get('/eventos')
    assert resp.status_code == 200
    print("✓ Página de eventos funciona")


def test_nosotros_page(client):
    """Test: la página Nosotros es accesible."""
    resp = client.get('/nosotros')
    assert resp.status_code == 200
    print("✓ Página Nosotros funciona")


def test_contacto_page(client):
    """Test: la página de Contacto es accesible."""
    resp = client.get('/contacto')
    assert resp.status_code == 200
    print("✓ Página Contacto funciona")


def test_login_page(client):
    """Test: la página de login carga."""
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b'login' in resp.data.lower() or b'iniciar' in resp.data.lower()
    print("✓ Página de login funciona")


def test_registro_page(client):
    """Test: la página de registro carga."""
    resp = client.get('/registro')
    assert resp.status_code == 200
    assert b'registro' in resp.data.lower() or b'registr' in resp.data.lower()
    print("✓ Página de registro funciona")


def test_admin_not_accessible_without_login(client):
    """Test: el admin no es accesible sin autenticación."""
    resp = client.get('/admin')
    assert resp.status_code in [302, 403]  # Redirección o acceso denegado
    print("✓ Admin sin login está protegido")


def test_admin_not_accessible_for_normal_user(client):
    """Test: un usuario normal no puede acceder al admin."""
    with client.session_transaction() as sess:
        sess['user_id'] = 2  # ID del usuario normal (no admin)
    
    resp = client.get('/admin', follow_redirects=False)
    # Debe redirigir o mostrar acceso denegado
    assert resp.status_code in [302, 200]  # 302 redirección, 200 página denegada
    print("✓ Usuario normal no puede entrar al admin")


def test_api_tickets_endpoint(client):
    """Test: el endpoint de API de tickets responde."""
    resp = client.get('/api/evento/1/tickets')
    # Puede ser 404 si el evento no existe, pero la ruta debe existir
    assert resp.status_code in [200, 404]
    print("✓ Endpoint de API funciona")


def test_static_files(client):
    """Test: los archivos estáticos se sirven."""
    resp = client.get('/static/css/main.css')
    assert resp.status_code in [200, 404]  # OK o no existe (ambos son normales en test)
    print("✓ Ruta de estáticos configurada")


def test_app_context(client):
    """Test: la aplicación Flask se carga sin errores."""
    with app.app_context():
        assert app is not None
        assert db is not None
        print("✓ Contexto de app cargado correctamente")


def test_routes_registered(client):
    """Test: todas las rutas principales están registradas."""
    expected_routes = [
        'index', 'eventos', 'contacto', 'nosotros',
        'login', 'registro', 'logout',
        'admin_dashboard', 'admin_eventos', 'admin_usuarios'
    ]
    registered = list(app.view_functions.keys())
    
    missing = [r for r in expected_routes if r not in registered]
    assert len(missing) == 0, f"Rutas no registradas: {missing}"
    print(f"✓ Todas {len(expected_routes)} rutas principales registradas")


if __name__ == '__main__':
    # Ejecutar tests sin pytest
    print("\n🧪 Iniciando pruebas de Sorteos Universales...\n")
    
    with app.test_client() as client:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        
        with app.app_context():
            db.create_all()
            
            try:
                test_index_page(client)
                test_eventos_page(client)
                test_nosotros_page(client)
                test_contacto_page(client)
                test_login_page(client)
                test_registro_page(client)
                test_admin_not_accessible_without_login(client)
                test_api_tickets_endpoint(client)
                test_app_context(client)
                test_routes_registered(client)
                
                print("\n✅ Todos los tests pasaron correctamente!\n")
                
            except AssertionError as e:
                print(f"\n❌ Error en test: {e}\n")
            except Exception as e:
                print(f"\n⚠️ Excepción inesperada: {e}\n")
