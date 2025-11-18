import { Hono } from 'hono';
import { drizzle } from 'drizzle-orm/d1';
import { eq } from 'drizzle-orm';
import { users } from '../db/schema';
import { hashPassword, verifyPassword, createAccessToken } from '../utils/auth';
import { authMiddleware } from '../middleware/auth';
import type { Env } from '../index';

const router = new Hono<{ Bindings: Env }>();

// Login endpoint
router.post('/login', async (c) => {
  try {
    const { username, password } = await c.req.json();

    if (!username || !password) {
      return c.json({ error: 'Username and password are required' }, 400);
    }

    const db = drizzle(c.env.DB);
    const user = await db.select().from(users).where(eq(users.username, username)).get();

    if (!user) {
      return c.json({ error: 'Invalid credentials' }, 401);
    }

    if (!user.isActive) {
      return c.json({ error: 'User account is inactive' }, 401);
    }

    const isValidPassword = await verifyPassword(password, user.hashedPassword);

    if (!isValidPassword) {
      return c.json({ error: 'Invalid credentials' }, 401);
    }

    const accessToken = createAccessToken(user, c.env.SECRET_KEY);

    return c.json({
      access_token: accessToken,
      token_type: 'bearer',
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        full_name: user.fullName,
        is_admin: user.isAdmin,
        is_super_admin: user.isSuperAdmin,
        organization_id: user.organizationId,
      },
    });
  } catch (error) {
    console.error('Login error:', error);
    return c.json({ error: 'Login failed' }, 500);
  }
});

// Get current user info
router.get('/me', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    const user = await db.select().from(users).where(eq(users.id, currentUser.id)).get();

    if (!user) {
      return c.json({ error: 'User not found' }, 404);
    }

    return c.json({
      id: user.id,
      username: user.username,
      email: user.email,
      full_name: user.fullName,
      is_active: user.isActive,
      is_admin: user.isAdmin,
      is_super_admin: user.isSuperAdmin,
      organization_id: user.organizationId,
    });
  } catch (error) {
    console.error('Get user error:', error);
    return c.json({ error: 'Failed to get user info' }, 500);
  }
});

// Token validation endpoint
router.post('/verify', async (c) => {
  try {
    const { token } = await c.req.json();

    if (!token) {
      return c.json({ valid: false, error: 'Token is required' }, 400);
    }

    const { verifyToken } = await import('../utils/auth');
    const payload = verifyToken(token, c.env.SECRET_KEY);

    if (!payload) {
      return c.json({ valid: false, error: 'Invalid or expired token' });
    }

    return c.json({
      valid: true,
      payload: {
        user_id: payload.sub,
        username: payload.username,
        organization_id: payload.organizationId,
        is_admin: payload.isAdmin,
        is_super_admin: payload.isSuperAdmin,
      },
    });
  } catch (error) {
    console.error('Token verification error:', error);
    return c.json({ valid: false, error: 'Token verification failed' }, 500);
  }
});

export default router;
