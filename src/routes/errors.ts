import { Hono } from 'hono';
import { drizzle } from 'drizzle-orm/d1';
import { and, eq, gte, lte, like, sql } from 'drizzle-orm';
import { authMiddleware, superAdminMiddleware } from '../middleware/auth';
import { medicationErrors, checklistEntries } from '../db/schema';
import type { Env } from '../index';

const errorsRouter = new Hono<{ Bindings: Env }>();

// Create a medication error record
errorsRouter.post('/', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const body = await c.req.json();

    const {
      checklist_entry_id,
      error_type,
      severity,
      stage,
      description,
      contributing_factors,
      occurred_at,
      detected_at,
    } = body;

    if (!error_type || !severity || !stage) {
      return c.json({ error: 'error_type, severity y stage son obligatorios' }, 400);
    }

    const db = drizzle(c.env.DB);

    const inserted = await db.insert(medicationErrors).values({
      organizationId: currentUser.organizationId,
      reportedByUserId: currentUser.id,
      checklistEntryId: checklist_entry_id || null,
      errorType: error_type,
      severity,
      stage,
      description: description || null,
      contributingFactors: contributing_factors || null,
      occurredAt: occurred_at || null,
      detectedAt: detected_at || null,
    }).returning().get();

    return c.json({ message: 'Error registrado', error: inserted }, 201);
  } catch (err) {
    console.error('Create medication error failed:', err);
    return c.json({ error: 'Error al registrar el evento' }, 500);
  }
});

// List medication errors with filters
errorsRouter.get('/', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const severity = c.req.query('severity');
    const errorType = c.req.query('error_type');
    const stage = c.req.query('stage');
    const startDate = c.req.query('start_date');
    const endDate = c.req.query('end_date');
    const search = c.req.query('search');
    const limit = parseInt(c.req.query('limit') || '100');

    const db = drizzle(c.env.DB);

    let whereClause = and(eq(medicationErrors.organizationId, currentUser.organizationId));

    const conditions: any[] = [eq(medicationErrors.organizationId, currentUser.organizationId)];
    if (severity) conditions.push(eq(medicationErrors.severity, severity));
    if (errorType) conditions.push(eq(medicationErrors.errorType, errorType));
    if (stage) conditions.push(eq(medicationErrors.stage, stage));
    if (startDate) conditions.push(gte(medicationErrors.occurredAt, startDate));
    if (endDate) conditions.push(lte(medicationErrors.occurredAt, endDate));
    if (search) conditions.push(like(medicationErrors.description, `%${search}%`));

    if (conditions.length > 1) {
      // @ts-ignore
      whereClause = and(...conditions);
    }

    const rows = await db.select().from(medicationErrors).where(whereClause).limit(limit).all();

    return c.json({ total: rows.length, errors: rows });
  } catch (err) {
    console.error('List medication errors failed:', err);
    return c.json({ error: 'Error al obtener eventos' }, 500);
  }
});

// Metrics: error rate vs administrations
errorsRouter.get('/metrics', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const days = parseInt(c.req.query('days') || '30');
    const db = drizzle(c.env.DB);

    const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().slice(0, 19).replace('T', ' ');

    // Total administrations (checklist entries) in period
    const checklistRows = await db.select().from(checklistEntries).where(and(
      eq(checklistEntries.organizationId, currentUser.organizationId),
      gte(checklistEntries.fechaHora, since)
    )).all();

    // Medication errors in period
    const errorRows = await db.select().from(medicationErrors).where(and(
      eq(medicationErrors.organizationId, currentUser.organizationId),
      gte(medicationErrors.occurredAt, since)
    )).all();

    const administrations = checklistRows.length;
    const errorsCount = errorRows.length;
    const errorRate = administrations > 0 ? ((errorsCount / administrations) * 100).toFixed(2) : '0.00';

    // Severity breakdown
    const severityTotals: Record<string, number> = {};
    errorRows.forEach(e => {
      severityTotals[e.severity] = (severityTotals[e.severity] || 0) + 1;
    });

    // Error type breakdown
    const typeTotals: Record<string, number> = {};
    errorRows.forEach(e => {
      typeTotals[e.errorType] = (typeTotals[e.errorType] || 0) + 1;
    });

    return c.json({
      period_days: days,
      administrations,
      errors: errorsCount,
      error_rate: errorRate,
      severity_breakdown: severityTotals,
      type_breakdown: typeTotals,
    });
  } catch (err) {
    console.error('Metrics medication errors failed:', err);
    return c.json({ error: 'Error al generar métricas' }, 500);
  }
});

// Timeline (daily counts)
errorsRouter.get('/timeline', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const days = parseInt(c.req.query('days') || '30');
    const db = drizzle(c.env.DB);

    const sinceDate = new Date(Date.now() - days * 86400000);

    const errorRows = await db.select().from(medicationErrors).where(and(
      eq(medicationErrors.organizationId, currentUser.organizationId),
      gte(medicationErrors.occurredAt, sinceDate.toISOString().slice(0, 19).replace('T', ' '))
    )).all();

    const daily: Record<string, { total: number; severe: number }> = {};
    errorRows.forEach(e => {
      const day = (e.occurredAt || '').slice(0, 10);
      if (!daily[day]) daily[day] = { total: 0, severe: 0 };
      daily[day].total += 1;
      if (e.severity === 'severe' || e.severity === 'sentinel') daily[day].severe += 1;
    });

    const timeline = Object.entries(daily).map(([date, v]) => ({ date, total: v.total, severe: v.severe }));
    timeline.sort((a, b) => a.date.localeCompare(b.date));

    return c.json({ period_days: days, timeline });
  } catch (err) {
    console.error('Timeline medication errors failed:', err);
    return c.json({ error: 'Error al generar timeline' }, 500);
  }
});

// Mark resolved
errorsRouter.post('/:id/resolve', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const id = parseInt(c.req.param('id'));
    const body = await c.req.json().catch(() => ({}));

    const db = drizzle(c.env.DB);

    // Verify ownership
    const existing = await db.select().from(medicationErrors).where(and(
      eq(medicationErrors.id, id),
      eq(medicationErrors.organizationId, currentUser.organizationId)
    )).get();

    if (!existing) {
      return c.json({ error: 'Evento no encontrado' }, 404);
    }

    await db.update(medicationErrors)
      .set({ resolved: 1, resolutionNotes: body.resolution_notes || null })
      .where(eq(medicationErrors.id, id))
      .run();

    return c.json({ message: 'Evento marcado como resuelto' });
  } catch (err) {
    console.error('Resolve medication error failed:', err);
    return c.json({ error: 'Error al marcar resuelto' }, 500);
  }
});

// Super admin: global error rate across organizations
errorsRouter.get('/global/summary', superAdminMiddleware, async (c) => {
  try {
    const days = parseInt(c.req.query('days') || '30');
    const since = new Date(Date.now() - days * 86400000).toISOString().slice(0, 19).replace('T', ' ');
    const db = drizzle(c.env.DB);

    const errorRows = await db.select().from(medicationErrors).where(gte(medicationErrors.occurredAt, since)).all();
    const administrationsRows = await db.select().from(checklistEntries).where(gte(checklistEntries.fechaHora, since)).all();

    const errorRate = administrationsRows.length > 0 ? ((errorRows.length / administrationsRows.length) * 100).toFixed(2) : '0.00';

    return c.json({
      period_days: days,
      total_errors: errorRows.length,
      total_administrations: administrationsRows.length,
      global_error_rate: errorRate,
    });
  } catch (err) {
    console.error('Global summary failed:', err);
    return c.json({ error: 'Error al generar resumen global' }, 500);
  }
});

export default errorsRouter;
