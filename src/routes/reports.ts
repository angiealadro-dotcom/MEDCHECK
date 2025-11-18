import { Hono } from 'hono';
import { drizzle } from 'drizzle-orm/d1';
import { eq, and, gte, sql } from 'drizzle-orm';
import { checklistEntries } from '../db/schema';
import { authMiddleware } from '../middleware/auth';
import type { Env } from '../index';

const router = new Hono<{ Bindings: Env }>();

// Get quality indicators (Los 10 Correctos)
router.get('/quality-indicators', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    // Get period from query (default: last 30 days)
    const days = parseInt(c.req.query('days') || '30');
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    // Get all entries for the period
    const entries = await db.select().from(checklistEntries)
      .where(and(
        eq(checklistEntries.organizationId, currentUser.organizationId),
        gte(checklistEntries.fechaHora, startDate.toISOString())
      ))
      .all();

    const total = entries.length;

    if (total === 0) {
      return c.json({
        period_days: days,
        total_entries: 0,
        indicators: {},
      });
    }

    // Calculate compliance for each of the 10 rights
    const calculateCompliance = (field: keyof typeof checklistEntries.$inferSelect) => {
      const compliant = entries.filter(e => e[field] === true).length;
      return {
        compliant,
        total,
        percentage: ((compliant / total) * 100).toFixed(2),
      };
    };

    const indicators = {
      paciente_correcto: calculateCompliance('pacienteCorrecto'),
      medicamento_correcto: calculateCompliance('medicamentoCorrecto'),
      dosis_correcta: calculateCompliance('dosisCorrecta'),
      via_correcta: calculateCompliance('viaCorrecta'),
      hora_correcta: calculateCompliance('horaCorrecta'),
      fecha_vencimiento_verificada: calculateCompliance('fechaVencimientoVerificada'),
      educacion_paciente: calculateCompliance('educacionPaciente'),
      registro_correcto: calculateCompliance('registroCorrecto'),
      alergias_verificadas: calculateCompliance('alergiasVerificadas'),
      responsabilidad_personal: calculateCompliance('responsabilidadPersonal'),
    };

    // Calculate overall compliance (all 10 rights)
    const allRightsCompliant = entries.filter(e =>
      e.pacienteCorrecto &&
      e.medicamentoCorrecto &&
      e.dosisCorrecta &&
      e.viaCorrecta &&
      e.horaCorrecta &&
      e.fechaVencimientoVerificada &&
      e.educacionPaciente &&
      e.registroCorrecto &&
      e.alergiasVerificadas &&
      e.responsabilidadPersonal
    ).length;

    return c.json({
      period_days: days,
      total_entries: total,
      overall_compliance: {
        compliant: allRightsCompliant,
        total,
        percentage: ((allRightsCompliant / total) * 100).toFixed(2),
      },
      indicators,
    });

  } catch (error) {
    console.error('Quality indicators error:', error);
    return c.json({ error: 'Failed to get quality indicators' }, 500);
  }
});

// Get compliance by area
router.get('/compliance-by-area', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    const days = parseInt(c.req.query('days') || '30');
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const entries = await db.select().from(checklistEntries)
      .where(and(
        eq(checklistEntries.organizationId, currentUser.organizationId),
        gte(checklistEntries.fechaHora, startDate.toISOString())
      ))
      .all();

    // Group by area
    const byArea: Record<string, any> = {};

    entries.forEach(entry => {
      const area = entry.area || 'Sin área';
      if (!byArea[area]) {
        byArea[area] = { total: 0, compliant: 0 };
      }
      byArea[area].total++;
      if (entry.cumple) {
        byArea[area].compliant++;
      }
    });

    // Calculate percentages
    const result = Object.entries(byArea).map(([area, data]) => ({
      area,
      total: data.total,
      compliant: data.compliant,
      percentage: ((data.compliant / data.total) * 100).toFixed(2),
    }));

    return c.json({
      period_days: days,
      areas: result,
    });

  } catch (error) {
    console.error('Compliance by area error:', error);
    return c.json({ error: 'Failed to get compliance by area' }, 500);
  }
});

// Get compliance trend (daily)
router.get('/compliance-trend', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    const days = parseInt(c.req.query('days') || '30');
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const entries = await db.select().from(checklistEntries)
      .where(and(
        eq(checklistEntries.organizationId, currentUser.organizationId),
        gte(checklistEntries.fechaHora, startDate.toISOString())
      ))
      .all();

    // Group by date
    const byDate: Record<string, any> = {};

    entries.forEach(entry => {
      const date = entry.fechaHora?.split('T')[0] || 'unknown';
      if (!byDate[date]) {
        byDate[date] = { total: 0, compliant: 0 };
      }
      byDate[date].total++;
      if (entry.cumple) {
        byDate[date].compliant++;
      }
    });

    // Calculate percentages and sort
    const result = Object.entries(byDate)
      .map(([date, data]) => ({
        date,
        total: data.total,
        compliant: data.compliant,
        percentage: ((data.compliant / data.total) * 100).toFixed(2),
      }))
      .sort((a, b) => a.date.localeCompare(b.date));

    return c.json({
      period_days: days,
      trend: result,
    });

  } catch (error) {
    console.error('Compliance trend error:', error);
    return c.json({ error: 'Failed to get compliance trend' }, 500);
  }
});

// Get summary statistics
router.get('/summary', authMiddleware, async (c) => {
  try {
    const currentUser = c.get('user');
    const db = drizzle(c.env.DB);

    const days = parseInt(c.req.query('days') || '30');
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);

    const entries = await db.select().from(checklistEntries)
      .where(and(
        eq(checklistEntries.organizationId, currentUser.organizationId),
        gte(checklistEntries.fechaHora, startDate.toISOString())
      ))
      .all();

    const total = entries.length;
    const compliant = entries.filter(e => e.cumple).length;
    const nonCompliant = total - compliant;

    // Count entries by shift (turno)
    const byShift = entries.reduce((acc, entry) => {
      const shift = entry.turno || 'Sin turno';
      acc[shift] = (acc[shift] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    // Count entries by area
    const byArea = entries.reduce((acc, entry) => {
      const area = entry.area || 'Sin área';
      acc[area] = (acc[area] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return c.json({
      period_days: days,
      total_entries: total,
      compliant: compliant,
      non_compliant: nonCompliant,
      compliance_rate: total > 0 ? ((compliant / total) * 100).toFixed(2) : '0.00',
      by_shift: byShift,
      by_area: byArea,
    });

  } catch (error) {
    console.error('Summary error:', error);
    return c.json({ error: 'Failed to get summary' }, 500);
  }
});

export default router;
