// Cloudflare Pages Worker for FastAPI
export default {
  async fetch(request, env) {
    // Importar el módulo de Python
    const { runPython } = await import('./pyodide-worker.js');
    
    // Ejecutar la aplicación FastAPI
    return await runPython(request, env);
  }
}
