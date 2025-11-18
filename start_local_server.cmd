@echo off
setlocal

REM Launch MedCheck locally with one double-click
REM - Activates virtualenv
REM - Sets PYTHONPATH
REM - Starts Uvicorn with autoreload on port 8001

REM Detect workspace root (this script's directory)
cd /d "%~dp0"

if not exist venv (
  echo [ERROR] No se encontró la carpeta venv. Crea el entorno virtual primero.
  echo        python -m venv venv
  echo        .\venv\Scripts\activate && pip install -r requirements.txt
  pause
  exit /b 1
)

call .\venv\Scripts\activate
set PYTHONPATH=.
set APP_PORT=8002

REM Opcional: abre el navegador automáticamente
start "" http://127.0.0.1:%APP_PORT%/

REM Limitar observadores del autoreload (sin exclusiones para evitar problemas de comodines en Windows)
uvicorn app.main:app --reload --reload-dir app --reload-dir templates --port %APP_PORT% --log-level warning

endlocal
