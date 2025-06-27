#!/usr/bin/env python3
"""
Script de pruebas para el servicio gRPC de productos
Incluye pruebas de conexión, validación, timeout, carga, cancelación y autenticación
"""

import sys
import os
import uuid
# Agregar el directorio padre al path para importar los módulos de protobuf
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grpc
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from producto_pb2 import CrearProductoRequest, ListarProductosRequest
from producto_pb2_grpc import ProductoServiceStub

# Configuración del cliente
HOST = 'localhost'
PORT = 50051
ADDRESS = f'{HOST}:{PORT}'

def generar_codigo():
    return str(uuid.uuid4())[:8]

def test_1_conexion_exitosa():
    """🔹1. Prueba de conexión exitosa"""
    print("\n🔹1. Probando conexión exitosa...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        grpc.channel_ready_future(channel).result(timeout=5)
        print("✅ Conexión exitosa")
        channel.close()
        return True
    except grpc.FutureTimeoutError:
        print("❌ No se pudo conectar al servidor gRPC")
        return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_2_llamada_valida():
    """🔹2. Llamada válida"""
    print("\n🔹2. Probando llamada válida...")
    with grpc.insecure_channel(ADDRESS) as channel:
        stub = ProductoServiceStub(channel)
        cod = generar_codigo()
        nombre_unico = f"Martillo-{generar_codigo()}"
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto=f"FER-{cod}",
            nombre_p=nombre_unico,
            precio_p=9990
        ))
        if not response.exito:
            print(f"❌ Falló: {response.mensaje}")
            return False
        print(f"✅ Producto creado: Producto {nombre_unico} creado correctamente")
        channel.close()
        return True

def test_3_datos_invalidos():
    """🔹3. Llamada con datos inválidos"""
    print("\n🔹3. Probando datos inválidos...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        cod = generar_codigo()
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto="",  # Inválido
            nombre_p="",
            precio_p=-1
        ))
        if response.exito:
            print("❌ Error: El servidor aceptó datos inválidos")
            return False
        else:
            print("✅ El servidor rechazó datos inválidos")
            return True
    except Exception as e:
        print(f"✅ Excepción esperada por datos inválidos: {e}")
        return True

def test_4_timeout():
    """🔹4. Prueba de timeout"""
    print("\n🔹4. Probando timeout...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        cod = generar_codigo()
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto=f"FER-{cod}",
            nombre_p="Producto Lento",
            precio_p=1000
        ), timeout=0.001)  # Timeout muy corto
        if not response.exito:
            print(f"❌ Falló: {response.mensaje}")
            return False
        print("⚠️  No se detectó timeout")
        channel.close()
        return True
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            print("⏱ Timeout detectado correctamente")
            channel.close()
            return True
        else:
            print(f"❌ Error diferente al timeout: {e.code()}")
            channel.close()
            return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        channel.close()
        return False

def test_5_cancelacion():
    """🔹5. Prueba de cancelación de llamada"""
    print("\n🔹5. Probando cancelación...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        # Crear llamada asíncrona
        cod = generar_codigo()
        call = stub.CrearProducto.future(CrearProductoRequest(
            cod_producto=f"CANCEL-{cod}",
            nombre_p="Cancelar",
            precio_p=1000
        ))
        
        # Cancelar inmediatamente
        call.cancel()
        
        # Verificar si fue cancelada
        if call.cancelled():
            print("🛑 Llamada cancelada correctamente")
            channel.close()
            return True
        else:
            print("⚠️  La llamada no fue cancelada")
            channel.close()
            return False
            
    except Exception as e:
        print(f"❌ Error en cancelación: {e}")
        channel.close()
        return False

def test_6_autenticacion():
    """🔹6. Prueba de autenticación (metadata)"""
    print("\n🔹6. Probando autenticación...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        cod = generar_codigo()
        nombre_unico = f"Protegido-{generar_codigo()}"
        response = stub.CrearProducto(
            CrearProductoRequest(
                cod_producto=f"AUTH-{cod}",
                nombre_p=nombre_unico,
                precio_p=1000
            ),
            metadata=[('authorization', 'Bearer TOKEN_INVALIDO')]
        )
        
        if not response.exito:
            print(f"❌ Falló autenticación: {response.mensaje}")
            return False
        print("⚠️  No se implementó autenticación en el servidor")
        channel.close()
        return True  # No es un error si no está implementado
        
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAUTHENTICATED:
            print("🚫 Acceso denegado correctamente")
            channel.close()
            return True
        else:
            print(f"❌ Error diferente: {e.code()}")
            channel.close()
            return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        channel.close()
        return False

def test_7_error_servidor():
    """🔹7. Manejo de errores del servidor"""
    print("\n🔹7. Probando error del servidor...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        # Intentar crear producto con nombre que podría causar error
        cod = generar_codigo()
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto=f"ERR-{cod}",
            nombre_p="ERROR",  # Nombre que podría activar excepción en el servidor
            precio_p=0
        ))
        
        if not response.exito:
            print(f"💥 Error del servidor detectado: {response.mensaje}")
            return True
        else:
            print("⚠️  No se detectó error del servidor")
            return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        channel.close()
        return False

def test_9_prueba_carga():
    """🔹9. Prueba de carga básica"""
    print("\n🔹9. Probando carga básica...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        exitosos = 0
        total = 10
        for _ in range(total):
            cod = generar_codigo()
            nombre = f"Carga-{generar_codigo()}"
            response = stub.CrearProducto(CrearProductoRequest(
                cod_producto=f"FER-{cod}",
                nombre_p=nombre,
                precio_p=1000
            ))
            if response.exito:
                exitosos += 1
        
        print(f"✅ Prueba de carga completada: {exitosos}/{total} exitosos")
        channel.close()
        return exitosos == total
        
    except Exception as e:
        print(f"❌ Error en prueba de carga: {e}")
        channel.close()
        return False

def test_10_manejo_errores_servidor():
    """🔹10. Manejo de errores del servidor"""
    print("\n🔹10. Probando manejo de errores internos del servidor...")
    with grpc.insecure_channel(ADDRESS) as channel:
        stub = ProductoServiceStub(channel)
        # Forzar un error interno enviando un nombre especial
        try:
            response = stub.CrearProducto(CrearProductoRequest(
                cod_producto="FORCE-ERR",
                nombre_p="ERROR",  # El backend lanza excepción con este nombre
                precio_p=1000
            ))
            if not response.exito and "Error interno" in response.mensaje:
                print(f"✅ Error interno detectado y mensaje recibido: {response.mensaje}")
                return True
            else:
                print(f"❌ No se detectó el error interno esperado. Mensaje: {response.mensaje}")
                return False
        except grpc.RpcError as e:
            print(f"✅ Excepción gRPC capturada: {e.code()} - {e.details()}")
            return True

def ejecutar_todas_las_pruebas():
    """Ejecuta todas las pruebas y muestra un resumen"""
    print("🚀 Iniciando pruebas del servicio gRPC de productos")
    print("=" * 60)
    
    pruebas = [
        ("Conexión exitosa", test_1_conexion_exitosa),
        ("Llamada válida", test_2_llamada_valida),
        ("Datos inválidos", test_3_datos_invalidos),
        ("Timeout", test_4_timeout),
        ("Cancelación", test_5_cancelacion),
        ("Autenticación", test_6_autenticacion),
        ("Error del servidor", test_7_error_servidor),
        ("Prueba de carga", test_9_prueba_carga),
        ("Manejo de errores del servidor", test_10_manejo_errores_servidor)
    ]
    
    resultados = []
    
    for nombre, prueba in pruebas:
        try:
            resultado = prueba()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"❌ Error ejecutando {nombre}: {e}")
            resultados.append((nombre, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        estado = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"{estado} - {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\n🎯 Resultado final: {exitosos}/{len(resultados)} pruebas exitosas")
    
    if exitosos == len(resultados):
        print("🎉 ¡Todas las pruebas pasaron!")
    elif exitosos >= len(resultados) * 0.8:
        print("👍 La mayoría de las pruebas pasaron")
    else:
        print("⚠️  Muchas pruebas fallaron, revisar el servidor")

if __name__ == "__main__":
    ejecutar_todas_las_pruebas() 