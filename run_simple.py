from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="MedCheck - Sistema Simplificado")

@app.get("/")
async def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>MedCheck</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            p {
                color: #666;
                font-size: 18px;
            }
            .success {
                color: #22c55e;
                font-size: 48px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success">✅</div>
            <h1>¡MedCheck está funcionando!</h1>
            <p>Sistema de Verificación de Medicamentos</p>
            <p><small>Versión 1.0 - Simplificada</small></p>
        </div>
    </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "MedCheck funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando MedCheck...")
    print("📍 Abre tu navegador en: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
