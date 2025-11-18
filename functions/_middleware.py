# Cloudflare Pages Functions Middleware
# Este archivo hace que Cloudflare Pages ejecute nuestra app FastAPI

from app.main import app
from mangum import Mangum

# Mangum es un adaptador ASGI para serverless
handler = Mangum(app, lifespan="off")

async def onRequest(context):
    """
    Cloudflare Pages Functions handler
    """
    return await handler(context.request, context)
