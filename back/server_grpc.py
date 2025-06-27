import grpc
from concurrent import futures
import producto_pb2_grpc
import producto_pb2
import os
from supabase.client import create_client
from dotenv import load_dotenv
from typing import Optional
import base64
import time

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Variables de entorno SUPABASE_URL y SUPABASE_KEY no configuradas")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def generar_codigo_producto():
    """Genera un código secuencial FER-001, FER-002, etc."""
    try:
        # Obtener todos los productos que empiecen con FER- para encontrar el máximo
        productos = supabase.table('productos').select('cod_producto').like('cod_producto', 'FER-%').execute()
        
        max_numero = 0
        if productos.data:
            for producto in productos.data:
                codigo = producto['cod_producto']
                if codigo.startswith('FER-'):
                    try:
                        numero = int(codigo[4:])  # Extraer el número después de "FER-"
                        if numero > max_numero:
                            max_numero = numero
                    except ValueError:
                        continue
        
        siguiente_numero = max_numero + 1
        return f"FER-{siguiente_numero:03d}"  # Formato: FER-001, FER-002, etc.
        
    except Exception as e:
        print(f"Error generando código: {str(e)}")
        # Fallback: usar timestamp
        return f"FER-{int(time.time() * 1000) % 1000:03d}"

class ProductoServiceServicer(producto_pb2_grpc.ProductoServiceServicer):
    def CrearProducto(self, request, context):
        try:
            cod_producto = request.cod_producto
            if not cod_producto or cod_producto.strip() == "":
                cod_producto = generar_codigo_producto()
            if not request.nombre_p or request.precio_p <= 0:
                return producto_pb2.CrearProductoResponse(
                    exito=False, 
                    mensaje="Datos inválidos: nombre y precio son requeridos"
                )
            if request.nombre_p.strip() == "":
                return producto_pb2.CrearProductoResponse(
                    exito=False, 
                    mensaje="El nombre del producto no puede estar vacío"
                )
            if len(request.nombre_p) > 100:
                return producto_pb2.CrearProductoResponse(
                    exito=False,
                    mensaje="El nombre del producto no puede tener más de 100 caracteres"
                )
            if request.precio_p <= 0:
                return producto_pb2.CrearProductoResponse(
                    exito=False, 
                    mensaje="El precio debe ser mayor a 0"
                )
            if request.nombre_p == "ERROR":
                raise Exception("Falla simulada del servidor para pruebas")
            existing_product = supabase.table('productos').select('cod_producto').eq('cod_producto', cod_producto).execute()
            if existing_product.data:
                return producto_pb2.CrearProductoResponse(
                    exito=False, 
                    mensaje=f"El producto con código {cod_producto} ya existe"
                )
            data = {
                'cod_producto': cod_producto,
                'nombre_p': request.nombre_p,
                'precio_p': request.precio_p
            }
            if request.imagen:
                data['imagen'] = request.imagen
            result = supabase.table('productos').insert(data).execute()
            if result.data:
                return producto_pb2.CrearProductoResponse(
                    exito=True, 
                    mensaje=f"Producto {request.nombre_p} creado correctamente"
                )
            else:
                return producto_pb2.CrearProductoResponse(
                    exito=False, 
                    mensaje="Error al guardar en la base de datos"
                )
        except Exception as e:
            return producto_pb2.CrearProductoResponse(
                exito=False, 
                mensaje=f"Error interno: {str(e)}"
            )

    def ListarProductos(self, request, context):
        try:
            # Obtener todos los productos de la base de datos
            result = supabase.table('productos').select('*').execute()
            
            if result.data:
                productos = []
                for item in result.data:
                    # Calcular stock total sumando todas las sucursales
                    stock_response = supabase.table('producto_sucursal').select('unidades').eq('cod_producto', item['cod_producto']).execute()
                    
                    stock_total = 0
                    if stock_response.data:
                        stock_total = sum(stock_item['unidades'] for stock_item in stock_response.data)
                    
                    producto = producto_pb2.Producto(
                        cod_producto=item.get('cod_producto', ''),
                        nombre_p=item.get('nombre_p', ''),
                        precio_p=item.get('precio_p', 0.0),
                        unidades_p=stock_total  # Usar el stock total calculado
                    )
                    
                    # Si hay imagen, convertirla a bytes
                    if item.get('imagen'):
                        if isinstance(item['imagen'], str):
                            # Si es base64, convertir a bytes
                            producto.imagen = base64.b64decode(item['imagen'])
                        else:
                            # Si ya es bytes
                            producto.imagen = item['imagen']
                    
                    productos.append(producto)
                
                return producto_pb2.ListarProductosResponse(productos=productos)
            else:
                return producto_pb2.ListarProductosResponse(productos=[])
                
        except Exception as e:
            print(f"Error al listar productos: {str(e)}")
            return producto_pb2.ListarProductosResponse(productos=[])

    def AsignarProductoASucursal(self, request, context):
        try:
            # Validar datos
            if not request.cod_producto or not request.cod_sucursal or request.unidades is None:
                return producto_pb2.RespuestaGeneral(
                    exito=False,
                    mensaje="Faltan datos requeridos"
                )
            if request.unidades < 0:
                return producto_pb2.RespuestaGeneral(
                    exito=False,
                    mensaje="Las unidades no pueden ser negativas"
                )
            # Verificar existencia de producto
            producto = supabase.table('productos').select('cod_producto').eq('cod_producto', request.cod_producto).execute()
            if not producto.data:
                return producto_pb2.RespuestaGeneral(
                    exito=False,
                    mensaje="El producto no existe"
                )
            # Verificar existencia de sucursal
            sucursal = supabase.table('sucursal').select('cod_sucursal').eq('cod_sucursal', request.cod_sucursal).execute()
            if not sucursal.data:
                return producto_pb2.RespuestaGeneral(
                    exito=False,
                    mensaje="La sucursal no existe"
                )
            # Actualizar o crear registro en producto_sucursal
            stock = supabase.table('producto_sucursal').select('unidades').eq('cod_producto', request.cod_producto).eq('cod_sucursal', request.cod_sucursal).execute()
            if stock.data:
                # Actualizar unidades
                supabase.table('producto_sucursal').update({'unidades': request.unidades}).eq('cod_producto', request.cod_producto).eq('cod_sucursal', request.cod_sucursal).execute()
            else:
                # Crear registro
                supabase.table('producto_sucursal').insert({
                    'cod_producto': request.cod_producto,
                    'cod_sucursal': request.cod_sucursal,
                    'unidades': request.unidades
                }).execute()
            return producto_pb2.RespuestaGeneral(
                exito=True,
                mensaje="Unidades asignadas correctamente"
            )
        except Exception as e:
            return producto_pb2.RespuestaGeneral(
                exito=False,
                mensaje=f"Error interno: {str(e)}"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    producto_pb2_grpc.add_ProductoServiceServicer_to_server(ProductoServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Servidor gRPC escuchando en el puerto 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 