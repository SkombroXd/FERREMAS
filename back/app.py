from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os, uuid, json
from supabase import create_client
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
            # Obtener productos con stock bajo
            productos = supabase.table('productos').select('*').lt('unidades_p', 10).execute()
            
            for producto in productos.data:
                mensaje = {
                    'tipo': 'stock_bajo',
                    'producto': producto['nombre_p'],
                    'stock': producto['unidades_p']
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
    response = supabase.table('productos').select('*').execute()
    return jsonify(response.data)

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
        
        # Crear detalles de boleta y actualizar stock
        for producto in productos:
            detalle_data = {
                'cod_producto': producto['cod_producto'],
                'orden_compra': orden_compra,
                'subtotal_c': producto['subtotal'],
                'unidades_c': producto['cantidad']
            }
            print("Creando detalle:", detalle_data)
            supabase.table('detalle_boleta').insert(detalle_data).execute()
            
            # Actualizar stock
            stock_actual = supabase.table('productos').select('unidades_p').eq('cod_producto', producto['cod_producto']).execute().data[0]['unidades_p']
            nuevo_stock = stock_actual - producto['cantidad']
            print(f"Actualizando stock de {producto['cod_producto']}: {stock_actual} -> {nuevo_stock}")
            
            # Actualizar stock en la base de datos
            supabase.table('productos').update({
                'unidades_p': nuevo_stock
            }).eq('cod_producto', producto['cod_producto']).execute()
            
            # Verificar si el stock quedó bajo
            if nuevo_stock < 10:
                mensaje = {
                    'tipo': 'stock_bajo',
                    'producto': producto['nombre_p'],
                    'stock': nuevo_stock
                }
                notificaciones_queue.put(mensaje)
        
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
            
            return jsonify({
                'status': 'success',
                'buy_order': result['buy_order'],
                'amount': result['amount'],
                'card_number': result['card_detail']['card_number']
            })
        else:
            # Si el pago falla, revertir los cambios
            supabase.table('detalle_boleta').delete().eq('orden_compra', orden_compra).execute()
            supabase.table('boleta').delete().eq('orden_compra', orden_compra).execute()
            
            return jsonify({
                'status': 'error',
                'message': 'Pago no autorizado'
            }), 400
            
    except Exception as e:
        print(f"Error en commit_transaction: {str(e)}")  # Agregar log para depuración
        return jsonify({'error': str(e)}), 500

@app.route('/api/actualizar-stock', methods=['POST'])
def actualizar_stock():
    try:
        data = request.get_json()
        cod_producto = data.get('cod_producto')
        cantidad = data.get('cantidad')

        if not cod_producto or not cantidad:
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        # Obtener stock actual
        producto = supabase.table('productos').select('unidades_p').eq('cod_producto', cod_producto).execute()
        if not producto.data:
            return jsonify({'error': 'Producto no encontrado'}), 404

        stock_actual = producto.data[0]['unidades_p']
        nuevo_stock = stock_actual + cantidad

        # Actualizar stock
        supabase.table('productos').update({
            'unidades_p': nuevo_stock
        }).eq('cod_producto', cod_producto).execute()

        # Verificar si el stock sigue bajo después de la actualización
        if nuevo_stock < 10:
            mensaje = {
                'tipo': 'stock_bajo',
                'producto': producto.data[0]['nombre_p'],
                'stock': nuevo_stock
            }
            notificaciones_queue.put(mensaje)

        return jsonify({
            'success': True,
            'stock_actual': nuevo_stock
        })

    except Exception as e:
        print(f"Error al actualizar stock: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

