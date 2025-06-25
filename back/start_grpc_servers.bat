@echo off
echo Iniciando servidores gRPC para FERREMAS...

echo.
echo 1. Iniciando servidor gRPC en puerto 50051...
start "Servidor gRPC" python server_grpc.py

echo.
echo 2. Iniciando proxy gRPC-Web en puerto 8080...
start "Proxy gRPC-Web" grpcwebproxy-v0.15.0-win64.exe --backend_addr=localhost:50051 --run_tls_server=false --allow_all_origins --server_http_debug_port=8080

echo.
echo 3. Iniciando servidor Flask en puerto 5000...
start "Servidor Flask" python app.py

echo.
echo Todos los servidores han sido iniciados:
echo - Servidor gRPC: localhost:50051 (para comunicación backend)
echo - Proxy gRPC-Web: localhost:8080 (para comunicación frontend)
echo - Servidor Flask: localhost:5000 (para APIs REST)
echo.
echo El componente crearproducto ahora usa gRPC con protobuf!
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause > nul 