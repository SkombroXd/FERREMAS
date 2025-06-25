from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os, uuid, json
from supabase.client import create_client
from dotenv import load_dotenv
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from datetime import datetime
import queue
import threading
import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Variables de entorno SUPABASE_URL y SUPABASE_KEY no configuradas")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

# Configuración simple de CORS
CORS(app, resources={
    r"/*": {
        "origins": "http://localhost:4200",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Cola para notificaciones SSE
notificaciones_queue = queue.Queue()

# Configuración de Transbank
options = WebpayOptions(
    commerce_code="597055555532",
    api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
    integration_type=IntegrationType.TEST
)

def verificar_stock_bajo():
    while True:
        try:
            # Obtener productos con stock bajo por sucursal
            # Consultar producto_sucursal para obtener stock bajo por sucursal
            stock_bajo_response = supabase.table('producto_sucursal').select(
                'unidades, cod_sucursal, productos(cod_producto, nombre_p), sucursal(nombre_sucursal)'
            ).lt('unidades', 10).execute()
            
            for item in stock_bajo_response.data:
                if item['productos'] and item['sucursal']:
                    mensaje = {
                        'tipo': 'stock_bajo',
                        'producto': item['productos']['nombre_p'],
                        'stock': item['unidades'],
                        'cod_producto': item['productos']['cod_producto'],
                        'sucursal': item['sucursal']['nombre_sucursal'],
                        'cod_sucursal': item['cod_sucursal']
                    }
                    notificaciones_queue.put(mensaje)
            
            time.sleep(60)  # Verificar cada minuto
        except Exception as e:
            print(f"Error en verificación de stock: {str(e)}")
            time.sleep(60)

# Iniciar thread de verificación de stock
threading.Thread(target=verificar_stock_bajo, daemon=True).start()

@app.route('/api/notificaciones', methods=['GET'])
def notificaciones():
    def generar_eventos():
        while True:
            try:
                mensaje = notificaciones_queue.get()
                yield f"data: {json.dumps(mensaje)}\n\n"
            except Exception as e:
                print(f"Error en SSE: {str(e)}")
                time.sleep(1)

    return Response(generar_eventos(), mimetype='text/event-stream')

@app.route('/api/create-transaction', methods=['POST'])
def create_transaction():
    data = request.get_json()
    amount = int(data.get('amount'))
    buy_order  = str(uuid.uuid4().hex[:26])
    session_id = str(uuid.uuid4())
    return_url = "http://localhost:4200/checkout"

    transaction = Transaction(options)
    tx = transaction.create(buy_order=buy_order, session_id=session_id, amount=amount, return_url=return_url)



    return jsonify({ 'url': tx['url'], 'token_ws': tx['token'] })

@app.route('/api/commit-transaction', methods=['GET'])
def commit_transaction():
    token = request.args['token_ws']
    result = Transaction(options).commit(token)

    return jsonify({
      'buy_order':   result['buy_order'],
      'amount':      result['amount'],
      'card_number': result['card_detail']['card_number'],
      'status':      result['status']
    })

@app.route('/api/lista-productos', methods=['GET'])
def lista_productos():
    try:
        # Obtener productos con su stock total
        response = supabase.table('productos').select('*').execute()
        
        # Para cada producto, calcular el stock total sumando todas las sucursales
        productos_con_stock = []
        for producto in response.data:
            # Obtener stock total del producto sumando todas las sucursales
            stock_response = supabase.table('producto_sucursal').select('unidades').eq('cod_producto', producto['cod_producto']).execute()
            
            stock_total = 0
            if stock_response.data:
                stock_total = sum(item['unidades'] for item in stock_response.data)
            
            # Agregar el stock total al producto
            producto_con_stock = producto.copy()
            producto_con_stock['unidades_p'] = stock_total
            productos_con_stock.append(producto_con_stock)
        
        return jsonify(productos_con_stock)
    except Exception as e:
        print(f"Error en lista_productos: {str(e)}")
        return jsonify([]), 500

@app.route('/api/procesar-pago', methods=['POST', 'OPTIONS'])
def procesar_pago():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        print("Recibiendo solicitud de pago...")
        data = request.get_json()
        print("Datos recibidos:", data)
        
        productos = data.get('productos', [])
        total = int(data.get('total', 0))
        
        print(f"Productos: {productos}")
        print(f"Total: {total}")
        
        # Generar orden de compra
        orden_compra = str(uuid.uuid4())[:8]
        print(f"Orden de compra generada: {orden_compra}")
        
        # Crear boleta
        boleta_data = {
            'orden_compra': orden_compra,
            'total_compra': total,
            'num_tarjeta': 0
        }
        print("Creando boleta:", boleta_data)
        supabase.table('boleta').insert(boleta_data).execute()
        
        # Crear detalles de boleta repartiendo por sucursal
        for producto in productos:
            cantidad_restante = producto['cantidad']
            cod_producto = producto['cod_producto']
            precio_unitario = producto['precio_p'] if 'precio_p' in producto else (producto['subtotal'] / producto['cantidad'])

            # Obtener todas las sucursales con stock para este producto, ordenadas por unidades ascendente
            sucursales_stock = supabase.table('producto_sucursal').select('cod_sucursal, unidades').eq('cod_producto', cod_producto).gte('unidades', 1).order('unidades', desc=False).execute().data

            for sucursal in sucursales_stock:
                if cantidad_restante <= 0:
                    break
                unidades_disponibles = sucursal['unidades']
                unidades_a_vender = min(unidades_disponibles, cantidad_restante)
                subtotal = unidades_a_vender * precio_unitario

                # Insertar en detalle_boleta
                detalle_data = {
                    'cod_producto': cod_producto,
                    'cod_sucursal': sucursal['cod_sucursal'],
                    'orden_compra': orden_compra,
                    'subtotal_c': subtotal,
                    'unidades_c': unidades_a_vender
                }
                print("Creando detalle:", detalle_data)
                supabase.table('detalle_boleta').insert(detalle_data).execute()

                # Actualizar stock en producto_sucursal
                nuevo_stock = unidades_disponibles - unidades_a_vender
                supabase.table('producto_sucursal').update({'unidades': nuevo_stock}).eq('cod_producto', cod_producto).eq('cod_sucursal', sucursal['cod_sucursal']).execute()

                cantidad_restante -= unidades_a_vender

            if cantidad_restante > 0:
                print(f"No hay suficiente stock para el producto {cod_producto}. Faltaron {cantidad_restante} unidades.")
        
        # Crear transacción en Transbank
        buy_order = orden_compra
        session_id = str(uuid.uuid4())
        return_url = "http://localhost:4200/checkout"
        
        print("Creando transacción en Transbank...")
        transaction = Transaction(options)
        tx = transaction.create(
            buy_order=buy_order,
            session_id=session_id,
            amount=total,
            return_url=return_url
        )
        print("Transacción creada:", tx)
        
        return jsonify({
            'url': tx['url'],
            'token_ws': tx['token'],
            'orden_compra': orden_compra
        })
        
    except Exception as e:
        print(f"Error en procesar_pago: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/commit-transaction', methods=['POST', 'OPTIONS'])
def commit_transaction_post():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        data = request.get_json()
        token = data.get('token_ws')
        orden_compra = data.get('orden_compra')
        
        result = Transaction(options).commit(token)
        
        if result['status'] == 'AUTHORIZED':
            # Actualizar número de tarjeta en la boleta
            supabase.table('boleta').update({
                'num_tarjeta': result['card_detail']['card_number']
            }).eq('orden_compra', orden_compra).execute()
            
            # Obtener detalles de la boleta para actualizar el stock
            detalles = supabase.table('detalle_boleta').select('*').eq('orden_compra', orden_compra).execute()
            
            # Actualizar stock para cada producto
            for detalle in detalles.data:
                try:
                    # Obtener producto completo
                    producto = supabase.table('productos').select('*').eq('cod_producto', detalle['cod_producto']).execute()
                    if producto.data:
                        # Obtener stock actual de la sucursal (asumiendo sucursal 1 por defecto)
                        stock_response = supabase.table('producto_sucursal').select('unidades').eq('cod_producto', detalle['cod_producto']).eq('cod_sucursal', 1).execute()
                        
                        if stock_response.data:
                            stock_actual = stock_response.data[0]['unidades']
                            nuevo_stock = stock_actual - detalle['unidades_c']
                            
                            # Actualizar stock en la sucursal
                            supabase.table('producto_sucursal').update({
                                'unidades': nuevo_stock
                            }).eq('cod_producto', detalle['cod_producto']).eq('cod_sucursal', 1).execute()
                            
                            # Enviar notificación de actualización de stock
                            mensaje = {
                                'tipo': 'stock_bajo' if nuevo_stock < 10 else 'stock_actualizado',
                                'producto': producto.data[0]['nombre_p'],
                                'stock': nuevo_stock,
                                'cod_producto': detalle['cod_producto'],
                                'sucursal': 1
                            }
                            notificaciones_queue.put(mensaje)
                            
                            # Esperar un momento para asegurar que la notificación se procese
                            time.sleep(0.1)
                except Exception as e:
                    print(f"Error al actualizar stock del producto {detalle['cod_producto']}: {str(e)}")
                    continue
            
            return jsonify({
                'status': 'success',
                'buy_order': result['buy_order'],
                'amount': result['amount'],
                'card_number': result['card_detail']['card_number']
            })
        else:
            # Si el pago falla, eliminar la boleta y sus detalles
            supabase.table('detalle_boleta').delete().eq('orden_compra', orden_compra).execute()
            supabase.table('boleta').delete().eq('orden_compra', orden_compra).execute()
            
            return jsonify({
                'status': 'error',
                'message': 'Pago no autorizado'
            }), 400
            
    except Exception as e:
        print(f"Error en commit_transaction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/actualizar-stock', methods=['POST'])
def actualizar_stock():
    try:
        data = request.get_json()
        cod_producto = data.get('cod_producto')
        cod_sucursal = data.get('cod_sucursal', 1)  # Default a sucursal 1 si no se especifica
        cantidad = data.get('cantidad')

        if not cod_producto or not cantidad:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        # Obtener producto completo
        producto = supabase.table('productos').select('*').eq('cod_producto', cod_producto).execute()
        if not producto.data:
            return jsonify({'error': 'Producto no encontrado'}), 404

        # Obtener stock actual de la sucursal
        stock_actual_response = supabase.table('producto_sucursal').select('unidades').eq('cod_producto', cod_producto).eq('cod_sucursal', cod_sucursal).execute()
        
        if not stock_actual_response.data:
            return jsonify({'error': 'Registro de stock no encontrado para esta sucursal'}), 404
        
        stock_actual = stock_actual_response.data[0]['unidades']
        nuevo_stock = stock_actual + cantidad

        # Actualizar stock en la sucursal específica
        supabase.table('producto_sucursal').update({
            'unidades': nuevo_stock
        }).eq('cod_producto', cod_producto).eq('cod_sucursal', cod_sucursal).execute()

        # Enviar notificación de actualización de stock
        mensaje = {
            'tipo': 'stock_bajo' if nuevo_stock < 10 else 'stock_actualizado',
            'producto': producto.data[0]['nombre_p'],
            'stock': nuevo_stock,
            'cod_producto': cod_producto,
            'sucursal': cod_sucursal
        }
        notificaciones_queue.put(mensaje)

        return jsonify({
            'success': True,
            'stock_actual': nuevo_stock,
            'sucursal': cod_sucursal
        })

    except Exception as e:
        print(f"Error al actualizar stock: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/crear-producto', methods=['POST'])
def crear_producto():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not data.get('nombreP') or not data.get('precioP'):
            return jsonify({
                'exito': False,
                'mensaje': 'Nombre y precio son requeridos'
            }), 400
        
        # Generar código secuencial automático
        cod_producto = generar_codigo_producto()
        
        # Preparar datos para la tabla productos
        producto_data = {
            'cod_producto': cod_producto,
            'nombre_p': data['nombreP'],
            'precio_p': float(data['precioP'])
        }
        
        # Si hay imagen, guardarla
        if data.get('imagen'):
            producto_data['imagen'] = data['imagen']
        
        # Insertar en la tabla productos
        result = supabase.table('productos').insert(producto_data).execute()
        
        if result.data:
            # Obtener todas las sucursales para crear registros de stock
            sucursales = supabase.table('sucursal').select('cod_sucursal').execute()
            
            if sucursales.data:
                # Crear registros de stock en producto_sucursal con 0 unidades
                stock_data = []
                for sucursal in sucursales.data:
                    stock_data.append({
                        'cod_producto': cod_producto,
                        'cod_sucursal': sucursal['cod_sucursal'],
                        'unidades': 0
                    })
                
                # Insertar registros de stock
                supabase.table('producto_sucursal').insert(stock_data).execute()
            
            return jsonify({
                'exito': True,
                'mensaje': f'Producto {data["nombreP"]} creado correctamente con código {cod_producto}'
            })
        else:
            return jsonify({
                'exito': False,
                'mensaje': 'Error al guardar en la base de datos'
            }), 500
            
    except Exception as e:
        print(f"Error en crear_producto: {str(e)}")
        return jsonify({
            'exito': False,
            'mensaje': f'Error interno: {str(e)}'
        }), 500

@app.route('/api/productos-sucursal/<int:cod_sucursal>', methods=['GET'])
def productos_sucursal(cod_sucursal):
    try:
        # Obtener productos con stock en la sucursal específica
        response = supabase.table('producto_sucursal').select(
            'unidades, productos(cod_producto, nombre_p, precio_p, imagen)'
        ).eq('cod_sucursal', cod_sucursal).gte('unidades', 1).execute()
        
        productos_con_stock = []
        for item in response.data:
            if item['productos']:  # Verificar que el producto existe
                producto = item['productos']
                producto_con_stock = {
                    'cod_producto': producto['cod_producto'],
                    'nombre_p': producto['nombre_p'],
                    'precio_p': producto['precio_p'],
                    'imagen': producto.get('imagen'),
                    'unidades_p': item['unidades']
                }
                productos_con_stock.append(producto_con_stock)
        
        return jsonify(productos_con_stock)
    except Exception as e:
        print(f"Error en productos_sucursal: {str(e)}")
        return jsonify([]), 500

@app.route('/api/productos-sucursal-stock/<int:cod_sucursal>', methods=['GET'])
def productos_sucursal_stock(cod_sucursal):
    try:
        # Obtener TODOS los productos de la sucursal (incluyendo los que tienen 0 stock)
        response = supabase.table('producto_sucursal').select(
            'unidades, productos(cod_producto, nombre_p, precio_p, imagen)'
        ).eq('cod_sucursal', cod_sucursal).execute()
        
        productos_sucursal = []
        for item in response.data:
            if item['productos']:  # Verificar que el producto existe
                producto = item['productos']
                producto_sucursal = {
                    'cod_producto': producto['cod_producto'],
                    'nombre_p': producto['nombre_p'],
                    'precio_p': producto['precio_p'],
                    'imagen': producto.get('imagen'),
                    'unidades_p': item['unidades']
                }
                productos_sucursal.append(producto_sucursal)
        
        return jsonify(productos_sucursal)
    except Exception as e:
        print(f"Error en productos_sucursal_stock: {str(e)}")
        return jsonify([]), 500

@app.route('/api/sucursales', methods=['GET'])
def obtener_sucursales():
    try:
        response = supabase.table('sucursal').select('*').execute()
        return jsonify(response.data)
    except Exception as e:
        print(f"Error obteniendo sucursales: {str(e)}")
        return jsonify([]), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

