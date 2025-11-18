import { Hono } from 'hono';
import { drizzle } from 'drizzle-orm/d1';
import { eq, and, sql } from 'drizzle-orm';
import { organizations, users, checklistEntries } from '../db/schema';
import { hashPassword } from '../utils/auth';
import { authMiddleware, superAdminMiddleware } from '../middleware/auth';
import type { Env } from '../index';

const router = new Hono<{ Bindings: Env }>();

// Register new organization (public endpoint)
router.post('/register', async (c) => {
  try {
    const body = await c.req.json();

    const {
      organization_name,
      organization_slug,
      contact_email,
      contact_phone,
      institution_type,
      country,
      city,
      address,
      admin_username,
      admin_password,
      admin_full_name,
    } = body;

    // Validaciones
    if (!organization_name || !organization_slug || !contact_email || !admin_username || !admin_password) {
      return c.json({ error: 'Missing required fields' }, 400);
    }

    if (admin_password.length < 8) {
      return c.json({ error: 'Password must be at least 8 characters' }, 400);
    }

    const db = drizzle(c.env.DB);

    // Verificar que el slug no exista
    const existingOrg = await db.select().from(organizations)
      .where(eq(organizations.slug, organization_slug))
      .get();

    if (existingOrg) {
      return c.json({ error: 'Organization slug already exists' }, 409);
    }

    // Verificar que el username no exista
    const existingUser = await db.select().from(users)
      .where(eq(users.username, admin_username))
      .get();

    if (existingUser) {
      return c.json({ error: 'Username already exists' }, 409);
    }

    // Crear organización
    const trialEndsAt = new Date();
    trialEndsAt.setDate(trialEndsAt.getDate() + 30);

    const newOrg = await db.insert(organizations).values({
      name: organization_name,
      slug: organization_slug,
      contactEmail: contact_email,
      contactPhone: contact_phone,
      institutionType: institution_type,
      country: country,
      city: city,
      address: address,
      isActive: true,
      plan: 'free',
      maxUsers: 5,
      trialEndsAt: trialEndsAt.toISOString(),
    }).returning().get();

    // Crear usuario admin de la organización
    const hashedPwd = await hashPassword(admin_password);

    const newUser = await db.insert(users).values({
      email: contact_email,
      username: admin_username,
      hashedPassword: hashedPwd,
      fullName: admin_full_name || admin_username,
      isActive: true,
      isAdmin: true,
      isSuperAdmin: false,
      organizationId: newOrg.id,
    }).returning().get();

    return c.json({
      message: 'Organization registered successfully',
      organization: {
        id: newOrg.id,
        name: newOrg.name,
        slug: newOrg.slug,
        plan: newOrg.plan,
        trial_ends_at: newOrg.trialEndsAt,
      },
      admin_user: {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
      },
    }, 201);

  } catch (error) {
    console.error('Organization registration error:', error);
    return c.json({ error: 'Failed to register organization' }, 500);
  }
});

// List all organizations (super admin only)
router.get('/list', authMiddleware, superAdminMiddleware, async (c) => {
  try {
    const db = drizzle(c.env.DB);

    // Get all organizations with user count
    const orgs = await db.select({
      id: organizations.id,
      name: organizations.name,
      slug: organizations.slug,
      contactEmail: organizations.contactEmail,
      contactPhone: organizations.contactPhone,
      institutionType: organizations.institutionType,
      country: organizations.country,
      city: organizations.city,
      isActive: organizations.isActive,
      plan: organizations.plan,
      maxUsers: organizations.maxUsers,
      createdAt: organizations.createdAt,
      trialEndsAt: organizations.trialEndsAt,
      userCount: sql<number>`(SELECT COUNT(*) FROM users WHERE organization_id = ${organizations.id})`,
      activeUserCount: sql<number>`(SELECT COUNT(*) FROM users WHERE organization_id = ${organizations.id} AND is_active = 1)`,
      checklistCount: sql<number>`(SELECT COUNT(*) FROM checklist_entries WHERE organization_id = ${organizations.id})`,
    }).from(organizations).all();

    return c.json({
      total: orgs.length,
      organizations: orgs,
    });

  } catch (error) {
    console.error('List organizations error:', error);
    return c.json({ error: 'Failed to list organizations' }, 500);
  }
});

// Get organization details
router.get('/:id', authMiddleware, async (c) => {
  try {
    const orgId = parseInt(c.req.param('id'));
    const currentUser = c.get('user');

    // Los usuarios normales solo pueden ver su propia organización
    if (!currentUser.isSuperAdmin && currentUser.organizationId !== orgId) {
      return c.json({ error: 'Forbidden' }, 403);
    }

    const db = drizzle(c.env.DB);
    const org = await db.select().from(organizations)
      .where(eq(organizations.id, orgId))
      .get();

    if (!org) {
      return c.json({ error: 'Organization not found' }, 404);
    }

    return c.json(org);

  } catch (error) {
    console.error('Get organization error:', error);
    return c.json({ error: 'Failed to get organization' }, 500);
  }
});

// Toggle organization active status (super admin only)
router.post('/:id/toggle-active', authMiddleware, superAdminMiddleware, async (c) => {
  try {
    const orgId = parseInt(c.req.param('id'));
    const db = drizzle(c.env.DB);

    const org = await db.select().from(organizations)
      .where(eq(organizations.id, orgId))
      .get();

    if (!org) {
      return c.json({ error: 'Organization not found' }, 404);
    }

    const newStatus = !org.isActive;

    await db.update(organizations)
      .set({ isActive: newStatus })
      .where(eq(organizations.id, orgId))
      .run();

    return c.json({
      message: `Organization ${newStatus ? 'activated' : 'deactivated'}`,
      is_active: newStatus,
    });

  } catch (error) {
    console.error('Toggle organization error:', error);
    return c.json({ error: 'Failed to toggle organization status' }, 500);
  }
});

export default router;
