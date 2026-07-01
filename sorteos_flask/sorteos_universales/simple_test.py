#!/usr/bin/env python
"""
simple_test.py — Test rápido para Sorteos Universales
"""
import sys
sys.path.insert(0, '.')

from app import app
from flask import url_for

print("\n🧪 Iniciando pruebas rápidas de Sorteos Universales...\n")

# Usar el test client
client = app.test_client()

tests_passed = 0
tests_failed = 0

def test(name, condition, details=""):
    global tests_passed, tests_failed
    if condition:
        print(f"✓ {name}")
        tests_passed += 1
    else:
        print(f"✗ {name} {details}")
        tests_failed += 1

# Test 1: Homepage
resp = client.get('/')
test("Homepage carga (status 200)", resp.status_code == 200, f"Got {resp.status_code}")

# Test 2: Página de eventos
resp = client.get('/eventos')
test("Página de eventos carga", resp.status_code == 200, f"Got {resp.status_code}")

# Test 3: Página nosotros
resp = client.get('/nosotros')
test("Página Nosotros carga", resp.status_code == 200, f"Got {resp.status_code}")

# Test 4: Página contacto
resp = client.get('/contacto')
test("Página Contacto carga", resp.status_code == 200, f"Got {resp.status_code}")

# Test 5: Login page
resp = client.get('/login')
test("Página Login carga", resp.status_code == 200, f"Got {resp.status_code}")

# Test 6: Registro page
resp = client.get('/registro')
test("Página Registro carga", resp.status_code == 200, f"Got {resp.status_code}")

# Test 7: Admin sin autenticación
resp = client.get('/admin', follow_redirects=False)
test("Admin redirige sin autenticación", resp.status_code in [302, 307], f"Got {resp.status_code}")

# Test 8: API de tickets
resp = client.get('/api/evento/1/tickets')
test("API de tickets existe", resp.status_code in [200, 404], f"Got {resp.status_code}")

# Test 9: Rutas registradas
routes = list(app.view_functions.keys())
has_index = 'index' in routes
has_admin = 'admin_dashboard' in routes
has_login = 'login' in routes
test("Rutas clave registradas", has_index and has_admin and has_login, f"index:{has_index}, admin:{has_admin}, login:{has_login}")

# Test 10: Verificar que admin_dashboard existe en el mapa de rutas
url_map = str(app.url_map)
has_admin_route = '/admin' in url_map
test("Ruta /admin existe en mapa", has_admin_route)

print(f"\n{'='*50}")
print(f"Resultados: {tests_passed} pasados, {tests_failed} fallidos")
print(f"{'='*50}\n")

if tests_failed == 0:
    print("✅ ¡TODOS LOS TESTS PASARON!\n")
    sys.exit(0)
else:
    print("❌ Algunos tests fallaron.\n")
    sys.exit(1)
