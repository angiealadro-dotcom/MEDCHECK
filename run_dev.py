#!/usr/bin/env python3
"""
MedCheck Development Server Launcher
-------------------------------------
Script multiplataforma para iniciar el servidor de desarrollo.
Uso: python run_dev.py
"""
import subprocess
import sys
import os
import webbrowser
from pathlib import Path
import time

def check_venv():
    """Verifica si estamos en un entorno virtual"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        print("⚠️  ADVERTENCIA: No se detectó un entorno virtual activado")
        print("   Recomendación: Activa el entorno virtual primero:")
        if sys.platform == "win32":
            print("   .\\venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        print()
    return in_venv

def check_requirements():
    """Verifica que las dependencias estén instaladas"""
    try:
        import fastapi
        import uvicorn
        return True
    except ImportError:
        print("❌ Dependencias no encontradas")
        print("   Instala las dependencias con:")
        print("   pip install -r requirements.txt")
        return False

def main():
    print("=" * 60)
    print("🏥 MedCheck - Development Server")
    print("=" * 60)
    print()

    # Verificar entorno virtual
    check_venv()

    # Verificar dependencias
    if not check_requirements():
        sys.exit(1)

    # Configuración
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8002"))

    print(f"📍 Host: {host}")
    print(f"🔌 Puerto: {port}")
    print(f"🔄 Auto-reload: Activado")
    print(f"📁 Directorio: {Path.cwd()}")
    print()
    print("🚀 Iniciando servidor...")
    print("-" * 60)
    print()

    # Abrir navegador automáticamente después de un delay
    url = f"http://{host}:{port}"
    def open_browser():
        time.sleep(2)  # Esperar a que el servidor inicie
        print(f"🌐 Abriendo navegador: {url}")
        webbrowser.open(url)

    import threading
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Construir comando de uvicorn
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port),
        "--reload",
        "--reload-dir", "app",
        "--reload-dir", "templates",
        "--log-level", "info"
    ]

    try:
        # Iniciar servidor
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print()
        print("🛑 Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al iniciar el servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
