import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { serveStatic } from 'hono/cloudflare-workers';

// Routers
import authRouter from './routes/auth';
import checklistRouter from './routes/checklist';
import organizationsRouter from './routes/organizations';
import reportsRouter from './routes/reports';
import remindersRouter from './routes/reminders';

// Types
export type Env = {
  DB: D1Database;
  SECRET_KEY: string;
  VAPID_PUBLIC_KEY: string;
  VAPID_PRIVATE_KEY: string;
  ENVIRONMENT: string;
  APP_NAME: string;
};

const app = new Hono<{ Bindings: Env }>();

// Middleware
app.use('*', logger());
app.use('*', cors({
  origin: '*',
  allowHeaders: ['Content-Type', 'Authorization'],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
}));

// Static files
app.use('/static/*', serveStatic({ root: './' }));

// Health check
app.get('/health', (c) => {
  return c.json({
    status: 'ok',
    app: c.env.APP_NAME || 'MedCheck',
    environment: c.env.ENVIRONMENT || 'development',
    timestamp: new Date().toISOString(),
  });
});

// API Routes
app.route('/auth', authRouter);
app.route('/checklist', checklistRouter);
app.route('/organizations', organizationsRouter);
app.route('/reports', reportsRouter);
app.route('/reminders', remindersRouter);

// Root - serve landing page
app.get('/', async (c) => {
  return c.html(`
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>MedCheck - Sistema de Gestión de Seguridad del Paciente</title>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        .container {
          background: white;
          padding: 3rem;
          border-radius: 20px;
          box-shadow: 0 20px 60px rgba(0,0,0,0.3);
          max-width: 500px;
          text-align: center;
        }
        h1 { color: #667eea; margin-bottom: 1rem; font-size: 2.5rem; }
        p { color: #666; margin-bottom: 2rem; line-height: 1.6; }
        .btn {
          display: inline-block;
          padding: 1rem 2rem;
          margin: 0.5rem;
          background: #667eea;
          color: white;
          text-decoration: none;
          border-radius: 10px;
          transition: all 0.3s;
          font-weight: 600;
        }
        .btn:hover { background: #764ba2; transform: translateY(-2px); }
        .btn-secondary { background: #48bb78; }
        .btn-secondary:hover { background: #38a169; }
        .features {
          margin-top: 2rem;
          text-align: left;
        }
        .feature {
          margin: 1rem 0;
          padding-left: 1.5rem;
          position: relative;
        }
        .feature:before {
          content: "✓";
          position: absolute;
          left: 0;
          color: #48bb78;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🏥 MedCheck</h1>
        <p>Sistema Multi-Tenant de Gestión de Seguridad del Paciente</p>

        <div class="features">
          <div class="feature">Registro de Los 10 Correctos</div>
          <div class="feature">Dashboard de Indicadores de Calidad</div>
          <div class="feature">Multi-Tenant (Organizaciones Independientes)</div>
          <div class="feature">Reportes y Análisis en Tiempo Real</div>
          <div class="feature">Notificaciones Push</div>
        </div>

        <div style="margin-top: 2rem;">
          <a href="/login" class="btn">Iniciar Sesión</a>
          <a href="/organizations/register" class="btn btn-secondary">Registrar Organización</a>
        </div>

        <p style="margin-top: 2rem; font-size: 0.9rem; color: #999;">
          Powered by Cloudflare Workers + D1
        </p>
      </div>
    </body>
    </html>
  `);
});

// 404 handler
app.notFound((c) => {
  return c.json({ error: 'Not Found' }, 404);
});

// Error handler
app.onError((err, c) => {
  console.error('Error:', err);
  return c.json({
    error: err.message || 'Internal Server Error',
    stack: c.env.ENVIRONMENT === 'development' ? err.stack : undefined,
  }, 500);
});

export default app;
