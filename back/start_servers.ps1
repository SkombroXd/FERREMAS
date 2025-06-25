Write-Host "Iniciando servidores del backend FERREMAS..." -ForegroundColor Green

Write-Host ""
Write-Host "1. Iniciando servidor gRPC en puerto 50051..." -ForegroundColor Yellow
Start-Process python -ArgumentList "server_grpc.py" -WindowStyle Minimized

Write-Host ""
Write-Host "2. Iniciando proxy gRPC-Web en puerto 8080..." -ForegroundColor Yellow
Start-Process "./grpcwebproxy-v0.15.0-win64.exe" -ArgumentList "--backend_addr=localhost:50051", "--run_tls_server=false", "--allow_all_origins", "--server_http_debug_port=8080" -WindowStyle Minimized

Write-Host ""
Write-Host "3. Iniciando servidor Flask en puerto 5000..." -ForegroundColor Yellow
Start-Process python -ArgumentList "app.py" -WindowStyle Minimized

Write-Host ""
Write-Host "Todos los servidores han sido iniciados:" -ForegroundColor Green
Write-Host "- Servidor gRPC: localhost:50051" -ForegroundColor Cyan
Write-Host "- Proxy gRPC-Web: localhost:8080" -ForegroundColor Cyan
Write-Host "- Servidor Flask: localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona cualquier tecla para cerrar esta ventana..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 