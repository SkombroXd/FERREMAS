# Configuración del Proyecto FERREMAS

## Estructura del Proyecto

```
FERREMAS/
├── back/                    # Backend (Flask + gRPC)
│   ├── app.py              # Servidor Flask (puerto 5000)
│   ├── server_grpc.py      # Servidor gRPC (puerto 50051)
│   ├── producto.proto      # Definición de protobuf
│   ├── grpcwebproxy-v0.15.0-win64.exe  # Proxy gRPC-Web
│   └── start_servers.bat   # Script de inicio (Windows)
├── front/app/              # Frontend (Angular)
│   └── src/
│       ├── app/            # Componentes Angular
│       └── protos/         # Archivos protobuf generados
```

## Configuración del Backend

### 1. Instalar dependencias Python
```bash
cd back
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
Crear archivo `.env` en la carpeta `back/`:
```env
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_de_supabase
```

### 3. Iniciar servidores del backend

**Opción A: Script automático (Recomendado)**
```bash
# Windows (CMD)
start_servers.bat

# Windows (PowerShell)
.\start_servers.ps1
```

**Opción B: Manual**
```bash
# Terminal 1: Servidor gRPC
python server_grpc.py

# Terminal 2: Proxy gRPC-Web
./grpcwebproxy-v0.15.0-win64.exe --backend_addr=localhost:50051 --run_tls_server=false --allow_all_origins --server_http_debug_port=8080

# Terminal 3: Servidor Flask
python app.py
```

## Configuración del Frontend

### 1. Instalar dependencias Node.js
```bash
cd front/app
npm install
```

### 2. Iniciar servidor de desarrollo
```bash
npm start
```

El frontend estará disponible en: http://localhost:4200

## Puertos Utilizados

- **Frontend Angular**: http://localhost:4200
- **Backend Flask**: http://localhost:5000
- **Servidor gRPC**: localhost:50051
- **Proxy gRPC-Web**: http://localhost:8080

## Funcionalidades

### Rutas Disponibles
- `/home` - Página principal
- `/stock` - Gestión de inventario
- `/crearproducto` - Crear nuevos productos (usando gRPC)
- `/checkout` - Proceso de pago
- `/pago` - Confirmación de pago

### Servicios
- **gRPC**: Creación de productos con imágenes
- **REST API**: Lista de productos, procesamiento de pagos
- **Transbank**: Integración de pagos
- **Supabase**: Base de datos

## Solución de Problemas

### Error de conexión gRPC
1. Verificar que el servidor gRPC esté ejecutándose en puerto 50051
2. Verificar que el proxy gRPC-Web esté ejecutándose en puerto 8080
3. Revisar la consola del navegador para errores de CORS

### Error de conexión a Supabase
1. Verificar que las variables de entorno estén configuradas correctamente
2. Verificar la conectividad a internet
3. Revisar las credenciales de Supabase

### Error de compilación Angular
1. Verificar que Node.js esté instalado correctamente
2. Ejecutar `npm install` para reinstalar dependencias
3. Limpiar cache: `npm cache clean --force` 