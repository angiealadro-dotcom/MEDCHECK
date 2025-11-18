import { Hono } from 'hono';
import { drizzle } from 'drizzle-orm/d1';
import { eq, and, gte, lte, desc } from 'drizzle-orm';
import { checklistEntries } from '../db/schema';
import { authMiddleware } from '../middleware/auth';
import type { Env } from '../index';

const router = new Hono<{ Bindings: Env }>();

// Create checklist entry
router.post('/', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const body = await c.req.json();

    const {
      area,
      turno,
      protocolo_etapa,
      item,
      cumple,
      observaciones,
      // Los 10 Correctos
      paciente_correcto,
      medicamento_correcto,
      dosis_correcta,
      via_correcta,
      hora_correcta,
      fecha_vencimiento_verificada,
      educacion_paciente,
      registro_correcto,
      alergias_verificadas,
      responsabilidad_personal,
    } = body;

    const db = drizzle(c.env.DB);

    const newEntry = await db.insert(checklistEntries).values({
      area,
      turno,
      protocoloEtapa: protocolo_etapa,
      item,
      cumple,
      observaciones,
      usuario: currentUser.username,
      pacienteCorrecto: paciente_correcto,
      medicamentoCorrecto: medicamento_correcto,
      dosisCorrecta: dosis_correcta,
      viaCorrecta: via_correcta,
      horaCorrecta: hora_correcta,
      fechaVencimientoVerificada: fecha_vencimiento_verificada,
      educacionPaciente: educacion_paciente,
      registroCorrecto: registro_correcto,
      alergiasVerificadas: alergias_verificadas,
      responsabilidadPersonal: responsabilidad_personal,
      organizationId: currentUser.organizationId,
    }).returning().get();

    return c.json(newEntry, 201);

  } catch (error) {
    console.error('Create checklist error:', error);
    return c.json({ error: 'Failed to create checklist entry' }, 500);
  }
});

// Get checklist entries (filtered by organization)
router.get('/', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    // Query parameters
    const limit = parseInt(c.req.query('limit') || '100');
    const offset = parseInt(c.req.query('offset') || '0');
    const area = c.req.query('area');
    const startDate = c.req.query('start_date');
    const endDate = c.req.query('end_date');

    let query = db.select().from(checklistEntries)
      .where(eq(checklistEntries.organizationId, currentUser.organizationId))
      .orderBy(desc(checklistEntries.fechaHora));

    // Apply filters
    if (area) {
      query = query.where(and(
        eq(checklistEntries.organizationId, currentUser.organizationId),
        eq(checklistEntries.area, area)
      ));
    }

    if (startDate) {
      query = query.where(and(
        eq(checklistEntries.organizationId, currentUser.organizationId),
        gte(checklistEntries.fechaHora, startDate)
      ));
    }

    if (endDate) {
      query = query.where(and(
        eq(checklistEntries.organizationId, currentUser.organizationId),
        lte(checklistEntries.fechaHora, endDate)
      ));
    }

    const entries = await query.limit(limit).offset(offset).all();

    return c.json({
      total: entries.length,
      limit,
      offset,
      data: entries,
    });

  } catch (error) {
    console.error('Get checklist entries error:', error);
    return c.json({ error: 'Failed to get checklist entries' }, 500);
  }
});

// Get single checklist entry
router.get('/:id', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const entryId = parseInt(c.req.param('id'));
    const db = drizzle(c.env.DB);

    const entry = await db.select().from(checklistEntries)
      .where(and(
        eq(checklistEntries.id, entryId),
        eq(checklistEntries.organizationId, currentUser.organizationId)
      ))
      .get();

    if (!entry) {
      return c.json({ error: 'Checklist entry not found' }, 404);
    }

    return c.json(entry);

  } catch (error) {
    console.error('Get checklist entry error:', error);
    return c.json({ error: 'Failed to get checklist entry' }, 500);
  }
});

// Update checklist entry
router.put('/:id', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const entryId = parseInt(c.req.param('id'));
    const body = await c.req.json();
    const db = drizzle(c.env.DB);

    // Verify entry exists and belongs to user's organization
    const existingEntry = await db.select().from(checklistEntries)
      .where(and(
        eq(checklistEntries.id, entryId),
        eq(checklistEntries.organizationId, currentUser.organizationId)
      ))
      .get();

    if (!existingEntry) {
      return c.json({ error: 'Checklist entry not found' }, 404);
    }

    const updatedEntry = await db.update(checklistEntries)
      .set({
        area: body.area,
        turno: body.turno,
        protocoloEtapa: body.protocolo_etapa,
        item: body.item,
        cumple: body.cumple,
        observaciones: body.observaciones,
        pacienteCorrecto: body.paciente_correcto,
        medicamentoCorrecto: body.medicamento_correcto,
        dosisCorrecta: body.dosis_correcta,
        viaCorrecta: body.via_correcta,
        horaCorrecta: body.hora_correcta,
        fechaVencimientoVerificada: body.fecha_vencimiento_verificada,
        educacionPaciente: body.educacion_paciente,
        registroCorrecto: body.registro_correcto,
        alergiasVerificadas: body.alergias_verificadas,
        responsabilidadPersonal: body.responsabilidad_personal,
      })
      .where(eq(checklistEntries.id, entryId))
      .returning()
      .get();

    return c.json(updatedEntry);

  } catch (error) {
    console.error('Update checklist entry error:', error);
    return c.json({ error: 'Failed to update checklist entry' }, 500);
  }
});

// Delete checklist entry
router.delete('/:id', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const entryId = parseInt(c.req.param('id'));
    const db = drizzle(c.env.DB);

    // Only admins can delete
    if (!currentUser.isAdmin) {
      return c.json({ error: 'Admin access required' }, 403);
    }

    // Verify entry exists and belongs to user's organization
    const existingEntry = await db.select().from(checklistEntries)
      .where(and(
        eq(checklistEntries.id, entryId),
        eq(checklistEntries.organizationId, currentUser.organizationId)
      ))
      .get();

    if (!existingEntry) {
      return c.json({ error: 'Checklist entry not found' }, 404);
    }

    await db.delete(checklistEntries)
      .where(eq(checklistEntries.id, entryId))
      .run();

    return c.json({ message: 'Checklist entry deleted successfully' });

  } catch (error) {
    console.error('Delete checklist entry error:', error);
    return c.json({ error: 'Failed to delete checklist entry' }, 500);
  }
});

export default router;
