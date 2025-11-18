import { Context, Next } from 'hono';
import { drizzle } from 'drizzle-orm/d1';
import { eq } from 'drizzle-orm';
import { users } from '../db/schema';
import { verifyToken, extractBearerToken, type TokenPayload } from '../utils/auth';
import type { Env } from '../index';

export interface AuthContext {
  user: {
    id: number;
    username: string;
    organizationId: number;
    isAdmin: boolean;
    isSuperAdmin: boolean;
  };
}

export async function authMiddleware(c: Context<{ Bindings: Env }>, next: Next) {
  const authHeader = c.req.header('Authorization');
  const token = extractBearerToken(authHeader);

  if (!token) {
    return c.json({ error: 'No token provided' }, 401);
  }

  const secretKey = c.env.SECRET_KEY;
  const payload = verifyToken(token, secretKey);

  if (!payload) {
    return c.json({ error: 'Invalid or expired token' }, 401);
  }

  // Verificar que el usuario existe y está activo
  const db = drizzle(c.env.DB);
  const user = await db.select().from(users).where(eq(users.id, parseInt(payload.sub))).get();

  if (!user || !user.isActive) {
    return c.json({ error: 'User not found or inactive' }, 401);
  }

  // Agregar información del usuario al contexto
  c.set('user', {
    id: user.id,
    username: user.username,
    organizationId: user.organizationId,
    isAdmin: user.isAdmin,
    isSuperAdmin: user.isSuperAdmin,
  });

  await next();
}

export async function adminMiddleware(c: Context<{ Bindings: Env }>, next: Next) {
  const user = c.get('user') as AuthContext['user'];

  if (!user || !user.isAdmin) {
    return c.json({ error: 'Admin access required' }, 403);
  }

  await next();
}

export async function superAdminMiddleware(c: Context<{ Bindings: Env }>, next: Next) {
  const user = c.get('user') as AuthContext['user'];

  if (!user || !user.isSuperAdmin) {
    return c.json({ error: 'Super admin access required' }, 403);
  }

  await next();
}
