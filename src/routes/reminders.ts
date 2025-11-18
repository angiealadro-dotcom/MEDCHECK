import { Hono } from 'hono';
import { drizzle } from 'drizzle-orm/d1';
import { eq, and, lte, isNull } from 'drizzle-orm';
import { reminders } from '../db/schema';
import { authMiddleware } from '../middleware/auth';
import type { Env } from '../index';

const router = new Hono<{ Bindings: Env }>();

// Create reminder
router.post('/', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const body = await c.req.json();

    const { title, body: reminderBody, scheduled_at } = body;

    if (!title || !scheduled_at) {
      return c.json({ error: 'Title and scheduled_at are required' }, 400);
    }

    const db = drizzle(c.env.DB);

    const newReminder = await db.insert(reminders).values({
      userId: currentUser.id,
      title,
      body: reminderBody,
      scheduledAt: scheduled_at,
      active: true,
      organizationId: currentUser.organizationId,
    }).returning().get();

    return c.json(newReminder, 201);

  } catch (error) {
    console.error('Create reminder error:', error);
    return c.json({ error: 'Failed to create reminder' }, 500);
  }
});

// Get user's reminders
router.get('/', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    const userReminders = await db.select().from(reminders)
      .where(and(
        eq(reminders.userId, currentUser.id),
        eq(reminders.organizationId, currentUser.organizationId)
      ))
      .all();

    return c.json({ reminders: userReminders });

  } catch (error) {
    console.error('Get reminders error:', error);
    return c.json({ error: 'Failed to get reminders' }, 500);
  }
});

// Get pending reminders (for processing)
router.get('/pending', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    const now = new Date().toISOString();

    const pendingReminders = await db.select().from(reminders)
      .where(and(
        eq(reminders.userId, currentUser.id),
        eq(reminders.active, true),
        isNull(reminders.sentAt),
        lte(reminders.scheduledAt, now)
      ))
      .all();

    return c.json({ reminders: pendingReminders });

  } catch (error) {
    console.error('Get pending reminders error:', error);
    return c.json({ error: 'Failed to get pending reminders' }, 500);
  }
});

// Mark reminder as sent
router.post('/:id/mark-sent', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const reminderId = parseInt(c.req.param('id'));
    const db = drizzle(c.env.DB);

    // Verify reminder belongs to user
    const reminder = await db.select().from(reminders)
      .where(and(
        eq(reminders.id, reminderId),
        eq(reminders.userId, currentUser.id)
      ))
      .get();

    if (!reminder) {
      return c.json({ error: 'Reminder not found' }, 404);
    }

    await db.update(reminders)
      .set({ sentAt: new Date().toISOString() })
      .where(eq(reminders.id, reminderId))
      .run();

    return c.json({ message: 'Reminder marked as sent' });

  } catch (error) {
    console.error('Mark reminder sent error:', error);
    return c.json({ error: 'Failed to mark reminder as sent' }, 500);
  }
});

// Delete reminder
router.delete('/:id', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const reminderId = parseInt(c.req.param('id'));
    const db = drizzle(c.env.DB);

    // Verify reminder belongs to user
    const reminder = await db.select().from(reminders)
      .where(and(
        eq(reminders.id, reminderId),
        eq(reminders.userId, currentUser.id)
      ))
      .get();

    if (!reminder) {
      return c.json({ error: 'Reminder not found' }, 404);
    }

    await db.delete(reminders)
      .where(eq(reminders.id, reminderId))
      .run();

    return c.json({ message: 'Reminder deleted successfully' });

  } catch (error) {
    console.error('Delete reminder error:', error);
    return c.json({ error: 'Failed to delete reminder' }, 500);
  }
});

export default router;
