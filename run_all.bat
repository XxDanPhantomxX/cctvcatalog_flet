@echo off
REM =====================================================
REM Ejecutar Web + LocalTunnel en una sola consola
REM =====================================================

REM Activar entorno virtual
call ".venv\Scripts\activate.bat"

REM =====================================================
REM Establecer modo de ejecución (para que Python lo detecte)
REM =====================================================
set MODE=web

REM =====================================================
REM Ejecutar Web + Flet
REM =====================================================
echo Iniciando Web (Flet Dashboard)...
start "" /B flet run "src\main.py" --web --port 8501

REM Esperar 3 segundos para que el servidor Web esté listo
timeout /t 3 /nobreak

REM =====================================================
REM Ejecutar LocalTunnel
REM =====================================================
echo Iniciando LocalTunnel...
lt --port 8501 --subdomain cctvcatalog

REM Mantener la ventana abierta para ver logs
pause






