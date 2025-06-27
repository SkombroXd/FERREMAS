@echo off
echo 🧪 EJECUTANDO PRUEBAS SSE - FERREMAS
echo ======================================
echo.
echo Asegúrate de que el servidor Flask esté ejecutándose en http://localhost:5000
echo.
echo Ejecutando script de pruebas automatizadas...
echo.

python test_sse\test_sse_automated.py

echo.
echo ======================================
echo Pruebas completadas.
echo.
echo Para usar la herramienta HTML:
echo 1. Abrir test_sse\sse_test.html en tu navegador
echo 2. Hacer clic en "Conectar SSE"
echo.
pause 