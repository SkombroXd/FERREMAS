import grpc
from concurrent import futures
import producto_pb2_grpc
import producto_pb2
import os
from supabase.client import create_client
from dotenv import load_dotenv
from typing import Optional
import base64

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Variables de entorno SUPABASE_URL y SUPABASE_KEY no configuradas")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class ProductoServiceServicer(producto_pb2_grpc.ProductoServiceServicer):
    def CrearProducto(self, request, context):
        try:
            # Guardar producto en la base de datos
            data = {
                'cod_producto': request.cod_producto,
                'nombre_p': request.nombre_p,
                'precio_p': request.precio_p,
                'unidades_p': request.unidades_p
            }
            
            # Si hay imagen, guardarla en binario
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
                    producto = producto_pb2.Producto(
                        cod_producto=item.get('cod_producto', ''),
                        nombre_p=item.get('nombre_p', ''),
                        precio_p=item.get('precio_p', 0.0),
                        unidades_p=item.get('unidades_p', 0)
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

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    producto_pb2_grpc.add_ProductoServiceServicer_to_server(ProductoServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Servidor gRPC escuchando en el puerto 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve() 