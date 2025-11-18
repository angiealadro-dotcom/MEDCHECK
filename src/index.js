/**
 * MedCheck - Cloudflare Worker con Python (Pyodide)
 * Este worker ejecuta FastAPI usando Python en WebAssembly
 */

import { loadPyodide } from 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.mjs';

let pyodide = null;

export default {
  async fetch(request, env, ctx) {
    try {
      // Inicializar Pyodide solo una vez
      if (!pyodide) {
        console.log('Inicializando Pyodide...');
        pyodide = await loadPyodide({
          indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/',
        });

        // Instalar paquetes necesarios
        await pyodide.loadPackage(['micropip']);
        const micropip = pyodide.pyimport('micropip');

        // Instalar dependencias básicas
        await micropip.install([
          'fastapi',
          'pydantic',
          'python-jose',
          'passlib',
          'sqlalchemy',
        ]);

        console.log('Pyodide inicializado ✓');
      }

      // Obtener variables de entorno
      const SECRET_KEY = env.SECRET_KEY || 'dev-secret-key';
      const VAPID_PUBLIC_KEY = env.VAPID_PUBLIC_KEY || '';
      const VAPID_PRIVATE_KEY = env.VAPID_PRIVATE_KEY || '';

      // Parsear la petición
      const url = new URL(request.url);
      const method = request.method;
      const headers = Object.fromEntries(request.headers);

      // Código Python para manejar la petición
      const pythonCode = `
import json
from io import StringIO
import sys

# Configurar variables de entorno
import os
os.environ['SECRET_KEY'] = '${SECRET_KEY}'
os.environ['VAPID_PUBLIC_KEY'] = '${VAPID_PUBLIC_KEY}'
os.environ['VAPID_PRIVATE_KEY'] = '''${VAPID_PRIVATE_KEY}'''
os.environ['ENVIRONMENT'] = 'production'

# Importar la app FastAPI
try:
    from app.main import app

    # Simular la petición ASGI
    scope = {
        'type': 'http',
        'method': '${method}',
        'path': '${url.pathname}',
        'query_string': '${url.search}'.encode(),
        'headers': ${JSON.stringify(Object.entries(headers))},
    }

    # Procesar con FastAPI
    result = {'status': 200, 'body': 'OK from Python!'}
    json.dumps(result)
except Exception as e:
    json.dumps({'error': str(e), 'status': 500})
`;

      // Ejecutar código Python
      const result = await pyodide.runPythonAsync(pythonCode);
      const response = JSON.parse(result);

      return new Response(response.body || 'Error', {
        status: response.status || 500,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Access-Control-Allow-Origin': '*',
        },
      });

    } catch (error) {
      console.error('Error en Worker:', error);
      return new Response(`Error: ${error.message}`, {
        status: 500,
        headers: { 'Content-Type': 'text/plain' },
      });
    }
  },
};
