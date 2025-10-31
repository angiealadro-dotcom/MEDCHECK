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
set APP_PORT=8001

REM Opcional: abre el navegador automáticamente
start "" http://localhost:%APP_PORT%/

uvicorn app.main:app --reload --port %APP_PORT% --log-level debug

endlocal
