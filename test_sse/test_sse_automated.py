#!/usr/bin/env python3
"""
Script de prueba automatizada para SSE - FERREMAS
Ejecuta todas las pruebas de SSE de forma automática

Ubicación: test_sse/test_sse_automated.py
Ejecutar desde la raíz del proyecto: python test_sse/test_sse_automated.py
"""

import requests
import json
import time
import threading
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:5000"
TEST_MESSAGES = []

def log(message):
    """Función para logging con timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_verify_data():
    """Prueba 0: Verificar datos existentes"""
    log("🧪 PRUEBA 0: Verificar datos existentes")
    try:
        # Verificar sucursales
        response = requests.get(f"{BASE_URL}/api/sucursales")
        if response.status_code == 200:
            sucursales = response.json()
            log(f"✅ Sucursales encontradas: {len(sucursales)}")
            for suc in sucursales:
                log(f"   - Sucursal {suc['cod_sucursal']}: {suc['nombre_sucursal']}")
        else:
            log(f"❌ Error obteniendo sucursales: {response.status_code}")
            return False
        
        # Verificar productos
        response = requests.get(f"{BASE_URL}/api/lista-productos")
        if response.status_code == 200:
            productos = response.json()
            log(f"✅ Productos encontrados: {len(productos)}")
            # Buscar FER_007 específicamente
            fer_007 = next((p for p in productos if p['cod_producto'] == 'FER_007'), None)
            if fer_007:
                log(f"✅ Producto FER_007 encontrado: {fer_007['nombre_p']}")
            else:
                log("⚠️ Producto FER_007 no encontrado, usando primer producto disponible")
                if productos:
                    log(f"   - Usando: {productos[0]['cod_producto']}: {productos[0]['nombre_p']}")
        else:
            log(f"❌ Error obteniendo productos: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        log(f"❌ Error verificando datos: {str(e)}")
        return False

def test_connection():
    """Prueba 1: Conexión exitosa"""
    log("🧪 PRUEBA 1: Conexión exitosa")
    try:
        response = requests.get(f"{BASE_URL}/api/notificaciones", stream=True, timeout=5)
        if response.status_code == 200:
            log("✅ Conexión SSE exitosa")
            return True
        else:
            log(f"❌ Error en conexión: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error de conexión: {str(e)}")
        return False

def test_manual_message():
    """Prueba 2: Envío de mensaje manual"""
    log("🧪 PRUEBA 2: Mensaje manual")
    try:
        data = {
            "mensaje": "Prueba automatizada de SSE",
            "cod_sucursal": 1,
            "stock": 5
        }
        response = requests.post(f"{BASE_URL}/api/test-sse", json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                log("✅ Mensaje manual enviado correctamente")
                return True
            else:
                log(f"❌ Error en respuesta: {result}")
                return False
        else:
            log(f"❌ Error HTTP: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error enviando mensaje: {str(e)}")
        return False

def test_order_messages():
    """Prueba 3: Orden de mensajes"""
    log("🧪 PRUEBA 3: Orden de mensajes")
    try:
        response = requests.get(f"{BASE_URL}/api/sse-orden")
        if response.status_code == 200:
            result = response.json()
            log(f"✅ {result['cantidad']} mensajes ordenados enviados")
            return True
        else:
            log(f"❌ Error en prueba de orden: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error en prueba de orden: {str(e)}")
        return False

def test_performance():
    """Prueba 4: Rendimiento"""
    log("🧪 PRUEBA 4: Rendimiento")
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/api/sse-rendimiento")
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            duration_ms = (end_time - start_time) * 1000
            duration_sec = (end_time - start_time)
            
            # Calcular estimación en segundos
            if duration_sec < 1:
                time_estimate = f"{duration_sec:.2f} segundos"
            elif duration_sec < 2:
                time_estimate = f"{duration_sec:.1f} segundo"
            else:
                time_estimate = f"{duration_sec:.0f} segundos aprox."
            
            log(f"✅ {result['cantidad']} mensajes enviados en {duration_ms:.2f}ms ({time_estimate})")
            return True
        else:
            log(f"❌ Error en prueba de rendimiento: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error en prueba de rendimiento: {str(e)}")
        return False

def test_error_json():
    """Prueba 5: Manejo de JSON malformado"""
    log("🧪 PRUEBA 5: JSON malformado")
    try:
        response = requests.get(f"{BASE_URL}/api/sse-error-json")
        if response.status_code == 200:
            result = response.json()
            log(f"✅ JSON malformado enviado: {result['status']}")
            return True
        else:
            log(f"❌ Error en prueba de JSON: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error en prueba de JSON: {str(e)}")
        return False

def test_server_close():
    """Prueba 6: Cierre de servidor"""
    log("🧪 PRUEBA 6: Cierre de servidor")
    try:
        response = requests.get(f"{BASE_URL}/api/sse-cierre")
        if response.status_code == 200:
            result = response.json()
            log(f"✅ Mensaje de cierre enviado: {result['status']}")
            return True
        else:
            log(f"❌ Error en prueba de cierre: {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ Error en prueba de cierre: {str(e)}")
        return False

def test_stock_update():
    """Prueba 7: Actualización de stock"""
    log("🧪 PRUEBA 7: Actualización de stock")
    try:
        # Primero obtener productos disponibles
        response = requests.get(f"{BASE_URL}/api/lista-productos")
        if response.status_code != 200:
            log(f"❌ Error obteniendo productos: {response.status_code}")
            return False
        
        productos = response.json()
        if not productos:
            log("❌ No hay productos disponibles")
            return False
        
        # Buscar FER-002 específicamente o usar el primer producto disponible
        cod_producto = "FER-002"
        fer_002 = next((p for p in productos if p['cod_producto'] == 'FER-002'), None)
        if not fer_002:
            cod_producto = productos[0]['cod_producto']
            log(f"⚠️ FER-002 no encontrado, usando: {cod_producto}")
        else:
            log(f"✅ Producto FER-002 encontrado: {fer_002['nombre_p']}")
        
        # Obtener sucursales disponibles
        response = requests.get(f"{BASE_URL}/api/sucursales")
        if response.status_code != 200:
            log(f"❌ Error obteniendo sucursales: {response.status_code}")
            return False
        
        sucursales = response.json()
        if not sucursales:
            log("❌ No hay sucursales disponibles")
            return False
        
        # Usar la primera sucursal disponible
        cod_sucursal = sucursales[0]['cod_sucursal']
        
        data = {
            "cod_producto": cod_producto,
            "cod_sucursal": cod_sucursal,
            "cantidad": 8  # Solo 8 unidades para no agregar demasiado stock
        }
        
        log(f"📦 Actualizando stock: {cod_producto} en sucursal {cod_sucursal} (+8 unidades)")
        
        response = requests.post(f"{BASE_URL}/api/actualizar-stock", json=data)
        if response.status_code == 200:
            result = response.json()
            log(f"✅ Stock actualizado: {result['stock_actual']} unidades en sucursal {result['sucursal']}")
            return True
        else:
            log(f"❌ Error actualizando stock: {response.status_code}")
            # Intentar con otra sucursal si hay más de una
            if len(sucursales) > 1:
                cod_sucursal = sucursales[1]['cod_sucursal']
                data["cod_sucursal"] = cod_sucursal
                log(f"🔄 Intentando con sucursal alternativa: {cod_sucursal}")
                
                response2 = requests.post(f"{BASE_URL}/api/actualizar-stock", json=data)
                if response2.status_code == 200:
                    result = response2.json()
                    log(f"✅ Stock actualizado en sucursal alternativa: {result['stock_actual']} unidades en sucursal {result['sucursal']}")
                    return True
                else:
                    log(f"❌ Error en ambas sucursales: {response.status_code}, {response2.status_code}")
                    return False
            else:
            return False
    except Exception as e:
        log(f"❌ Error en actualización de stock: {str(e)}")
        return False

def test_multiple_connections():
    """Prueba 8: Múltiples conexiones"""
    log("🧪 PRUEBA 8: Múltiples conexiones")
    
    def create_connection(conn_id):
        try:
            response = requests.get(f"{BASE_URL}/api/notificaciones", stream=True, timeout=3)
            if response.status_code == 200:
                log(f"✅ Conexión {conn_id} establecida")
                return True
            else:
                log(f"❌ Error en conexión {conn_id}: {response.status_code}")
                return False
        except Exception as e:
            log(f"❌ Error en conexión {conn_id}: {str(e)}")
            return False
    
    # Crear 3 conexiones simultáneas
    threads = []
    results = []
    
    for i in range(3):
        thread = threading.Thread(target=lambda i=i: results.append(create_connection(i+1)))
        threads.append(thread)
        thread.start()
    
    # Esperar a que terminen
    for thread in threads:
        thread.join()
    
    success_count = sum(results)
    log(f"✅ {success_count}/3 conexiones exitosas")
    return success_count >= 2  # Al menos 2 de 3 deben funcionar

def run_all_tests():
    """Ejecutar todas las pruebas"""
    log("🚀 INICIANDO PRUEBAS AUTOMATIZADAS SSE")
    log("=" * 50)
    
    tests = [
        ("Verificar datos existentes", test_verify_data),
        ("Conexión exitosa", test_connection),
        ("Mensaje manual", test_manual_message),
        ("Orden de mensajes", test_order_messages),
        ("Rendimiento", test_performance),
        ("JSON malformado", test_error_json),
        ("Cierre de servidor", test_server_close),
        ("Actualización de stock", test_stock_update),
        ("Múltiples conexiones", test_multiple_connections)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # Pausa entre pruebas
        except Exception as e:
            log(f"❌ Error ejecutando {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen de resultados
    log("=" * 50)
    log("📊 RESUMEN DE PRUEBAS")
    log("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        log(f"{status} - {test_name}")
        if result:
            passed += 1
    
    log("=" * 50)
    log(f"🎯 RESULTADO FINAL: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        log("🎉 ¡TODAS LAS PRUEBAS SSE PASARON EXITOSAMENTE!")
    elif passed >= total * 0.8:
        log("⚠️ La mayoría de las pruebas pasaron")
    else:
        log("❌ Muchas pruebas fallaron - revisar implementación")
    
    return passed == total

if __name__ == "__main__":
    print("🧪 SCRIPT DE PRUEBAS AUTOMATIZADAS SSE - FERREMAS")
    print("Ubicación: test_sse/test_sse_automated.py")
    print("Asegúrate de que el servidor Flask esté ejecutándose en http://localhost:5000")
    print()
    
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        log("⏹️ Pruebas interrumpidas por el usuario")
        exit(1)
    except Exception as e:
        log(f"❌ Error fatal: {str(e)}")
        exit(1) 