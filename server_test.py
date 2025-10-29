from http.server import HTTPServer, SimpleHTTPRequestHandler

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>MedCheck - Test</title>
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
                .box {
                    background: white;
                    padding: 60px;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                }
                h1 { color: #333; font-size: 48px; margin: 0 0 20px 0; }
                .check { font-size: 80px; color: #22c55e; }
                p { color: #666; font-size: 20px; }
            </style>
        </head>
        <body>
            <div class="box">
                <div class="check">✅</div>
                <h1>¡Funciona!</h1>
                <p>MedCheck está corriendo correctamente</p>
                <p><small>Puerto 8080</small></p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

print("🚀 Servidor de prueba iniciado")
print("📍 Abre tu navegador en: http://127.0.0.1:8080")
print("⏹  Presiona Ctrl+C para detener\n")

server = HTTPServer(('127.0.0.1', 8080), MyHandler)
server.serve_forever()
