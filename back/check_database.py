import os
from supabase.client import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Variables de entorno SUPABASE_URL y SUPABASE_KEY no configuradas")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_and_fix_database():
    try:
        # Intentar obtener la estructura de la tabla productos
        print("Verificando estructura de la tabla productos...")
        
        # Intentar insertar un producto de prueba para ver qué columnas existen
        test_data = {
            'cod_producto': 'TEST001',
            'nombre_p': 'Producto Test',
            'precio_p': 100.0,
            'unidades_p': 10
        }
        
        try:
            result = supabase.table('productos').insert(test_data).execute()
            print("✅ Columna unidades_p existe y funciona correctamente")
            
            # Eliminar el producto de prueba
            supabase.table('productos').delete().eq('cod_producto', 'TEST001').execute()
            print("✅ Producto de prueba eliminado")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error al insertar: {error_msg}")
            
            if "unidades_p" in error_msg:
                print("🔧 La columna unidades_p no existe. Necesitas agregarla manualmente en Supabase.")
                print("\nPara agregar la columna, ve a tu dashboard de Supabase y:")
                print("1. Ve a la tabla 'productos'")
                print("2. Agrega una nueva columna llamada 'unidades_p'")
                print("3. Tipo: integer")
                print("4. Default value: 0")
                print("5. Allow nullable: true")
                
                # Intentar sin la columna unidades_p
                test_data_fixed = {
                    'cod_producto': 'TEST002',
                    'nombre_p': 'Producto Test 2',
                    'precio_p': 100.0
                }
                
                try:
                    result = supabase.table('productos').insert(test_data_fixed).execute()
                    print("✅ Insertado sin unidades_p - la tabla funciona con las columnas existentes")
                    
                    # Eliminar el producto de prueba
                    supabase.table('productos').delete().eq('cod_producto', 'TEST002').execute()
                    
                except Exception as e2:
                    print(f"❌ Error incluso sin unidades_p: {str(e2)}")
        
        # Verificar qué columnas existen realmente
        print("\nVerificando columnas existentes...")
        try:
            result = supabase.table('productos').select('*').limit(1).execute()
            if result.data:
                columns = list(result.data[0].keys())
                print(f"✅ Columnas existentes: {columns}")
            else:
                print("ℹ️ La tabla está vacía")
        except Exception as e:
            print(f"❌ Error al verificar columnas: {str(e)}")
            
    except Exception as e:
        print(f"❌ Error general: {str(e)}")

if __name__ == "__main__":
    check_and_fix_database() 