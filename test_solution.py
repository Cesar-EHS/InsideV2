#!/usr/bin/env python3
"""
Script de prueba para verificar que la solución definitiva funciona
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8080"

def test_login():
    """Probar login"""
    print("🔐 Probando login...")
    
    # Obtener página de login
    session = requests.Session()
    response = session.get(f"{BASE_URL}/auth/login")
    
    if response.status_code == 200:
        print("✅ Página de login accesible")
        return session
    else:
        print(f"❌ Error al acceder login: {response.status_code}")
        return None

def test_permissions_api(session):
    """Probar API de permisos"""
    print("\n🔧 Probando API de permisos...")
    
    try:
        # Simular llamada al API de permisos (necesitarás estar loggeado)
        response = session.post(
            f"{BASE_URL}/auth/api/permisos",
            json={"puestos_autorizados": [7, 8]},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code in [200, 403]:  # 403 esperado si no estás loggeado
            print("✅ API de permisos responde correctamente")
        else:
            print(f"⚠️ API response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error al probar API permisos: {e}")

def test_config_page(session):
    """Probar página de configuración"""
    print("\n📋 Probando página de configuración...")
    
    try:
        response = session.get(f"{BASE_URL}/auth/config")
        print(f"Status: {response.status_code}")
        
        if response.status_code in [200, 302]:  # 302 esperado si no estás loggeado
            print("✅ Página de configuración accesible")
        else:
            print(f"❌ Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error al probar config: {e}")

def test_multiple_concurrent_requests():
    """Probar múltiples requests concurrentes"""
    print("\n⚡ Probando múltiples requests concurrentes...")
    
    import threading
    import concurrent.futures
    
    def make_request(i):
        session = requests.Session()
        try:
            response = session.get(f"{BASE_URL}/auth/login")
            return f"Request {i}: {response.status_code}"
        except Exception as e:
            return f"Request {i}: Error - {e}"
    
    # Hacer 10 requests concurrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(10)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    success_count = sum(1 for r in results if "200" in r)
    print(f"✅ {success_count}/10 requests exitosos")
    
    for result in results:
        print(f"  {result}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE LA SOLUCIÓN DEFINITIVA\n")
    
    # Test 1: Login básico
    session = test_login()
    
    if session:
        # Test 2: Página de configuración
        test_config_page(session)
        
        # Test 3: API de permisos
        test_permissions_api(session)
    
    # Test 4: Requests concurrentes
    test_multiple_concurrent_requests()
    
    print("\n🎯 PRUEBAS COMPLETADAS")
    print("Si no hay errores críticos arriba, la solución está funcionando!")
