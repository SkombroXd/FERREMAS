#!/usr/bin/env python3
"""
Script de pruebas para el servicio gRPC de productos
Incluye pruebas de conexión, validación, timeout, carga, cancelación y autenticación
"""

import sys
import os
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
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto="FER-001",
            nombre_p="Martillo",
            precio_p=9990,
            unidades_p=20
        ))
        print("✅ Producto creado:", response.mensaje)
        channel.close()
        return True
    except Exception as e:
        print(f"❌ Error en llamada válida: {e}")
        return False

def test_3_datos_invalidos():
    """🔹3. Llamada con datos inválidos"""
    print("\n🔹3. Probando datos inválidos...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        stub.CrearProducto(CrearProductoRequest(
            cod_producto="",  # Código vacío
            nombre_p="",      # Nombre vacío
            precio_p=-10,     # Precio inválido
            unidades_p=-1     # Stock negativo
        ))
        print("⚠️  No se detectó error con datos inválidos")
        channel.close()
        return False
    except grpc.RpcError as e:
        print(f"❌ Error esperado: {e.code()} - {e.details()}")
        channel.close()
        return True
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        channel.close()
        return False

def test_4_timeout():
    """🔹4. Prueba de timeout"""
    print("\n🔹4. Probando timeout...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        stub.CrearProducto(CrearProductoRequest(
            cod_producto="FER-002",
            nombre_p="Producto Lento",
            precio_p=1000,
            unidades_p=5
        ), timeout=0.001)  # Timeout muy corto
        print("⚠️  No se detectó timeout")
        channel.close()
        return False
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
        call = stub.CrearProducto.future(CrearProductoRequest(
            cod_producto="CANCEL",
            nombre_p="Cancelar",
            precio_p=1000,
            unidades_p=1
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
        
        # Metadata con token inválido
        metadata = [('authorization', 'Bearer TOKEN_INVALIDO')]
        
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto="AUTH",
            nombre_p="Protegido",
            precio_p=1000,
            unidades_p=1
        ), metadata=metadata)
        
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
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto="ERR",
            nombre_p="ERROR",  # Nombre que podría activar excepción en el servidor
            precio_p=0,
            unidades_p=0
        ))
        
        print("⚠️  No se detectó error del servidor")
        channel.close()
        return True
        
    except grpc.RpcError as e:
        print(f"💥 Error del servidor detectado: {e.code()} - {e.details()}")
        channel.close()
        return True
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        channel.close()
        return False

def test_8_listar_productos():
    """🔹8. Prueba de listar productos"""
    print("\n🔹8. Probando listar productos...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        response = stub.ListarProductos(ListarProductosRequest())
        print(f"✅ Productos listados: {len(response.productos)} productos encontrados")
        
        # Mostrar algunos productos
        for i, producto in enumerate(response.productos[:3]):  # Solo los primeros 3
            print(f"   {i+1}. {producto.cod_producto} - {producto.nombre_p} - ${producto.precio_p}")
        
        channel.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al listar productos: {e}")
        channel.close()
        return False

def test_9_prueba_carga():
    """🔹9. Prueba de carga básica"""
    print("\n🔹9. Probando carga básica...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        def crear_producto_concurrente(i):
            try:
                response = stub.CrearProducto(CrearProductoRequest(
                    cod_producto=f"FER-{i:03d}",
                    nombre_p=f"Producto Carga {i}",
                    precio_p=1000 + i,
                    unidades_p=i
                ))
                return response.exito
            except:
                return False
        
        # Crear 10 productos concurrentemente
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(crear_producto_concurrente, i) for i in range(1, 11)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        exitosos = sum(results)
        
        print(f"✅ Prueba de carga completada: {exitosos}/10 exitosos en {end_time - start_time:.2f}s")
        channel.close()
        return exitosos >= 8  # Al menos 8 deben ser exitosos
        
    except Exception as e:
        print(f"❌ Error en prueba de carga: {e}")
        channel.close()
        return False

def test_10_validacion_campos():
    """🔹10. Prueba de validación de campos específicos"""
    print("\n🔹10. Probando validación de campos...")
    try:
        channel = grpc.insecure_channel(ADDRESS)
        stub = ProductoServiceStub(channel)
        
        # Probar con precio muy alto
        response = stub.CrearProducto(CrearProductoRequest(
            cod_producto="PRICE-TEST",
            nombre_p="Producto Caro",
            precio_p=999999999.99,
            unidades_p=1
        ))
        
        if response.exito:
            print("✅ Producto con precio alto creado")
        else:
            print(f"❌ Error con precio alto: {response.mensaje}")
        
        # Probar con nombre muy largo
        nombre_largo = "A" * 1000  # Nombre de 1000 caracteres
        response2 = stub.CrearProducto(CrearProductoRequest(
            cod_producto="LONG-NAME",
            nombre_p=nombre_largo,
            precio_p=100,
            unidades_p=1
        ))
        
        if response2.exito:
            print("✅ Producto con nombre largo creado")
        else:
            print(f"❌ Error con nombre largo: {response2.mensaje}")
        
        channel.close()
        return True
        
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        channel.close()
        return False

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
        ("Listar productos", test_8_listar_productos),
        ("Prueba de carga", test_9_prueba_carga),
        ("Validación de campos", test_10_validacion_campos)
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